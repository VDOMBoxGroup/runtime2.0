
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ..auxiliary import section, show, warn
from .auxiliary import query


REQUEST = "<action name=\"state\"/>"
REQUEST_THREAD = "<action name=\"state\"><option name=\"thread\">%s</option></action>"
REQUES_OBJECT = "<action name=\"state\"><option name=\"object\">%s</option></action>"

SUMMARY = "SUMMARY"
THREAD = "THREAD"
OBJECT = "OBJECT"

MISSING = "MISSING"


def builder(parser):
    # <reply>
    def reply():
        result = Structure(process=None, resources=None, threads=[], objects=[],
            objects_count=None, garbage_count=None, collection=None)
        # <process>
        def process(id):
            result.process = id
            # <usage>
            def usage(utime, stime, maxrss, idrss, ixrss):
                result.resources = Structure(utime=utime, stime=stime, maxrss=maxrss, idrss=idrss, ixrss=ixrss)
            # </usage>
            return usage
        # </process>
        # <threads>
        def threads():
            # <thread>
            def thread(id, name, alive=None, smart=None, daemon=None):
                _stack = []
                # <stack>
                def stack():
                    # <frame>
                    def frame(name, path, line):
                        _stack.append((name, path, line))
                    # </frame>
                    return frame
                # </stack>
                result.threads.append((id, name, alive != "no", smart != "no", daemon == "yes", _stack))
                return stack
            # </thread>
            return thread
        # </threads>
        # <objects>
        def objects():
            # <object>
            def object(id, type):
                _attributes = []
                # <attributes>
                def attributes():
                    # <attribute>
                    def attribute(name):
                        context = Structure(id=None, type=None, value=None)
                        # <object>
                        def object(id, type):
                            context.id = id
                            context.type = type
                            context.value = yield VALUE
                        # </object>
                        yield object
                        _attributes.append((name, context.id, context.type, context.value))
                    # </attribute>
                    return attribute
                # </attributes>
                result.objects.append((id, type, _attributes))
                return attributes
            # </object>
            return object
        # </objects>
        # <garbage-collector>
        def garbage_collector():
            # <objects>
            def objects():
                result.objects_count = yield VALUE
            # </objects>
            # <garbage>
            def garbage():
                result.garbage_count = yield VALUE
            # </garbage>
            # <collection>
            def collection():
                result.collection = [None, None, None]
                context = Structure(index=0)
                # <generation>
                def generation():
                    if context.index > 2:
                        raise ParsingException("Too much generations")
                    result.collection[context.index] = yield VALUE
                    context.index += 1
                # </generation>
                return generation
            # </collection>
            return objects, garbage, collection
        # </garbage-collector>
        yield process, threads, objects, garbage_collector
        parser.accept(result)
    # </reply>
    return reply


def run(address=None, port=None, timeout=None, thread=None, object=None):
    """
    query server state
    :param address: specifies server address
    :key int port: specifies server port
    :key float timeout: specifies timeout to wait for reply
    :key thread: query thread state by its name or identifier
    :key object: query object state by its type name or identifier
    """
    try:
        if thread:
            caption = "query thread state"
            mode = THREAD
            request = REQUEST_THREAD % thread
        elif object:
            caption = "query object state"
            mode = OBJECT
            request = REQUES_OBJECT % object
        else:
            caption = "query state"
            mode = SUMMARY
            request = REQUEST

        message = query(caption, address, port, request, timeout=timeout)
        parser = Parser(builder=builder, notify=True, supress=True)
        result = parser.parse(message)
        if not result:
            raise Exception("Incorrect response")
    except ParsingException as error:
        warn("unable to parse, line %s: %s" % (error.lineno, error))
        raise
    else:
        if mode is SUMMARY:
            if result.process is not None:
                with section("process", result.process):
                    if result.resources is not None:
                        show("utime", result.resources.utime)
                        show("stime", result.resources.stime)
                        show("maxrss", result.resources.maxrss)
                        show("idrss", result.resources.idrss)
                        show("ixrss", result.resources.ixrss)

            if result.threads is not None:
                with section("threads", len(result.threads)):
                    for id, name, alive, smart, daemon, stack in result.threads:
                        details = [_f for _f in (id,
                            None if alive else "complete",
                            None if smart else "simple",
                            "daemon" if daemon else None) if _f]
                        show("%s (%s)" % (name, ", ".join(details)))

            if result.objects_count is not None:
                show("objects", result.objects_count)

            if result.garbage_count is not None:
                show("garbage", result.garbage_count)

            if result.collection is not None:
                show("collection", " / ".join(result.collection))

        elif mode is THREAD:
            if len(result.threads) != 1:
                show("no thread information")
            else:
                id, name, alive, smart, daemon, stack = result.threads[0]
                with section("summary"):
                    show("identifier", id)
                    show("name", name)
                    show("alive", "yes" if alive else "no")
                    show("smart", "yes" if smart else "no")
                    show("daemon", "yes" if daemon else "no")
                if stack:
                    with section("stack"):
                        for name, path, line in reversed(stack):
                            show("%s:%s:%s" % (path, name, line))

        elif mode is OBJECT:
            if len(result.objects) != 1:
                show("no object information")
            else:
                id, type, attributes = result.objects[0]
                with section("summary"):
                    show("id", id)
                    show("type", type)
                with section("attributes"):
                    for name, id, type, value in attributes:
                        if type == "NoneType":
                            show(name, "None")
                        elif value:
                            show(name, "%s (%s) = %s" % (type, id, value))
                        else:
                            show(name, "%s (%s)" % (type, id))
