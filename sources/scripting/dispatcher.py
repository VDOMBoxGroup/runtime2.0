from __future__ import absolute_import

from builtins import str
from builtins import object
from threading import RLock
from logs import log

# import SOAPpy

from utils.properties import roproperty
from utils.tracing import format_exception_trace, show_exception_trace

import managers

# import utils
# from utils.exception import *
# from utils.exception import VDOM_exception_handler


UNKNOWN = "UNKNOWN"


class DispatcherEntry(object):

    def __init__(self, entries, type):
        self._entries = entries
        self._type = type
        self._module = None
        self._handlers = {}

    type = roproperty("_type")
    handlers = roproperty("_handlers")

    def new(self, name):
        self._handlers[name] = UNKNOWN

    def __getitem__(self, name):
        handler = self._handlers.get(name)
        if handler is UNKNOWN:
            with self._entries._lock:
                handler = self._handlers.get(name)
                if handler is UNKNOWN:
                    if not self._module:
                        try:
                            self._module = __import__(self._type.module_name)
                        except BaseException:
                            log.error("[Dispatcher] Unable to import module: %s" % format_exception_trace())
                            self._module = {"__doc__": "Unable to load %s" % self._type.module_name}
                    self._handlers[name] = handler = getattr(self._module, name, None)
        return handler


class DispatcherEntries(object):

    def __init__(self):
        self._lock = RLock()
        self._entries = {}

    def __getitem__(self, type):
        if type in self._entries:
            return self._entries[type]
        else:
            with self._lock:
                entry = self._entries.get(type)
                if not entry:
                    self._entries[type] = entry = DispatcherEntry(self, type)
                return entry


class Dispatcher(object):

    def __init__(self):
        self._entries = DispatcherEntries()
        self._remote_methods = DispatcherEntries()

    def add_handler(self, type, name):
        self._entries[type].new(name)

    def add_remote_method(self, type, name):
        self._remote_methods[type].new(name)

    # Underscores are used to avoid name conflicts with keywords
    def dispatch_handler(self, _object_, _name_, *arguments, **keywords):
        handler = self._entries[_object_.type][_name_]
        if handler:
            try:
                return handler(_object_, *arguments, **keywords)
            except BaseException:
                show_exception_trace(caption="Unhandled exception in %s %s handler" % (_object_.type, _name_), locals=True)

    # Underscores are used to avoid name conflicts with keywords
    def dispatch_remote_method(self, _object_, _name_, *arguments, **keywords):
        method = self._remote_methods[_object_.type][_name_]
        session_id = keywords.pop("session_id")
        if session_id:
            arguments = arguments + (session_id,)
        if method:
            return method(_object_, *arguments, **keywords)


    def dispatch_action(self, app_id, object_id, func_name, xml_param, xml_data):
        app = managers.memory.applications.get(app_id)
        if not app:
            raise Exception("Application not found:%s"%app_id)
        obj = app.objects.catalog[object_id]
        action = obj.actions.get(func_name) if obj else None
        if not action:
            raise Exception("Action not found:%s"%func_name)

        request = managers.request_manager.get_request()
        request.arguments().arguments({"xml_param": [xml_param], "xml_data": [xml_data]})

        try:
            managers.engine.execute(action)
        except Exception as error:
            if hasattr(error, "message") and isinstance(error.message, str):
                message = str(error).encode("utf8")
            else:
                message = str(error)
            import SOAPpy
            from .soap.errors import remote_method_call_error
            raise SOAPpy.faultType(remote_method_call_error, _("Remote method call error"), message)

        response = request.session().value("response")
        request.session().remove("response")
        return response or ""
VDOM_dispatcher = Dispatcher
