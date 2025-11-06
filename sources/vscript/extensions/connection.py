


import urllib.request, urllib.error, urllib.parse, http.client, codecs
from email.parser import Parser
from io import StringIO
from .. import errors
from ..subtypes import generic, boolean, binary, string, true, false, v_empty, v_mismatch, v_nothing


v_connectionerror=urllib.error.URLError


class v_proxy(generic):

	def __init__(self):
		generic.__init__(self)
		self._value={}


	def build_handler(self):
		return urllib.request.ProxyHandler(self._value)


	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			if len(arguments)>1: raise errors.wrong_number_of_arguments
			self._value[arguments[0].as_string]=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.type_mismatch
		else:
			if len(arguments)>1: raise errors.wrong_number_of_arguments
			return self._value[key.as_string]


class v_passwordmanager(generic):

	def __init__(self):
		generic.__init__(self)
		self._username=None
		self._password=None


	def build_handler(self, proxy):
		http_proxy=proxy.value.get("http", None)
		if http_proxy:
			if not http_proxy.starts_with("http://"): http_proxy="http://"+http_proxy
			password_manager=urllib.request.HTTPPasswordMgrWithDefaultRealm()
			password_manager.add_password(None, http_proxy, self._username, self._password)
			return urllib.request.ProxyBasicAuthHandler(password_manager)
		else:
			return None


	def v_username(self, **keywords):
		if "let" in keywords:
			self._username=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("username")
		else:
			return string(self._username) if self._username else v_empty

	def v_password(self, **keywords):
		if "let" in keywords:
			self._password=keywords["let"].as_string
		elif "set" in keywords:
			raise errors.object_has_no_property("password")
		else:
			return string(self._password) if self._password else v_empty


proxy_alias=v_proxy


class v_connection(generic):

	def __init__(self):
		generic.__init__(self)
		self._value=None
		self._encoding=None
		self._codec=None
		self._proxy=None
		self._authentication=None
		self._timeout=None


	def erase(self):
		if self._value:
			try: self._value.close()
			except http.client.HTTPException as error: raise urllib.error.URLError(error)
			self._value=None


	def v_encoding(self, **keywords):
		if "let" in keywords:
			encoding=keywords["let"].as_string
			try: self._encoding, self._codec=encoding, codecs.lookup(encoding)
			except LookupError: pass
		elif "set" in keywords:
			raise errors.object_has_no_property("encoding")
		else:
			return string(self._encoding) if self._encoding else v_empty

	def v_proxy(self, **keywords):
		if "let" in keywords:
			raise errors.object_has_no_property("proxy")
		elif "set" in keywords:
			self._proxy=keywords["set"].as_specific(proxy_alias)
		else:
			return self._proxy or v_nothing

	def v_isconnected(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("isconnected")
		else:
			return boolean(false if self._value is None else true)


	def v_open(self, url):
		if self._value is not None: raise errors.invalid_procedure_call(name=u"open")
		try:
			handlers, parameters=[], {}
			if self._proxy:
				handlers.append(self._proxy.build_handler())
				if self.authentication:
					handler=self._authentication.build_handler(self._proxy)
					if handler: handlers.append(handler)
			opener=urllib.request.build_opener(*handlers)
			if self._timeout: parameters["timeout"]=self._timeout
			self._value=opener.open(url.as_string, **parameters)
		except http.client.HTTPException as error:
			raise urllib.error.URLError(error)
		if self._value.url.startswith("http://"):
			mime=Parser().parsestr(self._value.info())
			encoding=mime.get_content_charset()
			try: self._encoding, self._codec=encoding, codecs.lookup(encoding)
			except LookupError: pass
		return v_mismatch

	def v_read(self):
		if self._value is None: raise errors.invalid_procedure_call(name=u"read")
		try: data=self._value.read()
		except http.client.HTTPException as error: raise urllib.error.URLError(error)
		if self._codec:
			try: return string(self._codec.decode(data))
			except UnicodeError: raise errors.invalid_procedure_call(name=u"read")
		else:
			return binary(data)

	def v_write(self, data):
		if self._value is None: raise errors.invalid_procedure_call(name=u"write")
		if self._codec:
			try: data=self._codec.encode(data.as_string)
			except UnicodeError: raise errors.invalid_procedure_call(name=u"write")
		else:
			data=data.as_binary
		try: self._value.write(data)
		except http.client.HTTPException as error: raise urllib.error.URLError(error)
		return v_mismatch

	def v_close(self):
		if self._value is None: raise errors.invalid_procedure_call(name=u"close")
		self.erase()
		return v_mismatch
