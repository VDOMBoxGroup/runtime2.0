from builtins import object
import re
import managers

from logs import log
from .scripting import ScriptingPackageLoader, ScriptingModuleLoader
from .manager import ImportManagerPackageLoader, ImportManagerModuleLoader
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec

SCRIPTING_MODULES = (
    "server", "application", "log", "session", "request", "response", "VDOM_object")  # "obsolete_request"
FULLNAME_REGEX = re.compile(
    r"^"
    r"(?:module_)([A-F\d]{8}_[A-F\d]{4}_[A-F\d]{4}_[A-F\d]{4}_[A-F\d]{12})" r"|"
    r"([A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})(?::([\d\w]+))?(?:\.([\d\w]+))?"
    r"$",
    re.IGNORECASE)


class ScriptingFinder(MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        if managers.has("memory", "engine"):
            scripting = __import__("scripting")
            self._scripting_modules = {name: getattr(scripting, name) for name in SCRIPTING_MODULES}

            match = FULLNAME_REGEX.match(fullname)
            if match:
                if match.lastindex == 1:
                    executable = managers.memory.types.get(match.group(1).replace("_", "-"))
                    if executable is None:
                        log.write("Unable to load missing module \"%s\"" % fullname)
                        raise ImportError
                    return ModuleSpec(fullname, ScriptingModuleLoader(fullname, executable))
                else:
                    application = managers.engine.application
                    if application is None:
                        # TODO: Remove this after support engine.application in application threads
                        application = managers.memory.applications[match.group(2)]
                        if application is None:
                            log.write("Unable to load \"%s\" library for missing application" % fullname)
                            raise ImportError
                        managers.engine.select(application=application)
                    elif application.id != match.group(2):
                        log.write("Unable to load \"%s\" library for %s application" % (fullname, application.id))
                        raise ImportError
                    context = match.group(3)
                    if context is None:
                        if match.lastindex == 2:
                            return ModuleSpec(fullname, ScriptingPackageLoader(fullname, self._scripting_modules))
                        else:
                            executable = application.libraries.get(match.group(4))
                            if executable is None:
                                return None
                            else:
                                return ModuleSpec(fullname, ScriptingModuleLoader(fullname, executable))
                    else:
                        if match.lastindex == 3:
                            return ModuleSpec(fullname, ImportManagerPackageLoader(fullname))
                        else:
                            initializer = managers.import_manager.lookup(context, match.group(4))
                            if initializer is None:
                                return None
                            else:
                                return ModuleSpec(fullname, ImportManagerModuleLoader(fullname, initializer))

        return None
