"""
Virtual hosting class. Allows to map hostnames and application identifiers.
"""

import managers

class VDOM_vhosting:

	def __init__(self):
		"""constructor"""
		self.__vhosting_data = {}
		ret = managers.storage.read_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"])
		if ret:
			self.__vhosting_data = ret

	#def __del__(self): #Not needed anymore - we sync immediately after making changes
	#	"""destructor"""
	#	self.sync()

	def sync(self):
		"""save the object into storage"""
		managers.storage.write_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"], self.__vhosting_data)

	def set_site(self, site, app_id):
		"""add/remove new site in virtual hosting or change it's id"""
		if app_id:
			self.__vhosting_data[site] = app_id
		elif site in self.__vhosting_data:
			del self.__vhosting_data[site]
		self.sync()

	def get_sites(self):
		"""get the list of registered sites"""
		return self.__vhosting_data.keys()

	def get_site(self, site):
		"""get site identifier by name"""
		if site and site in self.__vhosting_data:
			return self.__vhosting_data[site]
		return None

	def set_def_site(self, app_id):
		if app_id:
			self.__vhosting_data[0] = app_id
		elif 0 in self.__vhosting_data:
			del self.__vhosting_data[0]
		self.sync()

	def get_def_site(self):
		if 0 in self.__vhosting_data:
			return self.__vhosting_data[0]
		elif '0' in self.__vhosting_data:
			return self.__vhosting_data['0']
		return None

	def get_app_names(self, appid):
		r = []
		for name in self.__vhosting_data:
			if self.__vhosting_data[name] == appid:
				r.append(name)
		return r
