
from builtins import str
from .. import errors
from ..subtypes import generic, string
from ..variables import shadow


class v_vdomtype(generic):

	def __init__(self, type):
		generic.__init__(self)
		self._type=type

	
	def v_id(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("id")
		else:
			return string(str(self._type.id))

	def v_name(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("name")
		else:
			return string(str(self._type.name))


	def __repr__(self):
		return "VDOMTYPE@%08Xs:%r"%(id(self), self._type)
	

class v_vdomobject(generic):

	def __init__(self, object):
		generic.__init__(self)
		self._object=object

	
	def __getattr__(self, name):
		if name.startswith("v_"):
			name=name[2:]
			if name in self._object.attributes:
				return shadow(self, "wrapper_%s"%name)
			elif name in self._object.objects:
				return v_vdomobject(self._object.objects[name])
			else:
				raise errors.object_has_no_property(name)
		elif name.startswith("wrapper_"):
			return string(str(getattr(self._object, name[8:])))
		else:
			raise errors.object_has_no_property(name)

	def __setattr__(self, name, value):
		if name.startswith("v_"):
			name=name[2:]
			if name in self._object.attributes:
				setattr(self._object, name, value.as_string)
			elif name in self._object.objects:
				raise errors.type_mismatch
			else:
				raise errors.object_has_no_property(name)
		elif name.startswith("wrapper_"):
			setattr(self._object, name[8:], value.as_string)
		else:
			generic.__setattr__(self, name, value)

	
	def v_id(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("id")
		else:
			return string(self._object.id)

	def v_name(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("name")
		else:
			return string(self._object.name)

	def v_type(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("type")
		else:
			return v_vdomtype(self._object.type)

	
	def v_update(self, *arguments):
		self._object.update(*(argument.as_string.lower() for argument in arguments))

	def v_action(self, name, parameters=None, source=None):
		parameters=() if parameters is None else [parameter.as_string for parameter in parameters.as_array.items]
		self._object.action(name.as_string, parameters, None if source is None else source.as_string)
		

	def __repr__(self):
		return "VDOMOBJECT@%08X:%r"%(id(self), self._object)
	

class v_vdomapplication(generic):

	def __init__(self, application):
		generic.__init__(self)
		self._application=application

	def __getattr__(self, name):
		if name.startswith("v_"):
			name, objects=name[2:], self._application.get_objects_by_name()
			if name in objects:
				return v_vdomobject(objects[name])
			else:
				raise errors.object_has_no_property(name)
		else:
			raise errors.object_has_no_property(name)

	def __setattr__(self, name, value):
		if name.startswith("v_"):
			name=name[2:]
			if name in objects:
				raise errors.type_mismatch
			else:
				raise errors.object_has_no_property(name)
		else:
			generic.__setattr__(self, name, value)

	
	def v_id(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("id")
		else:
			return string(self._application.id)

	def v_name(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("name")
		else:
			return string(self._application.name)


	def __repr__(self):
		return "VDOMAPPLICATION@%08X:%r"%(id(self), self._application)
