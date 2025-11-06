
from collections import OrderedDict
from contextlib import closing

import managers
import file_access

from utils.structure import Structure
from utils.parsing import native, VALUE, IGNORE, Parser, ParsingException, SectionMustPrecedeError

from .auxiliary import ABSENT, section, show, warn


SHOW_ERRORS_ONLY = False


def builder(parser):
    # <Application>
    def Application():
        sections = OrderedDict()
        types = {}

        def count(section_name, element_name):

            @native
            def handler(name, attributes):
                if name == element_name:
                    sections[section_name] += 1
                attributes.clear()
                return IGNORE

            return handler

        # <Information>
        def Information():
            context = Structure(
                id=None,
                name=None,
                version=None,
                server_version=None,
                scripting_language=None)
            sections["Information"] = context
            # <ID>, ...
            @native
            def entry(name, attributes):
                for attribute_name, variable_name, lower in (
                        ("ID", "id", True),
                        ("Name", "name", False),
                        ("Version", "version", False),
                        ("ServerVersion", "server_version", False),
                        ("Serverversion", "server_version", False),
                        ("ScriptingLanguage", "scripting_language", False)):
                    if name == attribute_name:
                        value = yield VALUE
                        if lower:
                            value = value.lower()
                        setattr(context, variable_name, value)
                        return
                yield IGNORE
            # </ID>, ...
            return entry
        # </Information>
        # <Objects>
        def Objects():
            if "Information" not in sections:
                raise SectionMustPrecedeError("Information")
            sections["Objects"] = Structure(_value=0, _level=0, top_level=0)
            # <Object>
            def Object(ID, Name, Type):
                if not sections["Objects"]._level:
                    sections["Objects"].top_level += 1
                sections["Objects"]._value += 1
                try:
                    type = managers.memory.types[Type]
                except:
                    types[Type] = None
                else:
                    types[Type] = type
                # <Attributes>
                def Attributes():
                    return IGNORE
                # </Attributes>
                # <Objects>
                def Objects():
                    return Object
                # </Objects>
                # <Actions>
                def Actions():
                    return IGNORE
                # </Actions>
                sections["Objects"]._level += 1
                try:
                    yield Attributes, Objects, Actions
                finally:
                    sections["Objects"]._level -= 1
            # </Object>
            return Object
        # </Object>
        # <Actions>
        def Actions():
            if "Information" not in sections:
                raise SectionMustPrecedeError("Information")
            sections["Actions"] = None
            return IGNORE
        # </Actions>
        # <Structure>
        def _Structure():
            if "Objects" not in sections:
                raise SectionMustPrecedeError("Objects")
            sections["Structure"] = 0
            return count("Structure", "Object")
        # </Structure>
        # <Libraries>
        def Libraries():
            if "Information" not in sections:
                raise SectionMustPrecedeError("Information")
            sections["Libraries"] = 0
            return count("Libraries", "Library")
        # </Libraries>
        # Languages...
        # <Resources>
        def Resources():
            if "Information" not in sections:
                raise SectionMustPrecedeError("Information")
            sections["Resources"] = 0
            return count("Resources", "Resource")
        # </Resources>
        # <Databases>
        def Databases():
            if "Information" not in sections:
                raise SectionMustPrecedeError("Information")
            sections["Databases"] = 0
            return count("Databases", "Database")
        # </Databases>
        def E2VDOM():
            if "Information" not in sections:
                raise SectionMustPrecedeError("Information")
            context = Structure(events=0, actions=0)
            sections["E2VDOM"] = context
            # <Events>
            def Events():
                # <Event>
                def Event(ContainerID, ObjSrcID, ObjSrcName=None, TypeID=None, Name=None, Top=None, Left=None, State=None):
                    context.events += 1
                    return IGNORE
                # </Event>
                return Event
            # </Events>
            # <Actions>
            def Actions():
                # <Action>
                def Action(ID, ObjTgtID, ObjTgtName=None, Name=None, MethodName=None, Top=None, Left=None, State=None):
                    context.actions += 1
                    return IGNORE
                # </Action>
                return Action
            # </Actions>
            return Events, Actions
        def E2vdom():
            return E2VDOM()
        # </E2VDOM>
        # <Security>
        def Security():
            if "Information" not in sections:
                raise SectionMustPrecedeError("Information")
            sections["Security"] = None
            return IGNORE
        # </Security>
        yield Information, Objects, Actions, _Structure, Libraries, Resources, Databases, E2VDOM, E2vdom, Security
        parser.accept(sections, types)
    # </Application>
    return Application


def run(filename):
    """
    analyze application
    :arg filename: input file with application
    """
    try:
        file = managers.file_manager.open(file_access.FILE, None, filename, mode="rb")
    except Exception as error:
        warn("unable to open file: %s" % error)
    else:
        show("analyze application from %s" % filename)
        with closing(file):
            parser = Parser(builder=builder, notify=True, supress=True)
            try:
                parser.parse(file=file)
            except ParsingException as error:
                warn("unable to parse, line %s: %s" % (error.lineno, error))
            else:
                if not parser.result:
                    warn("no application")
                    return

                sections, types = parser.result
                information = sections.get("Information")
                if not information:
                    warn("no information")
                    return

                show("contains %s:%s" % (information.id, information.name.lower()))

                if parser.report:
                    if SHOW_ERRORS_ONLY:
                        entries = [line for line in parser.report if not line[1].startswith("Ignore")]
                        caption = "errors"
                    else:
                        entries = parser.report
                        caption = "notifications"

                    if entries:
                        with section(caption):
                            for lineno, message in entries:
                                show("%s at line %s" % (message, lineno))

                if parser.result:
                    with section("summary"):
                        for name in ("version", "server_version", "scripting_language"):
                            value = getattr(information, name) or "<empty>"
                            show(name.replace("_", " "), value)
                        show("used types", len(types))

                    with section("sections"):
                        for name, value in sections.items():
                            name = name.lower()
                            if name == "information":
                                continue

                            if isinstance(value, Structure):
                                with section(name.replace("_", " "), getattr(value, "_value", ABSENT)):
                                    for subname in dir(value):
                                        if subname[0] == "_":
                                            continue
                                        show(subname.replace("_", " "), getattr(value, subname))
                            elif value:
                                show(name, value)
                            else:
                                show(name)

                    with section("types"):
                        for uuid in sorted(types):
                            type = types[uuid]
                            show(uuid + (":%s" % type.name if type else ""))
