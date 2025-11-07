
import managers
from ... import errors
from ...subtypes import boolean, generic, string, true, false, v_empty, v_mismatch
from ...variables import variant
from .request import v_cookiescollection, v_sharedvariablescollection


class v_response(generic):

	def __init__(self):
		self._cookies=v_cookiescollection()
		self._sharedvariables=v_sharedvariablescollection()


	def v_cookies(self, name=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("cookies")
			else:
				return self._cookies
		else:
			return self._cookies(name, **keywords)

	def v_sharedvariables(self, name=None, **keywords):
		if name is None:
			if "let" in keywords or "set" in keywords:
				raise errors.object_has_no_property("sharedvariables")
			else:
				return self._sharedvariables
		else:
			return self._sharedvariables(name, **keywords)

	def v_isclientconnected(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("isclientconnected")
		else:
			return boolean(true)

	def v_result(self, **keywords):
		if "let" in keywords:
			managers.request_manager.current.wholeAnswer = keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("result")
		else:
			return string(managers.request_manager.current.wholeAnswer)


	def v_addheader(self, name, value):
		managers.request_manager.current.headers_out().headers() \
			.setdefault(name.as_string.lower(), value.as_string)
		return v_mismatch

	def v_redirect(self, url):
		managers.request_manager.current.redirect(url.as_string)
		return v_mismatch

	def v_write(self, data):
		managers.request_manager.current.write(data.as_string)
		return v_mismatch

	def v_sendfile(self, filename, content, contenttype=None):
		try:
			content=content.as_string.encode("utf8")
			content_type="text/plain" if contenttype is None else contenttype.as_stirng
		except errors.type_mismatch:
			content=content.as_binary
			content_type="application/octet-stream" if contenttype is None else contenttype.as_stirng
		request=managers.request_manager.current
		request.add_header("Content-type", content_type)
		request.add_header("Content-Disposition", "attachment; filename=\"%s\""%filename.as_string)
		request.add_header("Content-Length", str(len(content)))
		request.set_nocache()
		request.write(content)
