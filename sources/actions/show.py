

import re
from itertools import zip_longest

from .auxiliary.constants import TYPE, APPLICATION
from .auxiliary import escape, section, show, warn, search


COLORS = {
    1: "gray",
    2: "green",
    3: "red",
    4: "blue"
}

EXPLANATIONS = {
    "dynamic": {0: "no", 1: "yes"},
    "moveable": {0: "no", 1: "yes"},
    "resizable": {0: "no", 1: "vertically", 2: "horizontally", 3: "yes"},
    "interface_type": {
        1: "standard",
        2: "richtext editor",
        3: "text editor",
        4: "picture",
        5: "special table",
        6: "no WYSIWYG presentation"
    },
    "container": {1: "non-container", 2: "container", 3: "top level container"}
}


name_regex = re.compile(r"^([0-9A-Z]+)\((.*)\)", re.IGNORECASE)
dropdown_regex = re.compile(r"\|([^(|)]+)?\)")
lang_regex = re.compile(r"^#lang\((\d+)\)$", re.IGNORECASE)


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def unlang(subject, value):
    try:
        match = lang_regex.search(value)
        return subject.sentences["en_US"][int(match.group(1))]
    except BaseException:
        return value


def explain(name, value):
    if name == "password":
        return "<present>" if value else "<absent>"
    elif name == "category":
        return value.lower() or "<empty>"

    try:
        explanations = EXPLANATIONS[name]
    except KeyError:
        return None

    try:
        explanation = explanations[int(value)]
    except ValueError:
        return "%r (not a number)" % value
    except KeyError:
        return "%r (unknown)" % value
    else:
        return "%s (%s)" % (value, explanation)


def interface(subject, attribute):

    def dropdown(value):

        def compose(description, value):
            value = value.lower()
            description = unlang(subject, description).lower()
            if description:
                try:
                    value = int(value)
                    return "%s=%s" % (value, description)
                except ValueError:
                    if value == description:
                        return description
                return "%s=%s" % (escape(value), description)
            else:
                return value

        try:
            pairs = [(left[1:], right[:-1]) for left, right in grouper(value.split("|"), 2)]
            return "dropdown: %s" % ", ".join((compose(*pair) for pair in sorted(pairs, key=lambda pair: pair[-1])))
        except BaseException:
            raise
            return "dropdown"

    value = attribute.code_interface
    match = name_regex.search(value)
    if match:
        name = match.group(1).lower()
        if name == "dropdown":
            return dropdown(match.group(2))
        else:
            return name
    else:
        return value


def describe(subject, attribute):
    return unlang(subject, attribute.description) # .replace("\n", " ")


def group_color(subject, attribute):
    try:
        return COLORS[int(attribute.color_group)]
    except (ValueError, KeyError):
        return "unknown (%s)" % attribute.color_group


def visible(subject, attribute):
    return "yes" if attribute.visible else "no"


def default_value(subject, attribute):
    return escape(attribute.default_value) if attribute.default_value else "<empty>"


def validation_pattern(subject, attribute):
    return "<anything>" if attribute.validation_pattern in (".*", "^.*$") \
        else escape(attribute.validation_pattern)


def run(identifier, description=False, details=False):
    """
    show application or type
    :arg uuid_or_name identifier: application or type uuid or name
    :key switch description: show attributes description
    :key switch details: show attribute details
    """
    entity, subject = search(identifier)
    if entity is TYPE:
        names = ("id", "module_name", "name", "class_name",
        "category", "interface_type", "dynamic", "moveable", "resizable",
        "optimization_priority", "container", "containers", "render_type",
        "http_content_type", "remote_methods", "handlers", "languages", "version")
    elif entity is APPLICATION:
        names = ("id", "name", "owner", "password", "active", "index",
            "server_version", "scripting_language", "default_language")
    else:
        warn("unable to find: %s" % identifier)
        return

    if description:
        names = "id", "name"

    try:
        with section("summary"):
            show("entity", entity)
            for name in names:
                value = getattr(subject, name)
                explanation = explain(name, value)

                if explanation:
                    value = explanation
                elif isinstance(value, str):
                    value = value or "<empty>"
                elif isinstance(value, (tuple, list)):
                    if value:
                        value = ", ".join(item for item in sorted(value))
                    else:
                        value = "<empty>"
                else:
                    value = repr(value)

                show(name.replace("_", " "), value)

        if description:
            with section("description"):
                show(unlang(subject, subject.description or "<no description>"))

        if entity is TYPE:
            with section("attributes"):
                for attribute in subject.attributes.values():
                    name = attribute.name.replace("_", " ")
                    if details:
                        with section(name):
                            show("interface", interface(subject, attribute))
                            show("visible", visible(subject, attribute))
                            show("group color", group_color(subject, attribute))
                            show("default value", default_value(subject, attribute))
                            show("validation pattern", validation_pattern(subject, attribute))
                            if description:
                                show("description", describe(subject, attribute))
                    else:
                        if description:
                            show(name, describe(subject, attribute))
                        else:
                            show(name, interface(subject, attribute))

    except Exception as error:
        warn("unable to show %s: %s" % (entity, error))
        raise
