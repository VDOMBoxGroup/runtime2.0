
from copy import deepcopy
from .. import errors
from ..primitives import subtype
from .empty import v_empty
from .boolean import boolean, true, false
from ..variables import variant


class dictionary(subtype):
	def __init__(self, items=None):
		self._items={} if items is None else items

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			if len(arguments)!=1: raise errors.wrong_number_of_arguments
			self._items[arguments[0].subtype]=keywords["let"].as_simple
		elif "set" in keywords:
			if len(arguments)!=1: raise errors.wrong_number_of_arguments
			self._items[arguments[0].subtype]=keywords["set"].as_complex
		else:
			if len(arguments)!=1: raise errors.wrong_number_of_arguments
			return self._items.get(arguments[0].subtype, v_empty)

	copy=property(lambda self: dictionary({key.copy: value.copy \
		for key, value in self._items.items()}))

	code=property(lambda self: 9001)
	name=property(lambda self: "Dictionary")

	def erase(self, *arguments):
		if arguments:
			if len(arguments)>1: raise errors.wrong_number_of_arguments
			try: del self._items[arguments[0].as_simple]
			except KeyError: raise errors.invalid_procedure_call
		else:
			self._items.clear()

	as_simple=property(lambda self: self)
	as_dictionary=property(lambda self: self)

	def is_dictionary(self, function=None):
		return all((function(key, value) for ket, value in self._items.items())) if function \
			else True

	items=property(lambda self: self._items)

	def __iter__(self):
		for item in self._items:
			yield variant(item)

	def __len__(self):
		return len(self._items)

	def __contains__(self, value):
		return value.subtype in self._items

	def __repr__(self):
		return "DICTIONARY@%08X:%r"%(id(self), self._items)
