#from __future__ import absolute_import
import sys, datetime

if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins
    
#from future import standard_library
#standard_library.install_aliases()

from argparse import ArgumentParser


# python: http://bugs.python.org/issue7980
datetime.datetime.strptime("2012-01-01", "%Y-%m-%d")




#Hotfix to allow urllib certificate validation
try:
    import os, ssl, certifi
    def new_ssl_context_decorator(*args, **kwargs):
        kwargs['cafile'] = certifi.where()
        return ssl.create_default_context(*args, **kwargs)
    ssl._create_default_https_context = new_ssl_context_decorator
except ImportError:
    print("Unable to set default ssl validation context for urllib. Check certifi library presence")

# settings
from .importers.settings import SettingsImporter

importer = SettingsImporter()
sys.meta_path.append(importer)
settings = __import__("appsettings")
sys.meta_path.remove(importer)

# override
from .override import override  # noqa

parser = ArgumentParser(add_help=False)
parser.add_argument("-c", "--configure", dest="filename", default=None)

arguments, other = parser.parse_known_args()
if arguments.filename:
    override(arguments.filename)

import logs  # noqa
# hack to run builder cleanly

if settings.MANAGE:
    from . import builder  # noqa


# initialize

from utils import codecs, system, threads  # noqa



# register libraries finder

from .importers.finder import ScriptingFinder  # noqa

sys.meta_path.append(ScriptingFinder())


# start log server

from logs import VDOM_log_server  # noqa

if settings.START_LOG_SERVER and settings.LOGGER == "native":
    VDOM_log_server().start()


# prepare manager

from .importers.manager import ImportManager  # noqa


# obsolete

from . import legacy  # noqa
from .debug import debug, DebugFile  # noqa

builtins.VDOM_CONFIG = legacy.VDOM_CONFIG
builtins.VDOM_CONFIG_1 = legacy.VDOM_CONFIG_1
builtins.system_options = {"server_license_type": "0", "firmware": "N/A", "card_state": "1", "object_amount": "15000"}
builtins.debug = debug
builtins.debugfile = DebugFile()
builtins._ = lambda value: value