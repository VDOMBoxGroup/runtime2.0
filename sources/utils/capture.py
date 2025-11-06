
from builtins import object
import sys
import os
import settings


class OutputCapture(object):

    _file = None
    _lines = ()

    def __init__(self, filename="capture.log"):
        self._filename = filename

    def __enter__(self):
        if self._file:
            raise Exception("Unable to re-enter")

        self._fullname = os.path.join(settings.TEMPORARY_LOCATION, self._filename)
        self._file = open(self._fullname, "w+")

        #HACK: doesn't fully understand how this work, but think it doesn't need fd, 
        # so comment for now, maybe need to rewrite Capture later

        # self._stdout = sys.stdout
        # self._stderr = sys.stderr

        # self._stdout_descriptor = self._stdout.fileno()
        # self._stderr_descriptor = self._stderr.fileno()

        # self._stdout_duplicate = os.dup(self._stdout_descriptor)
        # self._stderr_duplicate = os.dup(self._stderr_descriptor)

        # sys.stdout = self._file
        # sys.stderr = self._file

        # os.dup2(self._file.fileno(), self._stdout_descriptor)
        # os.dup2(self._file.fileno(), self._stderr_descriptor)

        return self

    def __exit__(self, extype, exvalue, extraceback):
        # os.dup2(self._stdout_duplicate, self._stdout_descriptor)
        # os.dup2(self._stderr_duplicate, self._stderr_descriptor)

        # os.close(self._stdout_duplicate)
        # os.close(self._stderr_duplicate)

        # sys.stdout = self._stdout
        # sys.stderr = self._stderr

        self._file.seek(0)
        self._lines = self._file.read().splitlines()

        self._file.close()
        self._file = None

        os.remove(self._fullname)

    lines = property(lambda self: self._lines)

    def write(self, message):
        if self._file:
            os.write(self._fullname, message + "\n")
        else:
            print(message)

    def flush(self):
        if self._file:
            os.fsync(self._fullname)
