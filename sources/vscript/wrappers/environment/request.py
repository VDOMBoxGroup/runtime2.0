
from builtins import str
import managers
from utils.file_argument import File_argument
from ... import errors
from ...subtypes import integer, generic, string, binary, v_empty, v_mismatch, v_nothing
from ...variables import variant
from ...conversions import pack, unpack


class v_cookiescollection(generic):

    def __call__(self, name, **keywords):
        if "let" in keywords:
            managers.request_manager.current.cookies()[name.as_string.encode("utf-8")]= \
                            keywords["let"].as_string.encode("utf-8")
        elif "set" in keywords:
            raise errors.object_has_no_property
        else:
            try:
                return string(managers.request_manager.current.cookies()[name.as_string.encode("utf-8")] \
                                              .value.decode("utf-8"))
            except KeyError:
                return v_empty

    def __iter__(self):
        for cookie in managers.request_manager.current.cookies().cookies():
            yield variant(string(str(cookie)))


class v_argumentscollection(generic):

    def __call__(self, name, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property
        else:
            try:
                value=managers.request_manager.current.arguments().arguments()[name.as_string][0]
            except KeyError:
                return v_empty
            try: 			
                if isinstance(value, str):
                    return string(str(value.decode("utf-8", "ignore")))
                else:
                    return string(str(value))

            except UnicodeDecodeError: 
                return binary(value)

    def __iter__(self):
        for argument in managers.request_manager.current.arguments().arguments():
            yield variant(string(str(argument)))


class v_file(generic):

    def __init__(self, file_argument):
        self._file_argument=file_argument

    def v_name(self, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property("name")
        else:
            return string(str(self._file_argument[1]))

    def v_contents(self, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property("contents")
        else:
            return binary(str(self._file_argument[0]))

class v_filescollection(generic):

    def __call__(self, name, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property
        else:
            try:
                value=managers.request_manager.current.arguments().arguments()[name.as_string]
            except KeyError:
                return v_nothing
            if isinstance(value, File_argument):
                return v_file(value)
            else:
                return v_nothing

    def __iter__(self):
        for argument, value in managers.request_manager.current.arguments().arguments().items():
            if isinstance(value, File_argument):
                yield variant(string(str(argument)))


class v_servervariablescollection(generic):

    variable_table={
            u"ALL_HTTP": lambda self: string(u"\n".join([u"HTTP_%s=%s"%(str(name.upper()) \
                                                                            .replace(u"-", u"_"), str(value)) for name, value in list(managers.request_manager \
                                                                                  .get_request().headers().headers().items())])),
            u"RAW_HTTP": lambda self: string(u"\n".join([u"%s=%s"%(str(name), \
                                                                   str(value)) for name, value in list(managers.request_manager.current.headers() \
                                                                                                       .headers().items())])),
            u"AUTH_PASSWORD": lambda self: v_empty,
            u"AUTH_TYPE": lambda self: string(u"Basic"),
            u"AUTH_USER": lambda self: string(str(managers.request_manager.current.session().user)),
            u"CONTENT_LENGTH": lambda self: v_empty,
            u"CONTENT_TYPE": lambda self: v_empty,
            u"GATEWAY_INTERFACE": lambda self: string(str(managers.request_manager \
                                                        .get_request().environment().environment()["GATEWAY_INTERFACE"])),
            u"QUERY_STRING": lambda self: string(str(managers.request_manager \
                                                     .get_request().environment().environment()["QUERY_STRING"])),
            u"LOCAL_ADDR": lambda self: v_empty,
            u"REMOTE_ADDR": lambda self: string(str(managers.request_manager \
                                                    .get_request().environment().environment()["REMOTE_ADDR"])),
            u"REMOTE_HOST": lambda self: v_empty,
            u"REMOTE_PORT": lambda self: string(str(managers.request_manager \
                                                    .get_request().environment().environment()["REMOTE_PORT"])),
            u"REMOTE_USER": lambda self: string(str(managers.request_manager.current.session().user)),
            u"REQUEST_METHOD": lambda self: string(str(managers.request_manager \
                                                       .get_request().environment().environment()["REQUEST_METHOD"])),
            u"SCRIPT_NAME": lambda self: string(str(managers.request_manager \
                                                    .get_request().environment().environment()["SCRIPT_NAME"])),
            u"SERVER_NAME": lambda self: string(str(managers.request_manager \
                                                    .get_request().environment().environment()["SERVER_NAME"])),
            u"SERVER_PORT": lambda self: string(str(managers.request_manager \
                                                    .get_request().environment().environment()["SERVER_PORT"])),
            u"SERVER_PORT_SECURE": lambda self: integer(0),
            u"SERVER_PROTOCOL": lambda self: string(str(managers.request_manager \
                                                        .get_request().environment().environment()["SERVER_PROTOCOL"])),
            u"SERVER_SOFTWARE": lambda self: string(str(managers.request_manager \
                                                        .get_request().environment().environment()["SERVER_SOFTWARE"])),
            u"UNENCODED_URL": lambda self: string(str(managers.request_manager \
                                                    .get_request().environment().environment()["SCRIPT_NAME"]+managers.request_manager \
                    .get_request().environment().environment()["QUERY_STRING"])),
            u"SCRIPT_NAME": lambda self: string(str(managers.request_manager \
                                                .get_request().environment().environment()["SCRIPT_NAME"]))}

    def __call__(self, name, **keywords):
        name=name.as_string.upper()
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property
        elif name.startswith(u"HEADER_"):
            return string(str(managers.request_manager.current.headers().headers()[name[7:]]))
        elif name.startswith(u"HTTP_"):
            return string(str(managers.request_manager.current.headers().headers()[name[5:].replace(u"_", u"-")]))
        else:
            return self.variable_table[name](self)

    def __iter__(self):
        for name in self.variable_table:
            yield variant(string(str(name)))
        for name in managers.request_manager.current.headers().headers():
            yield variant(string(u"HEADER_%s"%name))
            yield variant(string(u"HTTP_%s"%name.upper().replace(u"-", u"_")))


class v_parameterscollection(generic):

    def __call__(self, index, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property
        else:
            try:
                index, parameters=index.as_integer, managers.request_manager \
                                    .get_request().arguments().arguments()["xml_data"][0]
                if isinstance(parameters, list):
                    return string(str(parameters[index]))
                else:
                    return v_empty if index else string(str(parameters))
            except KeyError:
                return v_empty

    def __iter__(self):
        try:
            parameters=managers.request_manager.current.arguments().arguments()["xml_data"][0]
        except KeyError:
            return
        if isinstance(parameters, list):
            for parameter in parameters: yield variant(string(str(parameter)))
        else:
            yield variant(string(str(parameters)))


class v_sharedvariablescollection(generic):

    def __call__(self, name, **keywords):
        if "let" in keywords:
            managers.request_manager.current.shared_variables[name.as_string]=unpack(keywords["let"].as_simple)
        elif "set" in keywords:
            raise errors.object_has_no_property
        else:
            try:
                return pack(managers.request_manager.current.shared_variables[name.as_string])
            except KeyError:
                return v_empty

    def __iter__(self):
        for name in managers.request_manager.current.shared_variables:
            yield variant(string(str(name)))


class v_request(generic):

    def __init__(self):
        self._cookies=v_cookiescollection()
        self._arguments=v_argumentscollection()
        self._files=v_filescollection()
        self._servervariables=v_servervariablescollection()
        self._parameters=v_parameterscollection()
        self._sharedvariables=v_sharedvariablescollection()

    def v_cookies(self, name=None, **keywords):
        if name is None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("cookies")
            else:
                return self._cookies
        else:
            return self._cookies(name, **keywords)

    def v_arguments(self, name=None, **keywords):
        if name is None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("arguments")
            else:
                return self._arguments
        else:
            return self._arguments(name, **keywords)

    def v_form(self, name=None, **keywords):
        if name is None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("form")
            else:
                return self._arguments
        else:
            return self._arguments(name, **keywords)

    def v_files(self, name=None, **keywords):
        if name is None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("form")
            else:
                return self._files
        else:
            return self._files(name, **keywords)

    def v_querystring(self, name=None, **keywords):
        if name is None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("querystring")
            else:
                return self._arguments
        else:
            return self._arguments(name, **keywords)

    def v_servervariables(self, name=None, **keywords):
        if name is None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("servervariables")
            else:
                return self._servervariables
        else:
            return self._servervariables(name, **keywords)

    def v_parameters(self, index=None, **keywords):
        if index is None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("parameters")
            else:
                return self._parameters
        else:
            return self._parameters(index, **keywords)

    def v_sharedvariables(self, name=None, **keywords):
        if name is None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("sharedvariables")
            else:
                return self._sharedvariables
        else:
            return self._sharedvariables(name, **keywords)
