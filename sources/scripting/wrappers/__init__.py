from __future__ import absolute_import

from .server import VDOM_server
from .application import VDOM_application
from .session import VDOM_session
from .log import VDOM_log
from .request import VDOM_request
from .response import VDOM_response
from .tasks import Task

# from obsolete_request import VDOM_obsolete_request
from .. import packages


server = VDOM_server()
application = VDOM_application()
log = VDOM_log()
session = VDOM_session()
request = VDOM_request()
response = VDOM_response()

# obsolete_request = VDOM_obsolete_request()

environment = {
    "log": log,
    "server": server,
    "request": request,
    "response": response,
    "session": session,
    "application": application,
    "Task": Task,
    # "obsolete_request": obsolete_request,
    "packages": packages
}
