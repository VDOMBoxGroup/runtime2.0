
from builtins import object
import managers, security
from utils.exception import VDOM_exception

class VDOM_acl_manager(object):
	"""Defines acl-access and acl-storage methods"""

	def __init__(self):
		self.acl = managers.storage.read_object(VDOM_CONFIG["ACL-MANAGER-STORAGE-RECORD"])
		if(self.acl == None):
			self.acl = {}
			self.sync()

	def sync(self):
		"""Saves current state of manager in storage"""
		managers.storage.write_object_async(VDOM_CONFIG["ACL-MANAGER-STORAGE-RECORD"], self.acl)

	def __get_rule(self, object_id, username, access_type):
		"""
		Returns:
			True:   if allow-rule exists
			False:  if no such rule exists
		"""
		try:
			value = self.acl[object_id][username][access_type]
			return value
		except:
			return False	# No rule

	def __set_rule(self, object_id, username, access_type):
		""""""
		if object_id not in self.acl:
			self.acl[object_id] = {}
		if username not in self.acl[object_id]:
			self.acl[object_id][username] = {}
		self.acl[object_id][username][access_type] = 1
		self.sync()

	def __allow(self, object_id):
		# allow access if processing vdom request and accessing within the same application
		try:
			request = managers.request_manager.get_request()
		except:
			return True
		if hasattr(request, "request_type") and request.request_type in ["vdom", "action"]:
			app = request.application()
			if app and (app.id == object_id or app.objects.get(obj_id)):
				return True
			
	def __deny_protected(self,appid, access_type):
		# if (access_type == security.access_to_application) and managers.xml_manager.get_application(appid).protected == "1":
		# 	return True	
		if (access_type == security.access_to_application) and managers.memory.applications[appid].protected == "1":
			return True	
		
### PUBLIC INTERFACE ###
	def check_access(self, object_id, username, access_type):
		"""Returns True or False - have account "rule"-access to this object, also checks groups"""
		if "root" == username or "Admin" == username:
			return True
		tocheck = [username]
		checked = []
		while True:
			if len(tocheck) == 0:
				return False
			name = tocheck.pop(0)
			if self.__get_rule(object_id, name, access_type):
				return True
			checked.append(name)
			user = managers.user_manager.get_user_by_name(name)
			if user:
				for gr_name in user.member_of:
					if not gr_name in checked:
						tocheck.append(gr_name)

	def check_membership(self, username, groupname):
		tocheck = [groupname]
		checked = []
		user = managers.user_manager.get_user_by_name(username)
		while True:
			if len(tocheck) == 0:
				return False
			name = tocheck.pop(0)
			if name in user.member_of:
				return True
			checked.append(name)
			group = managers.user_manager.get_user_by_name(name)
			for gr_name in group.members:
				if managers.user_manager.get_group_by_name(gr_name) and gr_name not in checked:
					tocheck.append(gr_name)

	def add_access(self, object_id, username, access_type):
		"""Add new rule to object's ACL"""
		r = self.__set_rule(object_id, username, access_type)

	def remove_access(self, object_id, username, access_type):
		"""Delete rule from object's ACL"""
		try:
			self.acl[object_id][username].pop(access_type)
			self.sync()
		except: pass

	def session_user_has_access(self, object_id, access_type):
		"""Returns True or False - have account "rule"-access to this object"""
		if self.__allow(object_id):
			return True
		username = managers.request_manager.get_request().session().user
		if username:
			return self.check_access(object_id, username, access_type)
		return False

	def session_user_has_access2(self, app_id, object_id, access_type):
		"""Returns True or False - have account "rule"-access to this object, including inheritance"""
		if self.__allow(object_id):
			return True
		
		if self.__deny_protected(app_id,access_type):
			return False
		
		
		username = managers.request_manager.get_request().session().user
		if username:
			return self.check_access2(app_id, object_id, username, access_type)
		return False
	
	def session_user_can_manage(self):
		"""Returns True or False - if account in management group"""
		username = managers.request_manager.get_request().session().user
		if username:
			return self.check_membership(username, "ManagementLogin")
		return False		

	def grant_access_to_application(self, aid):
		"""grant access to application for the session user"""
		username = managers.request_manager.get_request().session().user
		if not username:
			return
		self.add_access(aid, username, security.create_object)
		self.add_access(aid, username, security.modify_object)
		self.add_access(aid, username, security.delete_object)
		self.add_access(aid, username, security.modify_structure)
		self.add_access(aid, username, security.inherit)

	def __check_access2_int(self, app_id, obj_id, username, access_type):
		"""checks access with inheritance"""
		if "vdombox" in [app_id, obj_id]:
			return self.check_access("vdombox", username, access_type)
		app = None
		try:
			app = managers.memory.applications.get(app_id)
		except:
			return False
		id_to_check = [app_id, "vdombox"]
		if app_id != obj_id:
			obj = app.objects.get(obj_id)
			if not obj: return False
			i = 0
			while obj:
				id_to_check.insert(i, obj.id)
				i += 1
				obj = obj.parent
		if self.check_access(id_to_check.pop(0), username, access_type):
			return True
		for ii in id_to_check:
			if security.inherit != access_type and self.__get_rule(ii, username, security.inherit) and self.check_access(ii, username, access_type):
				return True
		return False

	def check_access2(self, app_id, obj_id, username, access_type):
		"""checks access with inheritance"""
		if "root" == username or "Admin" == username:
			return True
		tocheck = [username]
		checked = []
		while True:
			if len(tocheck) == 0:
				return False
			name = tocheck.pop(0)
			if self.__check_access2_int(app_id, obj_id, name, access_type):
				return True
			checked.append(name)
			user = managers.user_manager.get_user_by_name(name)
			if user:
				for gr_name in user.member_of:
					if not gr_name in checked:
						tocheck.append(gr_name)
