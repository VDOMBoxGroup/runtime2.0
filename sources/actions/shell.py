
from builtins import input
import re
from itertools import islice

import startup
from logs import console
from utils.threads import intercept
from utils.tracing import show_exception_trace


ARGUMENTS_REGEX = re.compile("(\"(?:\\\\\"|[^\"\\\\])*\"|[^\"\s]+)")


def split(value):
    items = ARGUMENTS_REGEX.split(value)
    for index, item in enumerate(items):
        if index % 2:
            continue
        separator = item.strip()
        if separator:
            raise SyntaxError(separator)
    return tuple(item[1:-1] if item[0] == "\"" else item for item in islice(items, 1, None, 2))


def run():
    """
    enter interactive mode
    """
    intercept(ctrlc=lambda: None)
    parser = startup.manage.parser
    parser.disable(optional_actions=True)

    while 1:
        try:
            console.stdout.write("manage > ")
            command = input().strip().lstrip("-")
        except KeyboardInterrupt:
            return
        except EOFError:
            return

        keyword = command.lower()
        if keyword == "help":
            parser.print_help()
        elif keyword == "exit" or keyword == "quit":
            return
        else:
            try:
                arguments = parser.parse_args(split(command))
            except SyntaxError as error:
                console.write("error: unexpected symbol: %s" % error)
            except SystemExit:
                pass
            else:
                if arguments.action.run and arguments.action.run is not run:
                    try:
                        arguments.action.run(*arguments.action.arguments)
                    except Exception:
                        show_exception_trace(locals=True)
                else:
                    parser.print_usage()
