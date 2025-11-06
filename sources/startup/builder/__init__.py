
import os

from sys import exit
from argparse import ArgumentParser
from setuptools import Extension

import settings

from utils.output import show, warn
from .builder import Builder, ReportBuilderFailureError

EXTENSIONS = {
    "vdomxml": Extension("memory.vdomxml._loads",
        sources=["memory/vdomxml/loads.c"],
        include_dirs=["memory/vdomxml/include"])
}


class ArgumentsError(Exception):
    pass


class ExceptionalArgumentParser(ArgumentParser):

    def error(self, message):
        raise ArgumentsError(message)


parser = ExceptionalArgumentParser(add_help=False)
parser.add_argument("-c", "--configure", dest="filename", default=None)
subparsers = parser.add_subparsers(dest="action")
subparser = subparsers.add_parser("build")
subparsers.add_parser("deploy") #Fixed parser yielding everytime manage.py is called but without build parameters
subparsers.add_parser("install").add_argument("applicaion.xml")
subparser.add_argument("-l", "--list", action="store_true", dest="list", default=False,
    help="show availavle exensions")
subparser.add_argument("--cleanup", action="store_true", dest="cleanup", default=False,
    help="cleanup building directories")
subparser.add_argument("extensions", nargs="*", metavar="extension",
    help="optional extensions to build")

try:
    arguments = parser.parse_args()
except ArgumentsError as error:
    show_warning = True
else:
    show_warning = False

    if not os.path.isdir(settings.TEMPORARY_LOCATION):
        show("prepare temporary directory")
        try:
            os.makedirs(settings.TEMPORARY_LOCATION)
        except Exception as error:
            warn("unable to prepare temporary directory: %s" % error)
            exit(1)

    try:
        builder = Builder(EXTENSIONS)
        if getattr(arguments, 'list'):
            builder.list()
        elif getattr(arguments, 'cleanup'):
            builder.cleanup()
        elif  getattr(arguments, 'extensions'):
            builder.build(*arguments.extensions)
        else:
            builder.build()
    except ReportBuilderFailureError:
        # hack
        pass
        # exit(1)
    except BaseException:
        raise
    else:
        exit(0)
