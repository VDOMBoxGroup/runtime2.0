"""Request Manager module"""


import _thread

from utils.exception import VDOM_exception
from utils.semaphore import VDOM_semaphore


class VDOM_request_manager(dict):
    """Request manager class"""

    def __init__(self):
        """constructor"""
        dict.__init__(self)
        self.__sem = VDOM_semaphore()

    def __getitem__(self, key):
        raise AttributeError

    def __setitem__(self, key, value):
        raise AttributeError

    def __delitem__(self, key):
        raise AttributeError

    def __contains__(self, key):
        raise AttributeError

    def get_request(self):
        """This method should be thread-safe"""
        # self.__sem.lock()
        try:

            r = self.get(_thread.get_ident(), None)
            if r:
                return r
            raise VDOM_exception(("No request associated with current thread"))
        except Exception:
            raise VDOM_exception(("No request associated with current thread"))
        # finally:
        # self.__sem.unlock()

    def set_request(self, request):
        self.__sem.lock()
        # debug("set request")
        try:
            dict.__setitem__(self, _thread.get_ident(), request)
        finally:
            self.__sem.unlock()

    def remove_request(self):
        self.__sem.lock()
        # debug("remove request")
        try:
            dict.__delitem__(self, _thread.get_ident())
        except Exception:
            pass
        finally:
            self.__sem.unlock()

    current = property(get_request, set_request, remove_request)
