
from builtins import str
import types
from . import errors
from .subtypes import boolean, double, integer, null, string, v_null


all=["as_is", "as_value", "as_generic", "as_specific",
	"as_boolean", "as_double", "as_integer", "as_string",
	"as_array", "as_date", "as_binary",
	"pack", "unpack"]


def as_is(value):
	return value.subtype

def as_value(value):
	return value.as_simple

def as_generic(value):
	return value.as_generic

def as_specific(value, specific):
	return value.as_specific(specific)


def as_boolean(value):
	return value.as_boolean

def as_double(value):
	return value.as_double

def as_integer(value):
	return value.as_integer

def as_string(value):
	return value.as_string


def as_array(value):
	return value.as_array

def as_date(value):
	return value.as_date

def as_binary(value):
	return value.as_binary


def pack(value, default=None):
	def unknown(value): raise errors.type_mismatch
	return {
		int: lambda value: integer(value),
		int: lambda value: integer(value),
		str: lambda value: string(str(value)),
		str: lambda value: string(value),
		bool: lambda value: boolean(value),
		float: lambda value: double(value),
		type(None): lambda value: v_null} \
			.get(type(value), default or unknown)(value)

def unpack(value, default=None):
	def unknown(value): raise errors.type_mismatch
	return {
		integer: lambda value: value.value,
		string: lambda value: value.value,
		boolean: lambda value: value.value,
		double: lambda value: value.value,
		null: lambda value: None} \
			.get(type(value), default or unknown)(value)
