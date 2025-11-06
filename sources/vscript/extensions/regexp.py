
from builtins import str
import re
from .. import errors
from ..subtypes import boolean, generic, integer, string, true, false, v_empty
from ..variables import variant


class v_match(generic):

	def __init__(self, match):
		generic.__init__(self)
		self._match=match


	def v_firstindex(self, group=None, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property(u"firstindex")
		else:
			if group is None:
				start=self._match.start()
			else:
				group=group.as_simple
				if not isinstance(group, (integer, string)): raise errors.type_mismatch
				try: start=self._match.start(group.value)
				except IndexError: return v_empty
			return v_empty if start<0 else integer(start)

	def v_length(self, group=None, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property(u"length")
		else:
			if group is None:
				start, end=self._match.span()
			else:
				group=group.as_simple
				if not isinstance(group, (integer, string)): raise errors.type_mismatch
				try: start, end=self._match.span(group.value)
				except IndexError: return v_empty
			return v_empty if start<0 else integer(end-start)

	def v_value(self, group=None, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property(u"value")
		else:
			if group is None:
				value=self._match.group()
			else:
				group=group.as_simple
				if not isinstance(group, (integer, string)): raise errors.type_mismatch
				try: value=self._match.group(group.value)
				except IndexError: return v_empty
			return v_empty if value is None else string(str(value))
			

class v_matches(generic):

	def __init__(self, regexp, value):
		generic.__init__(self)
		self._regexp=regexp
		self._value=value
		self._cache=None


	def _get_collection(self):
		if self._cache is None:
			match=self._regexp.search(self._value)
			self._cache=[match] if match else []
		return self._cache

	_collection=property(_get_collection)


	def v_count(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("count")
		else:
			return integer(len(self._collection))

	def v_item(self, index, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("count")
		else:
			return v_match(self._collection[index.as_integer])


	def __iter__(self):
		match=self._regexp.search(self._value)
		if match is not None: yield variant(v_match(match))


class v_global_matches(v_matches):

	def _get_collection(self):
		if self._cache is None:
			self._cache=[match for match in self._regexp.finditer(self._value)]
		return self._cache

	_collection=property(_get_collection)


	def __iter__(self):
		for match in self._regexp.finditer(self._value):
			yield variant(v_match(match))


class v_regexp(generic):

	def __init__(self):
		generic.__init__(self)
		self._global=False
		self._ignorecase=False
		self._pattern=u""
		self._cache=None


	def _get_regex(self):
		if not self._cache:
			self._cache=re.compile(self._pattern, re.IGNORECASE if self._ignorecase else 0)
		return self._cache

	_regexp=property(_get_regex)


	def v_global(self, **keywords):
		if "let" in keywords:
			self._global=keywords["let"].as_boolean
		elif "set" in keywords:
			raise errors.object_has_no_property("global")
		else:
			return boolean(self._global)

	def v_ignorecase(self, **keywords):
		if "let" in keywords:
			self._ignorecase, self._cache=keywords["let"].as_boolean, None
		elif "set" in keywords:
			raise errors.object_has_no_property("ignorecase")
		else:
			return boolean(self._ignorecase)

	def v_pattern(self, **keywords):
		if "let" in keywords:
			self._pattern, self._cache=keywords["let"].as_string, None
		elif "set" in keywords:
			raise errors.object_has_no_property("pattern")
		else:
			return string(self._pattern)


	def v_execute(self, value):
		return v_global_matches(self._regexp, value.as_string) if self._global else v_matches(self._regexp, value.as_string)

	def v_replace(self, value, replace_string):
		return string(str(self._regexp.sub(replace_string.as_string, value.as_string, 0 if self._global else 1)))

	def v_test(self, value):
		return boolean(false if self._regexp.search(value.as_string) is None else true)
