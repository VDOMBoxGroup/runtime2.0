


import sys
import signal
from threading import current_thread, enumerate as enumerate_threads
from errno import EINTR

import settings
from utils.tracing import format_thread_trace
from utils.profiling import profiler
import utils.threads

from .thread import SmartThread
from .daemon import SmartDaemon


SERVER_VARIABLE_NAME = "server"

SHUTDOWN_TIME_TO_NOTIFY = 3
SHUTDOWN_CONSECUTIVE_NOTIFICATIONS = True


def search(name):
    for thread in enumerate_threads():
        if not isinstance(thread, SmartThread):
            continue
        if thread.name == name:
            return thread


def wait(seconds=None):
    thread = current_thread()
    event = thread._event if isinstance(thread, SmartThread) else utils.threads.event
    remainder = settings.QUANTUM if seconds is None else seconds
    while remainder > 0:
        timeout = min(settings.QUANTUM, remainder)
        if event.wait(timeout):
            break
        remainder -= timeout
    event.clear()


def stop(condition, quantum=settings.QUANTUM):
    last, tries = None, 0
    while 1:
        threads = tuple(thread for thread in enumerate_threads()
            if isinstance(thread, SmartThread) and condition(thread))
        if not threads:
            break
        for thread in threads:
            if not thread.stopping:
                thread.stop()
        thread = threads[0]
        if thread == last:
            if tries == SHUTDOWN_TIME_TO_NOTIFY // quantum:
                sys.stdout.write("Waiting for %s:\n%s" %
                    (thread.name, format_thread_trace(thread, indent="    ")))
                if SHUTDOWN_CONSECUTIVE_NOTIFICATIONS:
                    tries = 0
        else:
            last, tries = thread, 0
        try:
            thread.join(quantum)
        except IOError as error:
            if error.errno != EINTR:
                raise
        tries += 1


def intercept(handler=None, ctrlc=None):
    if handler:
        def sigterm_handler(signum=None, frame=None):
            handler()
        signal.signal(signal.SIGTERM, sigterm_handler)
    if ctrlc:
        def sigint_handler(signum=None, frame=None):
            # sys.stdout.write("Interrupt from keyboard")
            ctrlc()
        signal.signal(signal.SIGINT, sigint_handler)


def shutdown(quantum=settings.QUANTUM):
    profiler.save(force=True)

    server = getattr(utils.threads.main, SERVER_VARIABLE_NAME, None)
    if server:
        server.stop()

    stop(lambda thread: not thread.latter and not isinstance(thread, SmartDaemon), quantum=quantum)
    stop(lambda thread: not thread.latter and isinstance(thread, SmartDaemon) and not thread.dependencies,
        quantum=quantum)
    stop(lambda thread: not isinstance(thread, SmartDaemon), quantum=quantum)
    stop(lambda thread: isinstance(thread, SmartDaemon) and not thread.dependencies, quantum=quantum)
    stop(lambda thread: True, quantum=quantum)
