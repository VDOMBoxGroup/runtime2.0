# (c) 2009-2011 Martin Wendt and contributors; see WsgiDAV http://wsgidav.googlecode.com/
# Original PyFileServer (c) 2005 Ho Chun Wei.
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""
Implementation of a DAV provider that serves resource from a file system.

ReadOnlyFilesystemProvider implements a DAV resource provider that publishes
a file system for read-only access.
Write attempts will raise HTTP_FORBIDDEN.

FilesystemProvider inherits from ReadOnlyFilesystemProvider and implements the
missing write access functionality.

See `Developers info`_ for more information about the WsgiDAV architecture.

.. _`Developers info`: http://docs.wsgidav.googlecode.com/hg/html/develop.html
"""
from __future__ import absolute_import


from wsgidav.dav_error import DAVError, HTTP_FORBIDDEN, HTTP_REQUEST_TIMEOUT, util
from wsgidav.dav_provider import DAVProvider, _DAVResource


import os
import managers
from .webdav_cache import lru_cache
import posixpath
import tempfile
import logging
__docformat__ = "reStructuredText"

_logger = logging.getLogger(__name__)

BUFFER_SIZE = 8192


# 20000, not 1000: every file seen takes one entry, and a PROPFIND on a working
# folder puts in as many as it holds. At 1000, a single well-stocked folder
# evicted everything else and every re-read went back to the engine. An entry
# weighs a few hundred bytes.
@lru_cache(maxsize=20000)
def get_properties(app_id, obj_id, path):
    props = managers.dispatcher.dispatch_action(
        app_id, obj_id, "getResourseProperties", "", """{"path": "%s"}""" % path)
    if props:
        return (props, 1)


class VDOM_resource(_DAVResource):

    def __init__(self, path, is_collection, environ, app_id, obj_id, props=None):
        super(VDOM_resource, self).__init__(path, is_collection, environ)
        self._obj_id = obj_id
        self._app_id = app_id
        self._properties = props
        self._tmpfile = None  # Needed for fast upload

    def _get_info(self, prop):
        try:  # TODO! make lazy load with prop saving(beside cache)
            if not self._properties:
                self._properties = get_properties(
                    self._app_id, self._obj_id, self.path)[0]
            return self._properties.get(prop)
        except Exception:
            return None

    def get_content_length(self):
        if self.is_collection:
            return None
        return self._get_info("getcontentlength")

    def get_content_type(self):
        if self.is_collection:
            return None
        return self._get_info("getcontenttype")

    def get_creation_date(self):
        return self._get_info("creationdate")

    def get_directory_info(self):
        """Return a list of dictionaries with information for directory rendering.

        This default implementation return None, so the dir browser will traverse all members.

        This method COULD be implemented for collection resources.
        """
        assert self.is_collection
        return None

    def get_display_name(self):
        return self._get_info("dispayname") or self.name

    def get_etag(self):
        return self._get_info("getetag")

    def get_last_modified(self):
        return self._get_info("getlastmodified")

    def support_ranges(self):
        return True

    def support_etag(self):
        """No: this application has no ETag.

        wsgidav 4 asks for it, and its base version raises NotImplementedError -
        which is what turned everything touching a file into a 500, since do_PUT
        calls it to set the header.

        Answering "self.get_etag() is not None" would be correct and expensive:
        getResourseProperties and getMembers both return "getetag": None,
        always. So we paid a full property read after every write to learn there
        is no ETag. The day the application provides one, this method changes
        with it.
        """
        return False

    def get_content(self):
        """Open content as a stream for reading.

        See DAVResource.getContent()
        """
        assert not self.is_collection
        func_name = "open"
        xml_data = """{"path": "%s", "mode": "rb"}""" % self.path
        ret = managers.dispatcher.dispatch_action(
            self._app_id, self._obj_id, func_name, "", xml_data)
        if ret:
            return ret
        return None

    @property
    def parent(self):
        return util.get_uri_parent(self.path)

    @property
    def filename(self):
        return util.get_uri_name(self.path)

    def create_empty_resource(self, name):
        assert self.is_collection
        # The path is about to exist: forget having seen it missing.
        missing = self.provider._known_missing()
        if missing is not None:
            missing.discard(posixpath.normpath(util.join_uri(self.path, name)))
        # func_name = "createResource"
        return self.provider.create_resource_inst(self.path, name, self.environ)

        # xml_data = """{"path": "%s", "name": "%s"}""" % (self.path, name)
        # ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
        # if ret:
        # res = self.provider.get_resource_inst(util.join_uri(self.path, name), self.environ)
        # if res:
        # #get_properties.invalidate(self._app_id, self._obj_id, self.path)
        # return res

        # raise DAVError(HTTP_FORBIDDEN)

    def create_collection(self, name):
        assert self.is_collection
        # The path is about to exist: forget having seen it missing, otherwise
        # the re-read right after still believes it absent and MKCOL answers 403
        # for a folder that has just been created. Measured: that is exactly
        # what happened when the memo was added without this line.
        missing = self.provider._known_missing()
        if missing is not None:
            missing.discard(posixpath.normpath(util.join_uri(self.path, name)))
        func_name = "createCollection"
        xml_data = """{"path": "%s", "name": "%s"}""" % (self.path, name)
        ret = managers.dispatcher.dispatch_action(
            self._app_id, self._obj_id, func_name, "", xml_data)
        if ret:
            res = self.provider.get_resource_inst(
                util.join_uri(self.path, name), self.environ)
            if res:
                # get_properties.invalidate(self._app_id, self._obj_id, self.path)
                return res
        raise DAVError(HTTP_FORBIDDEN)

    def get_member(self, name, preloaded=None):
        assert self.is_collection
        return self.provider.get_resource_inst(util.join_uri(self.path, name),
                                               self.environ, preloaded)

    def get_member_names(self):
        assert self.is_collection
        memberNames = get_properties.get_children_names(
            self._app_id, self._obj_id, self.path)
        return memberNames

    def get_member_children(self):
        assert self.is_collection
        return get_properties.get_children(self._app_id, self._obj_id, self.path) or {}

    def get_member_list(self):
        """Return a list of direct members (Overwritten for later performance tuning).

        This default implementation calls self.get_member_names() and self.get_member() for each of them.
        """
        if not self.is_collection:
            raise NotImplementedError()
        memberList = []
        try:
            for name, child in self.get_member_children().items():
                member = self.get_member(name, child)
                if member is None:
                    # A child the provider cannot build is no reason to lose
                    # the whole listing. The assert that used to be here took
                    # the entire response down with it, as a 500.
                    debug("get_member_list: %s/%s introuvable, ignore" % (self.path, name))
                    continue
                memberList.append(member)
        except Exception as e:
            debug("get_member_list error on %s: %s" % (self.path, e))
            from utils.tracing import format_exception_trace
            debug(format_exception_trace())
            raise
        return memberList

    def begin_write(self, *, content_type=None):

        assert not self.is_collection
        self._tmpfile = tempfile.NamedTemporaryFile(
            "w+b", prefix="webdavupload", dir=VDOM_CONFIG["TEMP-DIRECTORY"], delete=False)
        return self._tmpfile
        # func_name = "open"
        # xml_data = """{"path": "%s", "mode": "wb"}""" % self.path
        # ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
        # if ret:
        # return ret
        # raise DAVError(HTTP_FORBIDDEN)

    def end_write(self, *, with_errors):
        """Called when PUT has finished writing.

        This is only a notification. that MAY be handled.
        """
        func_name = "put"
        # xml_data = """{"path": "%s"}""" % self.path
        data = {'path': posixpath.normpath(
            self.parent), 'handler': self._tmpfile, 'name': self.filename}
        data['overwrite'] = self._properties is not None
        managers.dispatcher.dispatch_action(
            self._app_id, self._obj_id, func_name, "", data)
        if os.path.exists(self._tmpfile.name):
            os.unlink(self._tmpfile.name)
        # get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.get_uri_parent(self.path)))

    def handle_delete(self):
        if self.provider.readonly:
            raise DAVError(HTTP_FORBIDDEN)
        # Keyword arguments: the wsgidav 4 signature is
        # check_write_permission(*, url, depth, token_list, principal).
        self.provider.lock_manager.check_write_permission(
            url=self.path,
            depth=self.environ.get("HTTP_DEPTH", "0"),
            token_list=self.environ["wsgidav.ifLockTokenList"],
            principal=self.environ.get("wsgidav.auth.user_name"))
        func_name = "delete"
        xml_data = """{"path": "%s"}""" % self.path
        ret = managers.dispatcher.dispatch_action(
            self._app_id, self._obj_id, func_name, "", xml_data)
        if ret:
            self._forget_locks_and_properties()
            return True
        else:
            if self.path == "/":
                get_properties.invalidate(self._app_id, self._obj_id, "/")
            else:
                get_properties.invalidate(
                    self._app_id, self._obj_id, posixpath.normpath(util.get_uri_parent(self.path)))

            raise DAVError(HTTP_FORBIDDEN)

    def _forget_locks_and_properties(self):
        """Whatever was attached to this path goes with it.

        wsgidav calls remove_all_locks nowhere: the provider that deletes does
        its own cleanup. Theirs does it inside delete(); here, handle_delete
        returns True - "I handled everything" - and wsgidav answers 204 at once
        without touching the lock manager.

        So the lock outlived the resource, held on a URL that no longer existed.
        A file client recopying does exactly this:

            PROPFIND 404 -> PUT 201 -> LOCK 200 -> DELETE 204 -> PUT 201 -> LOCK 423

        it deletes and recreates, and its own earlier lock blocks its way.
        Windows Explorer reports that 423 as a name conflict - "a file with the
        same name already exists" - about an empty folder, which leads nowhere.
        """
        try:
            self.remove_all_properties(recursive=True)
        except Exception as e:
            debug("WebDAV: properties of %s not cleaned up: %s" % (self.path, e))
        try:
            self.remove_all_locks(recursive=True)
        except Exception as e:
            debug("WebDAV: locks on %s not released: %s" % (self.path, e))

    def handle_copy(self, dest_path, *, depth_infinity):
        func_name = "copy"
        xml_data = """{"srcPath": "%s", "destPath": "%s"}""" % (
            self.path, dest_path)
        ret = managers.dispatcher.dispatch_action(
            self._app_id, self._obj_id, func_name, "", xml_data)
        if ret:
            # get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.get_uri_parent(destPath)))
            return True

        raise DAVError(HTTP_FORBIDDEN)

    def handle_move(self, dest_path):
        func_name = "move"
        xml_data = """{"srcPath": "%s", "destPath": "%s"}""" % (
            self.path, dest_path)
        ret = managers.dispatcher.dispatch_action(
            self._app_id, self._obj_id, func_name, "", xml_data)
        if ret:
            # The source no longer exists, and neither does what locked it.
            self._forget_locks_and_properties()
            return True

        raise DAVError(HTTP_FORBIDDEN)


# ===============================================================================
# FilesystemProvider
# ===============================================================================
class VDOM_Provider(DAVProvider):

    def __init__(self, appid, objid, readonly=False):
        super(VDOM_Provider, self).__init__()
        try:
            self.application = managers.memory.applications.get(appid)
            self.obj = self.application.objects.get(objid)
        except Exception:
            self.application = None
            self.obj = None

        self.readonly = readonly

    def __repr__(self):
        rw = "Read-Write"
        if self.readonly:
            rw = "Read-Only"
        return "%s for WebDAV (%s)" % (self.__class__.__name__, rw)

# def _setApplication(self, host):
#
# vh = managers.virtual_hosts
# app_id = vh.get_site(host.lower())
# if not app_id:
# app_id = vh.get_def_site()
# self.__app = managers.xml_manager.get_application(app_id)


# def _getObjectId(self, path):
# pathInfoParts = path.strip("/").split("/")
# name = pathInfoParts[0]
# if not self.__app:
# return None

# try:
# obj = self.__app.get_objects_by_name()[name.lower()]
# r  = util.toUnicode(obj.id) if obj else None
# except:
# r = ""
#     return r

    @staticmethod
    def _known_missing():
        """The paths already found absent during THIS request.

        get_properties caches non-empty answers only, so every question about a
        path that does not exist costs a round trip to the engine. wsgidav asks
        twice for the same file at the start of a PUT - do_PUT, then
        _evaluate_if_headers - and the file does not exist either time.

        The memo is carried by the request object: it is born and dies with it,
        so a file created elsewhere between two requests is seen normally.
        Putting absence into the global cache would be faster and wrong.
        """
        try:
            request = managers.request_manager.current
        except Exception:
            return None
        missing = getattr(request, "_dav_known_missing", None)
        if missing is None:
            missing = set()
            try:
                request._dav_known_missing = missing
            except Exception:
                return None
        return missing

    def get_resource_inst(self, path, environ, preloaded=None):
        """Return info dictionary for path.

        See DAVProvider.get_resource_inst()
        """
        self._count_get_resource_inst += 1
        path = posixpath.normpath(path or "/")
        missing = self._known_missing()
        if missing is not None and not preloaded and path in missing:
            return None
        try:
            if self.application and self.obj:
                if preloaded:
                    res = (preloaded,)
                else:
                    try:
                        res = get_properties(
                            self.application.id, self.obj.id, path)
                    except Exception as e:
                        debug("get_resource_inst error: %s" % e)
                        raise DAVError(HTTP_REQUEST_TIMEOUT)

                if not res or res[0] is None:
                    if missing is not None:
                        missing.add(path)
                    return None
                else:
                    is_collection = res[0]["resourcetype"] == "Directory"
                    return VDOM_resource(path, is_collection, environ, self.application.id, self.obj.id, res[0])

        except Exception as e:
            debug("get_resource_inst error: %s" % e)
            raise DAVError(HTTP_FORBIDDEN)
        return None

    def create_resource_inst(self, parent, name, environ):
        self._count_get_resource_inst += 1
        try:
            res = VDOM_resource(util.join_uri(
                parent, name), False, environ, self.application.id, self.obj.id, None)
            res.name = name
            # res.parent = parent
            return res
        except Exception:
            raise DAVError(HTTP_FORBIDDEN)
