from __future__ import division

from .. import errors
from ..lexemes import prefix
from ..primitives import subtype


class generic(subtype):

	def __call__(self, *arguments, **keywords):
		raise errors.object_has_no_property


	exception=property(lambda self: self().exception)
	value=property(lambda self: self().value)
	

	code=property(lambda self: 9)
	name=property(lambda self: self.__class__.__name__[2:] if self.__class__.__name__.startswith(prefix) else "Object")


	as_simple=property(lambda self: self().as_simple)
	as_complex=property(lambda self: self)
	as_array=property(lambda self: self().as_array)
	as_binary=property(lambda self: self().as_binary)
	as_boolean=property(lambda self: self().as_boolean)
	as_date=property(lambda self: self().as_date)
	as_double=property(lambda self: self().as_double)
	as_generic=property(lambda self: self)
	as_integer=property(lambda self: self().as_integer)
	as_string=property(lambda self: self().as_string)
	as_number=property(lambda self: self().as_double)

	def as_specific(self, specific):
		if not isinstance(self, specific):
			raise errors.object_required
		return self


	is_generic=property(lambda self: True)


	def __add__(self, another):
		return self()+another

	def __sub__(self, another):
		return self()-another

	def __mul__(self, another):
		return self()*another

	def __div__(self, another):
		return self().__truediv__(another)

	def __truediv__(self, another):
		return self().__truediv__(another)

	def __floordiv__(self, another):
		return self()//another

	def __mod__(self, another):
		return self()%another

	def __pow__(self, another):
		return self()**another


	def __eq__(self, another):
		return self()==another

	def __ne__(self, another):
		return self()!=another

	def __lt__(self, another):
		return self()<another

	def __gt__(self, another):
		return self()>another

	def __le__(self, another):
		return self()<=another

	def __ge__(self, another):
		return self()>=another


	def __and__(self, another):
		return self()&another

	def __or__(self, another):
		return self()|another

	def __xor__(self, another):
		return self()^another


	def __invert__(self):
		return ~self()
		
	def __neg__(self):
		return -self()

	def __pos__(self):
		return +self()

	def __abs__(self):
		return abs(self())


	def __int__(self):
		return int(self())
			
	def __float__(self):
		return float(self())
	
	def __unicode__(self):
		return str(self())
	
	def __bool__(self):
		return bool(self())


	def __repr__(self):
		return "GENERIC@%08X"%id(self)
