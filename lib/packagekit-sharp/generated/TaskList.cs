// This file was generated by the Gtk# code generator.
// Any changes made will be lost if regenerated.

namespace PackageKit {

	using System;
	using System.Collections;
	using System.Runtime.InteropServices;

#region Autogenerated code
	public class TaskList : GLib.Object {

		[Obsolete]
		protected TaskList(GLib.GType gtype) : base(gtype) {}
		public TaskList(IntPtr raw) : base(raw) {}

		[DllImport("libpackagekit-glib.dll")]
		static extern IntPtr pk_task_list_new();

		public TaskList () : base (IntPtr.Zero)
		{
			if (GetType () != typeof (TaskList)) {
				CreateNativeObject (new string [0], new GLib.Value[0]);
				return;
			}
			Raw = pk_task_list_new();
		}

		[GLib.CDeclCallback]
		delegate void ErrorCodeVMDelegate (IntPtr tlist, IntPtr client, int code, IntPtr details);

		static ErrorCodeVMDelegate ErrorCodeVMCallback;

		static void errorcode_cb (IntPtr tlist, IntPtr client, int code, IntPtr details)
		{
			try {
				TaskList tlist_managed = GLib.Object.GetObject (tlist, false) as TaskList;
				tlist_managed.OnErrorCode (GLib.Object.GetObject(client) as PackageKit.Client, (PackageKit.ErrorCodeEnum) code, GLib.Marshaller.Utf8PtrToString (details));
			} catch (Exception e) {
				GLib.ExceptionManager.RaiseUnhandledException (e, false);
			}
		}

		private static void OverrideErrorCode (GLib.GType gtype)
		{
			if (ErrorCodeVMCallback == null)
				ErrorCodeVMCallback = new ErrorCodeVMDelegate (errorcode_cb);
			OverrideVirtualMethod (gtype, "error-code", ErrorCodeVMCallback);
		}

		[GLib.DefaultSignalHandler(Type=typeof(PackageKit.TaskList), ConnectionMethod="OverrideErrorCode")]
		protected virtual void OnErrorCode (PackageKit.Client client, PackageKit.ErrorCodeEnum code, string details)
		{
			GLib.Value ret = GLib.Value.Empty;
			GLib.ValueArray inst_and_params = new GLib.ValueArray (4);
			GLib.Value[] vals = new GLib.Value [4];
			vals [0] = new GLib.Value (this);
			inst_and_params.Append (vals [0]);
			vals [1] = new GLib.Value (client);
			inst_and_params.Append (vals [1]);
			vals [2] = new GLib.Value (code);
			inst_and_params.Append (vals [2]);
			vals [3] = new GLib.Value (details);
			inst_and_params.Append (vals [3]);
			g_signal_chain_from_overridden (inst_and_params.ArrayPtr, ref ret);
			foreach (GLib.Value v in vals)
				v.Dispose ();
		}

		[GLib.CDeclCallback]
		delegate void ErrorCodeSignalDelegate (IntPtr arg0, IntPtr arg1, int arg2, IntPtr arg3, IntPtr gch);

		static void ErrorCodeSignalCallback (IntPtr arg0, IntPtr arg1, int arg2, IntPtr arg3, IntPtr gch)
		{
			PackageKit.ErrorCodeArgs args = new PackageKit.ErrorCodeArgs ();
			try {
				GLib.Signal sig = ((GCHandle) gch).Target as GLib.Signal;
				if (sig == null)
					throw new Exception("Unknown signal GC handle received " + gch);

				args.Args = new object[3];
				args.Args[0] = GLib.Object.GetObject(arg1) as PackageKit.Client;
				args.Args[1] = (PackageKit.ErrorCodeEnum) arg2;
				args.Args[2] = GLib.Marshaller.Utf8PtrToString (arg3);
				PackageKit.ErrorCodeHandler handler = (PackageKit.ErrorCodeHandler) sig.Handler;
				handler (GLib.Object.GetObject (arg0), args);
			} catch (Exception e) {
				GLib.ExceptionManager.RaiseUnhandledException (e, false);
			}
		}

		[GLib.Signal("error-code")]
		public event PackageKit.ErrorCodeHandler ErrorCode {
			add {
				GLib.Signal sig = GLib.Signal.Lookup (this, "error-code", new ErrorCodeSignalDelegate(ErrorCodeSignalCallback));
				sig.AddDelegate (value);
			}
			remove {
				GLib.Signal sig = GLib.Signal.Lookup (this, "error-code", new ErrorCodeSignalDelegate(ErrorCodeSignalCallback));
				sig.RemoveDelegate (value);
			}
		}

		[GLib.CDeclCallback]
		delegate void ChangedVMDelegate (IntPtr tlist);

		static ChangedVMDelegate ChangedVMCallback;

		static void changed_cb (IntPtr tlist)
		{
			try {
				TaskList tlist_managed = GLib.Object.GetObject (tlist, false) as TaskList;
				tlist_managed.OnChanged ();
			} catch (Exception e) {
				GLib.ExceptionManager.RaiseUnhandledException (e, false);
			}
		}

		private static void OverrideChanged (GLib.GType gtype)
		{
			if (ChangedVMCallback == null)
				ChangedVMCallback = new ChangedVMDelegate (changed_cb);
			OverrideVirtualMethod (gtype, "changed", ChangedVMCallback);
		}

		[GLib.DefaultSignalHandler(Type=typeof(PackageKit.TaskList), ConnectionMethod="OverrideChanged")]
		protected virtual void OnChanged ()
		{
			GLib.Value ret = GLib.Value.Empty;
			GLib.ValueArray inst_and_params = new GLib.ValueArray (1);
			GLib.Value[] vals = new GLib.Value [1];
			vals [0] = new GLib.Value (this);
			inst_and_params.Append (vals [0]);
			g_signal_chain_from_overridden (inst_and_params.ArrayPtr, ref ret);
			foreach (GLib.Value v in vals)
				v.Dispose ();
		}

		[GLib.Signal("changed")]
		public event System.EventHandler Changed {
			add {
				GLib.Signal sig = GLib.Signal.Lookup (this, "changed");
				sig.AddDelegate (value);
			}
			remove {
				GLib.Signal sig = GLib.Signal.Lookup (this, "changed");
				sig.RemoveDelegate (value);
			}
		}

		[GLib.CDeclCallback]
		delegate void StatusChangedVMDelegate (IntPtr tlist);

		static StatusChangedVMDelegate StatusChangedVMCallback;

		static void statuschanged_cb (IntPtr tlist)
		{
			try {
				TaskList tlist_managed = GLib.Object.GetObject (tlist, false) as TaskList;
				tlist_managed.OnStatusChanged ();
			} catch (Exception e) {
				GLib.ExceptionManager.RaiseUnhandledException (e, false);
			}
		}

		private static void OverrideStatusChanged (GLib.GType gtype)
		{
			if (StatusChangedVMCallback == null)
				StatusChangedVMCallback = new StatusChangedVMDelegate (statuschanged_cb);
			OverrideVirtualMethod (gtype, "status-changed", StatusChangedVMCallback);
		}

		[GLib.DefaultSignalHandler(Type=typeof(PackageKit.TaskList), ConnectionMethod="OverrideStatusChanged")]
		protected virtual void OnStatusChanged ()
		{
			GLib.Value ret = GLib.Value.Empty;
			GLib.ValueArray inst_and_params = new GLib.ValueArray (1);
			GLib.Value[] vals = new GLib.Value [1];
			vals [0] = new GLib.Value (this);
			inst_and_params.Append (vals [0]);
			g_signal_chain_from_overridden (inst_and_params.ArrayPtr, ref ret);
			foreach (GLib.Value v in vals)
				v.Dispose ();
		}

		[GLib.Signal("status-changed")]
		public event System.EventHandler StatusChanged {
			add {
				GLib.Signal sig = GLib.Signal.Lookup (this, "status-changed");
				sig.AddDelegate (value);
			}
			remove {
				GLib.Signal sig = GLib.Signal.Lookup (this, "status-changed");
				sig.RemoveDelegate (value);
			}
		}

		[GLib.CDeclCallback]
		delegate void MessageVMDelegate (IntPtr tlist, IntPtr client, int message, IntPtr details);

		static MessageVMDelegate MessageVMCallback;

		static void message_cb (IntPtr tlist, IntPtr client, int message, IntPtr details)
		{
			try {
				TaskList tlist_managed = GLib.Object.GetObject (tlist, false) as TaskList;
				tlist_managed.OnMessage (GLib.Object.GetObject(client) as PackageKit.Client, (PackageKit.MessageEnum) message, GLib.Marshaller.Utf8PtrToString (details));
			} catch (Exception e) {
				GLib.ExceptionManager.RaiseUnhandledException (e, false);
			}
		}

		private static void OverrideMessage (GLib.GType gtype)
		{
			if (MessageVMCallback == null)
				MessageVMCallback = new MessageVMDelegate (message_cb);
			OverrideVirtualMethod (gtype, "message", MessageVMCallback);
		}

		[GLib.DefaultSignalHandler(Type=typeof(PackageKit.TaskList), ConnectionMethod="OverrideMessage")]
		protected virtual void OnMessage (PackageKit.Client client, PackageKit.MessageEnum message, string details)
		{
			GLib.Value ret = GLib.Value.Empty;
			GLib.ValueArray inst_and_params = new GLib.ValueArray (4);
			GLib.Value[] vals = new GLib.Value [4];
			vals [0] = new GLib.Value (this);
			inst_and_params.Append (vals [0]);
			vals [1] = new GLib.Value (client);
			inst_and_params.Append (vals [1]);
			vals [2] = new GLib.Value (message);
			inst_and_params.Append (vals [2]);
			vals [3] = new GLib.Value (details);
			inst_and_params.Append (vals [3]);
			g_signal_chain_from_overridden (inst_and_params.ArrayPtr, ref ret);
			foreach (GLib.Value v in vals)
				v.Dispose ();
		}

		[GLib.CDeclCallback]
		delegate void MessageSignalDelegate (IntPtr arg0, IntPtr arg1, int arg2, IntPtr arg3, IntPtr gch);

		static void MessageSignalCallback (IntPtr arg0, IntPtr arg1, int arg2, IntPtr arg3, IntPtr gch)
		{
			PackageKit.MessageArgs args = new PackageKit.MessageArgs ();
			try {
				GLib.Signal sig = ((GCHandle) gch).Target as GLib.Signal;
				if (sig == null)
					throw new Exception("Unknown signal GC handle received " + gch);

				args.Args = new object[3];
				args.Args[0] = GLib.Object.GetObject(arg1) as PackageKit.Client;
				args.Args[1] = (PackageKit.MessageEnum) arg2;
				args.Args[2] = GLib.Marshaller.Utf8PtrToString (arg3);
				PackageKit.MessageHandler handler = (PackageKit.MessageHandler) sig.Handler;
				handler (GLib.Object.GetObject (arg0), args);
			} catch (Exception e) {
				GLib.ExceptionManager.RaiseUnhandledException (e, false);
			}
		}

		[GLib.Signal("message")]
		public event PackageKit.MessageHandler Message {
			add {
				GLib.Signal sig = GLib.Signal.Lookup (this, "message", new MessageSignalDelegate(MessageSignalCallback));
				sig.AddDelegate (value);
			}
			remove {
				GLib.Signal sig = GLib.Signal.Lookup (this, "message", new MessageSignalDelegate(MessageSignalCallback));
				sig.RemoveDelegate (value);
			}
		}

		[GLib.CDeclCallback]
		delegate void FinishedVMDelegate (IntPtr tlist, IntPtr client, int exit, uint runtime);

		static FinishedVMDelegate FinishedVMCallback;

		static void finished_cb (IntPtr tlist, IntPtr client, int exit, uint runtime)
		{
			try {
				TaskList tlist_managed = GLib.Object.GetObject (tlist, false) as TaskList;
				tlist_managed.OnFinished (GLib.Object.GetObject(client) as PackageKit.Client, (PackageKit.ExitEnum) exit, runtime);
			} catch (Exception e) {
				GLib.ExceptionManager.RaiseUnhandledException (e, false);
			}
		}

		private static void OverrideFinished (GLib.GType gtype)
		{
			if (FinishedVMCallback == null)
				FinishedVMCallback = new FinishedVMDelegate (finished_cb);
			OverrideVirtualMethod (gtype, "finished", FinishedVMCallback);
		}

		[GLib.DefaultSignalHandler(Type=typeof(PackageKit.TaskList), ConnectionMethod="OverrideFinished")]
		protected virtual void OnFinished (PackageKit.Client client, PackageKit.ExitEnum exit, uint runtime)
		{
			GLib.Value ret = GLib.Value.Empty;
			GLib.ValueArray inst_and_params = new GLib.ValueArray (4);
			GLib.Value[] vals = new GLib.Value [4];
			vals [0] = new GLib.Value (this);
			inst_and_params.Append (vals [0]);
			vals [1] = new GLib.Value (client);
			inst_and_params.Append (vals [1]);
			vals [2] = new GLib.Value (exit);
			inst_and_params.Append (vals [2]);
			vals [3] = new GLib.Value (runtime);
			inst_and_params.Append (vals [3]);
			g_signal_chain_from_overridden (inst_and_params.ArrayPtr, ref ret);
			foreach (GLib.Value v in vals)
				v.Dispose ();
		}

		[GLib.CDeclCallback]
		delegate void FinishedSignalDelegate (IntPtr arg0, IntPtr arg1, int arg2, uint arg3, IntPtr gch);

		static void FinishedSignalCallback (IntPtr arg0, IntPtr arg1, int arg2, uint arg3, IntPtr gch)
		{
			PackageKit.FinishedArgs args = new PackageKit.FinishedArgs ();
			try {
				GLib.Signal sig = ((GCHandle) gch).Target as GLib.Signal;
				if (sig == null)
					throw new Exception("Unknown signal GC handle received " + gch);

				args.Args = new object[3];
				args.Args[0] = GLib.Object.GetObject(arg1) as PackageKit.Client;
				args.Args[1] = (PackageKit.ExitEnum) arg2;
				args.Args[2] = arg3;
				PackageKit.FinishedHandler handler = (PackageKit.FinishedHandler) sig.Handler;
				handler (GLib.Object.GetObject (arg0), args);
			} catch (Exception e) {
				GLib.ExceptionManager.RaiseUnhandledException (e, false);
			}
		}

		[GLib.Signal("finished")]
		public event PackageKit.FinishedHandler Finished {
			add {
				GLib.Signal sig = GLib.Signal.Lookup (this, "finished", new FinishedSignalDelegate(FinishedSignalCallback));
				sig.AddDelegate (value);
			}
			remove {
				GLib.Signal sig = GLib.Signal.Lookup (this, "finished", new FinishedSignalDelegate(FinishedSignalCallback));
				sig.RemoveDelegate (value);
			}
		}

		[DllImport("libpackagekit-glib.dll")]
		static extern bool pk_task_list_contains_role(IntPtr raw, int role);

		public bool ContainsRole(PackageKit.RoleEnum role) {
			bool raw_ret = pk_task_list_contains_role(Handle, (int) role);
			bool ret = raw_ret;
			return ret;
		}

		[DllImport("libpackagekit-glib.dll")]
		static extern IntPtr pk_task_list_get_item(IntPtr raw, uint item);

		public PackageKit.TaskListItem GetItem(uint item) {
			IntPtr raw_ret = pk_task_list_get_item(Handle, item);
			PackageKit.TaskListItem ret = PackageKit.TaskListItem.New (raw_ret);
			return ret;
		}

		[DllImport("libpackagekit-glib.dll")]
		static extern uint pk_task_list_get_size(IntPtr raw);

		public uint Size {
			get {
				uint raw_ret = pk_task_list_get_size(Handle);
				uint ret = raw_ret;
				return ret;
			}
		}

		[DllImport("libpackagekit-glib.dll")]
		static extern bool pk_task_list_free(IntPtr raw);

		public bool Free() {
			bool raw_ret = pk_task_list_free(Handle);
			bool ret = raw_ret;
			return ret;
		}

		[DllImport("libpackagekit-glib.dll")]
		static extern IntPtr pk_task_list_get_type();

		public static new GLib.GType GType {
			get {
				IntPtr raw_ret = pk_task_list_get_type();
				GLib.GType ret = new GLib.GType(raw_ret);
				return ret;
			}
		}

		[DllImport("libpackagekit-glib.dll")]
		static extern bool pk_task_list_refresh(IntPtr raw);

		public bool Refresh() {
			bool raw_ret = pk_task_list_refresh(Handle);
			bool ret = raw_ret;
			return ret;
		}

		[DllImport("libpackagekit-glib.dll")]
		static extern bool pk_task_list_print(IntPtr raw);

		public bool Print() {
			bool raw_ret = pk_task_list_print(Handle);
			bool ret = raw_ret;
			return ret;
		}


		static TaskList ()
		{
			GtkSharp.PackagekitSharp.ObjectManager.Initialize ();
		}
#endregion
	}
}
