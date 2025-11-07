
from logs import server_log
from utils.tracing import show_exception_trace
from . import lexemes, errors


class vregister(object):

	def __init__(self, names):
		self._names=names

	def get_names(self):
		return self._names

	names=property(get_names)


class vinitialregister(vregister):

	def __init__(self, names=None):
		self._names={} if names is None else names

	def import_names(self, module_name, alias=super):
		if alias is super:
			alias=module_name

		try:
			module=__import__("vscript.%s"%module_name).__dict__[module_name]
		except:
			caption="Unable to import %s module"%module_name
			show_exception_trace(caption=caption)
			raise errors.internal_error(caption)

		for name in dir(module):
			if name.startswith(lexemes.prefix):
				self._names.setdefault(name, alias)

	def get_names(self):
		self.import_names("exceptions", alias=None)
		self.import_names("library", alias=None)
		self.import_names("extensions")
		self.__class__=vregister
		return self._names
		
	names=property(get_names)


register=vinitialregister()
