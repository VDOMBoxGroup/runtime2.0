
from builtins import input
from builtins import str

from builtins import object
import sys

from contextlib import contextmanager
from textwrap import wrap

import settings

from utils.structure import Structure
from utils.auxiliary import align
from utils.console import CONSOLE_WIDTH


ABSENT = "ABSENT"
AUTOINDENT = "AUTO"
ERROR_PREFIX = "ERROR: "


class ConsoleWrapper(object):

    def _get_stdout(self):
        logs = sys.modules.get("logs")
        if logs:
            return logs.console.stdout
        else:
            return sys.stdout

    stdout = property(_get_stdout)

    def write(self, message=None):
        logs = sys.modules.get("logs")
        if logs:
            logs.console.write(message)
        else:
            print(message or "")

    def error(self, message=None):
        logs = sys.modules.get("logs")
        if logs:
            logs.console.error(message)
        else:
            print(ERROR_PREFIX + (message or "").replace("\n", "\n" + ERROR_PREFIX))


console = ConsoleWrapper()
global_context = Structure(
    previous=None,
    show_section=None,
    indent="",
    width=settings.MANAGE_LINE_WIDTH)


def escape(value):
    return "\"%s\"" % value.replace("\"", "\\\"")


@contextmanager
def section(name=None, value=ABSENT, indent=None, longer=False, width=None, lazy=True):
    global global_context

    if indent is None:
        indent = global_context.indent

    def show_section():
        context.show_section = None
        if context.previous and context.previous.show_section:
            context.previous.show_section()
        show(name, value, indent, longer)

    context = Structure(
        previous=global_context,
        show_section=show_section,
        indent=indent + settings.LOGGING_INDENT,
        width=width or settings.MANAGE_LINE_WIDTH)

    if not (value is ABSENT and lazy):
        context.show_section()

    global_context = context
    try:
        yield
    finally:
        global_context = context.previous


def reformat(value, caption, continuation="", noclip=False):
    global global_context
    return "\n".join(("\n".join(wrap(
        part,
        initial_indent=caption,
        subsequent_indent=" " * len(caption) + continuation,
        width=CONSOLE_WIDTH if noclip else global_context.width,
        replace_whitespace=False,
        break_long_words=False))
        for part in value.splitlines()))


def show(name=None, value=ABSENT, indent=None, longer=False, continuation="", noclip=False):
    global global_context

    if indent is None:
        indent = global_context.indent

    if global_context.show_section:
        global_context.show_section()

    if not name:
        if name is not None:
            console.write()
        return

    if value is ABSENT:
        caption = indent
        value = name
    else:
        if isinstance(longer, bool):
            width = settings.MANAGE_LONG_NAME_WIDTH if longer else settings.MANAGE_NAME_WIDTH
        else:
            width = longer
        caption = align(name, width, filler="." if name else " ", indent=indent)

    if not isinstance(value, bytes):
        value = str(value)

    #Workaround for missing newline in console
    console.write(f"{reformat(value, caption, continuation=continuation, noclip=noclip)}\n") 


def warn(message, indent=None, continuation="", noclip=False):
    global global_context

    if indent is None:
        indent = ""
    elif indent is AUTOINDENT:
        indent = global_context.indent

    if global_context.show_section:
        global_context.show_section()

    if not isinstance(message, bytes):
        message = str(message)

    console.error(reformat(message, indent, continuation=continuation, noclip=noclip))


def confirm(message=None, question=None):
    if message:
        console.write(message)
    console.stdout.write("are you sure%s? ___\b\b\b" % (" to %s" % question if question else ""))
    answer = input()
    result = answer.lower() == "yes"
    if not result:
        console.write("unconfirmed")
    return result


def newline(lazy=True):
    global global_context

    def show_section():
        context.show_section = None
        if context.previous and context.previous.show_section:
            context.previous.show_section()
        show()

    context = Structure(
        previous=global_context,
        show_section=show_section,
        indent=global_context.indent,
        width=settings.MANAGE_LINE_WIDTH)

    if not lazy:
        context.show_section()

    global_context = context
