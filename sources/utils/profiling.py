
from builtins import object
import errno
import os.path

from time import time
from threading import local, RLock
from contextlib import contextmanager
from cProfile import Profile
from pstats import Stats

import settings

from logs import server_log


class ProfilerLocal(local):

    counter = 0
    profile = None


class Profiler(object):

    def __init__(self, name=None):
        self._lock = RLock()
        self._name = name or settings.PROFILE_DEFAULT_NAME
        self._location = settings.PROFILE_FILENAME_TEMPLATE % self._name
        self._stats = None
        self._local = ProfilerLocal()
        self._notch = time() - 1
        self._updates = False

    def _set_status(self, value):
        settings.PROFILING = value

    status = property(lambda self: settings.PROFILING, _set_status)

    def __enter__(self):
        if not settings.PROFILING:
            return self

        if not self._local.counter:
            self._local.profile = Profile()
            self._local.profile.enable()

        self._local.counter += 1
        return self

    def __exit__(self, extype, exvalue, extraceback):
        if not settings.PROFILING:
            return

        self._local.counter -= 1
        if not self._local.counter:
            self._local.profile.disable()
            self.aggregate(self._local.profile)
            self._local.profile = None

    def aggregate(self, profile_or_stats):
        with self._lock:
            if self._stats is None:
                self._stats = Stats(profile_or_stats)
            else:
                self._stats.add(profile_or_stats)
            self._updates = True

    def clear(self):
        with self._lock:
            if self._stats is not None:
                self._stats = None

    @contextmanager
    def hold(self, location=None):
        if not settings.PROFILING:
            yield None
        else:
            if location is None:
                location = self._location

            with self._lock:
                self.save(location=location, force=True)
                yield location

    def load(self, location=None):
        if not settings.PROFILING:
            return None

        if location is None:
            location = self._location

        with self._lock:
            self.save(location=location, force=True)
            try:
                with open(location, "rb") as file:
                    return file.read()
            except Exception as error:
                if isinstance(error, IOError) and error.errno == errno.ENOENT:
                    return None
                else:
                    raise

    def save(self, location=None, force=False):
        if not (settings.PROFILING and self._updates):
            return

        now = time()
        if not force and now < self._notch:
            return

        if location is None:
            location = self._location

        with self._lock:
            if self._stats:
                self._stats.dump_stats(location)
                if not force:
                    server_log.write("Save profiling statistics to \"%s\"" % os.path.basename(location))

            self._notch = now + settings.PROFILING_SAVE_PERIODICITY
            self._updates = False

    def autosave(self):
        self.save()
        for profiler in self._profilers.values():
            profiler.save()


class MainProfiler(Profiler):

    def __init__(self):
        super(MainProfiler, self).__init__()
        self._profilers = {settings.PROFILE_DEFAULT_NAME: self}

    def __call__(self, name):
        with self._lock:
            try:
                profiler = self._profilers[name]
            except KeyError:
                self._profilers[name] = profiler = Profiler(name)
            return profiler


profiler = MainProfiler()
