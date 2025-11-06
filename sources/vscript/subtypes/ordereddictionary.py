
from builtins import str
from .. import errors
from ..primitives import subtype
from .empty import v_empty
from ..variables import variant
from collections import OrderedDict


class ordereddictionary(subtype):
	def __init__(self, items=None):
		self._items = OrderedDict() if items is None else OrderedDict(items)

	def __call__(self, *arguments, **keywords):
		if len(arguments) != 1:
			raise errors.wrong_number_of_arguments

		if "let" in keywords:
			self._items[arguments[0].subtype]=keywords["let"].as_simple
		elif "set" in keywords:
			self._items[arguments[0].subtype]=keywords["set"].as_complex
		else:
			return self._items.get(arguments[0].subtype, v_empty)

	copy=property(lambda self: OrderedDict([(k.copy, v.copy) for k, v in self._items.items()]))

	code=property(lambda self: 9001)

	name=property(lambda self: "OrderedDictionary")

	def erase(self, *arguments):
		if arguments:
			if len(arguments) > 1:
				raise errors.wrong_number_of_arguments
			try:
				del self._items[arguments[0].as_simple]
			except KeyError:
				raise errors.invalid_procedure_call
		else:
			self._items.clear()

	as_simple=property(lambda self: self)

	as_dictionary=property(lambda self: self)

	def is_dictionary(self, func=None):
		return all((func(k, v) for k, v in self._items.items())) if func else True

	items=property(lambda self: self._items)

	def __iter__(self):
		for item in self._items:
			yield variant(item)

	def __len__(self):
		return len(self._items)

	def __contains__(self, value):
		return value.subtype in self._items

	def __repr__(self):
		return "ORDEREDDICTIONARY@%08X:%r"%(id(self), self._items)

	def __str__(self):
		return str(self._items)
