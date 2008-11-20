/* -*- Mode: C; tab-width: 8; indent-tabs-mode: t; c-basic-offset: 8 -*-
 *
 * Copyright (C) 2008 Richard Hughes <richard@hughsie.com>
 *
 * Licensed under the GNU General Public License Version 2
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

#include <syslog.h>
#include <glib.h>

#include "egg-debug.h"
#include "pk-syslog.h"

#define PK_SYSLOG_GET_PRIVATE(o) (G_TYPE_INSTANCE_GET_PRIVATE ((o), PK_TYPE_SYSLOG, PkSyslogPrivate))

struct PkSyslogPrivate
{
	gpointer		data;
	/* any logging instance data here */
};

G_DEFINE_TYPE (PkSyslog, pk_syslog, G_TYPE_OBJECT)
static gpointer pk_syslog_object = NULL;

/**
 * pk_syslog_add:
 **/
void
pk_syslog_add (PkSyslog *self, PkSyslogType type, const gchar *format, ...)
{
	va_list args;
	gchar va_args_buffer[1025];

	g_return_if_fail (PK_IS_SYSLOG (self));

	va_start (args, format);
	g_vsnprintf (va_args_buffer, 1024, format, args);
	va_end (args);

	/* auth messages are special */
	if (type == PK_SYSLOG_TYPE_AUTH)
		syslog (LOG_AUTHPRIV, "%s", va_args_buffer);

	egg_debug ("logging to syslog '%s'", va_args_buffer);
	syslog (LOG_DAEMON, "%s", va_args_buffer);
}

/**
 * pk_syslog_finalize:
 **/
static void
pk_syslog_finalize (GObject *object)
{
	PkSyslog *self;
	g_return_if_fail (PK_IS_SYSLOG (object));
	self = PK_SYSLOG (object);

	/* shut down syslog */
	closelog ();

	G_OBJECT_CLASS (pk_syslog_parent_class)->finalize (object);
}

/**
 * pk_syslog_class_init:
 **/
static void
pk_syslog_class_init (PkSyslogClass *klass)
{
	GObjectClass *object_class = G_OBJECT_CLASS (klass);
	object_class->finalize = pk_syslog_finalize;
	g_type_class_add_private (klass, sizeof (PkSyslogPrivate));
}

/**
 * pk_syslog_init:
 **/
static void
pk_syslog_init (PkSyslog *self)
{
	self->priv = PK_SYSLOG_GET_PRIVATE (self);

	/* open syslog */
	openlog ("PackageKit", LOG_NDELAY, LOG_USER);
}

/**
 * pk_syslog_new:
 * Return value: A new syslog class instance.
 **/
PkSyslog *
pk_syslog_new (void)
{
	if (pk_syslog_object != NULL) {
		g_object_ref (pk_syslog_object);
	} else {
		pk_syslog_object = g_object_new (PK_TYPE_SYSLOG, NULL);
		g_object_add_weak_pointer (pk_syslog_object, &pk_syslog_object);
	}
	return PK_SYSLOG (pk_syslog_object);
}

/***************************************************************************
 ***                          MAKE CHECK TESTS                           ***
 ***************************************************************************/
#ifdef EGG_TEST
#include "egg-test.h"

void
egg_test_syslog (EggTest *test)
{
	PkSyslog *self;

	if (!egg_test_start (test, "PkSyslog"))
		return;

	/************************************************************/
	egg_test_title (test, "get an instance");
	syslog = pk_syslog_new ();
	if (syslog != NULL)
		egg_test_success (test, NULL);
	else
		egg_test_failed (test, NULL);

	g_object_unref (syslog);

	egg_test_end (test);
}
#endif

