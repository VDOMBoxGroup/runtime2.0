
import managers


class VDOM_headers(object):

    def __getitem__(self, name):
        return managers.request_manager.current.headers_out().headers()[name.lower()]

    def __setitem__(self, name, value):
        managers.request_manager.current.headers_out().headers()[name.lower()] = value

    def get(self, name, default=None):
        return managers.request_manager.current.headers_out().headers().get(name.lower(), default)

    def keys(self):
        return managers.request_manager.current.headers_out().headers().keys()

    def __contains__(self, name):
        return name.lower() in managers.request_manager.current.headers_out().headers()

    def __iter__(self):
        return iter(managers.request_manager.current.headers_out().headers())


class VDOM_shared_variables(object):
    def __getitem__(self, name):
        return managers.request_manager.current.shared_variables.get(name)

    def __setitem__(self, name, value):
        managers.request_manager.current.shared_variables[name] = value

    def __delitem__(self, name):
        del managers.request_manager.current.shared_variables[name]

    def clear(self):
        managers.request_manager.current.shared_variables.clear()

    def keys(self):
        return managers.request_manager.current.shared_variables.keys()

    def copy(self):
        return managers.request_manager.current.shared_variables.copy()


class VDOM_response(object):

    def __init__(self):
        self._headers = VDOM_headers()
        self._shared_vars = VDOM_shared_variables()

    def _get_cookies(self):
        return managers.request_manager.current.response_cookies()

    def _get_binary(self):
        return managers.request_manager.current.binary()

    def _set_binary(self, value):
        managers.request_manager.current.binary(b=value)

    def _get_whole_answer(self):
        return managers.request_manager.current.wholeAnswer

    def _set_whole_answer(self, value):
        managers.request_manager.current.wholeAnswer = value

    def _set_nocache(self, value):
        if value:
            managers.request_manager.current.set_nocache()

    headers = property(lambda self: self._headers)
    cookies = property(_get_cookies)
    binary = property(_get_binary, _set_binary)
    nocache = property(fset=_set_nocache)
    result = property(_get_whole_answer, _set_whole_answer)
    shared_variables = property(lambda self: self._shared_vars)

    def write(self, value, continue_render=False):
        if isinstance(value, basestring):
            managers.request_manager.current.write(value)
        elif hasattr(value, "read"):
            managers.request_manager.current.write_handler(value)
        else:
            raise ValueError
        if not continue_render:
            managers.engine.terminate()

    def send_file(self, filename, length, handler, content_type=None, cache_control=True, continue_render=False):
        # return managers.request_manager.current.send_file(filename, length, handler, content_type)
        managers.request_manager.current.send_file(filename, length, handler, content_type, cache_control)
        if not continue_render:
            managers.engine.terminate()

    def redirect(self, target, continue_render=False):
        # managers.request_manager.current.redirect(target)
        # managers.engine.terminate()
        managers.request_manager.current.redirect(target)
        if not continue_render:
            managers.engine.terminate()

    def terminate(self):
        managers.engine.terminate()

    def send_htmlcode(self, code=200):
        managers.request_manager.current.send_htmlcode(code)
        managers.engine.terminate()
