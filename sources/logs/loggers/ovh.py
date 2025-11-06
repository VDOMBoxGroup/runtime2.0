
from collections import deque
from itertools import chain
from threading import Lock

import datetime
import json
import logging

import settings
from logs import log

from djehouty import SYSLOG_LEVELS, STRING_TYPE, INTEGER_TYPE
from djehouty.libltsv.handlers import LTSVTCPSocketHandler
from djehouty.libgelf.handlers import GELFTCPSocketHandler
from djehouty.libltsv.formatters import LTSVFormatter
from djehouty.libgelf.formatters import GELFFormatter

from .. import levels
from ..logger import BaseLogger


COUNTDOWN = 3.0
LOG_LEVELS = {
    levels.DEBUG: logging.DEBUG,
    levels.MESSAGE: logging.INFO,
    levels.WARNING: logging.WARNING,
    levels.ERROR: logging.ERROR}

CLEAN_TYPES = (STRING_TYPE, float) + INTEGER_TYPE
UNIX_ORIGIN = datetime.datetime(1970, 1, 1)


def escape(value):
    if isinstance(value, CLEAN_TYPES):
        return value
    elif value is None:
        return ""
    else:
        return repr(value)


class CleanLTSVFormatter(LTSVFormatter):

    def format(self, record):
        data = dict(
            message=record.getMessage(),
            level=SYSLOG_LEVELS.get(record.levelno, record.levelno),
            time=datetime.datetime.strftime(record.timestamp, self.default_datefmt),
            instance=record.instance)

        for name, value in chain(iter(self.static_fields.items()), iter(record.extra.items())):
            data[name] = escape(value)

        result = "\t".join(["%s:%s" % item for item in data.items()])
        if self.null_character:
            result += "\0"
        return result


class CleanGELFFormatter(GELFFormatter):

    def format(self, record):
        data = dict(
            version="1.1",
            host=self.hostname,
            short_message=record.getMessage(),
            level=SYSLOG_LEVELS.get(record.levelno),
            timestamp=(record.timestamp - UNIX_ORIGIN).total_seconds(),
            _instance=record.instance)

        for name, value in chain(iter(self.static_fields.items()), iter(record.extra.items())):
            data["_%s" % name] = escape(value)

        result = json.dumps(data)
        if self.null_character:
            result += "\0"
        return result


class Logger(BaseLogger):

    name = "OVH Logger"

    def __init__(self):

        def condition():
            with self._lock:
                return not self._queue

        super(Logger, self).__init__(condition=condition, countdown=COUNTDOWN)

        self._address = settings.OVH_LOGGING_ADDRESS
        self._port = settings.OVH_LOGGING_PORT
        self._engine = settings.OVH_LOGGING_ENGINE
        self._tls = settings.OVH_LOGGING_TLS
        self._token = settings.OVH_LOGGING_TOKEN

        if self._engine == "ltsv":
            logger_name = "djehouty-ltsv"
            handler_class = LTSVTCPSocketHandler
            handler_options = {}
            formatter_class = CleanLTSVFormatter
        elif self._engine == "gelf":
            logger_name = "djehouty-gelf"
            handler_class = GELFTCPSocketHandler
            handler_options = {"null_character": True}
            formatter_class = CleanGELFFormatter
        else:
            raise Exception("Unknown OVH engine: %s" % self._engine)

        self._lock = Lock()
        self._queue = deque()

        self._level = LOG_LEVELS[settings.LOG_LEVEL]
        self._instance = settings.INSTANCE

        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(self._level)

        handler = handler_class(
            host=self._address, port=self._port,
            static_fields={"X-OVH-TOKEN": self._token},
            level=self._level, use_tls=self._tls,
            **handler_options)

        static_fields = handler.formatter.static_fields
        null_character = handler.formatter.null_character
        handler.setFormatter(formatter_class(static_fields,
            null_character=null_character))

        self._logger.addHandler(handler)

    def ascribe(self, sublog):

        def enqueue(*values):
            with self._lock:
                self._queue.append((sublog, values))

        return enqueue

    def prepare(self):
        super(Logger, self).prepare()
        log.write("Using %s over %s" % (self._engine.upper(), "TLS" if self._tls else "TCP"))

    def work(self):
        with self._lock:
            try:
                sublog, values = self._queue.popleft()
            except IndexError:
                return

        name, _, subname = sublog.name.partition("/")

        try:
            timestamp, level, message, extra = sublog.describe(*values)
            extra.update(log=name, sublog=subname)
            self._logger.log(LOG_LEVELS[level], message,
                extra={"timestamp": timestamp, "instance": self._instance, "extra": extra})
        except:
            with self._lock:
                self._queue.append((sublog, values))
            raise
