#!/usr/bin/python

from startup import manage  # noqa
import managers

from logs import VDOM_log_manager
from startup import ImportManager
from file_access import VDOM_file_manager
from storage import VDOM_storage
from resource import VDOM_resource_manager
from database import VDOM_database_manager
from security import VDOM_user_manager, VDOM_acl_manager
from scripting import VDOM_compiler, VDOM_dispatcher, ScriptManager
from memory import VDOM_memory
from engine import VDOM_engine

from startup.manage import arguments
from logs import console


managers.register("log_manager", VDOM_log_manager)
managers.register("import_manager", ImportManager)
managers.register("file_manager", VDOM_file_manager, lazy=True)
managers.register("storage", VDOM_storage, lazy=True)
managers.register("resource_manager", VDOM_resource_manager, lazy=True)
managers.register("database_manager", VDOM_database_manager, lazy=True)
managers.register("user_manager", VDOM_user_manager, lazy=True)
managers.register("acl_manager", VDOM_acl_manager, lazy=True)
managers.register("dispatcher", VDOM_dispatcher, lazy=True)
managers.register("compiler", VDOM_compiler, lazy=True)
managers.register("script_manager", ScriptManager, lazy=True)
managers.register("memory", VDOM_memory, lazy=True)
managers.register("engine", VDOM_engine, lazy=True)


try:
    arguments.action.run(*arguments.action.arguments)
except Exception as error:
    console.error(error)
