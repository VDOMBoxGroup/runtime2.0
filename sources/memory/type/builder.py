
from builtins import map
import string
import base64

# FIXME TODO jsmin has issue with RegExp conditions.
# try:
#     import jsmin
# except ImportError as err:
jsmin = None

import file_access
import settings
import managers

from utils.parsing import \
    SectionMustPrecedeError, MissingSectionError, \
    UnexpectedElementValueError, UnexpectedAttributeValueError, \
    MissingElementError, MissingAttributeError

from ..constants import PYTHON_EXTENSION


def type_builder(parser, installation_callback=None):
    "legacy"  # select legacy builder mode
    # TODO: Check attributes values for validity
    def document_handler(name, attributes):
        if name == u"Type":
            # <Type>
            type = managers.memory.types.new_sketch(restore=True)
            sections = {}
            def type_handler(name, attributes):
                sections[name] = True
                if name == u"Information":
                    # <Information>
                    def information_handler(name, attributes):
                        if name == u"ID" or name == u"ExtRef":
                            # <ID>
                            def id_handler(value): type.id = value.lower()
                            parser.handle_value(name, attributes, id_handler)
                            # </ID>
                        elif name == u"Name":
                            # <Name>
                            def name_handler(value): type.name = value
                            parser.handle_value(name, attributes, name_handler)
                            # </Name>
                        elif name == u"DisplayName":
                            # <DisplayName>
                            def displayname_handler(value): type.display_name = value
                            parser.handle_value(name, attributes, displayname_handler)
                            # </DisplayName>
                        elif name == u"ClassName":
                            # <ClassName>
                            def classname_handler(value): type.class_name = value
                            parser.handle_value(name, attributes, classname_handler)
                            # </ClassName>
                        elif name == u"Description":
                            # <Description>
                            def description_handler(value): type.description = value
                            parser.handle_value(name, attributes, description_handler)
                            # </Description>
                        elif name == u"Version" or name == u"Tversion":
                            # <Version>
                            def version_handler(value): type.version = value
                            parser.handle_value(name, attributes, version_handler)
                            # </Version>
                        elif name == u"Category":
                            # <Category>
                            def category_handler(value): type.category = value
                            parser.handle_value(name, attributes, category_handler)
                            # </Category>
                        elif name == u"InterfaceType":
                            # <InterfaceType>
                            def interfacetype_handler(value): type.interface_type = value
                            parser.handle_value(name, attributes, interfacetype_handler)
                            # </InterfaceType>
                        elif name == u"Icon" or name == u"IconObject":
                            # <Icon>
                            def icon_handler(value): type.icon = value
                            parser.handle_value(name, attributes, icon_handler)
                            # </Icon>
                        elif name == u"EditorIcon" or name == u"WYSIWYG-IconObject":
                            # <EditorIcon>
                            def editoricon_handler(value): type.editor_icon = value
                            parser.handle_value(name, attributes, editoricon_handler)
                            # </EditorIcon>
                        elif name == u"StructureIcon" or name == u"MinIconObject":
                            # <StructureIcon>
                            def structureicon_handler(value): type.structure_icon = value
                            parser.handle_value(name, attributes, structureicon_handler)
                            # </StructureIcon>
                        elif name == u"Dynamic":
                            # <Dynamic>
                            def dynamic_handler(value):
                                try:
                                    type.dynamic = int(value)
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, dynamic_handler)
                            # </Dynamic>
                        elif name == u"Invisible":
                            # <Invisible>
                            def invisible_handler(value):
                                try:
                                    type.invisible = int(value)
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, invisible_handler)
                            # </Invisible>
                        elif name == u"Moveable":
                            # <Moveable>
                            def moveable_handler(value):
                                try:
                                    type.moveable = int(value)
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, moveable_handler)
                            # </Moveable>
                        elif name == u"Resizable":
                            # <Resizable>
                            def resizable_handler(value):
                                try:
                                    type.resizable = int(value)
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, resizable_handler)
                            # </Resizable>
                        elif name == u"OptimizationPriority" or name == u"OptHierarchy":
                            # <OptimizationPriority>
                            def optimizationpriority_handler(value):
                                try:
                                    type.optimization_priority = int(value)
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, optimizationpriority_handler)
                            # </OptimizationPriority>
                        elif name == u"Container":
                            # <Container>
                            def container_handler(value):
                                try:
                                    type.container = int(value)
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, container_handler)
                            # </Container>
                        elif name == u"Containers" or name == u"ContainerSupported":
                            # <Containers>
                            def containers_handler(value):
                                try:
                                    type.containers = list(map(str.strip, value.split(u","))) if value else []
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, containers_handler)
                            # </Containers>
                        elif name == u"RenderType":
                            # <RenderType>
                            def rendertype_handler(value): type.render_type = value.lower()
                            parser.handle_value(name, attributes, rendertype_handler)
                            # </RenderType>
                        elif name == u"HTTPContentType":
                            # <HTTPContentType>
                            def httpcontenttype_handler(value): type.http_content_type = value
                            parser.handle_value(name, attributes, httpcontenttype_handler)
                            # </HTTPContentType>
                        elif name == u"Handlers":
                            # <Handlers>
                            def handlers_handler(value):
                                try:
                                    type.handlers = [_f for _f in map(str.strip, value.split(u",")) if _f]
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                                for handler_name in type.handlers:
                                    managers.dispatcher.add_handler(type, handler_name)
                            parser.handle_value(name, attributes, handlers_handler)
                            # </Handlers>
                        elif name == u"RemoteMethods":
                            # <RemoteMethods>
                            def remotemethods_handler(value):
                                # type.remote_methods = value
                                try:
                                    type.remote_methods = [_f for _f in map(str.strip, value.split(u",")) if _f]
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                                for handler_name in type.remote_methods:
                                    managers.dispatcher.add_remote_method(type, handler_name)
                            parser.handle_value(name, attributes, remotemethods_handler)
                            # </RemoteMethods>
                        elif name == u"Languages" or name == u"SupportedLanguage":
                            # <Languages>
                            def languages_handler(value):
                                try:
                                    type.languages = list(map(str.strip, value.split(u",")))
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, languages_handler)
                            # </Languages>
                        elif name == "WCAG":
                            # <WCAG>
                            parser.handle_elements(name, attributes)
                            # </WCAG>
                        elif name == "XMLScriptName":
                            # <XMLScriptName>
                            parser.handle_elements(name, attributes)
                            # </XMLScriptName>
                        else:
                            parser.reject_elements(name, attributes)
                    def close_information_handler(name):
                        if type.id is None:
                            raise MissingElementError(u"ID")
                        if type.name is None:
                            raise MissingElementError(u"Name")
                        if installation_callback:
                            installation_callback(type)
                    parser.handle_elements(name, attributes, information_handler, close_information_handler)
                    # </Information>
                elif name == u"Attributes":
                    # <Attributes>
                    def attributes_handler(name, attributes):
                        if name == u"Attribute":
                            # <Attribute>
                            attribute = type.attributes.new_sketch(restore=True)
                            def attribute_handler(name, attributes):
                                if name == u"Name":
                                    # <Name>
                                    def name_handler(value): attribute.name = value
                                    parser.handle_value(name, attributes, name_handler)
                                    # </Name>
                                elif name == u"DisplayName":
                                    # <DisplayName>
                                    def displayname_handler(value): attribute.display_name = value
                                    parser.handle_value(name, attributes, displayname_handler)
                                    # </DisplayName>
                                elif name == u"Description" or name == u"Help":
                                    # <Description>
                                    def description_handler(value): attribute.description = value
                                    parser.handle_value(name, attributes, description_handler)
                                    # </Description>
                                elif name == u"DefaultValue":
                                    # <DefaultValue>
                                    def defaultvalue_handler(value): attribute.default_value = value
                                    parser.handle_value(name, attributes, defaultvalue_handler)
                                    # </DefaultValue>
                                elif name == u"RegularExpressionValidation":
                                    # <RegularExpressionValidation>
                                    # TODO: Verify accept anything in case of empty pattern
                                    # Here "or .*" is the hack to handle <RegularExpressionValidation/> elements
                                    def validationpattern_handler(value): attribute.validation_pattern = value or ".*"
                                    parser.handle_value(name, attributes, validationpattern_handler)
                                    # </RegularExpressionValidation>
                                elif name == u"ErrorValidationMessage":
                                    # <ErrorValidationMessage>
                                    def validationerrormessage_handler(value): attribute.validation_error_message = value
                                    parser.handle_value(name, attributes, validationerrormessage_handler)
                                    # </ErrorValidationMessage>
                                elif name == u"Visible":
                                    # <Visible>
                                    def visible_handler(value):
                                        try:
                                            attribute.visible = int(value)
                                        except ValueError:
                                            raise UnexpectedElementValueError(name)
                                    parser.handle_value(name, attributes, visible_handler)
                                    # </Visible>
                                elif name == u"InterfaceType":
                                    # <InterfaceType>
                                    def interfacetype_handler(value):
                                        try:
                                            # Here "or 0" is the hack to handle <InterfaceType/> elements
                                            attribute.interface_type = int(value or "0")
                                        except ValueError:
                                            raise UnexpectedElementValueError(name)
                                    parser.handle_value(name, attributes, interfacetype_handler)
                                    # </InterfaceType>
                                elif name == u"CodeInterface":
                                    # <InterfaceType>
                                    def codeinterface_handler(value): attribute.code_interface = value
                                    parser.handle_value(name, attributes, codeinterface_handler)
                                    # </InterfaceType>
                                elif name == u"ColorGroup" or name == u"Colorgroup":
                                    # <ColorGroup>
                                    def colorgroup_handler(value): attribute.color_group = value
                                    parser.handle_value(name, attributes, colorgroup_handler)
                                    # </ColorGroup>
                                elif name == u"Complexity":
                                    # <Complexity>
                                    def complexity_handler(value): attribute.complexity = int(value)
                                    parser.handle_value(name, attributes, complexity_handler)
                                    # </Complexity>
                                else:
                                    parser.reject_elements(name, attributes)
                            def close_attribute_handler(name):
                                if attribute.name is None:
                                    raise MissingElementError(u"Name")
                                if attribute.display_name is None:
                                    attribute.display_name = attribute.name
                                ~attribute
                            parser.handle_elements(name, attributes, attribute_handler, close_attribute_handler)
                            # </Attribute>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, attributes_handler)
                    # </Attributes>
                elif name == u"Languages" or name == u"LanguageData":
                    # <Languages>
                    def languages_handler(name, attributes):
                        if name == u"Language":
                            # <Language>
                            try:
                                language_code = attributes.pop(u"Code")
                            except KeyError:
                                raise MissingAttributeError(u"Code")
                            def language_handler(name, attributes):
                                if name == u"Sentence":
                                    # <Sentence>
                                    try:
                                        sentence_id = int(attributes.pop(u"ID"))
                                    except ValueError:
                                        raise UnexpectedAttributeValueError(u"ID")
                                    except KeyError:
                                        raise MissingAttributeError(u"ID")
                                    def sentence_handler(value): type.sentences[language_code][sentence_id] = value
                                    parser.handle_value(name, attributes, sentence_handler)
                                    # </Sentence>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, language_handler)
                            # </Language>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, languages_handler)
                    # </Languages>
                elif name == u"Resources":
                    # <Resources>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    def resources_handler(name, attributes):
                        if name == u"Resource":
                            # <Resource>
                            try:
                                resource_id = attributes.pop(u"ID")
                            except KeyError:
                                raise MissingAttributeError(u"ID")
                            try:
                                resource_name = attributes.pop(u"Name")
                            except KeyError:
                                raise MissingAttributeError(u"Name")
                            try:
                                resource_type = attributes.pop(u"Type")
                            except KeyError:
                                raise MissingAttributeError(u"Type")
                            def resource_handler(value):
                                data = base64.b64decode(value)
                                if resource_type == 'js' and jsmin is not None:
                                    data = jsmin.jsmin(data, quote_chars="'\"`")
                                managers.resource_manager.add_resource(type.id, None,
                                    {"id": resource_id, "name": resource_name, "res_format": resource_type},
                                    data, optimize=0)
                            parser.handle_value(name, attributes, resource_handler)
                            # </Resource>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, resources_handler)
                    # </Resources>
                elif name == u"SourceCode" or name == u"Sourcecode" or name == u"PythonClassSourceCode":
                    # <SourceCode>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    def handle_sourcecode(value):
                        # managers.file_manager.write(file_access.MODULE, type.id,
                        #     settings.TYPE_MODULE_NAME + PYTHON_EXTENSION, value, encoding="utf8")
                        if installation_callback:
                            type.source_code = value
                    parser.handle_value(name, attributes, handle_sourcecode)
                    # </SourceCode>
                elif name == u"Libraries":
                    # <Libraries>
                    def libraries_handler(name, attributes):
                        if name == u"Library":
                            # <Library>
                            try:
                                library_target = attributes.pop(u"Target").lower()
                            except KeyError:
                                raise MissingAttributeError(u"Target")
                            def library_handler(value):
                                if library_target:
                                    type.libraries[library_target].append(value)
                            parser.handle_value(name, attributes, library_handler)
                            # </Library>
                        elif name == u"ExternalLibrary" or name == u"ExtLibrary":
                            # <ExtLibrary>
                            try:
                                external_library_target = attributes.pop(u"Target")
                            except KeyError:
                                raise MissingAttributeError(u"Target")
                            def external_library_handler(value):
                                if external_library_target:
                                    type.external_libraries[external_library_target].append(value)
                            parser.handle_value(name, attributes, external_library_handler)
                            # </ExtLibrary>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, libraries_handler)
                    # </Libraries>
                elif name == u"E2VDOM" or name == u"E2vdom":
                    # <E2VDOM>
                    def e2vdom_handler(name, attributes):
                        if name == u"Events":
                            # <Events>
                            def events_handler(name, attributes):
                                if name == u"UserInterfaceEvents" or name == u"Userinterfaceevents":
                                    # <UserInterfaceEvents>
                                    def userinterface_handler(name, attributes):
                                        if name == u"Event":
                                            # <Event>
                                            event = type.user_interface_events.new_sketch(restore=True)
                                            try:
                                                event.name = attributes.pop(u"Name")
                                            except KeyError:
                                                raise MissingAttributeError(u"Name")
                                            try:
                                                event.description = attributes.pop(u"Description")
                                            except KeyError:
                                                try:
                                                    event.description = attributes.pop(u"Help")
                                                except KeyError:
                                                    pass
                                            def event_handler(name, attributes):
                                                if name == u"Parameters":
                                                    # <Parameters>
                                                    def parameters_handler(name, attributes):
                                                        if name == u"Parameter":
                                                            # <Parameter>
                                                            parameter = event.parameters.new_sketch(restore=True)
                                                            try:
                                                                parameter.name = attributes.pop(u"Name")
                                                            except KeyError:
                                                                raise MissingAttributeError(u"Name")
                                                            try:
                                                                parameter.description = attributes.pop(u"Description")
                                                            except KeyError:
                                                                try:
                                                                    parameter.description = attributes.pop(u"Help")
                                                                except KeyError:
                                                                    pass
                                                            try:
                                                                # Here "or 0" is the hack to handle Order="" attributes
                                                                parameter.order = int(attributes.pop(u"Order") or "0")
                                                            except KeyError:
                                                                pass
                                                            except ValueError:
                                                                raise UnexpectedAttributeValueError(u"Order")
                                                            if "VbType" in attributes:
                                                                attributes.pop("VbType")
                                                            else:
                                                                pass  # Just skip attribute
                                                            ~parameter
                                                            parser.handle_elements(name, attributes)
                                                            # </Parameter>
                                                        else:
                                                            parser.reject_elements(name, attributes)
                                                    parser.handle_elements(name, attributes, parameters_handler)
                                                    # </Parameters>
                                                else:
                                                    parser.reject_elements(name, attributes)
                                            def close_event_handler(name):
                                                ~event
                                            parser.handle_elements(name, attributes, event_handler, close_event_handler)
                                            # </Event>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    parser.handle_elements(name, attributes, userinterface_handler)
                                    # </UserInterfaceEvents>
                                elif name == u"ObjectEvents" or name == u"Objectevents":
                                    # <ObjectEvents>
                                    def objectevents_handler(name, attributes):
                                        if name == u"Event":
                                            # <Event>
                                            event = type.object_events.new_sketch(restore=True)
                                            try:
                                                event.name = attributes.pop(u"Name")
                                            except KeyError:
                                                raise MissingAttributeError(u"Name")
                                            try:
                                                event.description = attributes.pop(u"Description")
                                            except KeyError:
                                                try:
                                                    event.description = attributes.pop(u"Help")
                                                except KeyError:
                                                    pass
                                            def event_handler(name, attributes):
                                                if name == u"Parameters":
                                                    # <Parameters>
                                                    def parameters_handler(name, attributes):
                                                        if name == u"Parameter":
                                                            # <Parameter>
                                                            parameter = event.parameters.new_sketch(restore=True)
                                                            try:
                                                                parameter.name = attributes.pop(u"Name")
                                                            except KeyError:
                                                                raise MissingAttributeError(u"Name")
                                                            try:
                                                                parameter.description = attributes.pop(u"Description")
                                                            except KeyError:
                                                                try:
                                                                    parameter.description = attributes.pop(u"Help")
                                                                except KeyError:
                                                                    pass
                                                            try:
                                                                # Here "or 0" is the hack to handle Order="" attributes
                                                                parameter.order = int(attributes.pop(u"Order") or 0)
                                                            except KeyError:
                                                                pass
                                                            except ValueError:
                                                                raise UnexpectedAttributeValueError(u"Order")
                                                            ~parameter
                                                            parser.handle_elements(name, attributes)
                                                            # </Parameter>
                                                        else:
                                                            parser.reject_elements(name, attributes)
                                                    parser.handle_elements(name, attributes, parameters_handler)
                                                    # </Parameters>
                                                else:
                                                    parser.reject_elements(name, attributes)
                                            def close_event_handler(self, name):
                                                ~event
                                            parser.handle_elements(name, attributes, event_handler, close_event_handler)
                                            # </Event>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    parser.handle_elements(name, attributes, objectevents_handler)
                                    # </ObjectEvents>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, events_handler)
                            # </Events>
                        elif name == u"Actions":
                            # <Actions>
                            def actions_handler(name, attributes):
                                if name == u"Container":
                                    # <Container ID=u"">
                                    try:
                                        container_id = attributes.pop(u"ID", None)
                                    except KeyError:
                                        raise MissingAttributeError(u"ID")
                                    def container_handler(name, attributes):
                                        if name == u"Action":
                                            # <Action>
                                            action = type.actions.new_sketch(restore=True)
                                            action.scope = container_id
                                            try:
                                                action.name = attributes.pop(u"Name")
                                            except KeyError:
                                                try:
                                                    action.name = attributes.pop(u"MethodName")
                                                except KeyError:
                                                    raise MissingAttributeError(u"Name")
                                            try:
                                                action.display_name = attributes.pop(u"DisplayName")
                                            except KeyError:
                                                try:
                                                    action.display_name = attributes.pop(u"InterfaceName")
                                                except KeyError:
                                                    pass
                                            try:
                                                action.description = attributes.pop(u"Description")
                                            except KeyError:
                                                try:
                                                    action.description = attributes.pop(u"Help")
                                                except KeyError:
                                                    pass
                                            def action_handler(name, attributes):
                                                if name == u"Parameters":
                                                    # <Parameters>
                                                    def parameters_handler(name, attributes):
                                                        if name == u"Parameter":
                                                            # <Parameter>
                                                            parameter = action.parameters.new_sketch(restore=True)
                                                            try:
                                                                parameter.name = attributes.pop(u"Name")
                                                            except KeyError:
                                                                try:
                                                                    parameter.name = attributes.pop(u"ScriptName")
                                                                except KeyError:
                                                                    raise MissingAttributeError(u"Name")
                                                            try:
                                                                parameter.display_name = attributes.pop(u"DisplayName")
                                                            except KeyError:
                                                                try:
                                                                    parameter.display_name = attributes.pop(u"InterfaceName")
                                                                except KeyError:
                                                                    pass
                                                            try:
                                                                parameter.description = attributes.pop(u"Description")
                                                            except KeyError:
                                                                try:
                                                                    parameter.description = attributes.pop(u"Help")
                                                                except KeyError:
                                                                    pass
                                                            try:
                                                                parameter.default_value = attributes.pop(u"DefaultValue")
                                                            except KeyError:
                                                                pass
                                                            try:
                                                                parameter.validation_pattern = attributes.pop(u"RegularExpressionValidation")
                                                            except KeyError:
                                                                pass
                                                            try:
                                                                parameter.interface = attributes.pop(u"Interface")
                                                            except KeyError:
                                                                pass
                                                            ~parameter
                                                            parser.handle_elements(name, attributes)
                                                            # </Parameter>
                                                        else:
                                                            parser.reject_elements(name, attributes)
                                                    parser.handle_elements(name, attributes, parameters_handler)
                                                    # </Parameters>
                                                elif name == u"SourceCode" or name == u"Sourcecode":
                                                    # <SourceCode>
                                                    def sourcecode_handler(value):
                                                        action.source_code = value
                                                    parser.handle_value(name, attributes, sourcecode_handler)
                                                    # </SourceCode>
                                                else:
                                                    parser.reject_elements(name, attributes)
                                            def close_action_handler(name):
                                                ~action
                                            parser.handle_elements(name, attributes, action_handler, close_action_handler)
                                            # </Action>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    parser.handle_elements(name, attributes, container_handler)
                                    # </Container>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, actions_handler)
                            # </Actions>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, e2vdom_handler)
                    # </E2VDOM>
                else:
                    parser.reject_elements(name, attributes)
            def close_type_handler(name):
                if u"Information" not in sections:
                    raise MissingSectionError("Information")
                ~type
                parser.accept(type)
            parser.handle_elements(name, attributes, type_handler, close_type_handler)
            # </Type>
        else:
            parser.reject_elements(name, attributes)
    return document_handler
