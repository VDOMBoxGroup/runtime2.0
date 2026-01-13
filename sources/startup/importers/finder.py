import re
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec

import managers

from logs import log
from .scripting import ScriptingPackageLoader, ScriptingModuleLoader
from .manager import ImportManagerPackageLoader, ImportManagerModuleLoader


SCRIPTING_MODULES = ("server", "application", "log", "session", "request", "response", "VDOM_object")
FULLNAME_REGEX = re.compile(
    r"^"
    r"(?:module_)([A-F\d]{8}_[A-F\d]{4}_[A-F\d]{4}_[A-F\d]{4}_[A-F\d]{12})" r"|"
    r"([A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})(?::([\d\w]+))?(?:\.([\d\w]+))?" r"|" 
    r"(?::([\d\w]+))?(?:\.([\d\w]+))?"
    r"$",
    re.IGNORECASE)


class ScriptingFinder(MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        if managers.has("memory", "engine"):
            scripting = __import__("scripting")
            self._scripting_modules = {name: getattr(scripting, name) for name in SCRIPTING_MODULES}
            self.__class__ = ActualScriptingFinder
            return self.find_spec(fullname, path, target)
        else:
            return None

    def find_module(self, fullname, path=None):
        """Legacy find_module for backwards compatibility."""
        spec = self.find_spec(fullname, path)
        return spec.loader if spec else None


class ActualScriptingFinder(MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        print(f"Importer lookup>>> {fullname} ({path}, {target})\n")


        match = FULLNAME_REGEX.match(fullname)
        if match:
            if match.lastindex == 1:
                executable = managers.memory.types.get(match.group(1).replace("_", "-"))
                if executable is None:
                    log.write("Unable to load missing module \"%s\"" % fullname)
                    raise ImportError
                loader = ScriptingModuleLoader(fullname, executable)
                return ModuleSpec(fullname, loader)
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
                        loader = ScriptingPackageLoader(fullname, self._scripting_modules)
                        return ModuleSpec(fullname, loader, is_package=True)
                    else:
                        executable = application.libraries.get(match.group(4))
                        if executable is None:
                            return None
                        else:
                            loader = ScriptingModuleLoader(fullname, executable)
                            return ModuleSpec(fullname, loader)
                else:
                    if match.lastindex == 3:
                        loader = ImportManagerPackageLoader(fullname)
                        return ModuleSpec(fullname, loader, is_package=True)
                    else:
                        initializer = managers.import_manager.lookup(context, match.group(4))
                        if initializer is None:
                            return None
                        else:
                            loader = ImportManagerModuleLoader(fullname, initializer)
                            return ModuleSpec(fullname, loader)
        else:
            application = managers.engine.application
            if application is not None:
                executable = application.libraries.get(fullname)
                if executable:
                    loader = ScriptingModuleLoader(application.id + fullname, executable)
                    return ModuleSpec(fullname, loader)
        return None

    def find_module(self, fullname, path=None):
        """Legacy find_module for backwards compatibility."""
        spec = self.find_spec(fullname, path)
        return spec.loader if spec else None