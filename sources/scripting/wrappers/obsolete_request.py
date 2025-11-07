
import managers


class VDOM_obsolete_request(object):

	def __get_vdom(self):
		return managers.request_manager.current.vdom

	def __set_vdom(self, value):
		raise AttributeError

	vdom=property(__get_vdom, __set_vdom)

	def __get_session(self):
		return managers.request_manager.current.session()

	def __set_session(self, value):
		raise AttributeError

	session=property(__get_session, __set_session)

	#def set_user(self, name):
	#	self.session.value("username", name)

	def __get_arguments(self):
		return managers.request_manager.current.arguments().arguments()

	def __set_arguments(self, value):
		raise AttributeError

	arguments=property(__get_arguments, __set_arguments)

	def __get_files(self):
		return managers.request_manager.current.files

	def __set_files(self, value):
		raise AttributeError

	files=property(__get_files, __set_files)
	
	def __get_application_id(self):
		return managers.request_manager.current.app_id()

	def __set_application_id(self, value):
		raise AttributeError

	application_id=property(__get_application_id, __set_application_id)

	def __get_container_id(self):
		return managers.request_manager.current.container_id
	def __set_container_id(self, value):
		raise AttributeError
	container_id=property(__get_container_id, __set_container_id)

	def redirect(self, to):
		"""specify redirection to some url"""
		managers.request_manager.current.redirect(to)
		managers.engine.terminate()
		
	def terminate(self):
		"""Current request termination"""
		managers.engine.terminate()
		
	def application(self):
		return managers.request_manager.current.application()
	
	def __get_database_manager(self):
		return managers.database_manager

	def __set_database_manager(self, value):
		raise AttributeError

	database_manager=property(__get_database_manager, __set_database_manager)

	def __get_email_manager(self):
		return managers.email_manager

	def __set_email_manager(self, value):
		raise AttributeError

	email_manager=property(__get_email_manager, __set_email_manager)

	def __get_resource_manager(self):
		return managers.resource_manager

	def __set_resource_manager(self, value):
		raise AttributeError

	resource_manager=property(__get_resource_manager, __set_resource_manager)

	def __get_user_manager(self):
		return managers.user_manager

	def __set_user_manager(self, value):
		raise AttributeError

	user_manager=property(__get_user_manager, __set_user_manager)

	def __get_acl_manager(self):
		return managers.acl_manager

	def __set_acl_manager(self, value):
		raise AttributeError

	acl_manager=property(__get_acl_manager, __set_acl_manager)
	
	def __get_app_vhname(self):
		return managers.request_manager.current.app_vhname

	def __set_app_vhname(self, value):
		raise AttributeError

	app_vhname=property(__get_app_vhname, __set_app_vhname)

	def write(self, some, continue_render=False):
		managers.request_manager.current.write(some)
		if not continue_render:
			managers.engine.terminate()

	def write_handler(self, some):
		managers.request_manager.current.write_handler(some)

	def add_header(self, name, value):
		managers.request_manager.current.add_header(name, value)

	def add_client_action(self, id, data):
		managers.request_manager.current.add_client_action(id, data)

	def binary(self, b = None):
		return managers.request_manager.current.binary(b)

	def set_nocache(self):	
		return managers.request_manager.current.set_nocache()
	
	def send_file(self,filename, length, handler, content_type=None):
		return managers.request_manager.current.send_file(filename, length, handler, content_type)
	
	def __get_cookies(self):
		return managers.request_manager.current.cookies()

	def __set_cookies(self, value):
		raise AttributeError
	
	cookies=property(__get_cookies, __set_cookies)

	def __get_environment(self):
		return managers.request_manager.current.environment().environment()

	def __set_environment(self, value):
		raise AttributeError
	
	environment=property(__get_environment, __set_environment)
	