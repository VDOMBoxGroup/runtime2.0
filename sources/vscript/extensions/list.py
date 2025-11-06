
from .. import errors
from ..subtypes import generic, integer, v_mismatch
from ..variables import variant


class v_list(generic):

	def __init__(self, items=None):
		generic.__init__(self)
		self._items=[] if items is None else items

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			if len(arguments)!=1:
				raise errors.wrong_number_of_arguments
			try:
				self._items[arguments[0].as_integer]=keywords["let"].as_simple
			except IndexError:
				raise errors.subscript_out_of_range
		elif "set" in keywords:
			if len(arguments)!=1:
				raise errors.wrong_number_of_arguments
			try:
				self._items[arguments[0].as_integer]=keywords["set"].as_complex
			except IndexError:
				raise errors.subscript_out_of_range
		else:
			if len(arguments)!=1:
				raise errors.wrong_number_of_arguments
			try:
				return self._items[arguments[0].as_integer]
			except IndexError:
				raise errors.subscript_out_of_range


	items=property(lambda self: self._items)


	def erase(self, *arguments):
		if arguments:
			if len(arguments)>1: raise errors.wrong_number_of_arguments
			try: del self._items[arguments[0].as_integer]
			except KeyError: raise errors.subscript_out_of_range
		else:
			del self._items[:]


	@classmethod
	def v_from(cls, *items):
		return cls(items=list(items))

	@classmethod
	def v_fromarray(cls, array):
		return cls(items=array.as_array.flatten())


	def v_count(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.errors.object_has_no_property
		else:
			return integer(len(self._items))


	def v_append(self, value):
		self._items.append(value.subtype)
		return v_mismatch

	def v_insert(self, index, value):
		self._items.insert(index.as_integer, value.subtype)
		return v_mismatch

	def v_extend(self, another):
		self._items.extend(another.as_specific(v_list)._items)
		return v_mismatch

	def v_remove(self, value):
		try: self._items.remove(value.subtype)
		except ValueError: raise errors.element_not_found
		return v_mismatch

	def v_removeall(self, value):
		simple=value.as_simple
		self._items=[item for item in self._items if item!=simple]
		return v_mismatch

	def v_index(self, value):
		try: return integer(self._items.index(value.subtype))
		except ValueError: raise errors.element_not_found

	def v_push(self, value):
		self._items.append(value.subtype)
		return v_mismatch

	def v_pop(self, index=None):
		try: return self._items.pop(-1 if index is None else index.as_integer)
		except KeyError: raise errors.subscript_out_of_range


	def __iter__(self):
		for item in self._items: yield variant(item)

	def __len__(self):
		return integer(len(self._items))
