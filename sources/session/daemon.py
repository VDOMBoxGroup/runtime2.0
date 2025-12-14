
import sys
from utils.threads import VDOM_daemon


class VDOM_session_cleaner(VDOM_daemon):

    name = "Session Cleaner"

    def __init__(self, manager):
        VDOM_daemon.__init__(self, name=VDOM_session_cleaner.name)
        self.__manager = manager

    def prepare(self):
        sys.stdout.write("Start %s\n" % self.name)

    def cleanup(self):
        sys.stdout.write("Stop %s\n" % self.name)
        self.__manager.work()

    def work(self):
        self.__manager.work()
