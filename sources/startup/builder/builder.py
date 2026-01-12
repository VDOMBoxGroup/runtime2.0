import re
from pathlib import Path
from typing import Sequence

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

from sources import settings
from sources.utils.output import section, show, warn
from sources.utils.capture import OutputCapture


class ReportBuilderFailureError(Exception):
    pass


class BuildExtension(build_ext):
    def build_extensions(self):
        if settings.TREAT_WARNINGS_AS_ERRORS:
            options = {
                'msvc': (['/WX'], []),
                'unix': (['-Werror'], []),
            }

            if options := options.get(self.compiler.compiler_type):
                compiler_options, linker_options = options

                for extension in self.extensions:  # type: Extension
                    extension.extra_compile_args = compiler_options
                    extension.extra_link_args = linker_options

        super().build_extensions()


class Builder:
    def __init__(
        self,
        extensions: dict[str, Extension]
    ) -> None:
        self._extensions = extensions

    def execute(self, *options, **keywords) -> None:
        capture = OutputCapture('setup.log')
        try:
            with capture:
                self._run_setup(
                    args=options,
                    extensions=keywords.get('extensions', []),
                )

        except Exception as error:
            error_message = re.sub(r'^(error:\s)?', '', str(error), flags=re.IGNORECASE)

            show('')
            warn(error_message)

            for line in capture.lines:
                warn(
                    line,
                    indent=settings.LOGGING_INDENT,
                    continuation=settings.LOGGING_INDENT
                )
            raise ReportBuilderFailureError from error

    def list(self) -> None:
        with section('extensions'):
            for name in self._extensions:
                show(name)

    def cleanup(self) -> None:
        show('cleanup build directories')
        self.execute('clean')

    def build(self, *arguments) -> None:
        with section('build extensions'):
            target_names = arguments or self._extensions.keys()

            for name in target_names:
                if (extension := self._extensions.get(name)) is None:
                    warn(f'extension "{name}" not found')
                    raise ReportBuilderFailureError

                show(f'build {extension.name} extension')
                self.execute(
                    'build_ext',
                    '--inplace',
                    'clean',
                    extensions=[extension],
                )

    def _run_setup(
        self,
        args: Sequence[str],
        extensions: 'list[Extension]',
    ) -> None:
        setup(
            name='runtime',
            cmdclass={
                'build_ext': BuildExtension,
            },
            ext_modules=extensions,
            script_args=list(args),
            options={
                'build_ext': {
                    'build_lib': self._temporary,
                    'build_temp': self._temporary,
                },
                'clean': {
                    'build_lib': self._temporary,
                    'build_temp': self._temporary,
                }
            }
        )

    @property
    def _temporary(self) -> str:
        return str(
            Path(settings.TEMPORARY_LOCATION) / 'builder'
        )
