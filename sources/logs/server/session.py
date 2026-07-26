


import socket
from threading import Lock, enumerate as enumerate_threads
from utils.threads import SmartDaemon
from logs import server_log
from .. import actions
from ..packer import create_packer
from ..sublogs import ServerLog, ApplicationLog, NetworkLog, SecurityLog
from ..stream import LogSocketStream, NoDataException, ShutdownException
from ..loggers import Logger
from .reader import LogReader
from .writer import LogWriter


COUNTDOWN = 3.0


class LogServerSession(SmartDaemon):

    name = "Log Server Session"

    # assume

    _assume_request = create_packer("BS")

    def _do_assume(self):
        id, name = self._assume_request.unpack_from(self._stream)
        if id in self._mapping:
            raise Exception

        main = name.partition("/")[0]
        try:
            log = self._logs[main]
        except KeyError:
            raise Exception

        with self._lock:
            if name in self._writers:
                writer = self._writers[name]
            else:
                writer = self._writers[name] = LogWriter(name, log.formatter())

        self._mapping[id] = (log, writer, None)

    # revoke

    _revoke_request = create_packer("B")

    def _do_revoke(self):
        id, = self._revoke_request.unpack_from(self._stream)
        del self._mapping[id]

    # write

    _write_request = create_packer("BL")

    def _do_write(self):
        id, count = self._write_request.unpack_from(self._stream)
        try:
            log, writer, reader = self._mapping[id]
        except KeyError:
            raise Exception

        writer.write(*(log.packer.unpack_from(self._stream) for index in range(count)))

    # update

    _update_request = create_packer("B")
    _update_response = create_packer("L")

    def _do_update(self):
        id, = self._update_request.unpack_from(self._stream)
        try:
            log, writer, reader = self._mapping[id]
        except KeyError:
            raise Exception

        if reader is None:
            reader = LogReader(writer)
            self._mapping[id] = (log, writer, reader)

        self._update_response.pack_into(self._stream, reader.update())

    # read

    _read_request = create_packer("BLL")
    _read_response = create_packer("L")

    def _do_read(self):
        id, start, count = self._read_request.unpack_from(self._stream)
        try:
            log, writer, reader = self._mapping[id]
        except KeyError:
            raise Exception

        if reader is None:
            reader = LogReader(writer)
            self._mapping[id] = (log, writer, reader)

        entries = reader.read(start, count)
        self._read_response.pack_into(self._stream, len(entries))
        for entry in entries:
            log.packer.pack_into(self._stream, *entry)

    # main

    _classes = (
        ServerLog,
        ApplicationLog,
        NetworkLog,
        SecurityLog)
    _logs = {cls.name: cls for cls in _classes}
    _writers = {}
    _lock = Lock()
    _actions = {
        actions.ASSUME: _do_assume,
        actions.REVOKE: _do_revoke,
        actions.WRITE: _do_write,
        actions.UPDATE: _do_update,
        actions.READ: _do_read}

    def __init__(self, socket):

        def condition():
            for thread in enumerate_threads():
                if thread.name == Logger.name:
                    return False
            return True

        super(LogServerSession, self).__init__(name=LogServerSession.name,
            condition=condition, countdown=COUNTDOWN, latter=True)
        self._mapping = {}
        self._stream = LogSocketStream(self, socket)
        socket.settimeout(self.quantum)

    def prepare(self):
        server_log.write("Start " + self.name)

    def cleanup(self):
        server_log.write("Stop " + self.name)
        import traceback
        server_log.write( self.name + traceback.format_stack())
        
        self._stream = None

    _action_request = create_packer("B")

    def main(self):
        while self.running:
            try:
                ret = self._action_request.unpack_from(self._stream)
                if ret:
                    action, = ret
                    self._actions[action](self)
            except NoDataException:
                break
            except ShutdownException:
                break
            except socket.error as error:
                server_log.error(error.strerror or error.message)
                self.halt()
