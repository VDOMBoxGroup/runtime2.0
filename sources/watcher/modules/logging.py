from __future__ import absolute_import

# from sources import settings
import settings
from logs import log
from logs.levels import LEVEL_TO_NAME
from utils import verificators
from ..exceptions import OptionError


def logging(options):
    level = options.get("level")
    if level is not None:
        try:
            level = verificators.log_level(level)
        except ValueError:
            raise OptionError("Incorrect level")

        if settings.LOG_LEVEL != level:
            log.write("Assign log level to %s" % LEVEL_TO_NAME[level].lower())
            settings.LOG_LEVEL = level

    level = LEVEL_TO_NAME[settings.LOG_LEVEL].lower()
    yield "<reply><logging><level>%s</level></logging></reply>" % level
