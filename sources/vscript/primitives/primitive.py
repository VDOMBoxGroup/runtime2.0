
from builtins import object
from .. import errors


class primitive(object):

	def _get_subtype(self):
		raise errors.python_using_abstract

	def _get_copy(self):
		raise errors.python_using_abstract

	def _get_exception(self):
		raise errors.python_using_abstract

	def _get_value(self):
		raise errors.python_using_abstract
	
	subtype=property(_get_subtype)
	copy=property(_get_copy)
	exception=property(_get_exception)
	value=property(_get_value)


	def _get_byref(self):
		raise errors.python_using_abstract

	def _get_byval(self):
		raise errors.python_using_abstract

	byref=property(_get_byref)
	byval=property(_get_byval)
	

	def redim(self, preserve, *subscripts):
		raise errors.python_using_abstract

	def erase(self, *arguments):
		raise errors.python_using_abstract


	def _get_as_simple(self):
		raise errors.python_using_abstract

	def _get_as_complex(self):
		raise errors.python_using_abstract

	def _get_as_is(self):
		raise errors.python_using_abstract

	def _get_as_array(self):
		raise errors.python_using_abstract

	def _get_as_binary(self):
		raise errors.python_using_abstract

	def _get_as_boolean(self):
		raise errors.python_using_abstract

	def _get_as_date(self):
		raise errors.python_using_abstract

	def _get_as_dictionary(self):
		raise errors.python_using_abstract

	def _get_as_double(self):
		raise errors.python_using_abstract

	def _get_as_generic(self):
		raise errors.python_using_abstract

	def _get_as_integer(self):
		raise errors.python_using_abstract

	def _get_as_string(self):
		raise errors.python_using_abstract

	def _get_as_number(self):
		raise errors.python_using_abstract

	as_simple=property(_get_as_simple)
	as_complex=property(_get_as_complex)
	as_is=property(_get_as_is)
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

	def as_specific(self, specific):
		raise errors.python_using_abstract
