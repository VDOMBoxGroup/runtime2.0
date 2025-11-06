from __future__ import absolute_import

from builtins import str
import sys

from .headers import VDOM_dictionary

class VDOM_cookies(VDOM_dictionary):
	"""Server cookies"""

	def __init__(self, headers):
		""" Constructor """
		self.dict = {}
		if "cookie" in headers:
			cookie_list = headers["cookie"].split(';')
			for item in cookie_list:
				items = item.split('=')
				if len(items) == 2:
					self.dict[str(items[0]).strip().lower()] = str(items[1]).strip()

	def cookies(self, cookies=None):
		"""access cookies dictionary"""
		return self.dict

	def cookie(self, name, value=None, push=True):
		"""read or push/add cookie"""
		return self.value(name, value, push)

	def get_string(self):
		"""convert dictionary to the header string"""
		#return 
		string = ""
		for c in list(self.dict.keys()):
			if string != "": string += "; "
			string += ("%s=%s" % (c, self.dict[c]))
		return string
