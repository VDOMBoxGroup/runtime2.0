
from itertools import chain
from math import modf, copysign, fabs
from .. import errors
from ..subtypes import date, integer, string
from ..subtypes.date import encode_date, encode_time, decode_date


def v_formatdatetime(value, format=None):
	value=value.as_date
	format=0 if format is None else format.as_integer
	year, month, day, hour, minute, second=decode_date(value)
	if format==0:
		time, date=modf(value)
		if date:
			if time:
				return string("%d-%02d-%02d %02d:%02d:%02d"%(year, month, day, hour, minute, second))
			else:
				return string("%d-%02d-%02d"%(year, month, day))
		else:
			return string("%02d:%02d:%02d"%(hour, minute, second))
	elif format==1:
		return string("%d-%02d-%02d"%(year, month, day))
	elif format==2:
		return string("%d-%02d-%02d"%(year, month, day))
	elif format==3:
		return string("%02d:%02d:%02d"%(hour, minute, second))
	elif format==4:
		return string("%02d:%02d"%(hour, minute))
	else:
		raise errors.invalid_procedure_call("formatdatetime")


def formatnumber(value, precision, zero, parens, group, extra=""):
	value=round(float(value), precision)
	sign, value=copysign(1, value), fabs(value)
	fractional, integral=modf(value)
	fractional=round(fractional, precision)
	result=str(int(integral))
	if integral:
		if group:
			left=len(result)%3
			result=" ".join(chain((result[:left],), (result[index:index+3] for index in range(left, len(result), 3)))) if left \
				else " ".join(result[index:index+3] for index in range(0, len(result), 3))
	else:
		if not zero:
			result=""
	if precision:
		result+=("%0.*f"%(precision, fractional))[1:]
	result+=extra
	if sign<0:
		result="(%s)"%result if parens else "-"+result
	return result


def v_formatnumber(expression, numdigitsafterdecimal=None,
	includeleadingdigit=None, useparensfornegativenumbers=None, groupdigits=None):
	if numdigitsafterdecimal is None:
		precision=2
	else:
		precision=numdigitsafterdecimal.as_integer
		if precision<0:
			raise errors.invalid_procedure_call("formatnumber")
	if includeleadingdigit is None:
		zero=True
	else:
		value=includeleadingdigit.as_integer
		if value==-2 or value==-1:
			zero=True
		elif value==0:
			zero=False
		else:
			raise errors.invalid_procedure_call("formatnumber")
	if useparensfornegativenumbers is None:
		parens=False
	else:
		value=useparensfornegativenumbers.as_integer
		if value==-1:
			parens=True
		elif value==-2 or value==0:
			parens=False
		else:
			raise errors.invalid_procedure_call("formatnumber")
	if groupdigits is None:
		group=False
	else:
		value=groupdigits.as_integer
		if value==-1:
			group=True
		elif value==-2 or value==0:
			group=False
		else:
			raise errors.invalid_procedure_call("formatnumber")
	return string(formatnumber(expression.as_number, precision, zero, parens, group))

def v_formatcurrency(expression, numdigitsafterdecimal=None,
	includeleadingdigit=None, useparensfornegativenumbers=None, groupdigits=None):
	if numdigitsafterdecimal is None:
		precision=2
	else:
		precision=numdigitsafterdecimal.as_integer
		if precision<0:
			raise errors.invalid_procedure_call("formatcurrency")
	if includeleadingdigit is None:
		zero=True
	else:
		value=includeleadingdigit.as_integer
		if value==-2 or value==-1:
			zero=True
		elif value==0:
			zero=False
		else:
			raise errors.invalid_procedure_call("formatcurrency")
	if useparensfornegativenumbers is None:
		parens=False
	else:
		value=useparensfornegativenumbers.as_integer
		if value==-1:
			parens=True
		elif value==-2 or value==0:
			parens=False
		else:
			raise errors.invalid_procedure_call("formatcurrency")
	if groupdigits is None:
		group=False
	else:
		value=groupdigits.as_integer
		if value==-1:
			group=True
		elif value==-2 or value==0:
			group=False
		else:
			raise errors.invalid_procedure_call("formatcurrency")
	return string(formatnumber(expression.as_number, precision, zero, parens, group))

def v_formatpercent(expression, numdigitsafterdecimal=None,
	includeleadingdigit=None, useparensfornegativenumbers=None, groupdigits=None):
	if numdigitsafterdecimal is None:
		precision=2
	else:
		precision=numdigitsafterdecimal.as_integer
		if precision<0:
			raise errors.invalid_procedure_call("formatpercent")
	if includeleadingdigit is None:
		zero=True
	else:
		value=includeleadingdigit.as_integer
		if value==-2 or value==-1:
			zero=True
		elif value==0:
			zero=False
		else:
			raise errors.invalid_procedure_call("formatpercent")
	if useparensfornegativenumbers is None:
		parens=False
	else:
		value=useparensfornegativenumbers.as_integer
		if value==-1:
			parens=True
		elif value==-2 or value==0:
			parens=False
		else:
			raise errors.invalid_procedure_call("formatpercent")
	if groupdigits is None:
		group=False
	else:
		value=groupdigits.as_integer
		if value==-1:
			group=True
		elif value==-2 or value==0:
			group=False
		else:
			raise errors.invalid_procedure_call("formatpercent")
	return string(formatnumber(expression.as_number*100, precision, zero, parens, group, "%"))
