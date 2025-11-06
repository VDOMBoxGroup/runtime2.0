


from threading import enumerate as enumerate_threads
from .thread import SmartThread


class SmartDaemon(SmartThread):

    def __init__(self, name=None, quantum=None, condition=None, countdown=None, latter=False, dependencies=None):
        super(SmartDaemon, self).__init__(name=name, quantum=quantum, condition=condition, countdown=countdown, latter=latter)
        self.daemon = True
        self._dependencies = []

        if dependencies:
            if not isinstance(dependencies, (list, tuple)):
                dependencies = (dependencies,)

            mapping = {thread.name: thread for thread in enumerate_threads() if thread.name in dependencies}
            if len(mapping) < len(dependencies):
                raise Exception("Require %s thread(s) to run" % ", ".join(set(dependencies) - set(mapping)))

            for name, thread in list(mapping.items()):
                if not isinstance(thread, SmartDaemon):
                    raise Exception("Not smart daemon in dependencies")
                if thread.latter != self.latter:
                    raise Exception("Dependency must have same latter")
                self._dependencies.append(thread)

    dependencies = property(lambda self: tuple(thread for thread in self._dependencies if thread.is_alive()))

    def rely(self, daemon):
        if not isinstance(daemon, SmartDaemon):
            raise Exception("Require smart daemon")
        daemon._dependents.append(self)


VDOM_daemon = SmartDaemon
