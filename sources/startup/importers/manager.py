
import sys

from collections import defaultdict
# from threading import local

import managers
import importlib
from logs import log
from importlib.abc import Loader
from threading import Lock

importer_lock = Lock()
class ImportManagerLocal(object):  # local

    modules = defaultdict(dict)


class ImportManager(object):

    def __init__(self):
        self._local = ImportManagerLocal()

    def register(self, context, name, initializer):
        application = managers.engine.application
        if application is None:
            raise Exception("Unable to register library outside of application")
        context = ":".join((application.id, context))
        with importer_lock:
            try:
                self._local.modules[context][name] = initializer
                if context not in sys.modules:
                    __import__(context)
                del sys.modules[".".join((context, name))]
                del sys.modules[context].__dict__[name]
            except KeyError:
                pass
        
    def unregister(self, context, name=None):
        application = managers.engine.application
        if application is None:
            raise Exception("Unable to unregister library outside of application")
        context = ":".join((application.id, context))
        with importer_lock:
            if name is None:
                try:
                    del self._local.modules[context]
                    del sys.modules[context]
                except KeyError:
                    pass
            else:
                try:
                    del self._local.modules[context][name]
                    del sys.modules[".".join((context, name))]
                    del sys.modules[context].__dict__[name]
                except KeyError:
                    pass

    def lookup(self, context, name=None):
        application = managers.engine.application
        if application is None:
            raise Exception("Unable to lookup library outside of application")
        context = ":".join((application.id, context))
        package = self._local.modules.get(context)
        if name is None:
            return package
        if package is None:
            return None
        else:
            return package.get(name)


class ImportManagerPackageLoader(Loader):

    def __init__(self, fullname):
        self._fullname = fullname

    def exec_module(self, module):
        pass

    def create_module(self, spec):
        if spec.name != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, spec.name))
            raise ImportError

        import types
        module = types.ModuleType(self._fullname)
        module.__file__ = None
        module.__loader__ = self
        module.__package__ = self._fullname
        module.__path__ = []

        return module


class ImportManagerModuleLoader(Loader):

    def __init__(self, fullname, initializer):
        self._fullname = fullname
        self._initializer = initializer

    def exec_module(self, module):
        pass

    def create_module(self, spec):
        if spec.name != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, spec.name))
            raise ImportError

        package = self._fullname.partition(".")[0]
        context, separator, name = package.partition(":")
        import types
        module = types.ModuleType(self._fullname)
        module.__file__ = None
        module.__loader__ = self
        module.__package__ = package

        self._initializer(context, name, module.__dict__)

        return module
