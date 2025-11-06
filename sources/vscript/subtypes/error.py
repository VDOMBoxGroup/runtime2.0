
from builtins import str
from .. import errors
from ..primitives import subtype


class error(subtype):

	def __init__(self, value):
		self._value=value


	exception=property(lambda self: self._value)
	value=property(lambda self: self._value)


	code=property(lambda self: 10)
	name=property(lambda self: "Error")


	as_simple=property(lambda self: self)
	as_error=property(lambda self: self)


	def v_message(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property
		else:
			return string(str(str(self._value)))


	def __repr__(self):
		return "ERROR@%08X"%id(self)


from .string import string
