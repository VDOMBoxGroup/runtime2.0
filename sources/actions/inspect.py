
from utils.console import CONSOLE_WIDTH
from .auxiliary import section, show, warn, search_object, search_action


DEFAULT_DEPTH = 10

INDENT = "    "
SELECTION = "- "


def describe(item, extra=False):
    if hasattr(item, "is_object"):
        entity = item.type.name if item.is_object else "application"
        if item.is_object and item.type.name == "copy":
            copy = item.application.objects.catalog.get(item.attributes["source_object"])
            if copy:
                copy = describe(copy)
        else:
            copy = None
    else:
        entity = "action"
        copy = None

    return " ".join([_f for _f in (
        entity if extra else None,
        ":".join([_f for _f in (item.id, item.name.lower()) if _f]),
        ("-> %s" % copy) if copy else None) if _f])


def search_parents(item):
    items = []
    if not hasattr(item, "is_object"):
        item = item.owner
        items.append(item)
    if item.is_object:
        current = item.parent
        while current:
            items.append(current)
            current = current.parent
        items.append(item.application)
        items.reverse()
    return items


def show_level(item, level=0, expand=0, select=False, actions=False, indent=""):
    indent = indent + INDENT * level
    if select and len(indent) >= len(SELECTION):
        indent = indent[:-len(SELECTION)] + SELECTION

    show_underlying = hasattr(item, "is_object") and bool(item.objects or (actions and item.actions))
    if expand:
        details = ""
    else:
        details = "..." if show_underlying else ""
        show_underlying = False

    show("%s%s%s" % (indent, describe(item, extra=True), details), longer=True)
    if show_underlying:
        for subitem in item.objects.values():
            show_level(subitem, level + 1, expand=expand - 1 if expand else 0, actions=actions)
        if actions:
            for subitem in item.actions.values():
                show_level(subitem, level + 1)


def run(identifier, depth=DEFAULT_DEPTH, actions=False):
    """
    inspect object
    :arg uuid identifier: object uuid to inspect
    :key int depth: limit the depth of showing for underlying objects
    :key switch actions: show actions
    """
    subject = search_object(identifier)
    if subject:
        entity = subject.type.name if subject.is_object else "application"
    else:
        subject = search_action(identifier)
        if subject:
            entity = "action"
        else:
            warn("unable to find: %s" % identifier)
            return

    with section("summary"):
        show("type", entity)
        show("id", subject.id)
        show("name", subject.name)

    parents = search_parents(subject)
    with section("structure", width=CONSOLE_WIDTH):
        for level, item in enumerate(parents):
            show_level(item, level)
        show_level(subject, len(parents), expand=depth, select=True, actions=actions)
