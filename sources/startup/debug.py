
from builtins import object
import sys


LOGGING = None


def debug(message, tag="", console=None):
    sys.stdout.write("%s%s\n" % ("[%s]  " % tag if tag else "", message))


class DebugFile(object):

    def write(self, message):
        debug(message)
