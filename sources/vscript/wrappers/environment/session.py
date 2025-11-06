
from builtins import str
import managers
from ... import errors
from ...primitives import subtype
from ...subtypes import generic, string, v_empty


class v_session(generic):

	def v_sessionid(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("sessionid")
		else:
			return string(str(managers.request_manager.current.sid))

	def v_timeout(self, **keywords):
		raise errors.not_implemented
		
	def v_variables(self, name, **keywords):
		name=name.as_string
		if "let" in keywords:
			managers.request_manager.current.session().value(name, value=keywords["let"].as_is)
		elif "set" in keywords:
			managers.request_manager.current.session().value(name, value=keywords["set"].as_is)
		else:
			value=managers.request_manager.current.session().value(name)
			if isinstance(value, subtype):
				return value
			elif value is None:
				return v_empty
			else:
				raise errors.type_mismatch


	def v_abandon(self):
		raise errors.not_implemented
	
	def v_securitycode(self, **keywords):
		if "let" in keywords:
			managers.request_manager.current.session().value("SecurityCode", value=keywords["let"].as_string)
		elif "set" in keywords:
			raise errors.object_has_no_property("securitycode")
		else:
			value=managers.request_manager.current.session().value("SecurityCode")
			return v_empty if value is None else string(value)

