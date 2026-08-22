
def exception_message(error):
    """What "error.message" used to give in Python 2.

    Python 3 removed BaseException.message, so "except Exception as ex: ...
    ex.message" raises AttributeError from inside the handler and destroys the
    error it was meant to report - the failure then surfaces somewhere else, or
    not at all.

    A plain str(error) is not enough: several exception classes here and in the
    application set self.message themselves - vscript.errors, scripting.object,
    memory.vdomxml and memory.vdomjson among them - and some callers use that
    value as a lookup key. So the attribute wins where it exists, and str()
    covers the rest, which for a single-argument exception is the same string
    Python 2 gave. That makes this a safe replacement at every call site.
    """
    message = getattr(error, "message", None)
    return message if message is not None else str(error)


class VDOM_exception(Exception):

    def __init__(self, desc=""):
        self.__str = desc

    def __str__(self):
        return self.__str

    def __repr__(self):
        return self.__str


class VDOM_exception_element(VDOM_exception): # SOAP

    def __init__(self, name):
        VDOM_exception.__init__(self, "invalid element: \"%s\"" % name)


class VDOM_exception_param(VDOM_exception): # SOAP
    pass


class VDOMSecurityError(VDOM_exception):  # for security checks
    pass


class VDOM_exception_file_access(VDOM_exception): # scripting

    def __init__(self, s):
        VDOM_exception.__init__(self, "VDOM file access error: " + s)


class VDOM_mailserver_invalid_index(VDOM_exception):

    def __init__(self, index):
        VDOM_exception.__init__(self, "Mailserver have no messaeg with index: \"%s\"" % index)


class VDOMServiceCallError(Exception):
    pass


class VDOMSecureServerError(VDOM_exception):
    pass


class VDOMDatabaseAccessError(VDOM_exception):
    def __init__(self, s):
        VDOM_exception.__init__(self, "Database request failed: " + s)


VDOM_exception_sec = VDOMSecurityError
