
from builtins import next
from builtins import zip
from builtins import range
from copy import deepcopy
from .. import errors
from ..primitives import subtype
from .empty import v_empty
from .integer import integer
from ..variables import variant
from functools import reduce


def measure(items):
	subscripts=[]
	while True:
		subscripts.insert(0, len(items)-1)
		if not items: break
		items=items[0]
		if not isinstance(items, list): break
	return subscripts

def dim(subscripts):
	array=[v_empty]*(subscripts[0]+1)
	for subscript in subscripts[1:]:
		item=array
		array=[item]
		for index in range(subscript):
			array.append(deepcopy(item))
	return array

def copylist(items):
	return [copylist(item) for item in items] \
		if items and isinstance(items[0], list) \
		else [item.copy for item in items]

def redim(items, subscripts, index):
	subscript=subscripts[index]
	if index>0:
		if subscript!=len(items)-1:
			raise errors.subscript_out_of_range
		for item in items:
			redim(item, subscripts, index-1)
	else:
		if subscript<0:
			raise errors.subscript_out_of_range
		elif subscript<len(items)-1:
			del items[subscript+1:]
		elif subscript>len(items)-1:
			items.extend([v_empty]*(subscript+1-len(items)))

def erase(items):
	if items and isinstance(items[0], list):
		for item in items: erase(item)
	else:
		items[:]=[v_empty]*len(items)


class array(subtype):

	def __init__(self, items=None, subscripts=None, static=None):
		if items is not None:
			if not isinstance(items, list): items=list(items)
			self._items=items
			self._subscripts=measure(items)
			self._static=static
		elif subscripts is not None:
			if not isinstance(subscripts, list): items=list(items)
			self._items=dim(subscripts)
			self._subscripts=subscripts
			self._static=static
		else:
			self._items=[]
			self._subscripts=[-1]
			self._static=static

	def __call__(self, *arguments, **keywords):
		if "let" in keywords:
			if len(arguments)!=len(self._subscripts):
				raise errors.wrong_number_of_arguments
			simple, items=keywords["let"].as_simple, self._items
			try:
				for index in arguments[-1:0:-1]:
					items=items[index.as_integer]
				items[arguments[0].as_integer]=simple
			except IndexError:
				raise errors.subscript_out_of_range
		elif "set" in keywords:
			if len(arguments)!=len(self._subscripts):
				raise errors.wrong_number_of_arguments
			complex, items=keywords["set"].as_complex, self._items
			try:
				for index in arguments[-1:0:-1]:
					items=items[index.as_integer]
				items[arguments[0].as_integer]=complex
			except IndexError:
				raise errors.subscript_out_of_range
		else:
			if len(arguments)!=len(self._subscripts):
				raise errors.wrong_number_of_arguments
			result=self._items
			try:
				for index in reversed(arguments):
					result=result[index.as_integer]
				return result
			except IndexError:
				raise errors.subscript_out_of_range


	copy=property(lambda self: array(copylist(self._items),
		subscripts=deepcopy(self._subscripts), static=self._static))


	code=property(lambda self: 8204)
	name=property(lambda self: "Array")


	def redim(self, preserve, *subscripts):
		if self._static:
			raise errors.static_array
		if subscripts:
			self._subscripts=[subscript.as_integer for subscript in subscripts]
			if preserve: redim(self._items, self._subscripts, len(self._subscripts)-1)
			else: self._items=dim(self._subscripts)
		else:
			self._items=[]
			self._subscripts=[-1]

	def erase(self, *arguments):
		if self._static:
			if arguments:
				if len(arguments)>len(self._subscripts):
					raise errors.wrong_number_of_arguments
				elif len(arguments)<len(self._subscripts):
					items=self._items
					try:
						for index in reversed(arguments): items=items[index.as_integer]
					except IndexError:
						raise errors.subscript_out_of_range
					erase(items)
				else:
					items=self._items
					try:
						for index in arguments[-1:0:-1]: items=items[index.as_integer]
						items[arguments[0].as_integer]=v_empty
					except IndexError:
						raise errors.subscript_out_of_range
			else:
				erase(self._items)
		else:
			if arguments:
				if len(arguments)>1: raise errors.wrong_number_of_arguments
				try: del self._items[arguments[0].as_integer]
				except KeyError: raise errors.subscript_out_of_range
				self._subscripts[0]-=1
			else:
				del self._items[:]
				self._subscripts=[]


	as_simple=property(lambda self: self)
	as_array=property(lambda self: self)


	def is_array(self, *arguments, **keywords):
		if keywords:
			if "length" in keywords:
				if len(self._items)!=keywords.pop("length"):
					return False
			if keywords:
				raise TypeError("is_array got an unexpected keyword argument %r"%next(iter(keywords)))
		if arguments:
			if len(arguments)>1:
				return len(self._items)==len(arguments) and \
					all(function(item) for function, item in zip(arguments, self._items))
			elif isinstance(arguments[0], tuple):
				return len(self._items)==len(arguments[0]) and \
					all(function(item) for function, item in zip(arguments[0], self._items))
			else:
				if arguments[0].__code__.co_argcount>1:
					return all((arguments[0](index, item) for index, item in enumerate(self._items)))
				else:
					return arguments[0](self._items)
		return True

	dimension=property(lambda self: len(self._subscripts))
	items=property(lambda self: self._items)


	def subarray(self, *indices):
		if len(indices)>=len(self._subscripts): raise errors.wrong_number_of_arguments
		items=self._items
		try:
			for index in reversed(indices): items=items[index]
		except IndexError:
			raise errors.subscript_out_of_range
		return copylist(items)

	def flatten(self):
		if len(self._subscripts)==1:
			return list(self._items)
		else:
			return list(self)

	def lbound(self, dimension):
		if dimension<1 or dimension>len(self._subscripts):
			raise errors.subscript_out_of_range
		# NOTE: VBScript returns zero
		# if self._subscripts[dimension-1]<0:
		# 	raise errors.subscript_out_of_range
		return 0

	def ubound(self, dimension):
		if dimension<1 or dimension>len(self._subscripts):
			raise errors.subscript_out_of_range
		# NOTE: VBScript returns negative value
		# if self._subscripts[dimension-1]<0:
		# 	raise errors.subscript_out_of_range
		return self._subscripts[dimension-1]

	def append(self, value):
		if len(self._subscripts)!=1:
			raise errors.invalid_procedure_call
		if self._static:
			raise errors.static_array
		self._items.append(value.as_simple)
		self._subscripts[0]+=1

	def remove(self, value):
		if len(self._subscripts)!=1:
			raise errors.invalid_procedure_call
		if self._static:
			raise errors.static_array
		simple=value.as_simple
		self._items=[item for item in self._items if item!=simple]
		self._subscripts=[len(self._items)-1]

	def __iter__(self):
		edge=len(self._subscripts)-1
		if edge<0: return
		iterators=[None]*len(self._subscripts)
		iterators[edge]=iter(self._items)
		level=edge
		while level<=edge:
			if level:
				try:
					array=next(iterators[level])
				except StopIteration:
					level+=1
				else:
					level-=1
					iterators[level]=iter(array)
			else:
				for item in iterators[level]:
					yield variant(item)
				level+=1

	def __len__(self):
		return reduce(lambda x, y: x * (y + 1), self._subscripts, 1)


	def __repr__(self):
		return "ARRAY@%08X:%r"%(id(self), self._items)
