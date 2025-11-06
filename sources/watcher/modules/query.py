import codecs
import sys
import gc

from utils import verificators
from utils.checkinterval import maximal_check_interval

from .. import auxiliary
from ..exceptions import WatcherError
from ..auxiliary import select_types, select_objects, select_profiler, \
    generate_graph, generate_call_graph_profile, generate_call_graph


SERVER_ONLY = "server only"


def server_only(value):
    if value == "server only":
        return True
    elif value == "":
        return False
    else:
        raise ValueError


def query(options):
    gc.collect()

    if "types" in options:
        server_filter = options.get("types", use=server_only)
        types = select_types(server=server_filter)

        yield "<reply>"
        yield "<types>"
        for type in types:
            yield "<type id=\"%08X\" name=\"%s\"/>" % (id(type), codecs.encode(type, "xml"))
        yield "</types>"
        yield "</reply>"
    elif "objects" in options:
        selector = options.get("objects", use=auxiliary.verificators.objects_selector)
        source = options.get("source", use=auxiliary.verificators.objects_source)
        with maximal_check_interval:
            uuids = {id(object) for object in select_objects(selector, source=source)}

        yield "<reply>"
        yield "<objects>"
        for uuid in uuids:
            yield "<object id=\"%08X\"/>" % uuid
        yield "</objects>"
        yield "</reply>"
    elif "referrers" in options:
        selector = options.get("referrers", use=auxiliary.verificators.objects_selector)
        source = options.get("source", use=auxiliary.verificators.objects_source)
        with maximal_check_interval:
            objects = select_objects(selector, source=source)
            try:
                uuids = {id(referrer) for referrer in gc.get_referrers(*objects)} \
                    - {id(sys._getframe()), id(objects)}
            finally:
                del objects

        yield "<reply>"
        yield "<referrers>"
        for uuid in uuids:
            yield "<referrer id=\"%08X\"/>" % uuid
        yield "</referrers>"
        yield "</reply>"
    elif "referents" in options:
        selector = options.get("referents", use=auxiliary.verificators.objects_selector)
        source = options.get("source", use=auxiliary.verificators.objects_source)
        with maximal_check_interval:
            objects = select_objects(selector, source=source)
            try:
                uuids = {id(referrer) for referrer in gc.get_referents(*objects)} \
                    - {id(sys._getframe()), id(objects)}
            finally:
                del objects

        yield "<reply>"
        yield "<referents>"
        for uuid in uuids:
            yield "<referent id=\"%08X\"/>" % uuid
        yield "</referents>"
        yield "</reply>"
    elif "graph" in options:
        selector = options.get("graph", use=auxiliary.verificators.objects_selector)
        filter = options.get("filter", use=auxiliary.verificators.objects_filter)
        source = options.get("source", use=auxiliary.verificators.objects_source)
        depth = options.get("depth", use=verificators.integer)
        minify = options.get("minify", use=verificators.boolean)

        keywords = {}
        if depth is not None:
            keywords["depth"] = depth
        if minify is not None:
            keywords["minify"] = minify
            keywords["skip_functions"] = minify

        with maximal_check_interval:
            objects = select_objects(selector, server=False, filter=filter, source=source)

            yield "<reply>"
            yield "<graph>"
            yield codecs.encode("".join(generate_graph(objects, **keywords)), "xml")
            yield "</graph>"
            yield "</reply>"
    elif "profile" in options:
        name = options.get("profile", use=auxiliary.verificators.profiler_name)
        data = select_profiler(name).load()

        yield "<reply>"
        if data is None:
            yield "<profile/>"
        else:
            yield "<profile>"
            yield codecs.encode(data.encode("base64"), "cdata")
            yield "</profile>"
        yield "</reply>"
    elif "call-graph" in options:
        name = options.get("call-graph", use=auxiliary.verificators.profiler_name)
        node_threshold = options.get("node-threshold", use=verificators.float)
        edge_threshold = options.get("edge-threshold", use=verificators.float)
        color_nodes = options.get("color-nodes", use=verificators.boolean)

        keywords = {}
        if node_threshold is not None:
            keywords["node_threshold"] = node_threshold
        if edge_threshold is not None:
            keywords["edge_threshold"] = edge_threshold
        if color_nodes is not None:
            keywords["color_nodes"] = color_nodes

        with select_profiler(name).hold() as location:
            if location is None:
                raise WatcherError("Unable to obtain statistics")
            profile = generate_call_graph_profile(location)
        data = generate_call_graph(profile, **keywords) if profile else None

        yield "<reply>"
        if data is None:
            yield "<call-graph/>"
        else:
            yield "<call-graph>"
            yield codecs.encode(data, "xml")
            yield "</call-graph>"
        yield "</reply>"
