


import sys
import traceback


def quote(string):
    return string.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\0", "\\\\0")


def get_type_name(target=None, target_type=None):
    if target_type is None:
        target_type = type(target)
    name, module = target_type.__name__, getattr(target_type, "__module__", "__builtin__")
    return name if module == "__builtin__" else "%s.%s" % (module, name)


def get_thread_traceback(thread):
    return traceback.extract_stack(sys._current_frames()[thread.ident])
