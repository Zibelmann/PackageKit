#!/usr/bin/python
# {{{
# Licensed under the GNU General Public License Version 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Copyright (C) 2007 Ken VanDine <ken@vandine.org>
# Copyright (C) 2008 Richard Hughes <richard@hughsie.com>
# Copyright (C) 2008 Andres Vargas <zodman@foresightlinux.org>
# }}}

import sys
import os
import re
from conary import errors
from conary.deps import deps
from conary import dbstore, queryrep, versions, updatecmd
from conary.local import database
from conary import trove
from conary.conaryclient import cmdline
from conary.lib import util

from packagekit.backend import *
from packagekit.package import *
from packagekit.progress import PackagekitProgress
from conaryCallback import UpdateCallback, GetUpdateCallback
from conaryCallback import RemoveCallback, UpdateSystemCallback
from conaryFilter import *
from XMLCache import XMLCache as Cache
from conaryInit import *

from conary import conarycfg, conaryclient
from conarypk import ConaryPk
from pkConaryLog import *

pkpackage = PackagekitPackage()
sys.excepthook = util.genExcepthook()

def ExceptionHandler(func):
    return func
    def display(error):
        return str(error).replace('\n', ' ').replace("\t",'')
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        #except Exception:
        #    raise
        except conaryclient.NoNewTrovesError:
            return
        except conaryclient.DepResolutionFailure, e:
            self.error(ERROR_DEP_RESOLUTION_FAILED, display(e), exit=True)
        except conaryclient.UpdateError, e:
            # FIXME: Need a enum for UpdateError
            self.error(ERROR_UNKNOWN, display(e), exit=True)
        except Exception, e:
            self.error(ERROR_UNKNOWN, display(e), exit=True)
    return wrapper
def _format_str(str):
    """
    Convert a multi line string to a list separated by ';'
    """
    if str:
        lines = str.split('\n')
        return ";".join(lines)
    else:
        return ""

def _format_list(lst):
    """
    Convert a multi line string to a list separated by ';'
    """
    if lst:
        return ";".join(lst)
    else:
        return ""

class PackageKitConaryBackend(PackageKitBaseBackend):
    # Packages there require a reboot
    rebootpkgs = ("kernel", "glibc", "hal", "dbus")

    def __init__(self, args):
        PackageKitBaseBackend.__init__(self, args)

        # conary configurations
        conary = ConaryPk()
        self.cfg = conary.cfg
        self.client = conary.cli
        self.conary = conary
        self.callback = UpdateCallback(self, self.cfg)
        self.client.setUpdateCallback(self.callback)

    def _freezeData(self, version, flavor):
        frzVersion = version.freeze()
        frzFlavor = flavor.freeze()
        return ','.join([frzVersion, frzFlavor])

    def _thawData(self, frzVersion, frzFlavor ):
        version = versions.ThawVersion(frzVersion)
        flavor = deps.ThawFlavor(frzFlavor)
        return version, flavor

    def _get_arch(self, flavor):
        isdep = deps.InstructionSetDependency
        arches = [ x.name for x in flavor.iterDepsByClass(isdep) ]
        if not arches:
            arches = [ 'noarch' ]
        return ','.join(arches)

    @ExceptionHandler
    def check_installed(self, troveTuple):
        log.debug("============check installed =========")
        result = self.conary.query(troveTuple[0])
        if result:
            installed = INFO_INSTALLED
        else:
            installed = INFO_AVAILABLE
        return installed

    @ExceptionHandler
    def get_package_id(self, name, versionObj, flavor):

        version = versionObj.trailingRevision()


        cache = Cache()
        pkg  = cache.resolve(name)
        arch = self._get_arch(flavor)
        #data = versionObj.asString() + "#"
        data = ""
        if pkg:
            if "shortDesc" in pkg:
                data = pkg['shortDesc'].decode("UTF")
                if data == "." or data == "":
                    data = name.replace("-",' ').capitalize()
                
        return pkpackage.get_package_id(name, version, arch, data)

    @ExceptionHandler
    def get_package_from_id(self, package_id):
        """ package_id(string) =
        "dpaster;0.1-3-1;x86;Summary"
        """
        log.info("=========== get package from package_id ======================")
        name, verString, archString, data =  pkpackage.get_package_from_id(package_id)
        trove = self.conary.request_query(name)
        if trove:
            return trove
        else:
            return cli.query(name)

    def _do_search(self, filters, searchlist, where = "name"):
        """
         searchlist(str)ist as the package for search like
         filters(str) as the filter
        """
        fltlist = filters.split(';')
        if where != "name" and where != "details" and where != "group":
            log.info("where %s" % where)
            self.error(ERROR_UNKNOWN, "DORK---- search where not found")
        cache = Cache()
        log.debug((searchlist, where))
        log.info("searching  on cache... ")
        pkgList = cache.search(searchlist, where )
        log.info("end searching on cache... ")

        if len(pkgList) > 0 :
            #for i in troveTupleList:
            #    log.info("FOUND!!!!!! %s " % i["name"] )
            log.info("FOUND (%s) elements " % len(pkgList) )
            troveTupleList = pkgList
        else:
            log.info("NOT FOUND %s " % searchlist )
            troveTupleList = self.conary.query(searchlist)
            log.info(troveTupleList)
            if troveTupleList:
                troveTupleList = cache.convertTroveToDict( pkgList ) 
                log.info("convert")
                log.info(troveTupleList)

        self._resolve_list( fltlist, troveTupleList  )

    def _get_update(self, applyList, cache=True):
        from conary.conaryclient.update import NoNewTrovesError,DepResolutionFailure
        updJob = self.client.newUpdateJob()
        try:
            log.info("prepare updateJOb...............")
            suggMap = self.client.prepareUpdateJob(updJob, applyList)
            log.info("end prepare updateJOB..............")
        except NoNewTrovesError:
            self.error(ERROR_NO_PACKAGES_TO_UPDATE, "No new apps were found")
        except DepResolutionFailure as error :
            log.info(error.getErrorMessage())
            deps =  error.cannotResolve
            dep_package = [ str(i[0][0]).split(":")[0] for i in deps ]
            self.error(ERROR_DEP_RESOLUTION_FAILED,  "This package depends of:  %s" % " ,".join(set(dep_package)))
        if cache:
            Cache().cacheUpdateJob(applyList, updJob)
        return updJob, suggMap

    def _do_update(self, applyList):
        log.info("========= _do_update ========")
        jobPath = Cache().checkCachedUpdateJob(applyList)
        log.info(jobPath)
        if jobPath:
            updJob = self.client.newUpdateJob()
            try:
                updJob.thaw(jobPath)
            except IOError, err:
                updJob = None
        else:
            updJob,suggMap = self._get_update(applyList, cache=False)
        self.allow_cancel(False)
        try:
            restartDir = self.client.applyUpdateJob(updJob)
        except errors.InternalConaryError:
            self.error(ERROR_NO_PACKAGES_TO_UPDATE,"get-updates first and then update sytem")
        except trove.TroveIntegrityError: 
            self.error(ERROR_NO_PACKAGES_TO_UPDATE,"run get-updates again")
        return updJob

    def _get_package_update(self, name, version, flavor):
        if name.startswith('-'):
            applyList = [(name, (version, flavor), (None, None), False)]
        else:
            applyList = [(name, (None, None), (version, flavor), True)]
        return self._get_update(applyList)

    def _do_package_update(self, name, version, flavor):
        if name.startswith('-'):
            applyList = [(name, (version, flavor), (None, None), False)]
        else:
            applyList = [(name, (None, None), (version, flavor), True)]
        return self._do_update(applyList)

    def _resolve_list(self, filters, pkgsList ):
        log.info("======= _resolve_list =====")
        specList = []
        app_found = []
        for pkg in pkgsList:
            name = pkg["name"]
            log.info(name)
            trove = name, None , None 
            app_found.append(name)
            specList.append( trove  )
        trovesList = self.client.db.findTroves( None ,specList, allowMissing = True)
        log.info("Packages installed .... %s " % len(trovesList))
        pkgFilter = ConaryFilter(filters)
        #troves = trovesList.values()
        for trove in specList:
            if trove in trovesList:
                t = trovesList[trove]
                log.info(t)
                pkgFilter.add_installed( t )
                app_found.remove(t[0][0])

        log.info("Packages availables ........ %s " % len(app_found) )
        specList = []
        for i in set(app_found):
            trove = i, None, self.conary.flavor
            specList.append(trove)
        trovelist = self.client.repos.findTroves(self.conary.default_label, specList, allowMissing=True)

        for trove in specList:
            t = trovelist[trove]
            log.info(t)
            pkgFilter.add_available( t )

       
        package_list = pkgFilter.post_process()

        self._show_package_list(package_list)
 
    @ExceptionHandler
    def resolve(self, filters, package ):
        """ 
            @filters  (list)  list of filters
            @package (list ) list with packages name for resolve
        """
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)
        log.info("filters: %s package:%s " % (filters, package))

        cache = Cache()
        pkg_dict = cache.resolve( package[0] )
        log.info("doing a resolve")
        solved = False
        if pkg_dict is None:
            # verifica si esta en repositorios
            log.info("doing a rq")
            troveTuple = self.conary.query(package[0])
            if not troveTuple:
                return 
                #self.error(ERROR_INTERNAL_ERROR, "Package Not found")
                #log.info("PackageNot found on resolve")

            else:
                pkg_dict = {}
                pkg_dict["name"] =  troveTuple[0][0]
                solved = True
            

        filter = ConaryFilter(filters)

        installed = filter._pkg_is_installed( pkg_dict["name"] )
        
        if solved == False:
            troveTuple =  self.conary.request_query( package[0] )

        log.info(">>> %s" % troveTuple)

        if installed:
            filter.add_installed( troveTuple  )
        else:
            filter.add_available( troveTuple )

        package_list = filter.post_process()
        log.info("package_list %s" % package_list)
        self._show_package_list(package_list)

    def _show_package_list(self, lst):
        """ 
            HOW its showed on packageKit
            @lst(list(tuple) = [ ( troveTuple, status ) ]
        """
        for troveTuple, status in lst:
            # take the basic info
            name = troveTuple[0]
            version = troveTuple[1]
            flavor = troveTuple[2]
            # get the string id from packagekit 
            package_id = self.get_package_id(name, version, flavor)
            
            # split the list for get Determine info
            summary = package_id.split(";")
            meta = summary[3]
            log.info("====== show the package  %s" % name )
            self.package(package_id, status, meta )

    @ExceptionHandler
    def search_group(self, options, searchlist):
        '''
        Implement the {backend}-search-group functionality
        '''
        log.info("============= search_group ========")
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_QUERY)
        log.info("options: %s searchlist:%s "%(options, searchlist))
        self._do_search(options, searchlist, 'group')


    @ExceptionHandler
    def search_name(self, options, searchlist):
        '''
        Implement the {backend}-search-name functionality
        '''
        log.info("============= search_name ========")
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_QUERY)
        log.info("options: %s searchlist:%s "%(options, searchlist))
        self._do_search(options, searchlist, 'name')

    @ExceptionHandler
    def search_details(self, options, search):
        '''
        Implement the {backend}-search-details functionality
        '''
        log.info("============= search_details ========")
        self.allow_cancel(True)
        #self.percentage(None)
        self.status(STATUS_QUERY)
        log.info("options: %s searchlist:%s "%(options, search))
        self._do_search(options, search, 'details' )
       

    def get_requires(self, filters, package_ids, recursive_text):
        pass

    @ExceptionHandler
    def get_depends(self, filters, package_ids, recursive_text):
        name, version, flavor, installed = self._findPackage(package_ids[0])

        if name:
            if installed == INFO_INSTALLED:
                self.error(ERROR_PACKAGE_ALREADY_INSTALLED, 'Package already installed')

            else:
                updJob, suggMap = self._get_package_update(name, version,
                                                           flavor)
                for what, need in suggMap:
                    package_id = self.get_package_id(need[0], need[1], need[2])
                    depInstalled = self.check_installed(need[0])
                    if depInstalled == INFO_INSTALLED:
                        self.package(package_id, INFO_INSTALLED, '')
                    else:
                        self.package(package_id, INFO_AVAILABLE, '')
        else:
            self.error(ERROR_PACKAGE_ALREADY_INSTALLED, 'Package was not found')

    @ExceptionHandler
    def get_files(self, package_ids):
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)
        package_id = package_ids[0]
        def _get_files(troveSource, n, v, f):
            files = []
            troves = [(n, v, f)]
            trv = troveSource.getTrove(n, v, f)
            troves.extend([ x for x in trv.iterTroveList(strongRefs=True)
                                if troveSource.hasTrove(*x)])
            for n, v, f in troves:
                for (pathId, path, fileId, version, filename) in \
                    troveSource.iterFilesInTrove(n, v, f, sortByPath = True,
                                                 withFiles = True):
                    files.append(path)
            return files
        
        for package in package_id.split("&"):
            log.info(package)
            name, version, flavor, installed = self._findPackage(package)

            if installed == INFO_INSTALLED:
                files = _get_files(self.client.db, name, version, flavor)
            else:
                files = _get_files(self.client.repos, name, version, flavor)

            self.files(package_id, ';'.join(files))

    @ExceptionHandler
    def update_system(self):
        self.allow_cancel(True)
        self.status(STATUS_UPDATE)
        self.client.setUpdateCallback( UpdateSystemCallback(self, self.cfg) )
        updateItems = self.client.fullUpdateItemList()
        [ log.info(i) for i,ver,flav in updateItems]
        applyList = [ (x[0], (None, None), x[1:], True) for x in updateItems ]

        log.info(">>>>>>>>>> get update >>>>>>>>>>>>")
        #self._get_update(applyList)
        log.info(">>>>>>>>>> DO Update >>>>>>>>>>>>")
        jobs = self._do_update(applyList)
        log.info(">>>>>>>>>>END DO Update >>>>>>>>>>>>")
        log.info(jobs)
        self.client.setUpdateCallback(self.callback )

#    @ExceptionHandler
    def refresh_cache(self):
        #log.debug("refresh-cache command ")
    #    self.percentage()

        self.status(STATUS_REFRESH_CACHE)
        cache = Cache()
        cache.refresh()

    @ExceptionHandler
    def update(self, package_ids):
        '''
        Implement the {backend}-update functionality
        '''
        self.allow_cancel(True)
        self.percentage(0)
        self.status(STATUS_RUNNING)
        
        for package in package_ids.split(" "):
            name, version, flavor, installed = self._findPackage(package)
            if name:
                cli = ConaryPk()
                cli.update(name)
            else:
                self.error(ERROR_PACKAGE_ALREADY_INSTALLED, 'No available updates')

    def install_packages(self, package_ids):
        """
            alias of update_packages
        """
        self.update_packages(package_ids)

    @ExceptionHandler
    def update_packages(self, package_ids):
        '''
        Implement the {backend}-{install, update}-packages functionality
        '''

        for package_id in package_ids:
            name, version, flavor, installed = self._findPackage(package_id)
            log.info((name, version, flavor, installed ))

            self.allow_cancel(True)
            self.percentage(0)
            self.status(STATUS_RUNNING)

            if name:
                if installed == INFO_INSTALLED:
                    self.error(ERROR_PACKAGE_ALREADY_INSTALLED,
                        'Package already installed')

                self.status(STATUS_INSTALL)
                log.info(">>> Prepare Update")
                self._get_package_update(name, version, flavor)
                log.info(">>> end Prepare Update")
                self._do_package_update(name, version, flavor)
            else:
                self.error(ERROR_PACKAGE_ALREADY_INSTALLED, 'Package was not found')

    @ExceptionHandler
    def remove_packages(self, allowDeps, package_ids):
        '''
        Implement the {backend}-remove-packages functionality
        '''
        self.allow_cancel(True)
        self.percentage(0)
        self.status(STATUS_RUNNING)
        log.info("========== Remove Packages ============ ")
        log.info( allowDeps ) 
        self.client.setUpdateCallback(RemoveCallback(self, self.cfg))
        errors = ""
        #for package_id in package_ids.split('%'):
        for package_id in package_ids:
            name, version, flavor, installed = self._findPackage(package_id)
            if name:
                if not installed == INFO_INSTALLED:
                    self.error(ERROR_PACKAGE_NOT_INSTALLED, 'The package %s is not installed' % name)

                name = '-%s' % name
                self.status(STATUS_REMOVE)
                self._get_package_update(name, version, flavor)
                callback = self.client.getUpdateCallback()
                if callback.error:
                    self.error(ERROR_DEP_RESOLUTION_FAILED,', '.join(callback.error))
                        
                self._do_package_update(name, version, flavor)
            else:
                self.error(ERROR_PACKAGE_ALREADY_INSTALLED, 'The package was not found')
        self.client.setUpdateCallback(self.callback)

    def _get_metadata(self, package_id, field):
        '''
        Retrieve metadata from the repository and return result
        field should be one of:
                bibliography
                url
                notes
                crypto
                licenses
                shortDesc
                longDesc
                categories
        '''

        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_QUERY)
        n, v, f = self.get_package_from_id(package_id)
        trvList = self.client.repos.findTrove(self.cfg.installLabelPath,
                                     (n, v, f),
                                     defaultFlavor = self.cfg.flavor)

        troves = self.client.repos.getTroves(trvList, withFiles=False)
        result = ''
        for trove in troves:
            result = trove.getMetadata()[field]
        return result

    def _get_update_extras(self, package_id):
        notice = self._get_metadata(package_id, 'notice') or " "
        urls = {'jira':[], 'cve' : [], 'vendor': []}
        if notice:
            # Update Details
            desc = notice['description']
            # Update References (Jira, CVE ...)
            refs = notice['references']
            if refs:
                for ref in refs:
                    typ = ref['type']
                    href = ref['href']
                    title = ref['title']
                    if typ in ('jira', 'cve') and href != None:
                        if title == None:
                            title = ""
                        urls[typ].append("%s;%s" % (href, title))
                    else:
                        urls['vendor'].append("%s;%s" % (ref['href'], ref['title']))

            # Reboot flag
            if notice.get_metadata().has_key('reboot_suggested') and notice['reboot_suggested']:
                reboot = 'system'
            else:
                reboot = 'none'
            return _format_str(desc), urls, reboot
        else:
            return "", urls, "none"

    def _check_for_reboot(self, name):
        if name in self.rebootpkgs:
            self.require_restart(RESTART_SYSTEM, "")

    @ExceptionHandler
    def get_update_detail(self, package_ids):
        '''
        Implement the {backend}-get-update_detail functionality
        '''
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)
        package_id = package_ids[0]
        name, version,arch,summary  = pkpackage.get_package_from_id(package_id)
        cache = Cache()
        pkgDict = cache.resolve(name)
        #update = self._get_updated(pkg)
        update = None
        obsolete = None
        #desc, urls, reboot = self._get_update_extras(package_id)
        #cve_url = _format_list(urls['cve'])
        cve_url = None
        #bz_url = _format_list(urls['jira'])
        bz_url = None
        #vendor_url = _format_list(urls['vendor'])
        if pkgDict:
            if "url" in pkgDict:
                vendor_url = pkgDict["url"]
            else:
                vendor_url = ""
            if  name in self.rebootpkgs:
                reboot = True
            else:
                reboot = None
            if "longDesc" in pkgDict:
                desc = pkgDict["longDesc"]
            else:
                desc = ""
            self.update_detail(package_id, update, obsolete, vendor_url, bz_url, cve_url,
                    reboot, desc, changelog="", state="", issued="", updated=None)

   # @ExceptionHandler
    def get_details(self, package_ids):
        '''
        Print a detailed description for a given package
        '''
        self.allow_cancel(True)
        self.percentage(None)
        self.status(STATUS_INFO)

        log.info("========== get_details =============")
        log.info(package_ids[0])
        package_id = package_ids[0]
        #name, version, flavor, installed = self._findPackage(package_id)
        
        summary = package_id.split(";")
        log.info("====== geting summary")
        log.info(summary)
        name,version,arch,data = pkpackage.get_package_from_id(package_id)
        cache = Cache()
        pkgDict = cache.resolve(name)
        
        if name and pkgDict:
            shortDesc = ""
            longDesc = ""
            url = "http://www.foresightlinux.org/packages/%s.html" % name
            categories  = None

            if "shortDesc" in pkgDict:
                shortDesc = pkgDict["shortDesc"] 
            if "longDesc" in pkgDict:
                longDesc = pkgDict["longDesc"]
            if "url" in pkgDict:
                url = pkgDict["url"]
            if "category" in pkgDict:
                categories =  Cache().getGroup( pkgDict['category'])
            # Package size goes here, but I don't know how to find that for conary packages.
            self.details(package_id, None, categories, longDesc, url, 0)

    def _show_package(self, name, version, flavor, status):
        '''  Show info about package'''
        log.info(name)
        package_id = self.get_package_id(name, version, flavor)
        summary = package_id.split(";")
        if summary[3].split("#")[1]:
            metadata = eval(summary[3].split("#")[1])
        else:
            metadata = {}
        if metadata.has_key("shortDesc"):
            meta = metadata["shortDesc"]
        else:
            meta = " "
        self.package(package_id, status, meta)

    def _get_status(self, notice):
        # We need to figure out how to get this info, this is a place holder
        #ut = notice['type']
        # TODO : Add more types to check
        #if ut == 'security':
        #    return INFO_SECURITY
        #else:
        #    return INFO_NORMAL
        return INFO_NORMAL

    @ExceptionHandler
    def get_updates(self, filters):
        self.allow_cancel(True)
        self.percentage(0)
        self.status(STATUS_INFO)
        getUpdateC= GetUpdateCallback(self,self.cfg)
        self.client.setUpdateCallback(getUpdateC)
        log.info("callback changed")
        log.info("============== get_updates ========================")
        cli = ConaryPk()
        log.info("get fullUpdateItemList")
        updateItems =cli.cli.fullUpdateItemList()
#        updateItems = cli.cli.getUpdateItemList()
        applyList = [ (x[0], (None, None), x[1:], True) for x in updateItems ]
        log.info("_get_update ....")
        self.status(STATUS_RUNNING)
        updJob, suggMap = self._get_update(applyList)
        log.info("_get_update ....end.")

        jobLists = updJob.getJobs()
        log.info("getting JobLists...........")

        for num, job in enumerate(jobLists):
            name = job[0][0]

            # On an erase display the old version/flavor information.
            version = job[0][2][0]
            if version is None:
                version = job[0][1][0]

            flavor = job[0][2][1]
            if flavor is None:
                flavor = job[0][1][1]
            if name in self.rebootpkgs:
                info = INFO_SECURITY
            else:
                info = INFO_NORMAL
            self._show_package(name, version, flavor, info)
        log.info("============== end get_updates ========================")
        self.client.setUpdateCallback(self.callback)

    def _findPackage(self, package_id):
        '''
        find a package based on a package id (name;version;arch;summary)
        '''
        log.info("========== _findPackage ==========")
        log.info(package_id)
        troveTuples = self.get_package_from_id(package_id)
        log.info(troveTuples)
        for troveTuple in troveTuples:
            log.info("======== trove ")
            log.info(troveTuple)
            installed = self.check_installed(troveTuple)
            log.info(installed)
            name, version, flavor = troveTuple
            return name, version, flavor, installed
        else:
            self.error(ERROR_INTERNAL_ERROR, "package_id Not Correct ")

    def repo_set_data(self, repoid, parameter, value):
        '''
        Implement the {backend}-repo-set-data functionality
        '''
        pass

    def get_repo_list(self, filters):
        '''
        Implement the {backend}-get-repo-list functionality
        '''
        pass

    def repo_enable(self, repoid, enable):
        '''
        Implement the {backend}-repo-enable functionality
        '''
        pass

from pkConaryLog import pdb

def main():
    backend = PackageKitConaryBackend('')
    log.info("======== argv =========== ")
    log.info(sys.argv)
    backend.dispatcher(sys.argv[1:])

if __name__ == "__main__":
    main()
