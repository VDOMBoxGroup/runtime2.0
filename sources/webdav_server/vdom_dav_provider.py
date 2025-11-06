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


from collections import OrderedDict
from wsgidav.dav_error import DAVError, HTTP_FORBIDDEN,HTTP_REQUEST_TIMEOUT,HTTP_NOT_FOUND
from wsgidav.dav_provider import DAVProvider, DAVCollection, DAVNonCollection, _DAVResource
from wsgidav.prop_man.property_manager import PropertyManager
from io import StringIO


import os
import mimetypes
import shutil
import stat
import managers
from .webdav_request import VDOM_webdav_request
from .webdav_cache import lru_cache
import posixpath
import tempfile
import logging
__docformat__ = "reStructuredText"

_logger = logging.getLogger(__name__)

BUFFER_SIZE = 8192

@lru_cache(maxsize=1000)
def get_properties(app_id, obj_id, path):
	props = managers.dispatcher.dispatch_action(app_id, obj_id, "getResourseProperties", "", """{"path": "%s"}""" % path)
	if props:
		return (props, 1)


class VDOM_resource(_DAVResource):

	def __init__(self, path, isCollection, environ, app_id, obj_id, props=None):
		super(VDOM_resource, self).__init__(path, isCollection, environ)
		self._obj_id = obj_id
		self._app_id = app_id
		self._properties = props
		self._tmpfile = None #Needed for fast upload

	def _get_info(self, prop):
		try:#TODO! make lazy load with prop saving(beside cache)
			if not self._properties:
				self._properties= get_properties(self._app_id, self._obj_id, self.path)[0]
			return self._properties.get(prop)
		except:
			return None

	def getContentLength(self):
		if self.isCollection:
			return None
		return self._get_info("getcontentlength")

	def getContentType(self):
		if self.isCollection:
			return None
		return self._get_info("getcontenttype")

	def getCreationDate(self):
		return self._get_info("creationdate")

	def getDirectoryInfo(self):
		"""Return a list of dictionaries with information for directory 
		rendering.

		This default implementation return None, so the dir browser will
		traverse all members. 

		This method COULD be implemented for collection resources.
		"""
		assert self.isCollection
		return None

	def getDisplayName(self):
		return self._get_info("dispayname") or self.name

	def getEtag(self):
		return self._get_info("getetag")

	def getLastModified(self):
		return self._get_info("getlastmodified")

	def supportRanges(self):
		return True

	def getContent(self):
		"""Open content as a stream for reading.

		See DAVResource.getContent()
		"""
		assert not self.isCollection
		func_name = "open"
		xml_data = """{"path": "%s", "mode": "rb"}""" % self.path
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return ret
		return None
	@property
	def parent(self):
		return util.getUriParent(self.path)

	@property
	def filename(self):
		return util.getUriName(self.path)
	
	def createEmptyResource(self, name):
		assert self.isCollection
		#func_name = "createResource"
		return self.provider.createResourceInst(self.path,name, self.environ)
		
		#xml_data = """{"path": "%s", "name": "%s"}""" % (self.path, name)
		#ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		#if ret:
		#	res = self.provider.getResourceInst(util.joinUri(self.path, name), self.environ)
		#	if res:
		#		#get_properties.invalidate(self._app_id, self._obj_id, self.path)
		#		return res

		#raise DAVError(HTTP_FORBIDDEN)               

	def createCollection(self, name):
		assert self.isCollection
		func_name = "createCollection"
		xml_data = """{"path": "%s", "name": "%s"}""" % (self.path, name)
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			res = self.provider.getResourceInst(util.joinUri(self.path, name), self.environ)
			if res:
				#get_properties.invalidate(self._app_id, self._obj_id, self.path)
				return res
		raise DAVError(HTTP_FORBIDDEN)               


	def getMember(self, name, preloaded = None):
		assert self.isCollection
		return self.provider.getResourceInst(util.joinUri(self.path, name), 
		                                     self.environ,preloaded)	

	def getMemberNames(self):
		assert self.isCollection
		memberNames = get_properties.get_children_names(self._app_id, self._obj_id, self.path)
		return memberNames	
	
	def getMemberChildren(self):
		assert self.isCollection
		return get_properties.get_children(self._app_id, self._obj_id, self.path) or {}
		
	def getMemberList(self):
		"""Return a list of direct members (Overwritten for later performance tuning).

		This default implementation calls self.getMemberNames() and 
		self.getMember() for each of them.
		"""
		if not self.isCollection:
			raise NotImplementedError()
		memberList = [] 
		for name, child in self.getMemberChildren().items():
			member = self.getMember(name,child) 
			assert member is not None
			memberList.append(member)
		return memberList			

	def beginWrite(self, contentType=None):

		assert not self.isCollection
		self._tmpfile = tempfile.NamedTemporaryFile("w+b",prefix="webdavupload",dir=VDOM_CONFIG["TEMP-DIRECTORY"],delete=False)
		return self._tmpfile
		#func_name = "open"
		#xml_data = """{"path": "%s", "mode": "wb"}""" % self.path
		#ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		#if ret:
		#	return ret
		#raise DAVError(HTTP_FORBIDDEN)       


	def endWrite(self, withErrors):
		"""Called when PUT has finished writing.

		This is only a notification. that MAY be handled.
		"""
		func_name = "put"
		#xml_data = """{"path": "%s"}""" % self.path
		data = {'path':posixpath.normpath(self.parent), 'handler':self._tmpfile, 'name':self.filename}
		data['overwrite'] = self._properties is not None
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",data)
		if os.path.exists(self._tmpfile.name):
			os.unlink(self._tmpfile.name)
		#get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.getUriParent(self.path)))

	def handleDelete(self):
		if self.provider.readonly:
			raise DAVError(HTTP_FORBIDDEN)
		self.provider.lockManager.checkWritePermission(self.path, self.environ["HTTP_DEPTH"], 
		                                               self.environ["wsgidav.ifLockTokenList"], 
		                                               self.environ["wsgidav.username"])
		func_name = "delete"
		xml_data = """{"path": "%s"}""" % self.path
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return True
		else:
			if self.path == "/":
				get_properties.invalidate( self._app_id, self._obj_id, "/" )
			else:
				get_properties.invalidate( self._app_id, self._obj_id, posixpath.normpath(util.getUriParent(self.path)))

			raise DAVError(HTTP_FORBIDDEN)

	def handleCopy(self, destPath, depthInfinity):
		func_name = "copy"
		xml_data = """{"srcPath": "%s", "destPath": "%s"}""" % (self.path, destPath)
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			#get_properties.invalidate(self._app_id, self._obj_id, os.path.normpath(util.getUriParent(destPath)))
			return True

		raise DAVError(HTTP_FORBIDDEN)	

	def handleMove(self, destPath):
		func_name = "move"
		xml_data = """{"srcPath": "%s", "destPath": "%s"}""" % (self.path, destPath)
		ret = managers.dispatcher.dispatch_action(self._app_id, self._obj_id, func_name, "",xml_data)
		if ret:
			return True

		raise DAVError(HTTP_FORBIDDEN)	


#===============================================================================
# FilesystemProvider
#===============================================================================
class VDOM_Provider(DAVProvider):

	def __init__(self, appid, objid, readonly=False):
		super(VDOM_Provider, self).__init__()
		try:
			self.application = managers.memory.applications.get(appid)
			self.obj = self.application.objects.get(objid)
		except:
			self.application = None
			self.obj = None

		self.readonly = readonly


	def __repr__(self):
		rw = "Read-Write"
		if self.readonly:
			rw = "Read-Only"
		return "%s for WebDAV (%s)" % (self.__class__.__name__, rw)

#	def _setApplication(self, host):
#
#		vh = managers.virtual_hosts
#		app_id = vh.get_site(host.lower())
#		if not app_id:
#			app_id = vh.get_def_site()
#		self.__app = managers.xml_manager.get_application(app_id)


#	def _getObjectId(self, path):
#		pathInfoParts = path.strip("/").split("/")
#		name = pathInfoParts[0]
#		if not self.__app:
#			return None

#		try:        
#			obj = self.__app.get_objects_by_name()[name.lower()]
#			r  = util.toUnicode(obj.id) if obj else None
#		except:
#			r = ""
#		return r


	def getResourceInst(self, path, environ,preloaded = None):
		"""Return info dictionary for path.

		See DAVProvider.getResourceInst()
		"""
		self._count_getResourceInst += 1
		path = posixpath.normpath(path or "/")
		try:
			if self.application and self.obj:
				if preloaded:
					res = (preloaded,)
				else:
					try:
						res = get_properties(self.application.id, self.obj.id, path)
					except Exception as e:
						debug("getResourceInst error: %s"%e)
						raise DAVError(HTTP_REQUEST_TIMEOUT)

				if not res or res[0]==None:
					return None
				else:
					isCollection = True if res[0]["resourcetype"] == "Directory" else False
					return VDOM_resource(path, isCollection, environ, self.application.id, self.obj.id,res[0])

		except Exception as e:
			debug("getResourceInst error: %s"%e)
			raise DAVError(HTTP_FORBIDDEN)
		return None
	
	def createResourceInst(self, parent, name, environ):
		self._count_getResourceInst += 1
		try:
			res = VDOM_resource(util.joinUri(parent, name), False, environ, self.application.id, self.obj.id,None)
			res.name = name
			#res.parent = parent
			return res
		except:
			raise DAVError(HTTP_FORBIDDEN)	
		