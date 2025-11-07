
from weakref import ref
from threading import current_thread, Lock
import settings
from logs import console, log
from utils.tracing import format_exception_trace


LOGGING = None


class GenericOutput(object):

    def __init__(self, output):
        self._output = output
        self._buffer = []
        self._lock = Lock()

    def _write(self, message):
        raise NotImplementedError

    def write(self, message):
        with self._lock:
            try:
                most, last = message.rsplit("\n", 1)
            except ValueError:
                self._buffer.append(message)
            else:
                self._buffer.append(most)
                self._write("".join(self._buffer))
                self._buffer = [last]

    def flush(self):
        message = "".join(self._buffer)
        if message:
            self._write(message)
            self._buffer = []


class SeparateOutput(object):

    def __init__(self, output):
        self._output = output
        self._buffer = {}
        self._lock = Lock()

    def _write(self, message):
        raise NotImplementedError

    def write(self, message):

        def callback(weak):
            buffer = self._buffer.pop(weak, None)
            if buffer is not None:
                value = "".join(buffer)
                if value:
                    self._write("%s\n" % value)

        weak = ref(current_thread(), callback)

        # HACK: sometimes print output unexpected space
        if message == " " and weak not in self._buffer:
            return

        try:
            most, last = message.rsplit("\n", 1)
            most += "\n"
        except ValueError:
            try:
                self._buffer[weak].append(message)
            except KeyError:
                self._buffer[weak] = [message]
        else:
            try:
                buffer = self._buffer[weak]
            except KeyError:
                self._buffer[weak] = buffer = []
            else:
                buffer.append(most)
                most = "".join(buffer)

            with self._lock:
                self._write(most)
            buffer[:] = [last]

    def flush(self):
        thread = current_thread()
        try:
            rest = "".join(self._buffer[thread])
        except KeyError:
            pass
        else:
            if rest:
                with self._lock:
                    self._write(rest)
                self._buffer[thread] = []


class Output(SeparateOutput):

    def _write(self, message):
        if settings.LOGGING_OUTPUT and settings.LOGGER:
            log.write(message)
        else:
            console.write(message)


class ErrorOutput(SeparateOutput):

    def _write(self, message):
        if settings.LOGGING_OUTPUT and settings.LOGGER:
            log.error(message)
        else:
            console.error(message)
