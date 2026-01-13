import sys
import importlib
import importlib.util
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from collections import defaultdict
from threading import Lock

import managers

from logs import log


class ImportManagerLocal(object):

    def __init__(self):
        self.modules = defaultdict(dict)
        self.lock = Lock()


class ImportManager(object):

    def __init__(self):
        self._local = ImportManagerLocal()

    def register(self, context, name, initializer):
        application = managers.engine.application
        if application is None:
            raise Exception("Unable to register library outside of application")
        context = ":".join((application.id, context))
        
        with self._local.lock:
            self._local.modules[context][name] = initializer
            if context not in sys.modules:
                __import__(context)
            try:
                del sys.modules[".".join((context, name))]
                del sys.modules[context].__dict__[name]
            except KeyError:
                pass

    def unregister(self, context, name=None):
        application = managers.engine.application
        if application is None:
            raise Exception("Unable to unregister library outside of application")
        context = ":".join((application.id, context))
        
        if name is None:
            with self._local.lock:
                try:
                    del self._local.modules[context]
                    del sys.modules[context]
                except KeyError:
                    pass
        else:
            with self._local.lock:
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

    def create_module(self, spec):
        """Return None to use default module creation semantics."""
        return None

    def exec_module(self, module):
        """Execute the module in its own namespace."""
        module.__file__ = None
        module.__loader__ = self
        module.__package__ = self._fullname
        module.__path__ = []

    def load_module(self, fullname):
        """Legacy load_module for compatibility."""
        if fullname != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, fullname))
            raise ImportError

        spec = ModuleSpec(self._fullname, self, is_package=True)
        module = importlib.util.module_from_spec(spec)
        sys.modules[self._fullname] = module
        self.exec_module(module)
        return module


class ImportManagerModuleLoader(Loader):

    def __init__(self, fullname, initializer):
        self._fullname = fullname
        self._initializer = initializer

    def create_module(self, spec):
        """Return None to use default module creation semantics."""
        return None

    def exec_module(self, module):
        """Execute the module in its own namespace."""
        package = self._fullname.partition(".")[0]
        context, separator, name = package.partition(":")

        module.__file__ = None
        module.__loader__ = self
        module.__package__ = package
        
        self._initializer(context, name, module.__dict__)

    def load_module(self, fullname):
        """Legacy load_module for compatibility."""
        if fullname != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, fullname))
            raise ImportError

        spec = ModuleSpec(self._fullname, self)
        module = importlib.util.module_from_spec(spec)
        sys.modules[self._fullname] = module
        self.exec_module(module)
        return module
