
#
#
import os.path

from ast import literal_eval
from io import StringIO
from configparser import ConfigParser

import settings

from utils.auxiliary import enquote


DEFAULT_SECTION = "NONAME"
EXTRA_SECTIONS = "SERVER", "MANAGE", "WINDOWS", "LINUX", "FREEBSD"
MISSING = "MISSING"


def override(filename):
    if not os.path.isfile(filename):
        print("File to override settings not found: %s" % filename)
        return

    filelike = StringIO()
    filelike.write("[%s]\n" % DEFAULT_SECTION)

    with open(filename, "r") as file:
        filelike.write(file.read())

    filelike.seek(0)

    config = ConfigParser()
    config.readfp(filelike)

    def override_from_section(section):
        if not config.has_section(section):
            return

        for name, value in config.items(section):
            settings_name = name.replace("-", "_").upper()

            if settings_name.startswith("_"):
                print("Ignore unsupported option: %s" % enquote(name))
                continue

            current_value = getattr(settings, settings_name, MISSING)
            if current_value is MISSING:
                print("Ignore unknown option: %s" % enquote(name))
                continue

            try:
                new_value = literal_eval(value)
            except ValueError:
                print("Ignore wrong value for %s option: %s" % (enquote(name), enquote(value)))
                continue

            if not (current_value is None
                    or new_value is None
                    or type(new_value) is type(current_value)):
                print("Ignore %s value for %s %s option: %s" % (type(new_value).__name__,
                    type(current_value).__name__, enquote(name), enquote(value)))
                continue

            setattr(settings, settings_name, new_value)

    override_from_section(DEFAULT_SECTION)
    for name in EXTRA_SECTIONS:
        if getattr(settings, name):
            override_from_section(name)
