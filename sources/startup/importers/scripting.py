import sys
import importlib.util
from importlib.abc import Loader
from importlib.machinery import ModuleSpec

from logs import log


class ScriptingPackageLoader1(Loader):

    def __init__(self, fullname, modules):
        self._fullname = fullname
        self._modules = modules

    def create_module(self, spec):
        """Return None to use default module creation semantics."""
        return None

    def exec_module(self, module):
        """Execute the module in its own namespace."""
        module.__file__ = None
        module.__loader__ = self
        module.__package__ = self._fullname
        module.__path__ = []
        module.__dict__.update(self._modules)

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

class ScriptingPackageLoader(Loader):

    def __init__(self, fullname, modules):
        self._fullname = fullname
        self._modules = modules

    def exec_module(self, module):
        try:
            module.__dict__.update(self._modules)
        except Exception as e:
            log.write("Error compiling module \"%s\" cannot handle error \"%s\"" % (self._fullname, e))
            raise ImportError

    def create_module(self, spec):
        return None
        if spec.name != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, spec.name))
            raise ImportError

        spec = ModuleSpec(self._fullname, self)
        module = importlib.util.module_from_spec(spec)
        module.__file__ = None
        module.__loader__ = self
        module.__package__ = self._fullname
        module.__path__ = []

        return module

class ScriptingModuleLoader(Loader):

    def __init__(self, fullname, executable):
        self._fullname = fullname
        self._executable = executable

    def create_module(self, spec):
        """Return None to use default module creation semantics."""
        return None

    def exec_module(self, module):
        """Execute the module in its own namespace."""
        module.__file__ = self._executable.signature
        module.__loader__ = self
        module.__package__ = self._executable.package
        self._executable.execute(None, module.__dict__)

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
