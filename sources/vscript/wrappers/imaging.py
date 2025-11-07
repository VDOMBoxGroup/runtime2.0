
from importlib import import_module
import managers
from .. import errors
from ..subtypes import integer, generic, string, v_mismatch


VDOM_imaging = import_module("scripting.legacy.imaging").VDOM_imaging


def as_integer(value):
	return value.as_integer

def as_string(value):
	return value.as_string

def as_rgb(value):
	value=value.as_integer
	return value//65535, value//256%256, value%256


def adapt(arguments, adaptors, require=0, name=None):
	if len(arguments)<require or len(arguments)>len(adaptors):
		raise errors.wrong_number_of_arguments(name=name)
	return dict(((name, adaptor(argument)) \
		for (name, adaptor), argument in zip(adaptors, arguments)))


class v_vdomimaging(generic):

	def __init__(self):
		generic.__init__(self)
		self._application_id=managers.request_manager.current.application_id
		self._imaging=VDOM_imaging()


	def v_width(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("width")
		else:
			return integer(self._imaging.size[0])

	def v_height(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("height")
		else:
			return integer(self._imaging.size[1])


	def v_load(self, resource_id):
		self._imaging.load(self._application_id, resource_id.as_string)
		return v_mismatch

	def v_createfont(self, *arguments):
		adaptors=(("name", as_string), ("size", as_integer), ("color", as_string),
			("fontstyle", as_string), ("fontweight", as_string))
		self._imaging.create_font(**adapt(arguments, adaptors, name="createfont"))
		return v_mismatch

	def v_writetext(self, *arguments):
		adaptors=(("text", as_string), ("color", as_rgb), ("align", as_string),
			("ident", as_integer), ("textdecoration", as_string))
		self._imaging.write_text(**adapt(arguments, adaptors, require=1, name="writetext"))
		return v_mismatch

	def v_crop(self, x, y, w, h):
		self._imaging.crop(x.as_integer, y.as_integer, w.as_integer, h.as_integer)
		return v_mismatch

	def v_thumbnail(self, size):
		self._imaging.thumbnail(size.as_integer)
		return v_mismatch

	def v_savetemporary(self, label, *arguments):
		adaptors=(("format", as_string))
		id=self._imaging.save_temporary(self._application_id, None,
			label.as_string, **adapt(arguments, adaptors))
		return string(id)

	def v_save(self, name, *arguments):
		adaptors=(("format", as_string))
		id=self._imaging.save(self._application_id, name.as_string,
			**adapt(arguments, adaptors))
		return string(id)
