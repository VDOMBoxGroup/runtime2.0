
import sys
from threading import RLock

# def register(name, manager_class):
#     globals()[name] = manager_class()


# def has(*names):
#     namespace = globals()
#     for name in names:
#         if name not in namespace:
#             return False
#     return True

class Managers(object):

    __name__ = __name__

    def __init__(self):
        self._lock = RLock()
        self._lazy = {}

    def register(self, name, manager_class, lazy=False):
        with self._lock:
            if lazy:
                self._lazy[name] = manager_class
            else:
                setattr(self, name, manager_class())

    def has(self, *names):
        for name in names:
            if not (name in self.__dict__ or name in self._lazy):
                return False
        return True

    def __getattr__(self, name):
        with self._lock:
            instance = self.__dict__.get(name)
            if instance:
                return instance
            else:
                manager_class = self._lazy.get(name)
                if manager_class:
                    instance = manager_class()
                    setattr(self, name, instance)
                    return instance
                elif name == '__spec__':
                    return None
                else:
                    raise AttributeError(name)


sys.modules[__name__] = Managers()

# anounce globals for further linting
if __name__ not in sys.modules:
    from logs import VDOM_log_manager as log # noqa
    from storage import VDOM_storage as storage # noqa
    from file_access import VDOM_file_manager as file_access # noqa
    from request import VDOM_request_manager as  request_manager # noqa
    from resource import VDOM_resource_manager as resource_manager # noqa
    from database import VDOM_database_manager as databse_manager # noqa
    from scripting import VDOM_compiler as compiler, VDOM_dispatcher as dispatcher # noqa
    from memory import VDOM_memory as memory # noqa
    from engine import VDOM_engine as engine # noqa
    from server import VDOM_server as server# noqa
    # from mailing import VDOM_email_manager
    from session import VDOM_session_manager as session_manager # noqa
    from module import VDOM_module_manager as module_manager # noqa
    from soap import VDOM_soap_server as soap_server # noqa
    from webdav_server import VDOM_webdav_manager as webdav_manager # noqa

    import builtins
    from startup.debug import debug, DebugFile
    builtins.debug = debug
    builtins.debugfile = DebugFile()
    builtins._ = lambda value: value
    VDOM_CONFIG_1 = {}
    builtins.MANAGE = False
