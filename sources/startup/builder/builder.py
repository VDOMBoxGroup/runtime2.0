
import sys
import os.path
import re

from distutils.command.build_ext import build_ext
from setuptools import setup

import settings

from utils.output import section, show, warn
from utils.capture import OutputCapture


SETUP_SCRIPT = """
setup(name="runtime",
    cmdclass={"build_ext": BuildExtension},
    ext_modules=extensions,
    options={
        "build_ext": {"build_lib": temporary, "build_temp": temporary},
        "clean": {"build_lib": temporary, "build_temp": temporary}
    })
"""


class ReportBuilderFailureError(Exception):
    pass


class BuildExtension(build_ext):

    def build_extensions(self):

        def apply_options(**options):
            options = options.get(self.compiler.compiler_type)
            if options:
                if isinstance(options, list):
                    compiler_options, linker_options = options, None
                elif isinstance(options, tuple):
                    compiler_options, linker_options = options
                for extension in self.extensions:
                    if compiler_options:
                        extension.extra_compile_args = compiler_options
                    if linker_options:
                        extension.extra_link_args = linker_options

        if settings.TREAT_WARNINGS_AS_ERRORS:
            apply_options(msvc=["/WX"], unix=["-Werror"])

        build_ext.build_extensions(self)


class Builder(object):

    def __init__(self, extensions):
        self._temporary = os.path.join(settings.TEMPORARY_LOCATION, "builder")
        self._extensions = extensions

    def execute(self, *options, **keywords):
        capture = OutputCapture("setup.log")
        arguments_backup = sys.argv[:]
        try:
            sys.argv = ["setup.py"] + list(options)
            with capture:
                exec(SETUP_SCRIPT, {
                    "BuildExtension": BuildExtension,
                    "temporary": self._temporary,
                    "extensions": keywords.get("extensions"),
                    "setup": setup}, {})
        except BaseException as error:
            show("")
            warn(re.sub(r"^(error:\s)?", "", str(error), flags=re.IGNORECASE))
            for line in capture.lines:
                warn(line,
                    indent=settings.LOGGING_INDENT,
                    continuation=settings.LOGGING_INDENT)
            raise ReportBuilderFailureError
        finally:
            sys.argv = arguments_backup

    def list(self):
        with section("extensions"):
            for name in self._extensions:
                show(name)

    def cleanup(self):
        show("cleanup build directories")
        self.execute("clean")

    def build(self, *arguments):
        with section("build extensions"):
            for name in arguments or self._extensions:
                try:
                    extension = self._extensions[name]
                except KeyError:
                    warn("extension \"%s\" not found" % name)
                    raise ReportBuilderFailureError

                show("build %s extension" % extension.name)
                self.execute("build_ext", "--inplace", "clean", extensions=[extension])
