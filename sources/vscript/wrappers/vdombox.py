
import re, codecs, hashlib # SOAPpy
# from soap.soaputils import VDOM_session_protector
from .. import errors
from ..subtypes import boolean, generic, string, true, false, v_mismatch


class v_vdombox(generic):

	session_id_regex=re.compile("\<SessionId\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionId\>")
	session_key_regex=re.compile("\<SessionKey\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionKey\>")
	hash_string_regex=re.compile("\<HashString\>\<\!\[CDATA\[(\S+)\]\]\>\<\/HashString\>")
	key_regex=re.compile("(\r?\n\<Key\>\d+_\d+\<\/Key\>)$")


	def __init__(self):
		generic.__init__(self)
		self._server=None

	
	def v_isconnected(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("isconnected")
		else:
			return boolean(false if self._server is None else true)


	def v_open(self, address, username, password):
		raise errors.internal_error("NOT IMPLEMENTET - REQUIRE SOAP")
		if self._server is not None: raise errors.invalid_procedure_call("open")
		self._server=SOAPpy.WSDL.Proxy("http://%s/vdom.wsdl"%address)
		self._address=address.as_string
		self._username=username.as_string
		self._password=password.as_string
		response=self._server.open_session(self._username, hashlib.md5.new(self._password).hexdigest())
		# <Session>
		#   <SessionId><![CDATA[...]]></SessionId>
		#   <SessionKey><![CDATA[...]]></SessionKey>
		#   <HashString><![CDATA[...]]></HashString>
		# </Session>
		# <Hostname></Hostname>
		# <Username>root</Username>
		# <ServerVersion>x.x.xxxx</ServerVersion>
		match=self.session_id_regex.search(response)
		if match is None: raise errors.invalid_procedure_call(name=u"open")
		self._session_id=match.group(1)
		match=self.session_key_regex.search(response)
		if match is None: raise errors.invalid_procedure_call(name=u"open")
		self._session_key=match.group(1)
		match=self.hash_string_regex.search(response)
		if match is None: raise errors.invalid_procedure_call(name=u"open")
		self._hash_string=match.group(1)
		self._index=None
		self._protector=VDOM_session_protector(self._hash_string)
		return v_mismatch

	def v_close(self):
		if self._server is None: raise errors.invalid_procedure_call("close")
		self._server.close_session(self._session_id)
		self._server=None
		del self._address, self._username, self._password
		del self._session_id, self._session_key
		del self._hash_string, self._index, self._protector
		return v_mismatch

	def v_invoke(self, name, *arguments):
		if self._server is None: raise errors.invalid_procedure_call("invoke")
		self._session_key=self._protector.next_session_key(self._session_key)
		self._index=0 if self._index is None else self._index+1
		try: handler=getattr(self._server, name.as_string)
		except AttributeError: raise errors.invalid_procedure_call(name=u"invoke")
		arguments=tuple(argument.as_string for argument in arguments)
		response=handler(self._session_id, "%s_%s"%(self._session_key, self._index), *arguments)
		# ...
		# <Key>...</Key>
		response=u"<response>%s</response>"%response
		match=self.key_regex.search(response)
		if match: response=response[:match.start(1)]
		return string(response)
