
from itertools import chain
import managers
from memory import CONTAINER, TOP_CONTAINER


OBJECT_NAME = "Obj_%s"
TYPE_NAME = "VDOM_Type_%s"
OBJECT_TYPE_NAME = "VDOM_Obj_Type_%s"
ENGINE_NAME = "Obj_%s_EventEngine"
DISPATCHER_NAME = "Obj_%s_Dispatcher"
ELEMENT_NAME = "o_%s"


DEFAULT_RENDER_TYPE = "html"
DEFAULT_RENDER_CONTAINER = "2330fe83-8cd6-4ed5-907d-11874e7ebcf4"


DEFINE_ENGINE_AND_DISPATCHER = \
    u"if(typeof {engine_name}!=='undefined'){{" \
        "{engine_name}.stop();" \
        "delete {engine_name};" \
    "}}\n" \
    "if(typeof {dispatcher_name}!=='undefined'){{" \
        "delete {dispatcher_name};" \
    "}}\n" \
    "{dispatcher_name}=new VDOM_EventDispatcher();\n" \
    "{engine_name}=new VDOM_EventEngine({dispatcher_name}, EventQueue);"
ADD_DISPATCH_EVENT = u"{dispatcher_name}.addDispatchEvent({source}, {target});"

DEFINE_CLASS = \
    u"function {class_name}(id, eventEngine){{\n" \
        "this.Base=VDOM_Object;\n" \
        "this.Base(id, eventEngine);\n" \
        "{extra}" \
    "}};\n" \
    "{class_name}.prototype=new VDOM_Object;"\
    "\n"

DEFINE_CLASS_REGISTERATION = u"this.registerEvents([{events}]);"
DEFINE_CLASS_ACTION = \
    u"{class_name}.prototype.{name}=function({parameters}){{" \
        "{source}" \
    "}}"
DEFINE_BUBBLE_EVENT = \
    u"{object_name}.bubbleEvent=function(e){{" \
        "{object_name}.riseEvent('tfrEvent', e.parameters, {parent_engine_name});" \
    "}};"

DEFINE_OBJECT = u"{object_name}=new {prefix}{class_name}(\"{element_name}\", {engine_name});"

DEFINE_EVENT_QUEUE = u"if(typeof EventQueue === 'undefined')EventQueue=new VDOM_EventQueue;"
DEFINE_WINDOW_EVENT_QUEUE = u"if(typeof window.EventQueue === 'undefined')window.EventQueue=new VDOM_EventQueue;"

START_ENGINE = u"{engine_name}.start();"

INIT_OPEN = u"function initE2VDOM(){\n"
INIT_CLOSE = u"};\ninitE2VDOM();"

WINDOW_OPEN = u"(function(window, $){"
WINDOW_CLOSE = u"})(window, jQuery);"

DYNAMIC_OPEN = u"if (!('{class_name}' in window)){{"
DYNAMIC_CLOSE = u"window.{class_name} = {class_name};}}"

ON_READY_OPEN = u";jQuery(document).ready(function($){"
ON_READY_CLOSE = u"});"


def compile_registations(container, parent, dynamic):
    id4code = container._id.replace("-", "_")

    object_name = OBJECT_NAME % id4code
    engine_name = ENGINE_NAME % id4code
    dispatcher_name = DISPATCHER_NAME % id4code

    lines = []

    # lines.append(ON_READY_OPEN)

    lines.append(DEFINE_ENGINE_AND_DISPATCHER.format(
        engine_name=engine_name,
        dispatcher_name=dispatcher_name))

    
    #OBJECT_TYPE_NAME never used
    #lines.append(DEFINE_CLASS.format(
    #    class_name=OBJECT_TYPE_NAME % id4code,
    #    extra=""))
    
    
    def iterate_container_and_non_containers():
        yield container._origin
        for subobject in container._origin.objects.values():
            if subobject.is_non_container:
                yield subobject

    for object in iterate_container_and_non_containers():
        for event in object.events.values():
            for callee in event.callees:
                lines.append(ADD_DISPATCH_EVENT.format(
                    dispatcher_name=dispatcher_name,
                    source=u"\"{element_name}:{name}\"".format(
                        element_name=ELEMENT_NAME % event.source_object.id.replace("-", "_"),
                        name=event.name),
                    target="\"server\"" if callee.is_action else u"\"{object_name}:{name}({parameters})\"".format(
                        object_name=OBJECT_NAME % callee.target_object.id.replace("-", "_"),
                        name=callee.name,
                        parameters=", ".join((value.replace('"', r'\"') for value in callee.parameters.values())))))
        object_id4code = object.id.replace("-", "_")
        lines.append(DEFINE_OBJECT.format(
            object_name=OBJECT_NAME % object_id4code,
            prefix="window." if dynamic else "",
            class_name=TYPE_NAME % object.type.id.replace("-", "_"),
            element_name=ELEMENT_NAME % object_id4code,
            engine_name=engine_name))

    # for subobject in container._origin.objects.itervalues():
    #     subobject_id4code = subobject.id.replace("-", "_")
    #     lines.append(DEFINE_OBJECT.format(
    #         object_name=OBJECT_NAME % subobject_id4code,
    #         prefix="window." if dynamic else "",
    #         class_name=TYPE_NAME % subobject.type.id.replace("-", "_"),
    #         element_name=ELEMENT_NAME % subobject_id4code,
    #         engine_name=engine_name))

    # lines.append(DEFINE_OBJECT.format(
    #     object_name=object_name,
    #     prefix="",
    #     class_name=TYPE_NAME % container._origin.type.id.replace("-", "_"),
    #     element_name=ELEMENT_NAME % id4code,
    #     engine_name=engine_name))

    if parent:
        # TODO: check is there really must be "eventEngine" with lower case "e"
        # TODO: check is bubble events are really necessary?
        lines.append(DEFINE_BUBBLE_EVENT.format(
            object_name=object_name,
            # parent_engine_name="Obj_%s_eventEngine" % parent.replace("-", "_")))
            parent_engine_name=ENGINE_NAME % parent.replace("-", "_")))

    lines.append(START_ENGINE.format(
        engine_name=engine_name))

    # lines.append(ON_READY_CLOSE)

    return "\n".join(lines)


def compile_declaration(render_container, vdomtype, lines, dynamic=False):
    class_name = TYPE_NAME % vdomtype.id.replace("-", "_")

    if dynamic:
        lines.append(DYNAMIC_OPEN.format(class_name=class_name))

    events = ", ".join(["\"%s\"" % event.name
        for event in chain(iter(vdomtype.user_interface_events.values()), iter(vdomtype.object_events.values()))])
    lines.append(DEFINE_CLASS.format(
        class_name=class_name,
        extra=DEFINE_CLASS_REGISTERATION.format(events=events) if events else ""))

    actions = vdomtype.actions.get(render_container)  # was "2330fe83-8cd6-4ed5-907d-11874e7ebcf4"
    if actions:
        for action in actions:
            source_code = action.source_code.strip()
            lines.append(DEFINE_CLASS_ACTION.format(
                class_name=class_name,
                name=action.name,
                parameters=", ".join((parameter.name for parameter in action.parameters)),
                source=source_code))

    if dynamic:
        lines.append(DYNAMIC_CLOSE.format(class_name=class_name))

    lines.append("")  # just for code readability


def compile_declarations_n_libraries(types, render_type, render_container, registrations, dynamic=False):
    declarations = []

    if dynamic:
        declarations.append(WINDOW_OPEN)
        declarations.append(DEFINE_WINDOW_EVENT_QUEUE)
    else:
        declarations.append(DEFINE_EVENT_QUEUE)

    for vdomtype in types:
        #OBJECT_TYPE_NAME never used
        #if CONTAINER <= vdomtype.container <= TOP_CONTAINER:
        #    declarations.append(DEFINE_CLASS.format(
        #        class_name=TYPE_NAME % vdomtype.id.replace("-", "_"),
        #        extra=""))
            
        compile_declaration(render_container, vdomtype, declarations, dynamic=dynamic)

    if not dynamic:
        declarations.append(INIT_OPEN)

    declarations.extend(registrations)

    if dynamic:
        declarations.append(WINDOW_CLOSE)
        pass
    else:
        declarations.append(INIT_CLOSE)

    libraries = ("".join(library) for library in 
        (vdomtype.libraries[render_type] for vdomtype in types))

    return "\n".join(declarations), "\n".join(libraries)


# def compile_dynamic(container, actions=None):
#     id4code = container.id.replace("-", "_")

#     engine_name = ENGINE_NAME % id4code
#     dispatcher_name = DISPATCHER_NAME % id4code

#     lines = [DEFINE_WINDOW_EVENT_QUEUE]

#     for vdomtype in container._types:
#         compile_declaration(vdomtype, lines, in_window=True)

#     lines.append(DEFINE_ENGINE_AND_DISPATCHER.format(
#         engine_name=engine_name,
#         dispatcher_name=dispatcher_name))

#     if actions:

#         def escape_parameter(value):
#             if value and value[0] == '"':
#                 return "\"%s\"" % value[1:-1].replace('"', r'&quot;')
#             else:
#                 return value.replace('"', r'\"')

#         # actions = {(src_obj, event): [(dst_obj, action, param1, ...), ...], ...}
#         for event, actions in actions.iteritems():
#             for action in actions:
#                 lines.append(ADD_DISPATCH_EVENT.format(
#                     dispatcher_name=dispatcher_name,
#                     source="\"{element_name}:{name}\"".format(
#                         element_name=ELEMENT_NAME % event[0].replace("-", "_"),
#                         name=event[1]),
#                     target="\"{object_name}:{name}({parameters})\"".format(
#                         object_name=OBJECT_NAME % action[0].replace("-", "_"),
#                         name=action[1],
#                         parameters=", ".join(escape_parameter(value) for value in action[2:]))))

#     for event in container._origin.events.itervalues():
#         for callee in event.callees:
#             lines.append(ADD_DISPATCH_EVENT.format(
#                 dispatcher_name=dispatcher_name,
#                 source="\"{element_name}:{name}\"".format(
#                     element_name=ELEMENT_NAME % event.source_object.id.replace("-", "_"),
#                     name=event.name),
#                 target="\"server\"" if callee.is_action else "\"{object_name}:{name}({parameters})\"".format(
#                     object_name=OBJECT_NAME % callee.target_object.replace("-", "_"),
#                     name=callee.name,
#                     parameters=", ".join((value.replace('"', r'\"') for name, value in callee.parameters)))))

#     for subobject in container.objects.catalog.itervalues():
#         subobject_id4code = subobject.id.replace("-", "_")
#         lines.append(DEFINE_OBJECT.format(
#             object_name=OBJECT_NAME % subobject_id4code,
#             class_name=TYPE_NAME % subobject.type.id.replace("-", "_"),
#             element_name=ELEMENT_NAME % subobject_id4code,
#             engine_name=engine_name))

#     lines.append(START_ENGINE.format(
#         engine_name=engine_name))

#     return "\n".join(lines)
