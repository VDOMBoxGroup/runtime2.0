
import sys
from time import time
import settings
import utils.threads
from utils.singleton import Singleton
from .auxiliary import SERVER_VARIABLE_NAME


class SmartServer(Singleton):

    def __init__(self, quantum=None, condition=None, countdown=None):
        super(SmartServer, self).__init__()
        self._quantum = quantum
        self._condition = condition
        self._countdown = countdown
        self._stopping = None
        setattr(utils.threads.main, SERVER_VARIABLE_NAME, self)

    running = property(lambda self: not (self._stopping and
        (not callable(self._condition) or self._condition() or self.overtime > self._countdown)))
    stopping = property(lambda self: self._stopping)
    overtime = property(lambda self: None if self._stopping is None else max(0.0, time() - self._stopping))
    latter = property(lambda self: self._latter)

    def wait(self, seconds=None):
        quantum = settings.QUANTUM if self._quantum is None else self._quantum
        remainder = quantum if seconds is None else seconds
        while remainder > 0:
            timeout = min(quantum, remainder)
            if utils.threads.event.wait(timeout):
                break
            remainder -= timeout
        utils.threads.event.clear()

    def prepare(self):
        pass

    def cleanup(self):
        pass

    def work(self):
        pass

    def main(self):
        while self.running:
            self.wait(self.work())

    def start(self, on_ready= None):
        try:
            try:
                self.prepare()
                if on_ready:
                    on_ready()
                self.main()
            except Exception:
                sys.excepthook(*sys.exc_info())
        finally:
            try:
                self.cleanup()
            except Exception:
                sys.excepthook(*sys.exc_info())

    def stop(self):
        if not self._stopping:
            self._stopping = time()
            utils.threads.event.set()

    def halt(self):
        self._condition = None
        if not self._stopping:
            self.stop()


VDOM_server = SmartServer
