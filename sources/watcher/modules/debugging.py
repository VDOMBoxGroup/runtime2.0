from __future__ import absolute_import

# from sources import settings

import settings
from logs import log
from utils import verificators
from ..exceptions import OptionError


def debugging(options):
    show_page_debug = options.get("show-page-debug")
    if show_page_debug is not None:
        try:
            show_page_debug = verificators.enable_or_disable(show_page_debug)
        except ValueError:
            raise OptionError("Incorrect show page debug status")

        if settings.SHOW_PAGE_DEBUG != show_page_debug:
            log.write("%s show page debug" % ("Enable" if show_page_debug else "Disable"))
            settings.SHOW_PAGE_DEBUG = show_page_debug

    show_page_debug = "enabled" if settings.SHOW_PAGE_DEBUG else "disabled"
    yield "<reply><debugging><show-page-debug>%s</show-page-debug></debugging></reply>" % show_page_debug
