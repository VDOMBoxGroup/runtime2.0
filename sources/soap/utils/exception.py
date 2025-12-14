"""exception module"""


class VDOM_exception(Exception):
    """base exception class"""

    def __init__(self, desc=""):
        self.__str = desc

    def __str__(self):
        return self.__str

    def __repr__(self):
        return self.__str


class VDOM_exception_missing_type(VDOM_exception):

    def __init__(self, type_id):
        VDOM_exception.__init__(self, "type \"%s\" not found" % type_id)


class VDOM_exception_missing_app(VDOM_exception):

    def __init__(self, app_id):
        VDOM_exception.__init__(self, "application \"%s\" not found" % app_id)


class VDOM_exception_parse(VDOM_exception):

    def __init__(self, desc=""):
        VDOM_exception.__init__(self, "parse error: %s" % desc)


class VDOM_exception_app_load(VDOM_exception_parse):

    def __init__(self, app_id, desc=""):
        VDOM_exception_parse.__init__(
            self, "application \"%s\" load error: %s" % (app_id, desc))


class VDOM_exception_type_load(VDOM_exception_parse):

    def __init__(self, type_id, desc=""):
        VDOM_exception_parse.__init__(
            self, "type \"%s\" load error: %s" % (type_id, desc))


class VDOM_exception_dup(VDOM_exception_parse):
    pass


class VDOM_exception_name(VDOM_exception):
    pass


class VDOM_exception_element(VDOM_exception):

    def __init__(self, name):
        VDOM_exception.__init__(self, "invalid element: \"%s\"" % name)


class VDOM_exception_sec(VDOM_exception):  # for security checks
    pass


class VDOM_exception_lic(VDOM_exception):  # for license checks
    pass


class VDOM_exception_param(VDOM_exception):
    pass


class VDOM_exception_handler(VDOM_exception):

    def __init__(self, desc, name):
        VDOM_exception.__init__(self, "handler '%s' error: %s" % (name, desc))


class VDOM_exception_restart(VDOM_exception):
    pass


class VDOM_exception_vdommem(VDOM_exception):

    def __init__(self, s):
        VDOM_exception.__init__(self, "VDOM memory error: " + s)


class VDOM_exception_file_access(VDOM_exception):

    def __init__(self, s):
        VDOM_exception.__init__(self, "VDOM file access error: " + s)


class VDOMServiceCallError(Exception):
    pass


class VDOMSecureServerError(VDOM_exception):
    pass


class VDOMDatabaseAccessError(VDOM_exception):
    def __init__(self, s):
        VDOM_exception.__init__(self, "Database request failed: " + s)


class VDOM_mailserver_invalid_index(VDOM_exception):

    def __init__(self, index):
        VDOM_exception.__init__(
            self, "Mailserver have no messaeg with index: \"%s\"" % index)


class VDOM_timeout_exception(BaseException):
    pass
