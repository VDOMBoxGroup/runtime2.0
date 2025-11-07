
from threading import Lock
from weakref import WeakValueDictionary
from logs import server_log, network_log, security_log
from .sublogs import ApplicationLog


LOGGING = None


class VDOM_log_manager_logs(object):

    def __init__(self):
        self._application_logs = WeakValueDictionary()
        self._lock = Lock()

    server = property(lambda self: server_log)
    network = property(lambda self: network_log)
    security = property(lambda self: security_log)

    def application(self, id):
        with self._lock:
            try:
                return self._application_logs[id]
            except KeyError:
                self._application_logs[id] = log = ApplicationLog(id)
                return log


class LogManager(object):

    message_info = 0
    message_error = 1

    log_server = 0
    log_user = 1
    log_bug = 2

    message_types = {message_info: "INFO", message_error: "ERROR"}

    def __init__(self):
        self._logs = VDOM_log_manager_logs()

    logs = property(lambda self: self._logs)

    def info(self, log_type, message_text, caller=""):
        server_log.debug("%s (%s)" % (message_text, caller) if caller else message_text)

    def error(self, log_type, message_text, caller=""):
        server_log.error("%s (%s)" % (message_text, caller) if caller else message_text)

    def info_server(self, message_text, caller=None):
        server_log.debug("%s (%s)" % (message_text, caller) if caller else message_text)

    def error_server(self, message_text, caller=""):
        server_log.error("%s (%s)" % (message_text, caller) if caller else message_text)

    def info_user(self, message_text, caller=""):
        server_log.debug("%s (%s)" % (message_text, caller) if caller else message_text)

    def error_user(self, message_text, caller=""):
        server_log.error("%s (%s)" % (message_text, caller) if caller else message_text)

    def info_bug(self, message_text, caller=""):
        server_log.debug("%s (%s)" % (message_text, caller) if caller else message_text)

    def error_bug(self, message_text, caller=""):
        server_log.error("%s (%s)" % (message_text, caller) if caller else message_text)


VDOM_log_manager = LogManager
