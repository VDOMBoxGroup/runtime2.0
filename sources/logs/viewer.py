
from builtins import range
from builtins import object
import sys
import errno
import socket
import settings
import logs
from . import actions
from .packer import create_packer


VIEWER_TIMEOUT = 3.0


class LogViewerStream(object):

    def __init__(self, socket):
        self._socket = socket

    def read(self, size):
        value = self._socket.recv(size)
        if len(value) == size:
            return value
        chunks, left = [value], size - len(value)
        while left:
            chunk = self._socket.recv(left)
            if not chunk:
                raise socket.error(errno.EIO, "No data available")
            chunks.append(chunk)
            left -= len(chunk)
        return "".join(chunks)

    def write(self, data):
        offset = self._socket.send(data)
        while offset < len(data):
            offset += self._socket.send(data[offset:])


class LogViewer(object):

    _assume_request = create_packer("BBS")
    _update_request = create_packer("BB")
    _read_request = create_packer("BBLL")

    _update_response = create_packer("L")
    _read_response = create_packer("L")

    def __init__(self, log, address=settings.LOGGING_ADDRESS, port=settings.LOGGING_PORT, timeout=VIEWER_TIMEOUT):
        self._log = log
        self._formatter = None
        self._address = address
        self._port = port
        self._timeout = timeout
        self._stream = None

    def connect(self):
        logs.console.write("Connect to %s:%d" % (self._address, self._port))
        viewer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        viewer_socket.settimeout(self._timeout)
        viewer_socket.connect((self._address, self._port))
        self._stream = LogViewerStream(viewer_socket)
        self._assume_request.pack_into(self._stream, actions.ASSUME, 0, self._log.name)

    def update(self):
        if self._stream is None:
            self.connect()
        self._update_request.pack_into(self._stream, actions.UPDATE, 0)
        return self._update_response.unpack_from(self._stream)[0]

    def read(self, start=0, count=sys.maxsize, format=False, into=None):
        if self._stream is None:
            self.connect()
        self._read_request.pack_into(self._stream, actions.READ, 0, start, count)
        count, = self._read_response.unpack_from(self._stream)
        lines = (self._log.packer.unpack_from(self._stream) for index in range(count))
        if format:
            if self._formatter is None:
                self._formatter = self._log.formatter()
            lines = tuple(lines)
            lines = (self._formatter.format(*values) for values in lines)
        return tuple(lines)
