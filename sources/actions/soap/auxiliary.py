
from builtins import str
from hashlib import md5
from time import time

# from SOAPpy import faultType
from suds import WebFault

from utils.parsing import VALUE, Parser, ParsingException
from utils.remote_api import VDOMServiceSingleThread, VDOMServiceCallError
from ..auxiliary import show


class SOAPError(Exception):
    pass


def builder(parser):
    def Error():
        message = yield VALUE
        raise SOAPError(message)
    return Error


def soap_query(caption, address, user, password, method, *arguments, **keywords):
    application = keywords.get("application")

    start = time()
    show("%s %s" % (caption, address))

    try:
        connection = VDOMServiceSingleThread.connect(address, user, md5(password).hexdigest(), application)
        response = connection.remote(
            method,
            params=(list(arguments) if arguments else None),
            no_app_id=not application)
    except faultType as error:
        raise SOAPError(error.faultstring)
    except VDOMServiceCallError as error:
        raise SOAPError(error)
    except IOError as error:
        raise SOAPError(getattr(error, "strerror", None) or getattr(error, "message", None) or str(error))

    duration = time() - start

    try:
        Parser(builder=builder, notify=True, supress=True).parse(
            response.encode("utf8") if isinstance(response, str) else response)
    except ParsingException as error:
        raise SOAPError("Unable to parse response: %s" % error)

    show("done in %.3f s" % duration)
    return response
