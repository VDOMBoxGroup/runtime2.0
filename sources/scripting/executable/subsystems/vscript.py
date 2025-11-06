


from builtins import compile as python_compile
from importlib import import_module

import settings

from memory import VSCRIPT_EXTENSION, PYTHON_EXTENSION, SYMBOLS_EXTENSION, BYTECODE_EXTENSION
from ..constants import LISTING, SYMBOLS, BYTECODE
from ..bytecode import Bytecode
from ..exceptions import SourceSyntaxError, RequirePrecompileError


vengine = import_module("vscript.engine")
vcompile, vexecute, verrors = vengine.vcompile, vengine.vexecute, vengine.errors


class VScriptBytecode(Bytecode):

    __slots__ = ()

    source_extension = VSCRIPT_EXTENSION
    extensions = {BYTECODE: BYTECODE_EXTENSION, LISTING: PYTHON_EXTENSION, SYMBOLS: SYMBOLS_EXTENSION}

    @classmethod
    def compile(cls, executable, signature=None):
        try:
            listing, symbols = vcompile(executable.source_code,
                package=executable.package, bytecode=False, listing=settings.SHOW_VSCRIPT_LISTING, anyway=False)
        except verrors.lock_error:
            if settings.VSCRIPT_AUTO_PRECOMPILE:
                executable.cleanup()
                raise RequirePrecompileError("Require \"%s\" precompile" % executable.name, executable)
            else:
                raise
        except (verrors.invalid_character, verrors.syntax_error) as error:
            raise SourceSyntaxError(error.message, lineno=error.line)
        bytecode = python_compile(listing, signature or executable.signature, "exec")
        return cls(executable, bytecode, listing=listing, symbols=symbols)

    def execute(self, context, namespace, arguments):
        if arguments:
            raise verrors.internal_error("Dynamic handlers is not implemented")
        vexecute(self._bytecode, self._symbols, context, namespace)
