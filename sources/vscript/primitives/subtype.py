
import sys
from .. import errors
from .primitive import primitive


class subtype(primitive):
	def __call__(self, *arguments, **keywords):
		raise errors.type_mismatch

	def _get_exception(self):
		raise errors.type_mismatch

	def _get_value(self):
		raise errors.type_mismatch

	subtype=property(lambda self: self)
	copy=property(lambda self: self)
	exception=property(_get_exception)
	value=property(_get_value)

	def _get_code(self):
		raise errors.python_using_abstract

	def _get_name(self):
		raise errors.python_using_abstract

	code=property(_get_code)
	name=property(_get_name)

	add_table={}
	sub_table={}
	mul_table={}
	div_table={}
	floordiv_table={}
	mod_table={}
	pow_table={}

	eq_table={}
	ne_table={}
	lt_table={}
	gt_table={}
	le_table={}
	ge_table={}

	and_table={}
	or_table={}
	xor_table={}

	def redim(self, preserve, *subscripts):
		raise errors.type_mismatch

	def erase(self, *arguments):
		raise errors.type_mismatch

	def _get_as_simple(self):
		raise errors.type_mismatch

	def _get_as_complex(self):
		raise errors.object_required

	def _get_as_array(self):
		raise errors.type_mismatch

	def _get_as_binary(self):
		raise errors.type_mismatch

	def _get_as_boolean(self):
		raise errors.type_mismatch

	def _get_as_date(self):
		raise errors.type_mismatch

	def _get_as_dictionary(self):
		raise errors.type_mismatch

	def _get_as_double(self):
		raise errors.type_mismatch

	def _get_as_generic(self):
		raise errors.type_mismatch

	def _get_as_integer(self):
		raise errors.type_mismatch

	def _get_as_string(self):
		raise errors.type_mismatch

	def _get_as_number(self):
		raise errors.type_mismatch

	def _get_as_error(self):
		raise errors.type_mismatch

	as_simple=property(_get_as_simple)
	as_complex=property(_get_as_complex)
	as_is=property(lambda self: self)
	as_array=property(_get_as_array)
	as_binary=property(_get_as_binary)
	as_boolean=property(_get_as_boolean)
	as_date=property(_get_as_date)
	as_dictionary=property(_get_as_dictionary)
	as_ordereddictionary=property(_get_as_dictionary)
	as_double=property(_get_as_double)
	as_generic=property(_get_as_generic)
	as_integer=property(_get_as_integer)
	as_string=property(_get_as_string)
	as_number=property(_get_as_number)
	as_error=property(_get_as_error)

	def as_specific(self, specific):
		raise errors.type_mismatch

	is_empty=property(lambda self: False)
	is_null=property(lambda self: False)
	is_generic=property(lambda self: False)
	is_nothing=property(lambda self: False)

	def is_integer(self, value=None):
		return False

	def is_double(self, value=None):
		return False

	def is_date(self, year=None, month=None, day=None, hour=None, minute=None, second=None):
		return False

	def is_string(self, value=None):
		return False

	def is_boolean(self, value=None):
		return False

	def is_array(self, function=None, length=None, more=None):
		return False

	def is_dictionary(self, function=None):
		return False

	def is_ordereddictionary(self, function=None):
		return False

	def __iter__(self):
		raise errors.type_mismatch

	def __len__(self):
		raise errors.type_mismatch

	def __contains__(self, value):
		raise errors.type_mismatch

	def __add__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		try: return self.add_table.get(type(simple), unknown)(self, simple)
		except OverflowError: raise errors.overflow.with_traceback(sys.exc_info()[2])

	def __sub__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		try: return self.sub_table.get(type(simple), unknown)(self, simple)
		except OverflowError: raise errors.overflow.with_traceback(sys.exc_info()[2])

	def __mul__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		try: return self.mul_table.get(type(simple), unknown)(self, simple)
		except OverflowError: raise errors.overflow.with_traceback(sys.exc_info()[2])

	def __div__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		try: return self.div_table.get(type(simple), unknown)(self, simple)
		except OverflowError: raise errors.overflow.with_traceback(sys.exc_info()[2])
		except ZeroDivisionError: raise errors.division_by_zero.with_traceback(sys.exc_info()[2])

	def __floordiv__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		try: return self.floordiv_table.get(type(simple), unknown)(self, simple)
		except OverflowError: raise errors.overflow.with_traceback(sys.exc_info()[2])
		except ZeroDivisionError: raise errors.division_by_zero.with_traceback(sys.exc_info()[2])

	def __mod__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		try: return self.mod_table.get(type(simple), unknown)(self, simple)
		except OverflowError: raise errors.overflow.with_traceback(sys.exc_info()[2])
		except ZeroDivisionError: raise errors.division_by_zero.with_traceback(sys.exc_info()[2])

	def __pow__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		try: return self.pow_table.get(type(simple), unknown)(self, simple)
		except ValueError: raise errors.invalid_procedure_call.with_traceback(sys.exc_info()[2])
		except OverflowError: raise errors.overflow.with_traceback(sys.exc_info()[2])
		except ZeroDivisionError: raise errors.invalid_procedure_call.with_traceback(sys.exc_info()[2])

	def __eq__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		return self.eq_table.get(type(simple), unknown)(self, simple)

	def __ne__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		value=another.as_simple
		return self.ne_table.get(type(value), unknown)(self, value)

	def __lt__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		return self.lt_table.get(type(simple), unknown)(self, simple)

	def __gt__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		return self.gt_table.get(type(simple), unknown)(self, simple)

	def __le__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		return self.le_table.get(type(simple), unknown)(self, simple)

	def __ge__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		return self.ge_table.get(type(simple), unknown)(self, simple)


	def __and__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		return self.and_table.get(type(simple), unknown)(self, simple)

	def __or__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		return self.or_table.get(type(simple), unknown)(self, simple)

	def __xor__(self, another):
		def unknown(one, another): raise errors.type_mismatch
		simple=another.as_simple
		return self.xor_table.get(type(simple), unknown)(self, simple)

	def __invert__(self):
		raise errors.type_mismatch
		
	def __neg__(self):
		raise errors.type_mismatch

	def __pos__(self):
		raise errors.type_mismatch

	def __abs__(self):
		raise errors.type_mismatch

	def __int__(self):
		raise errors.type_mismatch
			
	def __float__(self):
		raise errors.type_mismatch

	def __str__(self):
		raise errors.python_avoid_using
	
	def __unicode__(self):
		raise errors.type_mismatch
	
	def __bool__(self):
		raise errors.type_mismatch
