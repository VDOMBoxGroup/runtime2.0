
from time import time

import re
import socket
import select
import settings

from ..auxiliary import show, newline
from utils.parsing import VALUE, Parser


FRAME = 64 * 1024
RESPONSE_PATTERN = re.compile(r"\s*(?:<reply>.+</reply>|<reply/>)\s*", re.DOTALL)
DEFAULT_TIMEOUT = 10.0


def builder(parser):
    # <reply>
    def reply():
        # <error>
        def error():
            message = yield VALUE
            raise Exception(message)
        # </error>
        yield error
    # </reply>
    return reply


def query(caption, address, port, request, timeout=None, datagrams=False):

    if address is None:
        address = settings.WATCHER_ADDRESS
    if port is None:
        port = settings.WATCHER_PORT
    if timeout is None:
        timeout = DEFAULT_TIMEOUT

    show("%s %s:%s" % (caption, address, port))

    sock = socket.socket(socket.AF_INET, (socket.SOCK_DGRAM if datagrams else socket.SOCK_STREAM))
    sock.settimeout(timeout)

    start = time()

    try:
        if datagrams:
            sock.sendto(request, (address, port))
        else:
            sock.connect((address, port))
            sock.send(request)

        if datagrams:
            message, address = sock.recvfrom(FRAME)
        else:
            message = ""
            while 1:
                reading, writing, erratic = select.select((sock,), (), (), timeout)
                if reading:
                    chunk = sock.recv(FRAME)
                    message += chunk
                    if RESPONSE_PATTERN.match(message):
                        break

        duration = time() - start
        Parser(builder=builder, notify=True, supress=True).parse(message)
        show("done in %.3f s" % duration)
        newline()
        return message
    except socket.timeout:
        raise Exception("timeout expired")
    except socket.error as error:
        raise Exception(error.strerror)
