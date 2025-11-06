
from builtins import next
from builtins import zip
from .. import errors
from ..subtypes import array, dictionary, integer, string, ordereddictionary


def v_array(*items):
	return array([item.as_simple for item in items])

def v_dictionary(*arguments):
	def iterator2(items, error=errors.wrong_number_of_arguments):
		iterator=iter(items)
		for key in iterator:
			try: yield key, next(iterator)
			except StopIteration: raise error
	count=len(arguments)
	if count==1:
		simple=arguments[0].as_simple
		if isinstance(simple, array):
			if simple.dimension==1: iterator=iterator2(simple, error=errors.invalid_procedure_call)
			elif simple.dimension==2: iterator=list(zip(simple.items[0], simple.items[1]))
			else: raise errors.invalid_procedure_call
		else:
			iterator=iterator2(arguments)
	elif count==2:
		simple1, simple2=arguments[0].as_simple, arguments[1].as_simple
		if isinstance(simple1, array) and isinstance(simple2, array) \
			and simple1.dimension==simple2.dimension==1:
			if len(simple1.items)!=len(simple2.items): raise errors.invalid_procedure_call
			iterator=list(zip(simple1.items, simple2.items))
		else:
			iterator=iterator2(arguments)
	else:
		iterator=iterator2(arguments)
	return dictionary({key.as_simple: value.as_simple for key, value in iterator})

def v_ordereddictionary(*arguments):
	def iterator2(items, error=errors.wrong_number_of_arguments):
		iterator=iter(items)
		for key in iterator:
			try:
				yield key, next(iterator)
			except StopIteration:
				raise error
	count=len(arguments)
	if count==1:
		simple=arguments[0].as_simple
		if isinstance(simple, array):
			if simple.dimension==1:
				iterator=iterator2(simple, error=errors.invalid_procedure_call)
			elif simple.dimension==2:
				iterator=list(zip(simple.items[0], simple.items[1]))
			else:
				raise errors.invalid_procedure_call
		else:
			iterator=iterator2(arguments)
	elif count==2:
		simple1, simple2=arguments[0].as_simple, arguments[1].as_simple
		if isinstance(simple1, array) and isinstance(simple2, array) \
			and simple1.dimension == simple2.dimension==1:
			if len(simple1.items) != len(simple2.items):
				raise errors.invalid_procedure_call
			iterator=list(zip(simple1.items, simple2.items))
		else:
			iterator=iterator2(arguments)
	else:
		iterator=iterator2(arguments)
	return ordereddictionary({k.as_simple: v.as_simple for k, v in iterator})

def v_subarray(value, *indices):
	return array(value.as_array.subarray(*(index.as_integer for index in indices)))

def v_lbound(value, dimension=None):
	return integer(value.as_array.lbound(1 if dimension is None else dimension.as_integer))

def v_ubound(value, dimension=None):
	return integer(value.as_array.ubound(1 if dimension is None else dimension.as_integer))


def v_filter(strings, substring, include=None, compare=None):
	strings, substring=strings.as_array, substring.as_string
	include=True if include is None else include.as_boolean
	compare=0 if compare is None else compare.as_integer
	if compare<0 or compare>1: raise errors.invalid_procedure_call(name="filter")
	values, substring=[], substring.lower() if compare else substring
	#print repr(strings), repr(include)
	for items in strings.items:
		items=items.as_string.lower() if compare else items.as_string
		if include and items.find(substring)>=0 or \
			not include and items.find(substring)<0:
			values.append(items)
	return array(values)

def v_join(strings, delimiter=None):
	delimiter=u" " if delimiter is None else delimiter.as_string
	return string(delimiter.join([items.as_string \
		for items in strings.as_array.items]))
