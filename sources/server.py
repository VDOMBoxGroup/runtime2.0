#!/usr/bin/python
# encoding: utf8

from startup import server  # noqa
import settings
import managers

from logs import VDOM_log_manager, console
from startup import ImportManager
from storage import VDOM_storage
from file_access import VDOM_file_manager  # VDOM_share
from request import VDOM_request_manager
from resource import VDOM_resource_manager, VDOM_resource_editor
from database import VDOM_database_manager
from security import VDOM_user_manager, VDOM_acl_manager
from scripting import VDOM_compiler, VDOM_dispatcher, ScriptManager
from memory import VDOM_memory
from engine import VDOM_engine

from server import VDOM_server
# from mailing import VDOM_email_manager
from session import VDOM_session_manager
from module import VDOM_module_manager
from soap import VDOM_soap_server
from webdav_server import VDOM_webdav_manager

managers.register("log_manager", VDOM_log_manager)
managers.register("import_manager", ImportManager)
managers.register("file_manager", VDOM_file_manager, lazy=True)
managers.register("storage", VDOM_storage, lazy=True)
# managers.register("file_share", VDOM_share, lazy=True)
managers.register("resource_manager", VDOM_resource_manager, lazy=True)
managers.register("database_manager", VDOM_database_manager, lazy=True)
managers.register("user_manager", VDOM_user_manager, lazy=True)
managers.register("acl_manager", VDOM_acl_manager, lazy=True)
managers.register("dispatcher", VDOM_dispatcher, lazy=True)
managers.register("compiler", VDOM_compiler, lazy=True)
managers.register("script_manager", ScriptManager, lazy=True)
managers.register("memory", VDOM_memory, lazy=not settings.MANUAL_GARBAGE_COLLECTING)
managers.register("engine", VDOM_engine, lazy=True)

managers.register("session_manager", VDOM_session_manager, lazy=True)
managers.register("request_manager", VDOM_request_manager, lazy=True)
managers.register("resource_editor", VDOM_resource_editor, lazy=True)
# managers.register("scheduler_manager", VDOM_scheduler_manager, lazy=True)
# managers.register("email_manager", VDOM_email_manager, lazy=True)
managers.register("module_manager", VDOM_module_manager)
managers.register("soap_server", VDOM_soap_server)
managers.register("webdav_manager", VDOM_webdav_manager, lazy=True)
managers.register("server", VDOM_server)

# Load the default application before anything can be served.
#
# This used to be passed to start() as on_ready, which SmartServer calls after
# prepare() - and prepare() is what starts the web server. So the application
# was loaded while the port was already accepting, and every request arriving
# in that window ran against an application that was still coming up.
#
# That window is where an application upgrades itself. Loading an application
# runs its `applicationonstart` action (MemoryApplicationGhost.on_start), which
# is the only place a schema migration can happen: an application deployed by
# swapping a container image is never installed or updated at runtime, it is
# simply present at the next start. Serving requests during that migration
# means serving them against a half-migrated schema, and the symptom is a 500
# naming a column that does not exist yet.
#
# Loading it here, before start(), closes the window: by the time the port is
# open the application is up and its schema is current.
if settings.PRELOAD_DEFAULT_APPLICATION:
    try:
        managers.memory.applications.default
    except Exception as error:
        # Do not refuse to start. A container that exits on a broken
        # application restarts in a loop and there is no way in to diagnose it;
        # one that serves errors can at least be reached and read.
        console.error("unable to preload the default application: %s" % error)
        from traceback import print_exc
        print_exc()

managers.server.start()
