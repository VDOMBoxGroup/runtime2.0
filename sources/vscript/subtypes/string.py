
from builtins import str
import sys
from .. import errors
from ..operations import div, mod
from ..primitives import subtype


class string(subtype):

	def __init__(self, value):
		#assert isinstance(value, unicode), "Got %s instead unicode string"%type(value)
		self._value=str(value)


	value=property(lambda self: self._value)


	code=property(lambda self: 8)
	name=property(lambda self: "String")


	as_simple=property(lambda self: self)
	as_boolean=property(lambda self: bool(self))
	as_date=property(lambda self: float(self))
	as_double=property(lambda self: float(self))
	as_integer=property(lambda self: int(self))
	as_string=property(lambda self: str(self))
	as_number=property(lambda self: float(self))


	def is_string(self, value=None):
		return True if value is None else self._value==value


	def __iter__(self):
		from ..variables import variant
		for character in self._value: yield variant(string(character))

	def __len__(self):
		return len(self._value)


	def __invert__(self):
		try: return integer(~int(round(float(self._value))))
		except ValueError: raise errors.type_mismatch
		
	def __neg__(self):
		try: return double(-float(self._value))
		except ValueError: raise errors.type_mismatch

	def __pos__(self):
		try: return double(+float(self._value))
		except ValueError: raise errors.type_mismatch

	def __abs__(self):
		try: return double(abs(float(self._value)))
		except ValueError: raise errors.type_mismatch


	def __int__(self):
		try: return int(round(float(self._value)))
		except ValueError: raise errors.type_mismatch

	def __float__(self):
		try: return float(self._value)
		except ValueError: raise errors.type_mismatch

	def __unicode__(self):
		return str(self._value)

	def __bool__(self):
		try:
			return bool(float(self._value))
		except ValueError:
			if self._value.lower()=="true": return True
			elif self._value.lower()=="false": return False
			else: raise errors.type_mismatch


	def __hash__(self):
		return hash(self._value)

	def __repr__(self):
		if hasattr(self, "_value"):
			return "STRING@%08X:%r"%(id(self), self._value)
		else:
			return "STRING@%08X:<UNINITIALIZED>"%(id(self))


from .boolean import boolean, true, false
from .date import date
from .double import double, nan, infinity
from .empty import empty, v_empty
from .generic import generic
from .integer import integer
from .null import null, v_null


string.add_table={
	empty: lambda self, another: string(str(self)+str(another)),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)+int(another)),
	double: lambda self, another: double(float(self)+float(another)),
	date: lambda self, another: date(float(self)+float(another)),
	string: lambda self, another: string(str(self)+str(another)),
	boolean: lambda self, another: double(float(self)+int(another))}

string.sub_table={
	empty: lambda self, another: double(float(self)-0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)-int(another)),
	double: lambda self, another: double(float(self)-float(another)),
	date: lambda self, another: date(float(self)-float(another)),
	string: lambda self, another: double(float(self)-float(another)),
	boolean: lambda self, another: double(float(self)-int(another))}

string.mul_table={
	empty: lambda self, another: double(float(self)*0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)*int(another)),
	double: lambda self, another: double(float(self)*float(another)),
	date: lambda self, another: double(float(self)*float(another)),
	string: lambda self, another: double(float(self)*float(another)),
	boolean: lambda self, another: double(float(self)*int(another))}

string.div_table={
	empty: lambda self, another: double(float(self)/0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)/int(another)),
	double: lambda self, another: double(float(self)/float(another)),
	date: lambda self, another: double(float(self)/float(another)),
	string: lambda self, another: double(float(self)/float(another)),
	boolean: lambda self, another: double(float(self)/int(another))}

string.floordiv_table={
	empty: lambda self, another: integer(div(int(self), 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(div(int(self), int(another))),
	double: lambda self, another: integer(div(int(self), int(another))),
	date: lambda self, another: integer(div(int(self), int(another))),
	string: lambda self, another: integer(div(int(self), int(another))),
	boolean: lambda self, another: integer(div(int(self), int(another)))}

string.mod_table={
	empty: lambda self, another: integer(mod(int(self), 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(mod(int(self), int(another))),
	double: lambda self, another: integer(mod(int(self), int(another))),
	date: lambda self, another: integer(mod(int(self), int(another))),
	string: lambda self, another: integer(mod(int(self), int(another))),
	boolean: lambda self, another: integer(mod(int(self), int(another)))}

string.pow_table={
	empty: lambda self, another: double(float(self)**0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)**int(another)),
	double: lambda self, another: double(float(self)**float(another)),
	date: lambda self, another: double(float(self)**float(another)),
	string: lambda self, another: double(float(self)**float(another)),
	boolean: lambda self, another: double(float(self)**int(another))}


string.eq_table={
	empty: lambda self, another: boolean(true) if str(self)==u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)==int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)==float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)==float(another) else boolean(false),
	string: lambda self, another: boolean(true) if str(self)==str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if str(self)==str(another) else boolean(false)}

string.ne_table={
	empty: lambda self, another: boolean(true) if str(self)!=u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)!=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)!=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)!=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if str(self)!=str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if str(self)!=str(another) else boolean(false)}

string.lt_table={
	empty: lambda self, another: boolean(true) if str(self)<u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)<int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)<float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)<float(another) else boolean(false),
	string: lambda self, another: boolean(true) if str(self)<str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if str(self)<str(another) else boolean(false)}

string.gt_table={
	empty: lambda self, another: boolean(true) if str(self)>u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)>int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)>float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)>float(another) else boolean(false),
	string: lambda self, another: boolean(true) if str(self)>str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if str(self)>str(another) else boolean(false)}

string.le_table={
	empty: lambda self, another: boolean(true) if str(self)<=u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)<=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)<=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)<=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if str(self)<=str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if str(self)<=str(another) else boolean(false)}

string.ge_table={
	empty: lambda self, another: boolean(true) if str(self)>=u"" else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if int(self)>=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)>=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)>=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if str(self)>=str(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if str(self)>=str(another) else boolean(false)}


string.and_table={
	empty: lambda self, another: integer(int(self)&0),
	null: lambda self, another: v_null if int(self) else integer(int(self)),
	integer: lambda self, another: integer(int(self)&int(another)),
	double: lambda self, another: integer(int(self)&int(another)),
	date: lambda self, another: integer(int(self)&int(another)),
	string: lambda self, another: integer(int(self)&int(another)),
	boolean: lambda self, another: integer(int(self)&int(another))}

string.or_table={
	empty: lambda self, another: integer(int(self)|0),
	null: lambda self, another: integer(int(self)) if int(self) else v_null,
	integer: lambda self, another: integer(int(self)|int(another)),
	double: lambda self, another: integer(int(self)|int(another)),
	date: lambda self, another: integer(int(self)|int(another)),
	string: lambda self, another: integer(int(self)|int(another)),
	boolean: lambda self, another: integer(int(self)|int(another))}

string.xor_table={
	empty: lambda self, another: integer(int(self)^0),
	null: lambda self, another: v_null if int(self) else v_null,
	integer: lambda self, another: integer(int(self)^int(another)),
	double: lambda self, another: integer(int(self)^int(another)),
	date: lambda self, another: integer(int(self)^int(another)),
	string: lambda self, another: integer(int(self)^int(another)),
	boolean: lambda self, another: integer(int(self)^int(another))}
