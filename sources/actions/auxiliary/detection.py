
import re
from contextlib import closing
import managers
import file_access
from utils.output import warn
from utils.parsing import native, Parser
from .constants import TYPE, APPLICATION, USER, GROUP


ENTITY_NAME_REGEX = re.compile("[a-z][_0-9a-z]*$", re.IGNORECASE)


def is_entity_name(value):
    return bool(ENTITY_NAME_REGEX.match(value))


def search(identifier=None, application=None, type=None, user=None, group=None):
    if user or group:
        if user:
            user = user.lower()
        if group:
            group = group.lower()
            if user and user != group:
                raise ValueError

        user_or_group = managers.user_manager.get_user_by_name(user or group)
        if user_or_group:
            entity = USER if managers.user_manager.user_exists(user_or_group.login) else GROUP
            if entity is USER and user or entity is GROUP and group:
                return entity, user_or_group

        user_or_group = managers.user_manager.get_user_by_id(user or group)
        if user_or_group:
            entity = USER if managers.user_manager.user_exists(user_or_group.login) else GROUP
            if entity is USER and user or entity is GROUP and group:
                return entity, user_or_group

        if user:
            for item in managers.user_manager.get_all_users():
                if item.login.lower().startswith(user):
                    return USER, item

        if group:
            for item in managers.user_manager.get_all_groups():
                if item.login.lower().startswith(group):
                    return GROUP, item

        if user:
            entity = "%s or %s" % (USER, GROUP) if group else USER
            identifier = user
        else:
            entity = GROUP
            identifier = group

        warn("unable to find %s with such uuid or name: %s" % (entity, identifier))
        return None, None
    else:
        if identifier:
            application = type = identifier

        if application:
            subject = managers.memory.applications.search(application, autocomplete=True)
            if subject:
                return APPLICATION, subject

        if type:
            subject = managers.memory.types.search(type, autocomplete=True)
            if subject:
                return TYPE, subject

        warn("unable to find application or type with such uuid or name")
        return None, None


def detect(filename):

    def builder(parser):
        @native
        def entity(name, attributes):
            if name == u"Type":
                parser.complete(TYPE)
            if name == u"Application":
                parser.complete(APPLICATION)
            else:
                parser.abort()
        return entity

    try:
        file = managers.file_manager.open(file_access.FILE, None, filename, mode="rb")
    except Exception as error:
        warn("unable to open file: %s" % error)
        return None
    else:
        with closing(file):
            try:
                entity = Parser(builder=builder, supress=True).parse(file=file)
                if entity is TYPE:
                    return entity
                elif entity is APPLICATION:
                    return entity
                else:
                    warn("file does not contain application or type")
                    return None
            except Exception as error:
                warn("unable to detect %s contents: %s" % (filename, error))
                return None


def search_object(identifier):
    for application in managers.memory.applications.values():
        if identifier == application.id:
            return application
        else:
            subject = application.objects.catalog.get(identifier)
            if subject is not None:
                return subject
    return None


def search_action(identifier):
    for application in managers.memory.applications.values():
        subject = application.actions.catalog.get(identifier)
        if subject is not None:
            return subject
    return None
