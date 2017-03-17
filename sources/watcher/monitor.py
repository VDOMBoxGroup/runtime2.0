
import sys
import settings
from logs import log
from utils.tracing import format_threads_trace
from utils.threads import SmartThread


class Monitor(SmartThread):

    name = "Monitor"

    def prepare(self):
        log.write("Start " + self.name)

    def cleanup(self):
        log.write("Stop " + self.name)

    def main(self):
        while self.running:
            sys.stdout.write("Running threads:\n%s" % format_threads_trace(indent="    "))
            self.wait(settings.MONITOR)
