"""
User class module
"""
from builtins import object
from hashlib import md5

class VDOM_user(object):
	"""User class defines behaviour of account"""

	def __init__(self):
		self.id = ""
		self.login = ""
		self.password = ""
		self.first_name = ""
		self.last_name = ""
		self.email = ""
		self.security_level = ""
		self.member_of = []	# list of group names
		self.system = False

	def get_password_hash(self):
		return md5(self.password).hexdigest()