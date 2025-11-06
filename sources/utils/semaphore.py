
from builtins import object
from threading import BoundedSemaphore


class VDOM_semaphore(object):

    def __init__(self, counter=1):
        self.__semaphore = BoundedSemaphore(counter)

    def lock(self):
        return self.__semaphore.acquire()

    def unlock(self):
        self.__semaphore.release()

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, extype, exvalue, traceback):
        self.unlock()
