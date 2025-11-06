
from builtins import str
import sys
from .. import errors
from ..operations import div, mod
from ..primitives import subtype


class integer(subtype):

	def __init__(self, value):
		#assert isinstance(value, int), "Got %s instead int"%type(value)
		self._value=int(value)


	value=property(lambda self: self._value)


	code=property(lambda self: 2)
	name=property(lambda self: "Integer")


	as_simple=property(lambda self: self)
	as_boolean=property(lambda self: bool(self))
	as_date=property(lambda self: float(self))
	as_double=property(lambda self: float(self))
	as_integer=property(lambda self: int(self))
	as_string=property(lambda self: str(self))
	as_number=property(lambda self: int(self))


	def is_integer(self, value=None):
		return True if value is None else self._value==value


	def __invert__(self):
		return integer(~self._value)
		
	def __neg__(self):
		return integer(-self._value)

	def __pos__(self):
		return integer(+self._value)

	def __abs__(self):
		return integer(abs(self._value))


	def __int__(self):
		return self._value
			
	def __float__(self):
		return float(self._value)
	
	def __unicode__(self):
		return str(self._value)
	
	def __bool__(self):
		return bool(self._value)


	def __hash__(self):
		return hash(self._value)

	def __repr__(self):
		return "INTEGER@%08X:%r"%(id(self), self._value)


from .boolean import boolean, true, false
from .date import date
from .double import double, nan, infinity
from .empty import empty, v_empty
from .generic import generic
from .null import null, v_null
from .string import string


integer.add_table={
	empty: lambda self, another: integer(int(self)+0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self)+int(another)),
	double: lambda self, another: double(int(self)+float(another)),
	date: lambda self, another: date(int(self)+float(another)),
	string: lambda self, another: double(int(self)+float(another)),
	boolean: lambda self, another: integer(int(self)+int(another))}

integer.sub_table={
	empty: lambda self, another: integer(int(self)-0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self)-int(another)),
	double: lambda self, another: double(int(self)-float(another)),
	date: lambda self, another: date(int(self)-float(another)),
	string: lambda self, another: double(int(self)-float(another)),
	boolean: lambda self, another: integer(int(self)-int(another))}

integer.mul_table={
	empty: lambda self, another: integer(int(self)*0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self)*int(another)),
	double: lambda self, another: double(int(self)*float(another)),
	date: lambda self, another: double(int(self)*float(another)),
	string: lambda self, another: double(int(self)*float(another)),
	boolean: lambda self, another: integer(int(self)*int(another))}

integer.div_table={
	empty: lambda self, another: double(int(self)/0.0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)/int(another)),
	double: lambda self, another: double(int(self)/float(another)),
	date: lambda self, another: double(int(self)/float(another)),
	string: lambda self, another: double(int(self)/float(another)),
	boolean: lambda self, another: double(float(self)/int(another))}

integer.floordiv_table={
	empty: lambda self, another: integer(div(int(self), 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(div(int(self), int(another))),
	double: lambda self, another: integer(div(int(self), int(another))),
	date: lambda self, another: integer(div(int(self), int(another))),
	string: lambda self, another: integer(div(int(self), int(another))),
	boolean: lambda self, another: integer(div(int(self), int(another)))}

integer.mod_table={
	empty: lambda self, another: integer(mod(int(self), 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(mod(int(self), int(another))),
	double: lambda self, another: integer(mod(int(self), int(another))),
	date: lambda self, another: integer(mod(int(self), int(another))),
	string: lambda self, another: integer(mod(int(self), int(another))),
	boolean: lambda self, another: integer(mod(int(self), int(another)))}

integer.pow_table={
	empty: lambda self, another: double(int(self)**0.0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)**int(another)),
	double: lambda self, another: double(int(self)**float(another)),
	date: lambda self, another: double(int(self)**float(another)),
	string: lambda self, another: double(int(self)**float(another)),
	boolean: lambda self, another: double(float(self)**int(another))}


integer.eq_table={
	empty: lambda self, another: boolean(true) if int(self)==0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)==int(another) else boolean(false),
	double: lambda self, another: boolean(true) if int(self)==float(another) else boolean(false),
	date: lambda self, another: boolean(true) if int(self)==float(another) else boolean(false),
	string: lambda self, another: boolean(true) if int(self)==float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if int(self)==int(another) else boolean(false)}

integer.ne_table={
	empty: lambda self, another: boolean(true) if int(self)!=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)!=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if int(self)!=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if int(self)!=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if int(self)!=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if int(self)!=int(another) else boolean(false)}

integer.lt_table={
	empty: lambda self, another: boolean(true) if int(self)<0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)<int(another) else boolean(false),
	double: lambda self, another: boolean(true) if int(self)<float(another) else boolean(false),
	date: lambda self, another: boolean(true) if int(self)<float(another) else boolean(false),
	string: lambda self, another: boolean(true) if int(self)<float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if int(self)<int(another) else boolean(false)}

integer.gt_table={
	empty: lambda self, another: boolean(true) if int(self)>0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)>int(another) else boolean(false),
	double: lambda self, another: boolean(true) if int(self)>float(another) else boolean(false),
	date: lambda self, another: boolean(true) if int(self)>float(another) else boolean(false),
	string: lambda self, another: boolean(true) if int(self)>float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if int(self)>int(another) else boolean(false)}

integer.le_table={
	empty: lambda self, another: boolean(true) if int(self)<=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)<=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if int(self)<=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if int(self)<=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if int(self)<=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if int(self)<=int(another) else boolean(false)}

integer.ge_table={
	empty: lambda self, another: boolean(true) if int(self)>=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)>=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if int(self)>=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if int(self)>=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if int(self)>=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if int(self)>=int(another) else boolean(false)}


integer.and_table={
	empty: lambda self, another: integer(int(self)&0),
	null: lambda self, another: v_null if int(self) else integer(int(self)),
	integer: lambda self, another: integer(int(self)&int(another)),
	double: lambda self, another: integer(int(self)&int(another)),
	date: lambda self, another: integer(int(self)&int(another)),
	string: lambda self, another: integer(int(self)&int(another)),
	boolean: lambda self, another: integer(int(self)&int(another))}

integer.or_table={
	empty: lambda self, another: integer(int(self)|0),
	null: lambda self, another: integer(int(self)) if int(self) else v_null,
	integer: lambda self, another: integer(int(self)|int(another)),
	double: lambda self, another: integer(int(self)|int(another)),
	date: lambda self, another: integer(int(self)|int(another)),
	string: lambda self, another: integer(int(self)|int(another)),
	boolean: lambda self, another: integer(int(self)|int(another))}

integer.xor_table={
	empty: lambda self, another: integer(int(self)^0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self)^int(another)),
	double: lambda self, another: integer(int(self)^int(another)),
	date: lambda self, another: integer(int(self)^int(another)),
	string: lambda self, another: integer(int(self)^int(another)),
	boolean: lambda self, another: integer(int(self)^int(another))}
