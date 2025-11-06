
from builtins import object
class Singleton(object):

    __instance = None

    def __init__(self):
        if Singleton.__instance:
            raise Exception("Unable to create singleton again")
        Singleton.__instance = self


VDOM_singleton = Singleton
