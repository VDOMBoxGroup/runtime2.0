
from builtins import str
import sys
from math import floor, fabs
from .. import errors
from ..operations import div, mod
from ..primitives import subtype


nan=float("nan")
infinity=float("inf")


class double(subtype):

	def __init__(self, value):
		# assert isinstance(value, float), "Got %s instead float"%type(value)
		self._value=float(value)


	value=property(lambda self: self._value)


	code=property(lambda self: 5)
	name=property(lambda self: "Double")


	as_simple=property(lambda self: self)
	as_boolean=property(lambda self: bool(self))
	as_double=property(lambda self: float(self))
	as_integer=property(lambda self: int(self))
	as_string=property(lambda self: str(self))
	as_number=property(lambda self: float(self))


	def is_double(self, value=None):
		return True if value is None \
			else self._value is nan if value is nan \
			else self._value is infinity if value is infinity \
			else abs(self._value-value)<=1E-12*fabs(max(self._value, value))


	def __invert__(self):
		return integer(~int(round(self._value)))
		
	def __neg__(self):
		return double(-self._value)

	def __pos__(self):
		return double(+self._value)

	def __abs__(self):
		return double(fabs(self._value))


	def __int__(self):
		return int(round(self._value))

	def __float__(self):
		return self._value
	
	def __unicode__(self):
		if self._value==nan:
			return u"NaN"
		elif self._value==infinity:
			return u"Infinity"
		elif self._value==-infinity:
			return u"-Infinity"
		elif floor(self._value)==self._value:
			return str(int(self._value))
		else:
			return str(self._value)
	
	def __bool__(self):
		return bool(self._value)


	def __hash__(self):
		return hash(self._value)

	def __repr__(self):
		return "DOUBLE@%08X:%r"%(id(self), self._value)


from .boolean import boolean, true, false
from .date import date
from .empty import empty, v_empty
from .generic import generic
from .integer import integer
from .null import null, v_null
from .string import string


double.add_table={
	empty: lambda self, another: double(float(self)+0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)+int(another)),
	double: lambda self, another: double(float(self)+float(another)),
	date: lambda self, another: date(float(self)+float(another)),
	string: lambda self, another: double(float(self)+float(another)),
	boolean: lambda self, another: double(float(self)+int(another))}

double.sub_table={
	empty: lambda self, another: double(float(self)-0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)-int(another)),
	double: lambda self, another: double(float(self)-float(another)),
	date: lambda self, another: date(float(self)-float(another)),
	string: lambda self, another: double(float(self)-float(another)),
	boolean: lambda self, another: double(float(self)-int(another))}

double.mul_table={
	empty: lambda self, another: double(float(self)*0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)*int(another)),
	double: lambda self, another: double(float(self)*float(another)),
	date: lambda self, another: double(float(self)*float(another)),
	string: lambda self, another: double(float(self)*float(another)),
	boolean: lambda self, another: double(float(self)*int(another))}

double.div_table={
	empty: lambda self, another: double(float(self)/0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)/int(another)),
	double: lambda self, another: double(float(self)/float(another)),
	date: lambda self, another: double(float(self)/float(another)),
	string: lambda self, another: double(float(self)/float(another)),
	boolean: lambda self, another: double(float(self)/int(another))}

double.floordiv_table={
	empty: lambda self, another: integer(div(int(self), 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(div(int(self), int(another))),
	double: lambda self, another: integer(div(int(self), int(another))),
	date: lambda self, another: integer(div(int(self), int(another))),
	string: lambda self, another: integer(div(int(self), int(another))),
	boolean: lambda self, another: integer(div(int(self), int(another)))}

double.mod_table={
	empty: lambda self, another: integer(mod(int(self), 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(mod(int(self), int(another))),
	double: lambda self, another: integer(mod(int(self), int(another))),
	date: lambda self, another: integer(mod(int(self), int(another))),
	string: lambda self, another: integer(mod(int(self), int(another))),
	boolean: lambda self, another: integer(mod(int(self), int(another)))}

double.pow_table={
	empty: lambda self, another: double(float(self)**0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)**int(another)),
	double: lambda self, another: double(float(self)**float(another)),
	date: lambda self, another: double(float(self)**float(another)),
	string: lambda self, another: double(float(self)**float(another)),
	boolean: lambda self, another: double(float(self)**int(another))}


double.eq_table={
	empty: lambda self, another: boolean(true) if float(self)==0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)==int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)==float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)==float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)==float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)==int(another) else boolean(false)}

double.ne_table={
	empty: lambda self, another: boolean(true) if float(self)!=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)!=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)!=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)!=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)!=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)!=int(another) else boolean(false)}

double.lt_table={
	empty: lambda self, another: boolean(true) if float(self)<0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)<int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)<float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)<float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)<float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)<int(another) else boolean(false)}

double.gt_table={
	empty: lambda self, another: boolean(true) if float(self)>0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)>int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)>float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)>float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)>float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)>int(another) else boolean(false)}

double.le_table={
	empty: lambda self, another: boolean(true) if float(self)<=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)<=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)<=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)<=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)<=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)<=int(another) else boolean(false)}

double.ge_table={
	empty: lambda self, another: boolean(true) if float(self)>=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)>=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)>=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)>=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)>=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)>=int(another) else boolean(false)}


double.and_table={
	empty: lambda self, another: integer(int(self)&0),
	null: lambda self, another: v_null if int(self) else integer(int(self)),
	integer: lambda self, another: integer(int(self)&int(another)),
	double: lambda self, another: integer(int(self)&int(another)),
	date: lambda self, another: integer(int(self)&int(another)),
	string: lambda self, another: integer(int(self)&int(another)),
	boolean: lambda self, another: integer(int(self)&int(another))}

double.or_table={
	empty: lambda self, another: integer(int(self)|0),
	null: lambda self, another: integer(int(self)) if int(self) else v_null,
	integer: lambda self, another: integer(int(self)|int(another)),
	double: lambda self, another: integer(int(self)|int(another)),
	date: lambda self, another: integer(int(self)|int(another)),
	string: lambda self, another: integer(int(self)|int(another)),
	boolean: lambda self, another: integer(int(self)|int(another))}

double.xor_table={
	empty: lambda self, another: integer(int(self)^0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self)^int(another)),
	double: lambda self, another: integer(int(self)^int(another)),
	date: lambda self, another: integer(int(self)^int(another)),
	string: lambda self, another: integer(int(self)^int(another)),
	boolean: lambda self, another: integer(int(self)^int(another))}
