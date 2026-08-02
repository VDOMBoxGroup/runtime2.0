from argparse import ArgumentParser
import sys
import datetime
import os

if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins


# python: http://bugs.python.org/issue7980
datetime.datetime.strptime("2012-01-01", "%Y-%m-%d")

# SOAPpy/version.py imports pkg_resources for nothing (both branches set the same
# version), which makes setuptools emit a deprecation warning on every start.
# stderr is routed to log.error, so it shows up as an ERROR - silence it here,
# before SOAPpy gets imported.
import warnings  # noqa: E402
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API", category=UserWarning)

# Hotfix to allow urllib certificate validation
try:
    import ssl
    import certifi

    def new_ssl_context_decorator(*args, **kwargs):
        kwargs['cafile'] = certifi.where()
        return ssl.create_default_context(*args, **kwargs)
    ssl._create_default_https_context = new_ssl_context_decorator
except ImportError:
    print("Unable to set default ssl validation context for urllib. Check certifi library presence")

# settings
from .importers.settings import SettingsImporter # noqa

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

# Route python warnings to the log at WARNING level. By default they are printed
# on stderr, which logs.output.ErrorOutput ascribes to log.error - so every
# deprecation notice from a dependency used to be reported as a server ERROR.

_show_warning = warnings.showwarning


def show_warning(message, category, filename, lineno, file=None, line=None):
    try:
        logs.log.warning("%s:%s: %s: %s" % (filename, lineno, category.__name__, message), module="Python")
    except Exception:  # logging not usable (too early, shutting down...): keep the default behaviour
        _show_warning(message, category, filename, lineno, file, line)


warnings.showwarning = show_warning

# HACK: to shut builder because it doesn't compile properly
if settings.MANAGE and "build" in other:
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
filename = os.path.splitext(os.path.basename(sys.argv[0]))[0].lower()
builtins._ = lambda value: value
