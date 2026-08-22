
import sys
from time import time
from threading import Thread, Event
import settings


class SmartThread(Thread):

    def __init__(self, name=None, quantum=None, condition=None, countdown=None, latter=False):
        super(SmartThread, self).__init__()

        # NOTE: init's name=... keyword seems not to work properly
        if name is not None:
            self.name = name

        self._quantum = quantum
        self._condition = condition
        self._countdown = countdown
        self._latter = latter
        self._stopping = None
        self._event = Event()

    quantum = property(lambda self: settings.QUANTUM if self._quantum is None else self._quantum)
    running = property(lambda self: not (self._stopping and
        (not callable(self._condition) or self._condition() or
            self._countdown and self.overtime > self._countdown)))
    stopping = property(lambda self: self._stopping)
    overtime = property(lambda self: None if self._stopping is None else max(0.0, time() - self._stopping))
    latter = property(lambda self: self._latter)

    def wait(self, seconds=None):
        quantum = settings.QUANTUM if self._quantum is None else self._quantum
        remainder = quantum if seconds is None else seconds
        while remainder > 0:
            timeout = min(quantum, remainder)
            if self._event.wait(timeout):
                break
            remainder -= timeout
        self._event.clear()

    def prepare(self):
        pass

    def cleanup(self):
        pass

    def work(self):
        pass

    def main(self):
        while self.running:
            self.wait(self.work())

    def run(self):
        try:
            try:
                self.prepare()
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
            self._event.set()

    def halt(self):
        self._condition = None
        if not self._stopping:
            self.stop()


VDOM_thread = SmartThread
