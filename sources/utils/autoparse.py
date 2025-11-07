
import inspect
import re

from types import FunctionType, ModuleType
from itertools import chain
from argparse import OPTIONAL, SUPPRESS, ArgumentParser, ArgumentTypeError, HelpFormatter, Action

import utils.verificators
from utils.structure import Structure
from utils.console import CONSOLE_WIDTH


SUPRESS_HELP = "SUPRESS HELP"
DOCSTRING_HELP_REGEX = re.compile(r"^\s*(?P<help>[^:].*)?$", re.MULTILINE)
DOCSTRING_ARGUMENT_REGEX = re.compile(
    r"^:(?P<kind>param(?:eter)?|arg(?:ument)?|key(?:word)?)"
    r"(?:\s+(?P<type>\w+))?\s+(?P<name>\w+):\s?(?P<help>.*)$", re.MULTILINE)
SWITCH_VALUES = {
    "0": False, "1": True,
    "no": False, "yes": True,
    "off": False, "on": True,
    "false": False, "true": True,
    "disabled": False, "enabled": True
}

ARGUMENT_ONLY = Structure(is_argument=True, is_keyword=False, is_polymorph=False)
ARGUMENT_AND_KEYWORDS = Structure(is_argument=True, is_keyword=True, is_polymorph=True)
KEYWORD_ONLY = Structure(is_argument=False, is_keyword=True, is_polymorph=False)

OPTION_TYPE = {
    "param": ARGUMENT_AND_KEYWORDS,
    "parameter": ARGUMENT_AND_KEYWORDS,
    "arg": ARGUMENT_ONLY,
    "argument": ARGUMENT_ONLY,
    "key": KEYWORD_ONLY,
    "keyword": KEYWORD_ONLY
}

DEFAULT_METADATA = ARGUMENT_AND_KEYWORDS, None, None, None

DEFAULT_ACTION_NAME = "DEFAULT"
ALIAS_NAME = "ALIAS"

OVERRIDE_ARGUMENT_STRING = False
ALTERNATIVE_ARGUMENT_STRING = False

MAXIMAL_HELP_WIDTH = 139


def switch(value):
    try:
        return SWITCH_VALUES[str(value).lower()]
    except KeyError:
        raise ValueError("Not an switch")


def make_verificator(verificator, name=None):
    def wrapper(value):
        try:
            return verificator(value)
        except ValueError as error:
            raise ArgumentTypeError(str(error))
    wrapper.name = name or verificator.__name__
    wrapper.verificator = verificator
    return wrapper


class HiddenHelpFormatter(HelpFormatter):

    def _format_action(self, action):
        if action.help is SUPRESS_HELP:
            return ""
        else:
            return super(HiddenHelpFormatter, self)._format_action(action)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            if action.nargs == 0:
                return ", ".join(action.option_strings)
            else:
                default = action.dest.upper()
                return "%s %s" % (", ".join(action.option_strings), self._format_args(action, default))


class StoreMandatoryAction(Action):

    def __init__(self, option_strings, dest, nargs=None, const=None,
            default=None, type=None, choices=None, required=False, help=None, metavar=None):
        if nargs == 0:
            raise ValueError("Require arguments to store")
        if const is not None and nargs != OPTIONAL:
            raise ValueError("Must be optional to store constant" % OPTIONAL)
        super(StoreMandatoryAction, self).__init__(option_strings=option_strings, dest=dest, nargs=nargs, const=const,
            default=default, type=type, choices=choices, required=required, help=help, metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) == self.default:
            setattr(namespace, self.dest, values)


verificators = {native.__name__: make_verificator(native, name=name)
    for native, name in (
        (int, "integer"), (int, "integer"),
        (float, "float"), (complex, "complex"),
        (str, "string"), (str, "stirng"),
        (bool, "boolean"),
        (tuple, "list"), (list, "list"), (dict, "mapping"), (set, "list"),
        (switch, "boolean"))}

for name in dir(utils.verificators):
    native = getattr(utils.verificators, name)
    if isinstance(native, FunctionType):
        verificators[name] = make_verificator(native)


def autoparse(alias, routine, subparsers, autoletters=True):
    spec = inspect.getfullargspec(routine)
    names, arguments, keywords, defaults = spec.args, spec.varargs, spec.kwonlyargs, spec.defaults
    metadata, description = {}, None

    index = len(names) - (len(defaults) if defaults else 0)
    mandatory = names[:index]
    optional = names[index:]

    docstirng = inspect.getdoc(routine)
    if docstirng:
        match = DOCSTRING_HELP_REGEX.match(docstirng)
        if match:
            description = match.group("help")
        matches = DOCSTRING_ARGUMENT_REGEX.finditer(docstirng)
        for match in matches:
            name = match.group("name")
            if name not in names and name != arguments:
                raise Exception("Argument \"%s\" is described but absent in \"%s\""
                    % (name, routine.__module__))

            try:
                entity = OPTION_TYPE[match.group("kind")]
            except KeyError:
                raise Exception("Wrong description for \"%s\" of \"%s\""
                    % (name, routine.__module__))

            media = match.group("type")
            metadata[name] = entity, media, verificators.get(media), match.group("help")

    def formatter(prog):
        width = min(MAXIMAL_HELP_WIDTH, CONSOLE_WIDTH)
        return HiddenHelpFormatter(prog, max_help_position=width * 3 // 2, width=width)

    subparser = subparsers.add_parser(alias, help=description, formatter_class=formatter)

    for name in mandatory:
        entity, media, verificator, description = metadata.get(name, (None, None, None))
        if entity.is_keyword:
            raise Exception("Argument \"%s\" is described as keyword of \"%s\""
                % (name, routine.__module__))
        subparser.add_argument(name, type=verificator, help=description)

    if defaults:
        letters = set("ch")
        for name, default in zip(optional, defaults):
            entity, media, verificator, description = metadata.get(name, DEFAULT_METADATA)
            keywords = {}

            if entity.is_keyword:
                if autoletters and name[0] not in letters:
                    flags = "-%s" % name[0], "--%s" % name
                    letters.add(name[0])
                else:
                    flags = "--%s" % name,

            if media == "switch":
                keywords["action"] = "store_false" if default else "store_true"
            else:
                keywords["action"] = StoreMandatoryAction
                keywords["type"] = verificator

                if entity.is_keyword and OVERRIDE_ARGUMENT_STRING:
                    value = getattr(verificator, "name", "string")
                    keywords["metavar"] = "<%s>" % value.replace("_", " ") \
                        if ALTERNATIVE_ARGUMENT_STRING else value.upper()

            if entity.is_polymorph:
                group = subparser.add_mutually_exclusive_group()
                group.add_argument(
                    name,
                    action=StoreMandatoryAction, type=verificator,
                    nargs=OPTIONAL, default=default,
                    help=SUPRESS_HELP)
                group.add_argument(
                    *flags,
                    default=default,
                    help=description,
                    **keywords)
            elif entity.is_argument:
                subparser.add_argument(
                    name,
                    action=StoreMandatoryAction, type=verificator,
                    nargs=OPTIONAL, default=default,
                    help=description)
            else:
                subparser.add_argument(
                    *flags,
                    default=default,
                    help=description,
                    **keywords)

    if arguments:
        entity, media, verificator, description = metadata.get(arguments, DEFAULT_METADATA)
        if entity.is_keyword:
            raise Exception("Optional arguments \"%s\" is described as keyword of \"%s\""
                % (arguments, routine.__module__))
        subparser.add_argument(arguments, type=verificator, nargs="*", help=description)

    return routine, names, arguments


class AutoArgumentParser(ArgumentParser):

    def __init__(self, *arguments, **keywords):
        self._disable_usage = False
        self._disable_help = False
        self._default = keywords.pop("default", None)
        package = keywords.pop("package", None)
        module = keywords.pop("module", None)
        alias = keywords.pop("alias", None)

        super(AutoArgumentParser, self).__init__(*arguments, **keywords)

        if module:
            self._package = package or module.__package__ + "."
            self._name = "#%s" % (alias or module.__name__)
            self._parsers = {}
            self._repository = {}

            subparsers = self.add_subparsers(dest=self._name)

            for name in dir(module):
                if name.startswith("_") or name == DEFAULT_ACTION_NAME:
                    continue

                submodule = getattr(module, name)
                if not isinstance(submodule, ModuleType):
                    continue
                if not (submodule.__package__ and (submodule.__package__ + ".").startswith(self._package)):
                    continue
                if not getattr(submodule, "AUTOPARSE", True):
                    continue

                description = submodule.__doc__.strip() if submodule.__doc__ else None
                run = getattr(submodule, "run", None)
                name = getattr(submodule, ALIAS_NAME, name)

                if isinstance(run, FunctionType):
                    self._repository[name] = autoparse(name, run, subparsers)
                elif run is None and submodule.__package__.endswith(submodule.__name__):
                    default_module = submodule.__dict__.get(DEFAULT_ACTION_NAME)
                    default_action = default_module.__dict__.get("run") if default_module else None
                    self._parsers[name] = subparsers.add_parser(name, help=description,
                        package=self._package, module=submodule, alias=name, default=default_action,
                        formatter_class=HiddenHelpFormatter)
        else:
            self._name = None

    default = property(lambda self: self._default)

    def parse_args(self, args=None, namespace=None):
        arguments = super(AutoArgumentParser, self).parse_args(args=args, namespace=namespace)

        if self._name:
            subparser, parser = self, None
            while subparser:
                parser = subparser
                name = getattr(arguments, parser._name)
                subparser = parser._parsers.get(name)

            entry = parser._repository.get(name)
            if entry:
                routine, names, remainder = parser._repository.get(name)
                arguments.action = Structure(
                    name=name,
                    run=routine,
                    arguments=chain((getattr(arguments, name) for name in names),
                        getattr(arguments, remainder) if remainder else ()))
            else:
                arguments.action = Structure(
                    name=name,
                    run=parser.default, # run=self._default,
                    arguments=())

        return arguments

    def error(self, message):
        if self._default and message.endswith("too few arguments"):
            return
        super(AutoArgumentParser, self).error(message)

    def disable(self, optional_actions=False, usage=False, help=False):
        if optional_actions:
            for action in self._get_optional_actions():
                action.help = SUPPRESS
        if usage:
            self._disable_usage = True
        if help:
            self._disable_help = True

    def print_usage(self, *arguments, **keywords):
        if self._disable_usage:
            return
        else:
            super(AutoArgumentParser, self).print_usage(*arguments, **keywords)

    def print_help(self, *arguments, **keywords):
        if self._disable_help:
            return
        else:
            super(AutoArgumentParser, self).print_help(*arguments, **keywords)
