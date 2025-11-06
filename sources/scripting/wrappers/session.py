
from builtins import object
import managers


class VDOM_session(object):

    def _get_id(self):
        return managers.request_manager.current.session().id()

    def __getitem__(self, name):
        if name == "response":  # temporary solution for backward compability of Whole
            return managers.request_manager.current.wholeAnswer
        return managers.request_manager.current.session()[name]

    def __setitem__(self, name, value):
        if name == "response":  # temporary solution for backward compability of Whole
            managers.request_manager.current.wholeAnswer = value
        managers.request_manager.current.session()[name] = value

    def __delitem__(self, name):
        del managers.request_manager.current.session()[name]

    def get(self, name, default=None):
        return managers.request_manager.current.session().get(name, default)

    def keys(self):
        return list(managers.request_manager.current.session().keys())

    def __iter__(self):
        return iter(managers.request_manager.current.session())

    id = property(_get_id)
