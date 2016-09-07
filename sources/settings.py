
SERVER_ID = "5ed67d80-9017-4753-9633-685a1926a6b9"

# defaults

DEFAULT_LANGUAGE = "en"
DEFAULT_APPLICATION = None

# server

SERVER_ADDRESS = ""
SERVER_PORT = 80

# locations

REPOSITORY_LOCATION = "../repository"
TYPES_LOCATION = "../types"
APPLICATIONS_LOCATION = "../applications"
RESOURCES_LOCATION = "../resources"
CACHE_LOCATION = "../cache"
DATA_LOCATION = "../data"
TEMPORARY_LOCATION = "../temp"

# possible layout for deploying

# REPOSITORY_LOCATION = "/var/vdom/repository"
# TYPES_LOCATION = "/var/vdom/types"
# APPLICATIONS_LOCATION = "/var/vdom/applications"
# RESOURCES_LOCATION = "/var/vdom/resources"
# CACHE_LOCATION = "/var/vdom/cache"
# DATA_LOCATION = "/var/vdom/data"
# TEMPORARY_LOCATION = "/tmp"

# other locations

DATABASES_LOCATION = DATA_LOCATION + "/databases"
STORAGE_LOCATION = DATA_LOCATION + "/storage"
LOGS_LOCATION = TEMPORARY_LOCATION

SERVER_PIDFILE_LOCATION = TEMPORARY_LOCATION + "/server.pid"
LOGGER_PIDFILE_LOCATION = TEMPORARY_LOCATION + "/logger.pid"

# obsolete locations

# LOCAL_LOCATION = "../local"
# MODULES_LOCATION = LOCAL_LOCATION + "/modules"
# LIBRARIES_LOCATION = LOCAL_LOCATION + "/libraries"

FONTS_LOCATION = "../fonts"

# memory

APPLICATION_FILENAME = "application.xml"
TYPE_FILENAME = "type.xml"
APPLICATION_LIBRARIES_DIRECTORY = "libraries"
TYPE_MODULE_NAME = "type"
REPOSITORY_TYPES_DIRECTORY = "types"
RESOURCE_LINE_LENGTH = 76
STORE_DEFAULT_VALUES = False
PRELOAD_DEFAULT_APPLICATION = False

# autosave

ALLOW_TO_CHANGE = None  # "00000000-0000-0000-0000-000000000000", ...
AUTOSAVE_APPLICATIONS = True

# sessions

SESSION_LIFETIME = 1200

# timeouts

SCRIPT_TIMEOUT = 30.1
COMPUTE_TIMEOUT = 30.1
RENDER_TIMEOUT = 30.1
WYSIWYG_TIMEOUT = 30.1

# threading

QUANTUM = 0.5
COUNTDOWN = 3.0
MAIN_NAME = "Main"

# logging

if SERVER:
    LOGGING = True
    if WINDOWS:
        START_LOG_SERVER = True
    else:
        START_LOG_SERVER = False
else:
    LOGGING = False
    START_LOG_SERVER = False

LOGGING_ADDRESS = "127.0.0.1"
LOGGING_PORT = 1010

LOGGING_TIMESTAMP = "%Y-%m-%d %H:%M:%S"

LOGGING_AUTOMODULE = True
LOGGING_OUTPUT = True
DISPLAY_WARININGS_ANYWAY = True
DISPLAY_ERRORS_ANYWAY = True

# profiling

PROFILING = False
PROFILE_LOCATION = TEMPORARY_LOCATION + "/server.prs"

# scripting

STORE_SYMBOLS = False
STORE_BYTECODE = False

# watcher

WATCHER = True
WATCHER_ADDRESS = "127.0.0.1"
WATCHER_PORT = 1011

# vscript

DISABLE_VSCRIPT = 0
OPTIMIZE_VSCRIPT_PARSER = 0
SHOW_VSCRIPT_LISTING = False

# emails

SMTP_SENDMAIL_TIMEOUT = 20.0
SMTP_SERVER_ADDRESS = ""
SMTP_SERVER_PORT = 25
SMTP_SERVER_USER = ""
SMTP_SERVER_PASSWORD = ""

# licensing

PRELICENSE = {}
