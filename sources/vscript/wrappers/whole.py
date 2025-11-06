
import sys, hashlib, xml.dom.minidom
import managers
from utils.remote_api import VDOMServiceSingleThread as VDOM_service
from .. import errors
from ..subtypes import array, boolean, generic, string, true, false, error, v_empty


class whole_error(errors.generic):

	def __init__(self, message, line=None):
		errors.generic.__init__(self,
			message=u"WHOLE error: %s"%message,
			line=line)

class whole_connection_error(whole_error):

	def __init__(self, url, login, message, line=None):
		whole_error.__init__(self,
			message=u"Unable to connect to %s as %s (%s)"%(url, login, message),
			line=line)

class whole_no_connection_error(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"No connection are established",
			line=line)

class whole_remote_call_error(whole_error):

	def __init__(self, url, message, line=None):
		whole_error.__init__(self,
			message=u"Unable to make remote call to %s (%s)"%(url, message),
			line=line)

class whole_incorrect_response_error(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"Incorrect response",
			line=line)

class whole_no_api_error(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"Application has no API support",
			line=line)

class whole_no_application_error(whole_error):

	def __init__(self, line=None):
		whole_error.__init__(self,
			message=u"Application not found",
			line=line)


v_wholeerror=error(whole_error)
v_wholeconnectionerror=error(whole_connection_error)
v_wholenoconnectionerror=error(whole_no_connection_error)
v_wholeremotecallerror=error(whole_remote_call_error)
v_wholeincorrectresponseerror=error(whole_incorrect_response_error)
v_wholenoapierror=error(whole_no_api_error)
v_wholenoapplicationerror=error(whole_no_application_error)


def search_for_application_id(name, string):
	document, name=xml.dom.minidom.parseString(string.encode("utf-8")), name.lower()
	try:
		for application_node in document.getElementsByTagName("Applications")[0].getElementsByTagName("Application"):
			if u"".join(node.data for node in application_node.getElementsByTagName("Name")[0].childNodes if node.nodeType==node.TEXT_NODE).lower()==name:
				return u"".join(node.data for node in application_node.getElementsByTagName("Id")[0].childNodes \
					if node.nodeType==node.TEXT_NODE)
		return None
	except KeyError:
		raise whole_incorrect_response_error

def search_for_api_container(string):
	document=xml.dom.minidom.parseString(string.encode("utf-8"))
	try:
		for object_node in document.getElementsByTagName("Objects")[0].getElementsByTagName("Object"):
			if object_node.attributes["Name"].nodeValue.lower()=="api":
				return object_node.attributes["ID"].nodeValue
		return None
	except KeyError:
		raise whole_incorrect_response_error

def search_for_action_names(string):
	document=xml.dom.minidom.parseString(string.encode("utf-8"))
	try:
		return [action_node.attributes["Name"].nodeValue \
			for action_node in document.getElementsByTagName("ServerActions")[0].getElementsByTagName("Action")]
	except KeyError:
		raise whole_incorrect_response_error


class v_wholeapplication(generic):

	def __init__(self, url, service, application):
		self._url=url
		self._service=service
		self._application=application
		try:
			result=self._service.remote("get_top_objects", None, False)
		except Exception as error:
			raise whole_remote_call_error(self._url, error)
		self._container=search_for_api_container(result)
		if not self._container:
			raise whole_no_api_error


	def v_application(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("application")
		else:
			if not self._service:
				raise whole_no_connection_error
			return string(self._application)

	def v_container(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("container")
		else:
			return string(self._container) if self._container else v_empty

	def v_actions(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("actions")
		else:
			if not self._service:
				raise whole_no_connection_error
			try:
				result=self._service.remote("get_server_actions_list", [self._container], False)
			except Exception as error:
				raise whole_remote_call_error(self._url, error)
			names=search_for_action_names(result)
			return array([string(name) for name in names if name.lower()!="onload"])


	def v_invoke(self, name, *arguments):
		if not self._service:
			raise whole_no_connection_error
		try:
			if arguments:
				if len(arguments)==1:
					parameter=arguments[0].as_string
				else:
					parameter=[argument.as_string for argument in arguments]
			else:
				parameter=None
			result=self._service.call(self._container, name.as_string, parameter)
		except Exception as error:
			raise whole_remote_call_error(self._url, "%s: %s"%(type(error), error)).with_traceback(sys.exc_info()[2])
		return string(result)


class v_wholeconnection(generic):
	
	def __init__(self):
		self._service=None


	def v_isconnected(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("isconnected")
		else:
			if not self._service: return boolean(false)
			try: self._service.remote("keep_alive", None, True)
			except: return boolean(false)
			return boolean(true)


	def v_open(self, url, login, password):
		self._url=url.as_string
		self._login=login.as_string
		self._password=hashlib.md5(password.as_string).hexdigest()
		try:
			self._service=VDOM_service.connect(self._url, self._login, self._password, None)
		except Exception as error:
			raise whole_connection_error(self._url, self._login, error)

	def v_close(self):
		self._service=None

	def v_applications(self, name, container=None, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.object_has_no_property("applications")
		else:
			if not self._service:
				raise whole_no_connection_error
			try:
				result=self._service.remote("list_applications", None, True)
			except Exception as error:
				raise whole_remote_call_error(self._url, error)
			application=search_for_application_id(name.as_string, result)
			if not application: raise whole_no_application_error
			try:
				service=VDOM_service.connect(self._url, self._login, self._password, application)
			except Exception as error:
				raise whole_connection_error(self._url, self._login, error)
			return v_wholeapplication(self._url, service, application)
