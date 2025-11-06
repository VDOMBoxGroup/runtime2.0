"""python handler module"""

import sys
from .module import VDOM_module
from utils.exception import VDOM_exception
import admin # noqa


class VDOM_module_python(VDOM_module):
    """process python scripts"""

    def run(self, request):
        """run python script"""
        script_name = request.environment().environment()["SCRIPT_NAME"]
        if script_name.startswith("/"):
            script_name = script_name[1:]
        script_name = script_name.split(".")[0]
        script_name = "_".join(script_name.split("-"))
        request.add_header("Content-Type", "text/html")
        try:
            if script_name.isalnum():
                exec("admin." + script_name + ".run(request)")
        except VDOM_exception as e:
            if e.message != "Authentication failed": #TODO: replace it with VDOM_exception_auth_failed
                # traceback.print_exc(file=debugfile)
                sys.excepthook(*sys.exc_info())
            debug("Error: %s" % e.message)
        except Exception as e:
            debug("Error: %s" % e)
            # traceback.print_exc(file=debugfile)
            sys.excepthook(*sys.exc_info())
        return request.output()
