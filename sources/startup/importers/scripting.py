from builtins import object
import sys

from logs import log
from importlib.abc import Loader


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


class ScriptingModuleLoader(Loader):

    def __init__(self, fullname, executable):
        self._fullname = fullname
        self._executable = executable

    def exec_module(self, module):
        try:
            self._executable.execute(None, module.__dict__)
        except Exception as e:
            log.write("Error compiling module \"%s\" cannot handle error \"%s\"" % (self._fullname, e))
            raise ImportError

    def create_module(self, spec):
        if spec.name != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, spec.name))
            raise ImportError

        import types
        module = types.ModuleType(self._fullname)
        module.__file__ = self._executable.signature
        module.__loader__ = self
        module.__package__ = self._executable.package

        return module
