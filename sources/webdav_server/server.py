from __future__ import absolute_import
from . import request_server
from wsgidav.wsgidav_app import DEFAULT_CONFIG
try:
    from wsgidav.wsgidav_app import WsgiDAVApp
except ImportError as e:
    raise RuntimeError("Could not import wsgidav package:\n%s\nSee http://wsgidav.googlecode.com/." % e)
from wsgidav.lock_man.lock_storage import LockStorageDict
from wsgidav.prop_man.property_manager import PropertyManager
from wsgidav.lock_man.lock_manager import LockManager
from wsgidav.mw.debug_filter import WsgiDavDebugFilter
from .vdom_dav_provider import VDOM_Provider
from .domain_controller import VDOM_domain_controller, VDOM_HTTPAuthenticator
from .vdom_dav_provider import get_properties
from wsgidav.error_printer import ErrorPrinter
from wsgidav.dir_browser import WsgiDavDirBrowser
import managers


class VDOM_webdav_manager(object):

    def __init__(self):
        self.__config = DEFAULT_CONFIG.copy()
        self.__config.update({"host": VDOM_CONFIG["SERVER-ADDRESS"],
                              "port": VDOM_CONFIG["SERVER-PORT"],
                              "propsmanager": True,
                              "provider_mapping": {},
                              "acceptbasic": True,  # Allow basic authentication, True or False
                              "acceptdigest": True,  # Allow digest authentication, True or False
                              "defaultdigest": True,
                              "verbose": 0,
                              "middleware_stack": [
                                  WsgiDavDirBrowser,
                                      VDOM_HTTPAuthenticator,
                                      ErrorPrinter,
                                      WsgiDavDebugFilter,
                              ]
                              })
        self.__index = {}
        self.__path_index = {}
        for app in managers.memory.applications.values():
            self.load_webdav(app.id)

    def load_webdav(self, appid):
        start_dav = False
        __conf = self.__config.copy()
        __conf["domaincontroller"] = VDOM_domain_controller(appid)
        app = managers.memory.applications[appid]
        for objid, obj in app.objects.items():
            if obj.type.id == '1a43b186-5c83-92fa-7a7f-5b6c252df941':
                __conf["provider_mapping"]["/" + obj.name.encode('utf8')] = VDOM_Provider(appid, obj.id)
                if not self.__index.get(appid):
                    self.__index[appid] = {obj.id : '/%s'%obj.name}
                    self.__path_index[(appid,obj.name)] = self.__index[appid]
                else:
                    self.__index[appid][obj.id] = "/%s"%obj.name
                    self.__path_index[(appid, obj.name)] = self.__index[appid]
                start_dav = True

        if start_dav: app.wsgidav_app = WsgiDAVApp(__conf)

    def add_webdav(self, appid, objid, sharePath):
        app = managers.memory.applications.get(appid)
        __conf = {}
        if not hasattr(app, "wsgidav_app"):
            __conf = self.__config.copy()
            __conf["domaincontroller"] = VDOM_domain_controller(appid)
            __conf["provider_mapping"][sharePath.encode('utf8')] = VDOM_Provider(appid, objid)
            app.wsgidav_app = WsgiDAVApp(__conf)
        else:
            provider = VDOM_Provider(appid, objid)
            provider.setSharePath(sharePath.encode('utf8'))
            provider.setLockManager(LockManager(LockStorageDict()))
            provider.setPropManager(PropertyManager())
            app.wsgidav_app.providerMap[sharePath.encode('utf8')] = provider
        #self.__index[appid][objid] = sharePath
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
            if sharePath.encode('utf8') in app.wsgidav_app.providerMap:
                del app.wsgidav_app.providerMap[sharePath.encode('utf8')]
                del self.__index[appid][objid]
                del self.__path_index[(appid, app.objects[objid].name)]
                if len(self.__index[appid]) == 0: del self.__index[appid]

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

    #def get_webdav_obj_by_path(self, appid, sharePath):
    #	if appid in self.__index:
    #		davs = self.__index[appid] or {}
    #		for key in davs:
    #			if davs[key] == 
    #	return None		

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
        get_properties.change_property_value(app_id, obj_id, path, propname, value)

    def change_parents_property(self, app_id, obj_id, path, propname, value):
        get_properties.change_parents_property(self, app_id, obj_id, path, propname, value)
