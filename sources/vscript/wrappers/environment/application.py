
import os
import managers
from file_access import storage
from utils.exception import VDOM_exception_file_access
from ... import errors
from ...subtypes import binary, generic, string, boolean, true, false, v_mismatch, v_nothing
from ...variables import variant


def normailze(filename):
	norm_name=os.path.normpath(filename)
	#rel_path=os.path.relpath(os.path.abspath(managers.file_manager.get_path(storage,
	#	managers.request_manager.current.application_id, None, norm_name)),
	#	os.path.abspath(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"]))
	rel_path=os.path.relpath(os.path.abspath(managers.file_manager.locate(storage,
		managers.request_manager.current.application_id, norm_name)),
		os.path.abspath(VDOM_CONFIG["FILE-STORAGE-DIRECTORY"]))
	if rel_path[:36]!=managers.request_manager.current.application_id:
		raise VDOM_exception_file_access("Provided file name is invalid")
	return norm_name


class v_storage(generic):
	
	def v_exists(self, filename):
		try:
			#return boolean(managers.file_manager.exists(storage,
			#	managers.request_manager.current.application_id, None,
			#	normailze(filename.as_string)))
			return boolean(managers.file_manager.exists(storage,
				managers.request_manager.current.application_id,
				normailze(filename.as_string)))
		except IOError as exception:
			raise errors.system_error(exception.strerror)
	
	def v_delete(self, filename):
		try:
			# managers.file_manager.delete(storage,
			#	managers.request_manager.current.application_id, None,
			#	normailze(filename.as_string))
			managers.file_manager.delete(storage,
				managers.request_manager.current.application_id,
				normailze(filename.as_string))
		except IOError as exception:
			raise errors.system_error(exception.strerror)
		return v_mismatch

	def v_read(self, filename):
		try:
			# contents=managers.file_manager.read(storage,
			#	managers.request_manager.current.application_id, None,
			#	normailze(filename.as_string))
			contents=managers.file_manager.read(storage,
				managers.request_manager.current.application_id,
				normailze(filename.as_string))
		except IOError as exception:
			raise errors.system_error(exception.strerror)
		try:
			return string(contents.decode("utf-8"))
		except UnicodeDecodeError:
			return binary(contents)

	def v_write(self, filename, contents, asynchronous=None):
		try:
			contents=contents.as_string.encode("utf-8")
		except errors.type_mismatch:
			contents=contents.as_binary
		try:
			# managers.file_manager.write(storage,
			#	managers.request_manager.current.application_id, None,
			#	normailze(filename.as_string), contents,
			#	write_async=False if asynchronous is None else asynchronous.as_boolean)
			managers.file_manager.write(storage,
				managers.request_manager.current.application_id,
				normailze(filename.as_string), contents,
				write_async=False if asynchronous is None else asynchronous.as_boolean)
		except IOError as exception:
			raise errors.system_error(exception.strerror)
		return v_mismatch


class v_application(generic):

	def __init__(self):
		self._storage=v_storage()

	def v_id(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("storage")
		else:
			return string(managers.request_manager.current.application().id)

	def v_name(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("storage")
		else:
			return string(managers.request_manager.current.application().name)

	def v_storage(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("storage")
		else:
			return self._storage
