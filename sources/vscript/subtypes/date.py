
from builtins import zip
from builtins import str

import sys, re, datetime
from math import modf, fabs
from .. import errors
from ..operations import div, mod
from ..primitives import subtype


def encode_date(year, month, day, hours=0, minutes=0, seconds=0):
	date_value=float(datetime.date(year, month, day).toordinal()-693594)
	time_value=float(hours*60*60+minutes*60+seconds)/86400
	return date_value-time_value if date_value<0 else date_value+time_value

def encode_time(hour, minute, second):
	return float(hour*60*60+minute*60+second)/86400

def decode_date(value):
	time_value, date_value=modf(value)
	time_value, date_value=int(round(fabs(time_value)*86400)), int(round(date_value+693594))
	date_value=datetime.date.fromordinal(date_value)
	seconds, time_value=time_value%60, time_value//60
	minutes, time_value=time_value%60, time_value//60
	return date_value.year, date_value.month, date_value.day, time_value, minutes, seconds


class date(subtype):

	pattern=re.compile(r"^(?:(?P<day>\d{1,2})[\.\-\/](?P<month>\d{1,2})(?:[\.\-\/](?P<year>\d{2,4}))?)?"\
		r"(?:(?(day)\s+)(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(?::(?P<second>\d{1,2}))?(?:\s*(?P<ampm>(?:am|aM|Am|AM|pm|pM|Pm|PM)))?)?$")
	pattern2=re.compile(r"^(?:(?P<year>\d{2,4})[\.\-\/](?P<month>\d{1,2})[\.\-\/](?P<day>\d{1,2}))?"\
		r"(?:(?(day)\s+)(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(?::(?P<second>\d{1,2}))?(?:\s*(?P<ampm>(?:am|aM|Am|AM|pm|pM|Pm|PM)))?)?$")

	def __init__(self, value):
		if isinstance(value, (int, float)):
			self._value=float(value)
		elif isinstance(value, bytes):
			match=self.pattern.match(value) or self.pattern2.match(value)
			if match:
				day=match.group("day")
				month=match.group("month")
				year=match.group("year") or str(datetime.datetime.today().year)
				hour=match.group("hour")
				minute=match.group("minute")
				second=match.group("second") or 0
				ampm=match.group("ampm")
				if len(year)==2: year="20"+year if year<"30" else "19"+year
				if day: year, month, day=int(year), int(month), int(day)
				else: year, month, day=1899, 12, 30
				if hour: hour, minute, second=int(hour), int(minute), int(second)
				else: hour, minute, second=0, 0, 0
				if ampm is not None:
					if hour>12: raise errors.invalid_date_format
					if ampm.lower()=="pm":
						hour+=12
						if hour==24: hour=0
				self._value=encode_date(year, month, day, hour, minute, second)
			else:
				raise errors.type_mismatch
		else:
			raise errors.type_mismatch
		if self._value<-657434 or self._value>=2958466:
			self.__class__=double


	value=property(lambda self: self._value)


	code=property(lambda self: 7)
	name=property(lambda self: "Date")


	as_simple=property(lambda self: self)
	as_boolean=property(lambda self: bool(self))
	as_date=property(lambda self: float(self))
	as_double=property(lambda self: float(self))
	as_integer=property(lambda self: int(self))
	as_string=property(lambda self: str(self))
	as_number=property(lambda self: float(self))


	def is_date(self, year=None, month=None, day=None, hour=None, minute=None, second=None):
		return all(x is None or x==y for x, y \
			in zip((year, month, day, hour, minute, second), decode_date(self._value))) \
			if any(x is not None for x in (month, day, hour, minute, second)) \
			else year is None or decode_date(self._value)==decode_date(year)


	separate=property(lambda self: decode_date(self._value))

	has_both=property(lambda self: all(modf(self._value)))
	has_date=property(lambda self: modf(self._value)[1]!=0)
	has_time=property(lambda self: modf(self._value)[0]!=0)

		
	def __invert__(self):
		return integer(~int(round(self._value)))
		
	def __neg__(self):
		return date(-self._value)

	def __pos__(self):
		return date(+self._value)

	def __abs__(self):
		return date(fabs(self._value))


	def __int__(self):
		return int(round(self._value))

	def __float__(self):
		return self._value

	def __unicode__(self):
		year, month, day, hour, minute, second=decode_date(self._value)
		if hour+minute+second:
			return u"%02d.%02d.%d %02d:%02d:%02d"%(day, month, year, hour, minute, second)
		else:
			return u"%02d.%02d.%d"%(day, month, year)
	
	def __bool__(self):
		return bool(self._value)


	def __hash__(self):
		return hash(self._value)
	
	def __repr__(self):
		return "DATE@%08X:%r:%s"%(id(self), self._value, str(self))


from .boolean import boolean, true, false
from .double import double, nan, infinity
from .empty import empty, v_empty
from .generic import generic
from .integer import integer
from .null import null, v_null
from .string import string


date.add_table={
	empty: lambda self, another: date(float(self)+0),
	null: lambda self, another: v_null,
	integer: lambda self, another: date(float(self)+int(another)),
	double: lambda self, another: date(float(self)+float(another)),
	date: lambda self, another: date(float(self)+float(another)),
	string: lambda self, another: date(float(self)+float(another)),
	boolean: lambda self, another: date(float(self)+int(another))}

date.sub_table={
	empty: lambda self, another: date(float(self)-0),
	null: lambda self, another: v_null,
	integer: lambda self, another: date(float(self)-int(another)),
	double: lambda self, another: date(float(self)-float(another)),
	date: lambda self, another: double(float(self)-float(another)),
	string: lambda self, another: date(float(self)-float(another)),
	boolean: lambda self, another: date(float(self)-int(another))}

date.mul_table={
	empty: lambda self, another: double(float(self)*0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)*int(another)),
	double: lambda self, another: double(float(self)*float(another)),
	date: lambda self, another: double(float(self)*float(another)),
	string: lambda self, another: double(float(self)*float(another)),
	boolean: lambda self, another: double(float(self)*int(another))}

date.div_table={
	empty: lambda self, another: double(float(self)/0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)/int(another)),
	double: lambda self, another: double(float(self)/float(another)),
	date: lambda self, another: double(float(self)/float(another)),
	string: lambda self, another: double(float(self)/float(another)),
	boolean: lambda self, another: double(float(self)/int(another))}

date.floordiv_table={
	empty: lambda self, another: integer(div(int(self), 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(div(int(self), int(another))),
	double: lambda self, another: integer(div(int(self), int(another))),
	date: lambda self, another: integer(div(int(self), int(another))),
	string: lambda self, another: integer(div(int(self), int(another))),
	boolean: lambda self, another: integer(div(int(self), int(another)))}

date.mod_table={
	empty: lambda self, another: integer(mod(int(self), 0)),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(mod(int(self), int(another))),
	double: lambda self, another: integer(mod(int(self), int(another))),
	date: lambda self, another: integer(mod(int(self), int(another))),
	string: lambda self, another: integer(mod(int(self), int(another))),
	boolean: lambda self, another: integer(mod(int(self), int(another)))}

date.pow_table={
	empty: lambda self, another: double(float(self)**0),
	null: lambda self, another: v_null,
	integer: lambda self, another: double(float(self)**int(another)),
	double: lambda self, another: double(float(self)**float(another)),
	date: lambda self, another: double(float(self)**float(another)),
	string: lambda self, another: double(float(self)**float(another)),
	boolean: lambda self, another: double(float(self)**int(another))}


date.eq_table={
	empty: lambda self, another: boolean(true) if float(self)==0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)==int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)==float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)==float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)==float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)==int(another) else boolean(false)}

date.ne_table={
	empty: lambda self, another: boolean(true) if float(self)!=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)!=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)!=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)!=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)!=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)!=int(another) else boolean(false)}

date.lt_table={
	empty: lambda self, another: boolean(true) if float(self)<0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)<int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)<float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)<float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)<float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)<int(another) else boolean(false)}

date.gt_table={
	empty: lambda self, another: boolean(true) if float(self)>0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)>int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)>float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)>float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)>float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)>int(another) else boolean(false)}

date.le_table={
	empty: lambda self, another: boolean(true) if float(self)<=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)<=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)<=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)<=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)<=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)<=int(another) else boolean(false)}

date.ge_table={
	empty: lambda self, another: boolean(true) if float(self)>=0 else boolean(false),
	null: lambda self, another: v_null,
	integer: lambda self, another: boolean(true) if float(self)>=int(another) else boolean(false),
	double: lambda self, another: boolean(true) if float(self)>=float(another) else boolean(false),
	date: lambda self, another: boolean(true) if float(self)>=float(another) else boolean(false),
	string: lambda self, another: boolean(true) if float(self)>=float(another) else boolean(false),
	boolean: lambda self, another: boolean(true) if float(self)>=int(another) else boolean(false)}


date.and_table={
	empty: lambda self, another: integer(int(self)&0),
	null: lambda self, another: v_null if int(self) else integer(int(self)),
	integer: lambda self, another: integer(int(self)&int(another)),
	double: lambda self, another: integer(int(self)&int(round(float(another)))),
	date: lambda self, another: integer(int(self)&int(round(float(another)))),
	string: lambda self, another: integer(int(self)&int(round(float(another)))),
	boolean: lambda self, another: integer(int(self)&int(another))}

date.or_table={
	empty: lambda self, another: integer(int(self)|0),
	null: lambda self, another: integer(int(self)) if int(self) else v_null,
	integer: lambda self, another: integer(int(self)|int(another)),
	double: lambda self, another: integer(int(self)|int(round(float(another)))),
	date: lambda self, another: integer(int(self)|int(round(float(another)))),
	string: lambda self, another: integer(int(self)|int(round(float(another)))),
	boolean: lambda self, another: integer(int(self)|int(another))}

date.xor_table={
	empty: lambda self, another: integer(int(self)^0),
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(self)^int(another)),
	double: lambda self, another: integer(int(self)^int(round(float(another)))),
	date: lambda self, another: integer(int(self)^int(round(float(another)))),
	string: lambda self, another: integer(int(self)^int(round(float(another)))),
	boolean: lambda self, another: integer(int(self)^int(another))}
