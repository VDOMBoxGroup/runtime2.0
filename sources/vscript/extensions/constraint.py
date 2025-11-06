
from builtins import next
from builtins import str
from collections import defaultdict
from types import MethodType, FunctionType
from .. import errors
from ..subtypes import generic, integer, string, dictionary, v_empty, v_mismatch
from ..variables import variant
from ..conversions import pack
from utils.constraint import Problem


class InstancesDict(defaultdict):

	def __missing__(self, key):
		return key()

class v_problem(generic):

	def __init__(self):
		generic.__init__(self)
		self._problem=Problem()
		self._instances=InstancesDict()
		self._iterator=None
		self._solution=None

	def v_solution(self, key=None, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property(u"solution")
		else:
			if self._iterator is None:
				self.v_solve()
			if key is None:
				return self._solution
			else:
				return self._solution(key)

	def v_addvariable(self, name, *values):
		name=name.as_string
		if len(values)<1:
			raise errors.wrong_number_of_arguments
		elif len(values)==1:
			unknown=values[0].subtype
			if unknown.is_array():
				values=tuple(value.value for value in unknown.items)
			else:
				values=(unknown.value,)
		else:
			values=tuple(value.value for value in values)
		try:
			self._problem.addVariable(name, values)
		except Exception as error:
			raise errors.internal_error(str(error))
		self._iterator=None
		return v_mismatch

	def v_addvariables(self, *arguments):
		if len(arguments)<2:
			raise errors.wrong_number_of_arguments
		elif len(arguments)==2:
			names=tuple(name.as_string for name in arguments[0].as_array.items)
		else:
			names=tuple(name.as_string for name in arguments[:-1])
		values=tuple(value.value for value in arguments[-1].as_array.items)
		try:
			self._problem.addVariables(names, values)
		except Exception as error:
			raise errors.internal_error(str(error))
		self._iterator=None
		return v_mismatch

	def v_addconstraint(self, klass, name, *names):
		instance=self._instances[klass]
		constraint=getattr(instance, "v_%s"%name.as_string)
		if not isinstance(constraint, MethodType):
			raise errors.expected_function
		code=constraint.__func__.__code__
		if code.co_argcount<2:
			raise errors.generic("Constraint function must have at least one argument")
		if names:
			if len(names) != code.co_argcount - 1:
				raise errors.generic("Constraint function takes exactly %d arguments: %d given" %
					(code.co_argcount - 1, len(names)))
			variables=tuple(name.value for name in names)
		else:
			variables=tuple(name[2:] for name in code.co_varnames[1:code.co_argcount])
		def wrapper(*arguments):
			arguments=(pack(argument) for argument in arguments)
			result=constraint(*arguments)
			return result.as_boolean
		try:
			self._problem.addConstraint(wrapper, variables)
		except Exception as error:
			raise errors.internal_error(str(error))
		self._iterator=None
		return v_mismatch

	def v_addconstraints(self, klass):
		instance=self._instances[klass]
		for name in dir(instance):
			if name.startswith("v_"):
				self.v_addconstraint(klass, string(name[2:]))
		return v_mismatch

	def v_again(self):
		try:
			self._iterator=self._problem.getSolutionIter()
		except KeyError as error:
			message = str(error)
			if message and message[0] == "'":
				raise errors.generic(u"Possible variable is not defined: %s" % message.replace("'", "\""))
			else:
				raise errors.internal_error(message)
		except Exception as error:
			raise errors.internal_error(str(error))
		return v_mismatch

	def v_solve(self):
		if self._iterator is None:
			self.v_again()
		try:
			solution=next(self._iterator)
		except StopIteration:
			self._solution=v_empty
		except Exception as error:
			raise errors.internal_error(str(error))
		else:
			self._solution=dictionary({string(str(key)): pack(value) \
				for key, value in solution.items()})
		return self._solution
