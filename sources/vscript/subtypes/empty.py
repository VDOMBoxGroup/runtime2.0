
from builtins import str
import sys
from .. import errors
from ..operations import div, mod
from ..primitives import subtype


class empty(subtype):

	code=property(lambda self: 0)
	name=property(lambda self: "Empty")


	as_simple=property(lambda self: self)
	as_boolean=property(lambda self: bool(self))
	as_date=property(lambda self: float(self))
	as_double=property(lambda self: float(self))
	as_integer=property(lambda self: int(self))
	as_string=property(lambda self: str(self))
	as_number=property(lambda self: int(self))


	is_empty=property(lambda self: self is v_empty)
	

	def __div__(self, another):
		try: return subtype.__div__(self, another)
		except errors.division_by_zero: raise errors.overflow.with_traceback(sys.exc_info()[2])


	def __invert__(self):
		return integer(-1)
		
	def __neg__(self):
		return integer(0)

	def __pos__(self):
		return v_empty

	def __abs__(self):
		return integer(0)


	def __copy__(self):
		return self

	def __deepcopy__(self, memo={}):
		return self


	def __int__(self):
		return 0

	def __float__(self):
		return 0.0

	def __unicode__(self):
		return u""

	def __bool__(self):
		return False


	def __repr__(self):
		return "EMPTY@%08X"%id(self)


v_empty=empty()


from .boolean import boolean, true, false
from .date import date
from .double import double, nan, infinity
from .generic import generic
from .integer import integer
from .null import null, v_null
from .string import string


empty.add_table={
	empty: lambda self, another: integer(0+0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(0+int(another)),
	double: lambda self, another: double(0+float(another)),
	date: lambda self, another: date(0+float(another)),
	string: lambda self, another: string(""+str(another)),
	boolean: lambda self, another: integer(0+int(another))}

empty.sub_table={
	empty: lambda self, another: integer(0-0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(0-int(another)),
	double: lambda self, another: double(0-float(another)),
	date: lambda self, another: date(0-float(another)),
	string: lambda self, another: double(0-float(another)),
	boolean: lambda self, another: integer(0-int(another))}

empty.mul_table={
	empty: lambda self, another: integer(0*0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(0*int(another)),
	double: lambda self, another: double(0*float(another)),
	date: lambda self, another: double(0*float(another)),
	string: lambda self, another: double(0*float(another)),
	boolean: lambda self, another: integer(0*int(another))}

empty.div_table={
	empty: lambda self, another: integer(0.0/0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(0.0/int(another)),
	double: lambda self, another: double(0.0/float(another)),
	date: lambda self, another: double(0.0/float(another)),
	string: lambda self, another: double(0.0/float(another)),
	boolean: lambda self, another: double(0.0/int(another))}

empty.floordiv_table={
	empty: lambda self, another: integer(div(0, 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(div(0, int(another))),
	double: lambda self, another: integer(div(0, int(another))),
	date: lambda self, another: integer(div(0, int(another))),
	string: lambda self, another: integer(div(0, int(another))),
	boolean: lambda self, another: integer(div(0, int(another)))}

empty.mod_table={
	empty: lambda self, another: integer(mod(0, 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(mod(0, int(another))),
	double: lambda self, another: integer(mod(0, int(another))),
	date: lambda self, another: integer(mod(0, int(another))),
	string: lambda self, another: integer(mod(0, int(another))),
	boolean: lambda self, another: integer(mod(0, int(another)))}

empty.pow_table={
	empty: lambda self, another: double(0.0**0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(0.0**int(another)),
	double: lambda self, another: double(0**float(another)),
	date: lambda self, another: double(0**float(another)),
	string: lambda self, another: double(0**float(another)),
	boolean: lambda self, another: double(0.0**int(another))}


empty.eq_table={
	empty: lambda self, another: boolean(true),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if 0==int(another) else boolean(false),
	double: lambda self, another: boolean(true) if 0==float(another) else boolean(false),
	date: lambda self, another: boolean(true) if 0==float(another) else boolean(false),
	string: lambda self, another: boolean(true) if u""==str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if 0==int(another) else boolean(false)}

empty.ne_table={
	empty: lambda self, another: boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if 0!=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if 0!=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if 0!=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if u""!=str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if 0!=int(another) else boolean(false)}

empty.lt_table={
	empty: lambda self, another: boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if 0<int(another) else boolean(false),
	double: lambda self, another: boolean(true) if 0<float(another) else boolean(false),
	date: lambda self, another: boolean(true) if 0<float(another) else boolean(false),
	string: lambda self, another: boolean(true) if u""<str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if 0<int(another) else boolean(false)}

empty.gt_table={
	empty: lambda self, another: boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if 0>int(another) else boolean(false),
	double: lambda self, another: boolean(true) if 0>float(another) else boolean(false),
	date: lambda self, another: boolean(true) if 0>float(another) else boolean(false),
	string: lambda self, another: boolean(true) if u"">str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if 0>int(another) else boolean(false)}

empty.le_table={
	empty: lambda self, another: boolean(true),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if 0<=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if 0<=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if 0<=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if u""<=str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if 0<=int(another) else boolean(false)}

empty.ge_table={
	empty: lambda self, another: boolean(true),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if 0>=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if 0>=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if 0>=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if u"">=str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if 0>=int(another) else boolean(false)}


empty.and_table={
	empty: lambda self, another: integer(0&0),
	null: lambda self, another: integer(0),
	integer: lambda self, another: integer(0&int(another)),
	double: lambda self, another: integer(0&int(another)),
	date: lambda self, another: integer(0&int(another)),
	string: lambda self, another: integer(0&int(another)),
	boolean: lambda self, another: integer(0&int(another))}

empty.or_table={
	empty: lambda self, another: integer(0|0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(0|int(another)),
	double: lambda self, another: integer(0|int(another)),
	date: lambda self, another: integer(0|int(another)),
	string: lambda self, another: integer(0|int(another)),
	boolean: lambda self, another: integer(0|int(another))}

empty.xor_table={
	empty: lambda self, another: integer(0^0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(0^int(another)),
	double: lambda self, another: integer(0^int(another)),
	date: lambda self, another: integer(0^int(another)),
	string: lambda self, another: integer(0^int(another)),
	boolean: lambda self, another: integer(0^int(another))}
