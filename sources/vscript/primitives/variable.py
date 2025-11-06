from __future__ import division

from builtins import str
import sys
from .. import errors
from .primitive import primitive
from ..subtypes import generic


class variable(primitive):

	def __getattr__(self, name):
		try:
			return getattr(self.as_complex, name)
		except AttributeError:
			raise errors.object_has_no_property(name).with_traceback(sys.exc_info()[2])


	def redim(self, preserve, *subscripts):
		self.subtype.redim(preserve, *subscripts)

	def erase(self, *arguments):
		self.subtype.erase(*arguments)


	as_simple=property(lambda self: self.subtype.as_simple)
	as_complex=property(lambda self: self.subtype.as_complex)
	as_is=property(lambda self: self.subtype.as_is)
	as_array=property(lambda self: self.subtype.as_array)
	as_binary=property(lambda self: self.subtype.as_binary)
	as_boolean=property(lambda self: self.subtype.as_boolean)
	as_date=property(lambda self: self.subtype.as_date)
	as_dictionary=property(lambda self: self.subtype.as_dictionary)
	as_ordereddictionary=property(lambda self: self.subtype.as_ordereddictionary)
	as_double=property(lambda self: self.subtype.as_double)
	as_generic=property(lambda self: self.subtype.as_generic)
	as_integer=property(lambda self: self.subtype.as_integer)
	as_string=property(lambda self: self.subtype.as_string)
	as_number=property(lambda self: self.subtype.as_number)
	as_error=property(lambda self: self.subtype.as_error)

	def as_specific(self, specific):
		return self.subtype.as_specific(specific)


	def __iter__(self):
		return iter(self.subtype)

	def __len__(self):
		return len(self.subtype)

	def __contains__(self, value):
		return value in self.subtype


	def __add__(self, another):
		return self.subtype+another

	def __sub__(self, another):
		return self.subtype-another

	def __mul__(self, another):
		return self.subtype*another

	def __div__(self, another):
		return self.subtype.__truediv__(another)

	def __truediv__(self, another):
		return self.subtype.__truediv__(another)

	def __floordiv__(self, another):
		return self.subtype//another

	def __mod__(self, another):
		return self.subtype%another

	def __pow__(self, another):
		return self.subtype**another


	def __eq__(self, another):
		return self.subtype==another

	def __ne__(self, another):
		return self.subtype!=another

	def __lt__(self, another):
		return self.subtype<another

	def __gt__(self, another):
		return self.subtype>another

	def __le__(self, another):
		return self.subtype<=another

	def __ge__(self, another):
		return self.subtype>=another


	def __and__(self, another):
		return self.subtype & another

	def __or__(self, another):
		return self.subtype | another

	def __xor__(self, another):
		return self.subtype ^ another


	def __invert__(self):
		return ~(self.subtype)
		
	def __neg__(self):
		return -(self.subtype)

	def __pos__(self):
		return +(self.subtype)

	def __abs__(self):
		return abs(self.subtype)


	def __int__(self):
		return int(self.subtype)

	def __float__(self):
		return float(self.subtype)

	def __str__(self):
		return str(self.subtype)

	def __unicode__(self):
		return str(self.subtype)

	def __bool__(self):
		return bool(self.subtype)


	def __hash__(self):
		return hash(self.subtype)
