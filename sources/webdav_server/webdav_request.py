

from builtins import object
import managers
from http.cookies import BaseCookie
from request.arguments import VDOM_request_arguments
from memory.interface import VDOM_memory_interface

class VDOM_webdav_request(object):

	def __init__(self, environment, args={}):
		"""constructor"""
		self.__environment = environment
		self.app_vhname = self.__environment["HTTP_HOST"].split(":")[0].lower()
		vh = managers.virtual_hosts    
		self.__app_id = vh.get_site(self.app_vhname) or vh.get_def_site()
		try:
			self.__app = managers.memory.applications.get(self.__app_id)
		except:
			self.__app = None
		self.__cookies = BaseCookie(environment.get("HTTP_COOKIE"))
		# session
		sid = ""
		cookies = self.__cookies #.cookies()
		if "sid" in args:
			#debug("Got session from arguments "+str(args["sid"]))
			sid = args["sid"]
		elif "sid" in cookies:
			#debug("Got session from cookies "+cookies["sid"].value)
			sid = cookies["sid"].value
		if sid == "":
			sid = managers.session_manager.create_session()
			#debug("Created session " + sid)
		else:
			x = managers.session_manager[sid]
			if x is None:
				#debug("Session " + sid + " expired")
				sid = managers.session_manager.create_session()
		#debug("Session ID "+str(sid))
		cookies["sid"] = sid
		args["sid"] = sid
		self.__session = managers.session_manager[sid]
		self.__arguments = VDOM_request_arguments(args)
		self.vdom = VDOM_memory_interface(self)
		self.application_id = self.__app_id
		self.sid = sid
		self.method = self.__environment["REQUEST_METHOD"].lower()
		self.vdom = VDOM_memory_interface(self)
		self.args = self.__arguments

	def arguments(self, args = None):
		""" request arguments """
		return self.__arguments

	def application(self):
		"""get application object"""
		return self.__app

	def app_id(self):
		"""get application identifier"""
		return self.__app_id

	def session(self):
		"""session object"""
		return self.__session