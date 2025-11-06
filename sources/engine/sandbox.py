
from builtins import object
import sys
import time
from utils.exception import VDOM_exception


class Sandbox(object):

    def __init__(self, routine):
        self.__routine = routine

    def execute(self, timeout, arguments=None):
        self.deadline = time.time() + timeout
        sys.settrace(self.globaltrace)
        try:
            if arguments:
                return self.__routine(*arguments)
            else:
                return self.__routine()
        finally:
            sys.settrace(None)

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if event == 'line' and time.time() > self.deadline:
            sys.settrace(None)
            raise VDOM_exception("Routine not responding in given timeout")
        return self.localtrace


VDOM_sandbox = Sandbox
