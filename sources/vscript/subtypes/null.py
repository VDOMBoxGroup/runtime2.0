
from .. import errors
from ..primitives import subtype


class null(subtype):

	value=property(lambda self: None)


	code=property(lambda self: 1)
	name=property(lambda self: "Null")


	as_simple=property(lambda self: self)


	is_null=property(lambda self: self is v_null)


	def __invert__(self):
		return v_null
		
	def __neg__(self):
		return v_null

	def __pos__(self):
		return v_null

	def __abs__(self):
		return v_null


	def __copy__(self):
		return self

	def __deepcopy__(self, memo={}):
		return self


	def __int__(self):
		return 0

	def __unicode__(self):
		return u"null"

	def __bool__(self):
		return False


	def __repr__(self):
		return "NULL@%08X"%id(self)


v_null=null()


from .boolean import boolean, true, false
from .date import date
from .double import double, nan, infinity
from .empty import empty, v_empty
from .generic import generic
from .integer import integer
from .string import string


null.add_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.sub_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.mul_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.div_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.floordiv_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.mod_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.pow_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}


null.eq_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.ne_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.lt_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.gt_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.le_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}

null.ge_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null,
	boolean: lambda self, another: v_null}


null.and_table={
	empty: lambda self, another: integer(0),
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null if int(another) else integer(0),
	double: lambda self, another: v_null if int(another) else integer(0),
	date: lambda self, another: v_null if int(another) else integer(0),
	string: lambda self, another: v_null if int(another) else integer(0),
	boolean: lambda self, another: v_null if bool(another) else boolean(bool(another))}

null.or_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: integer(int(another)) if int(another) else v_null,
	double: lambda self, another: integer(int(another)) if int(another) else v_null,
	date: lambda self, another: integer(int(another)) if int(another) else v_null,
	string: lambda self, another: integer(int(another)) if int(another) else v_null,
	boolean: lambda self, another: boolean(bool(another)) if bool(another) else v_null}

null.xor_table={
	empty: lambda self, another: v_null,
	null: lambda self, another: v_null,
	integer: lambda self, another: v_null,
	double: lambda self, another: v_null,
	date: lambda self, another: v_null,
	string: lambda self, another: v_null if int(another) else v_null,
	boolean: lambda self, another: v_null}
