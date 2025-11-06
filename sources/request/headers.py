
from builtins import str
from builtins import object
class VDOM_dictionary(object):
	"""base class for headers and cookies"""

	def __init__(self, arguments):
		"""constructor"""
		self.dict = {}

	def remove(self, name):
		"""remove key"""
		n = name.lower()
		if n in self.dict:
			del(self.dict[n])

	def push(self, name, value=None):
		"""replace key"""
		n = name.lower()
		if value:
			self.dict[n] = value
			return self.dict[n]
		if n in self.dict:
			return self.dict[n]
		return None

	def add(self, name, value=None):
		"""add value to the existing key or create a new one"""
		n = name.lower()
		if value:
			val = ""
			if n in self.dict: val = self.dict[n]
			if val == "": return self.push(n, value)
			val += (";%s" %  str(value))
			return self.push(n, val)
		return self.push(n)

	def value(self, name, value=None, push=True):
		"""common value management method"""
		if push: return self.push(name, value)
		return self.add(name, value)

	def __contains__(self, x):
		return x.lower() in self.dict


class VDOM_headers(VDOM_dictionary):
	"""Server headers"""

	def __init__(self, arguments):
		""" Constructor """
		self.dict = arguments

	def headers(self, headers=None):
		"""access headers dictionary"""
		return self.dict

	def header(self, name, value=None, push=True):
		"""read or push/add header"""
		return self.value(name, value, push)
