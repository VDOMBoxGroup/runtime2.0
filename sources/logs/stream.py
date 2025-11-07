
import errno
import socket


class NoDataException(socket.error):

    def __init__(self):
        socket.error.__init__(self, errno.EIO, "No data available")


class ShutdownException(socket.error):

    def __init__(self):
        socket.error.__init__(self, errno.EINTR, "Log server shutdown")


class LogSocketStream(object):

    def __init__(self, thread, socket):
        self._thread = thread
        self._socket = socket

    socket = property(lambda self: self._socket)

    def read(self, size):
        while 1:
            try:
                value = self._socket.recv(size)
                break
            except TimeoutError:
                return
            except socket.timeout:
                if not self._thread.running:
                    raise ShutdownException
        if len(value) == size:
            return value
        chunks, left = [value], size - len(value)
        while left:
            try:
                chunk = self._socket.recv(left)
            except socket.timeout:
                if not self._thread.running:
                    raise ShutdownException
                continue
            if not chunk:
                raise NoDataException
            chunks.append(chunk)
            left -= len(chunk)
        return "".join(chunks)

    def write(self, data):
        while 1:
            try:
                offset = self._socket.send(data)
                break
            except socket.timeout:
                if not self._thread.running:
                    raise ShutdownException
        while offset < len(data):
            try:
                offset += self._socket.send(data[offset:])
            except socket.timeout:
                if not self._thread.running:
                    raise ShutdownException
