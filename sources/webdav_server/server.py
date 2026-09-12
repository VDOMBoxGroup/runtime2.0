from __future__ import absolute_import
import copy
# from . import request_server
from wsgidav.wsgidav_app import DEFAULT_CONFIG
try:
    from wsgidav.wsgidav_app import WsgiDAVApp
except ImportError as e:
    raise RuntimeError(
        "Could not import wsgidav package:\n%s\nSee http://wsgidav.googlecode.com/." % e)
from wsgidav.lock_man.lock_storage import LockStorageDict
from wsgidav.prop_man.property_manager import PropertyManager
from wsgidav.lock_man.lock_manager import LockManager
from .vdom_dav_provider import VDOM_Provider
from .domain_controller import VDOM_domain_controller, VDOM_application_login
from wsgidav.http_authenticator import HTTPAuthenticator
from .vdom_dav_provider import get_properties
import logging
import managers


class _VDOM_log_handler(logging.Handler):
    """Route wsgidav's logging into the server's own log.

    wsgidav writes through the logging module, which went nowhere here:
    ErrorPrinter catches every provider exception, logs it and returns 500. So
    the client saw "500" and the server log carried nothing - there was no way
    to know what had failed. That is what made this port blind.
    """

    def emit(self, record):
        try:
            debug("wsgidav %s: %s" % (record.levelname.lower(), self.format(record)))
        except Exception:
            pass


def _brancher_journal_wsgidav():
    racine = logging.getLogger("wsgidav")
    if any(isinstance(h, _VDOM_log_handler) for h in racine.handlers):
        return
    racine.addHandler(_VDOM_log_handler())
    racine.setLevel(logging.INFO)
    racine.propagate = False



def _pile_middleware():
    """wsgidav's stack, plus the application sign-in.

    The one written here was in reverse order - wsgidav applies the first item
    as the outermost, so the directory browser reached the provider before any
    authentication - and it was missing RequestResolver, which wsgidav annotates
    "must be the last" because it is what routes a DAV method to the resource.
    So we start from wsgidav's own and add exactly one thing, in the place that
    matters: right after HTTPAuthenticator, hence after the credentials have
    been checked and before anything reaches the provider.
    """
    stack = list(DEFAULT_CONFIG["middleware_stack"])
    stack.insert(stack.index(HTTPAuthenticator) + 1, VDOM_application_login)
    return stack


class VDOM_webdav_manager(object):

    def __init__(self):
        _brancher_journal_wsgidav()
        self.__config = DEFAULT_CONFIG.copy()
        self.__config.update({
            "host": VDOM_CONFIG["SERVER-ADDRESS"],
            "port": VDOM_CONFIG["SERVER-PORT"],
            "property_manager": True,  # Updated property manager configuration
            "provider_mapping": {},
            "http_authenticator": {
                "accept_basic": True,  # Allow basic authentication, True or False
                "accept_digest": True,  # Allow digest authentication, True or False
                "default_to_digest": True,  # Updated to use new key
            },
            "verbose": 0,
            # 64 KiB per block instead of wsgidav's 8 KiB default: this is the
            # size of the reads and writes during a GET or a PUT, so eight times
            # fewer round trips on a large file.
            "block_size": 65536,
            "middleware_stack": _pile_middleware(),
        })
        self.__index = {}
        self.__path_index = {}
        for app in managers.memory.applications.values():
            self.load_webdav(app.id)

    def _config_for(self, appid):
        """A configuration of its own, per application.

        deepcopy, not copy: the nested http_authenticator and provider_mapping
        dictionaries were shared between every application, so configuring one
        share rewrote the others - including which application the domain
        controller speaks for.

        wsgidav 4 takes the controller as a class and builds it itself, so the
        application id travels in the config for the class to read.
        """
        conf = copy.deepcopy(self.__config)
        conf["provider_mapping"] = {}
        conf["http_authenticator"]["domain_controller"] = VDOM_domain_controller
        conf["vdom_appid"] = appid
        return conf

    def load_webdav(self, appid):
        start_dav = False
        __conf = self._config_for(appid)
        app = managers.memory.applications[appid]
        for objid, obj in app.objects.items():
            if obj.type.id == '1a43b186-5c83-92fa-7a7f-5b6c252df941':
                __conf["provider_mapping"]["/" + obj.name] = VDOM_Provider(appid, obj.id)
                if not self.__index.get(appid):
                    self.__index[appid] = {obj.id: '/%s' % obj.name}
                    self.__path_index[(appid, obj.name)] = self.__index[appid]
                else:
                    self.__index[appid][obj.id] = "/%s" % obj.name
                    self.__path_index[(appid, obj.name)] = self.__index[appid]
                start_dav = True

        if start_dav:
            try:
                app.wsgidav_app = WsgiDAVApp(__conf)
            except Exception as e:
                # Into the log, not onto an output nobody reads: that is
                # exactly how "Could not resolve domain controller class" stayed
                # invisible while every share was dead.
                debug("WebDAV: application %s, aucun partage monte: %s" % (appid, e))

    def add_webdav(self, appid, objid, sharePath):
        app = managers.memory.applications.get(appid)
        __conf = {}
        if not hasattr(app, "wsgidav_app"):
            __conf = self._config_for(appid)
            # str, not bytes: wsgidav 4 keys its share map by string, so an
            # encoded path was a key nothing would ever match.
            __conf["provider_mapping"][sharePath] = VDOM_Provider(appid, objid)
            app.wsgidav_app = WsgiDAVApp(__conf)
        else:
            provider = VDOM_Provider(appid, objid)
            provider.set_share_path(sharePath)
            provider.set_lock_manager(LockManager(LockStorageDict()))
            provider.set_prop_manager(PropertyManager())
            app.wsgidav_app.provider_map[sharePath] = provider
        # self.__index[appid][objid] = sharePath
        app = managers.memory.applications[appid]
        obj = app.objects.get(objid)
        if not self.__index.get(appid):
            self.__index[appid] = {objid: sharePath}
            self.__path_index[(appid, obj.name)] = self.__index[appid]
        else:
            self.__index[appid][objid] = sharePath
            self.__path_index[(appid, obj.name)] = self.__index[appid]

    def del_webdav(self, appid, objid, sharePath):
        app = managers.memory.applications.get(appid)
        if hasattr(app, "wsgidav_app"):
            if sharePath in app.wsgidav_app.provider_map:
                del app.wsgidav_app.provider_map[sharePath]
                del self.__index[appid][objid]
                del self.__path_index[(appid, app.objects[objid].name)]
                if len(self.__index[appid]) == 0:
                    del self.__index[appid]

    def list_webdav(self, appid):
        wdav = self.__index.get(appid)
        return list(wdav.keys()) if wdav else []

    def del_all_webdav(self, appid):
        app = managers.memory.applications.get(appid)
        if hasattr(app, "wsgidav_app"):
            delattr(app, 'wsgidav_app')
        if appid in self.__index:
            del self.__index[appid]

    def get_webdav_share_path(self, appid, objid):
        if appid in self.__index:
            return self.__index[appid].get(objid, None)
        return None

    def check_webdav_share_path(self, appid, pagename):
        if appid in self.__index:
            return (appid, pagename) in self.__path_index
        return False

    # def get_webdav_obj_by_path(self, appid, sharePath):
    # if appid in self.__index:
    # davs = self.__index[appid] or {}
    # for key in davs:
    # if davs[key] ==
    # return None

    def add_to_cache(self, appid, objid, path):
        if isinstance(path, str):
            try:
                utf8path = path.encode('utf8')
                path = utf8path
            except Exception as e:
                debug("Error: %s" % e)
        get_properties(appid, objid, path)

    def invalidate(self, appid, objid, path):
        get_properties.invalidate(appid, objid, path)

    def clear(self):
        get_properties.clear()

    def change_property_value(self, app_id, obj_id, path, propname, value):
        get_properties.change_property_value(
            app_id, obj_id, path, propname, value)

    def change_parents_property(self, app_id, obj_id, path, propname, value):
        get_properties.change_parents_property(
            self, app_id, obj_id, path, propname, value)
