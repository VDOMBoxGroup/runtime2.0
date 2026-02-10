
import inspect
import select

from logs import log
from utils.tracing import show_exception_trace
from utils.threads import SmartThread
from utils.parsing import Parser, ParsingException

from .exceptions import WatcherError
from .builder import builder
from .registry import modules


NAME_TEMPLATE = "%s %04X"


class WatcherSession(SmartThread):

    name = "Watcher Session"

    def __init__(self, socket, address):
        super(WatcherSession, self).__init__(name=NAME_TEMPLATE % (WatcherSession.name, address[1]))
        self._socket = socket
        self._address = address

    def prepare(self):
        log.write("Start " + self.name)

    def cleanup(self):
        log.write("Stop " + self.name)
        self._socket = None

    def main(self):
        parser = Parser(builder=builder, result=[])
        parser.cache = True
        parser.parse(chunk="<session>")
        while self.running:
            try:
                reading, writing, erratic = select.select((self._socket,), (), (), self.quantum)
            except OSError:
                log.error("Unable to check session state")
            else:
                if reading:
                    try:
                        message = self._socket.recv(4096)
                    except OSError:
                        log.error("Unable to receive request")
                        break
                    if not message:
                        break
                    try:
                        parser.parse(chunk=message)
                    except ParsingException:
                        log.error("Unable to parse request")
                        try:
                            self._socket.send(b"<reply><error>Incorrect request</error></reply>")
                        except OSError:
                            log.error("Unable to send response")
                        break
                    for name, options in parser.result:
                        try:
                            handler = modules[name]
                        except KeyError:
                            log.error("Unable to find action")
                            response = "<reply><error>Incorrect request</error></reply>"
                        else:
                            try:
                                log.write("Invoke \"%s\" for %s" % (name, self._address[0]))
                                if inspect.isgeneratorfunction(handler):
                                    response = "".join(handler(options))
                                else:
                                    response = handler(options)
                            except WatcherError as error:
                                response = "<reply><error>%s</error></reply>" % error
                                log.write(error)
                            except Exception as error:
                                message = "Execution error: %s" % error
                                response = "<reply><error>%s</error></reply>" % message
                                show_exception_trace(caption=message, locals=True)
                        if not response:
                            response = "<reply><error>No reply</error></reply>"
                        try:
                            self._socket.send(response.encode())
                        except OSError:
                            log.error("Unable to send response")
                            break
                    del parser.result[:]
        self._socket.close()
