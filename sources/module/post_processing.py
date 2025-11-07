"""url post processing module"""

import sys, re, traceback

from .module import VDOM_module_post, VDOM_module
import managers

rexp = re.compile(r"VDOMURL\((.*?)\)", re.IGNORECASE)

class VDOM_module_url(VDOM_module_post):
	"""url post processing module class"""

	def run(self, data):
		"""process all URLs"""
		result = VDOM_module_post.run(self, data)
		parts = rexp.split(result)

		request = managers.request_manager.get_request()

		idx = 0
		result = ""
		for part in parts:
			if idx % 2:
				# here need to modify url
				if -1 == part.find("?"):
					# no parameters
					part += ("?sid=" + request.sid)
				else:
					part += ("&sid=" + request.sid)
			result += part
			idx += 1

		return result


class VDOM_post_processing(VDOM_module):
	"""class that performs post processing using all modules above"""

	post_modules = [
		"VDOM_module_url"
	]

	def run(self, data):
		"""do post processing"""
		result = data
		for cls_name in VDOM_post_processing.post_modules:
			try:
				exec("module = " + cls_name + "()")
				if module:
					result = module.run(result)
			except:
				debug(("Post processing error %s, %s") % (cls_name, str(sys.exc_info()[0])))
				traceback.print_exc(file=debugfile)
		return result
