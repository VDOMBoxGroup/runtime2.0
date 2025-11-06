
from ... import errors
from ...subtypes import array, boolean, generic, integer, v_empty, v_mismatch
from ...variables import variant


class scripting_dictionary(generic):

	# TODO: Implement vTextCompare

	def __init__(self):
		generic.__init__(self)
		self._compare_mode=0
		self._items={}


	def v_comparemode(self, **keywords):
		if "let" in keywords:
			value=keywords["let"].as_integer
			if value<0 or value>2: raise errors.invalid_procedure_call
			if value in (1, 2): raise errors.not_implemented
			self._compare_mode=value
		elif "set" in keywords:
			raise errors.object_has_no_property
		else:
			return integer(self._compare_mode)

	def v_count(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property
		else:
			return integer(len(self._items))

	def v_item(self, key, **keywords):
		if "let" in keywords:
			self._items[key.subtype]=keywords["let"].as_simple
		elif "set" in keywords:
			self._items[key.subtype]=keywords["set"].as_complex
		else:
			try: return self._items[key.subtype]
			except KeyError: return v_empty

	def v_key(self, key, **keywords):
		if "let" in keywords:
			try: self._items[keywords["let"].subtype]=self._items[key.as_simple]
			except KeyError: raise errors.element_not_found
		elif "set" in keywords:
			try: self._items[keywords["set"].subtype]=self._items[key.as_complex]
			except KeyError: raise errors.element_not_found
		else:
			raise errors.object_has_no_property


	def v_add(self, key, item):
		self._items[key.subtype]=item.subtype
		return v_mismatch

	def v_exists(self, key):
		return boolean(key.subtype in self._items)

	def v_items(self):
		return array(list((iter(self._items.values()))))

	def v_keys(self):
		return array(list((iter(self._items.keys()))))

	def v_remove(self, key):
		try: del self._items[key.subtype]
		except KeyError: raise errors.element_not_found
		return v_mismatch

	def v_removeall(self):
		self._items.clear()
		return v_mismatch


	def __iter__(self):
		for item in self._items: yield variant(item)

	def __len__(self):
		return integer(len(self._items))


	def __repr__(self):
		return "GENERIC@%08X:DICTIONARY:%r"%(id(self), self._items)
