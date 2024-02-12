
import sys
import json
import managers
from StringIO import StringIO
from utils.structure import VDOM_structure
from utils.parsing import Parser, ParsingException, UnexpectedAttributeValueError, MissingAttributeError


class EventInfo(object):
    def __init__(self, event_source_id, event_name, event_parameters):
        self._event_source_id = event_source_id
        self._event_name = event_name
        self._event_parameters = event_parameters

    @property
    def event_source_id(self):
        return self._event_source_id

    @property
    def event_name(self):
        return self._event_name

    @property
    def event_parameters(self):
        return self._event_parameters


def calls_builder(parser):
    "legacy"  # select legacy builder mode
    def document_handler(name, attributes):
        if name == "Events" or name == "EVENTS":
            # <Events>
            structure = VDOM_structure(sid=None, appid=None, events=[], state=0)

            def events_handler(name, attributes):
                if name == "Application" or name == "APPLICATION":
                    # <Application>
                    try:
                        structure.appid=attributes.pop(u"ID")
                    except KeyError:
                        raise MissingAttributeError, u"ID"
                    parser.handle_elements(name, attributes)
                    # </Application>
                elif name == "Session" or name == "SESSION":
                    # <Session>
                    try:
                        structure.sid = attributes.pop(u"ID")
                    except KeyError:
                        raise MissingAttributeError(u"ID")
                    parser.handle_elements(name, attributes)
                    # </Session>
                elif name == "Event" or name == "EVENT":
                    # <Event>
                    try:
                        event_source_object_id = attributes.pop(u"ObjSrcID")
                    except KeyError:
                        try:
                            event_source_object_id = attributes.pop(u"objSrcID")
                        except KeyError:
                            raise MissingAttributeError(u"ObjSrcID")
                    event_source_object_id = "-".join(event_source_object_id[2:].split("_"))
                    try:
                        event_name = attributes.pop(u"Name")
                    except KeyError:
                        try:
                            event_name = attributes.pop(u"name")
                        except KeyError:
                            raise MissingAttributeError(u"Name")
                    event_parameters = {}

                    def event_handler(name, attributes):
                        if name == "Parameter" or name == "PARAMETER":
                            # <Parameter>
                            try:
                                parameter_name = attributes.pop(u"Name")
                            except KeyError:
                                try:
                                    parameter_name = attributes.pop(u"name")
                                except KeyError:
                                    raise MissingAttributeError(u"Name")

                            def parameter_handler(value):
                                event_parameters[parameter_name] = [value.replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').encode("utf8")]
                            parser.handle_value(name, attributes, parameter_handler)
                            # </Parameter>
                        else:
                            parser.reject_elements(name, attributes)

                    def close_event_handler(name):
                        structure.events.append(
                                                    EventInfo(event_source_object_id, event_name, event_parameters)
                                                )
                    parser.handle_elements(name, attributes, event_handler, close_event_handler)
                    # </Event>
                elif name == "SharedVariables" or name == "SV":
                    # <SV>
                    def shared_variables_handler(value):
                        # TODO: Check replaces...
                        managers.request_manager.current.shared_variables = \
                                                    json.loads(value.replace('&quot;', '"').replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&'))
                    parser.handle_value(name, attributes, shared_variables_handler)
                    # </SV>
                elif name == "State" or name == "STATE":
                    # <Session>
                    try:
                        structure.state = int(attributes.pop(u"Value"))
                    except ValueError:
                        raise UnexpectedAttributeValueError(u"Value")
                    except KeyError:
                        try:
                            structure.state = int(attributes.pop(u"value"))
                        except ValueError:
                            raise UnexpectedAttributeValueError(u"Value")
                        except KeyError:
                            raise MissingAttributeError(u"Value")
                    parser.handle_elements(name, attributes)
                    # </Session>
                else:
                    parser.reject_elements(name, attributes)

            def close_events_handler(name):
                parser.accept(structure)
            parser.handle_elements(name, attributes, events_handler, close_events_handler)
            # </Events>
        else:
            parser.reject_elements(name, attributes)
    return document_handler


def run(request):
    args = request.arguments().arguments()
    request.render_type = "e2vdom"
    datafield = args.get("datafield")
    sid = args.get("sid")
    if datafield:
        datafield = datafield[0]
    if sid and datafield:
        # debug(
        # 	u"- - - - - - - - - - - - - - - - - - - -\n"
        # 	u"%s\n"
        # 	u"- - - - - - - - - - - - - - - - - - - -\n" %
        # 	datafield)
        request.request_type = "action"
        try:
            ev = Parser(builder=calls_builder).parse(datafield)
        except ParsingException as error:
            debug("Unable to parse data: %s" % error)
        app = request.application()
        # TODO: Check ev.state for correct values - may be incorrect state value
        try:
            state = request.session().states[ev.state]
        except KeyError:
            state = None
        if app is None:
            request.set_application_id(ev.appid)
            app = request.application()
        if sid is None:
            sid = ev.sid
        if app.id != ev.appid:
            debug("Event: Application mismatch")
        elif state is None:
            debug("Event: Unknown state")
        elif sid != ev.sid:
            debug("Event: Session mismatch")
            rr = "<SESSIONISOVER />"
            request.write("<ACTIONS>%s</ACTIONS>" % rr.encode("utf-8"))
        else:
            request.last_state = state
            #debug("INCOMING STATE: %s"%request.last_state["#"])
            #request.add_header("Content-Type", "text/xml")
            request.add_header("Content-Type", "text/plain")
            r = {}
            err = None
            try:
                # print "E2VDOM >>>", ev.events
                for event_info in ev.events:
                    obj = app.objects.catalog.get(event_info.event_source_id)
                    if obj is None:
                        debug("Event: Incorrect source object")
                        continue
                    h = app.events.catalog.get((event_info.event_source_id, event_info.event_name))  # all
                    if h is None:
                        debug("Event: No such event")
                        continue
                    # for callee in h.callees:
                    # print "CALLEE >>>", callee
                    for callee in h.callees:
                        if not callee.is_action:
                            continue
                        params = event_info.event_parameters
                        params.update({
                            "sender": [event_info.event_source_id],
                            "sender_event": [event_info.event_name]
                        })
                        request.arguments().arguments(params)
                        request.container_id = callee.owner
                        result = managers.engine.execute(callee, render=1)
                        for key in result:
                            k_ob = app.objects.catalog.get(key)
                            k_ob_parent_id = k_ob.parent.id if k_ob.parent else ""
                            r[key] = (result[key], k_ob_parent_id, k_ob.type.container, k_ob.type.id)
            except Exception:
                sys.excepthook(*sys.exc_info())
                # from utils.tracing import format_exception_trace
                # debug("E2VDOM Action Error:\n%s" % format_exception_trace())
                import traceback
                traceback.print_exc()
                # from StringIO import StringIO
                # err = StringIO()
                # debug("Error: %s" % str(e))

            if err:
                if VDOM_CONFIG_1["DEBUG"] == "1":
                    request.write("<ERROR>%s</ERROR>"%err.getvalue().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))
                else:
                    request.write('<ERROR/>')
            else:
                if request.action_result:
                    request.write(request.action_result.getvalue().encode("utf-8"))

                rr = StringIO()
                for key in r:
                    rr.write("""<OBJECT ID="%s" PARENT="%s" CONTAINER="%s" TYPE="%s"><![CDATA[%s]]></OBJECT>\n""" % (key.replace("-", "_"), r[key][1].replace("-", "_"), r[key][2], r[key][3], r[key][0].replace("]"+"]>", "]]"+"]]><![CD"+"ATA[>")))
                request.write("<ACTIONS>%s</ACTIONS>" % rr.getvalue().encode("utf-8"))
                request.write("<SV>%s</SV>" % json.dumps(request.shared_variables).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))

            #debug("OUTCOMING STATE: %s"%(request.next_state or request.last_state)["#"])
            #request.write("<STATE value=\"%s\"/>"%0)
            request.write("<STATE value=\"%s\"/>"%(request.next_state or request.last_state)["#"])

            """
            print
            states=request.session().states
            for state in states: print state
                print
            """
