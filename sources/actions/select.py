import managers
import sys

from .auxiliary import section, show, warn, search

DEFAULT = 0


def update(data, identifier, entry):
    if identifier:
        data[entry] = str(identifier)
    elif (entry) in data:
        del data[entry]


def lookup(data, entry):
    try:
        identifier = data[entry]
    except KeyError:
        return None
    else:
        try:
            application = managers.memory.applications[identifier]
        except KeyError:
            return str(identifier)
        else:
            return "%s:%s" % (application.id, application.name.lower())


def select(application, name=None):
    with section("select %s %s" % (application, ("for %s" % name if name else "as default")), lazy=False):
        try:
            data = managers.storage.read_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"]) or {}
            update(data, application.id, name or DEFAULT)
            managers.storage.write_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"], data)
        except Exception as error:
            warn("unable to select application: %s" % error)
            sys.exit(1)


def delete_(name=None):
    with section("delete %s" % ("association for %s" % name if name else "default association"), lazy=False):
        try:
            data = managers.storage.read_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"]) or {}
            update(data, None, name or DEFAULT)
            managers.storage.write_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"], data)
        except Exception as error:
            warn("unable to delete association: %s" % error)


def display(name=None):
    try:
        data = managers.storage.read_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"]) or {}
    except Exception as error:
        warn("unable to retrieve data: %s" % error)

    if name:
        identifier = lookup(data, name)
        if identifier:
            show("application for %s is %s" % (name, identifier))
        else:
            show("no application for %s" % name)
    else:
        if not data:
            show("no default application")
        else:
            default = lookup(data, DEFAULT)
            if default:
                show("default application is %s" % default)
            with section("available associations"):
                for name in data:
                    if name is DEFAULT:
                        continue
                    show(str(name), lookup(data, name))


def run(identifier=None, name=None, delete=False):
    """
    select default application
    :arg uuid_or_name identifier: application uuid or name
    :key name: specify name
    :key switch delete: delete association
    """
    if delete and identifier:
        warn("identifier is not allowed on delete: %s" % identifier)
        return

    if delete:
        delete_(name)
    elif identifier is None:
        display(name)
    else:
        entity, application = search(application=identifier)
        if application is None:
            warn("unable to find: %s" % identifier)
        select(application, name)
