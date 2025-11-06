


import gprof2dot
from io import StringIO


DEFAULT_NODE_THRESHOLD = 0.5
DEFAULT_EDGE_THRESHOLD = 0.1
DEFAULT_COLOR_NODES = True


def generate_call_graph_profile(location):
    try:
        return gprof2dot.PstatsParser(location).parse()
    except IOError:
        return None


def generate_call_graph(profile, node_threshold=DEFAULT_NODE_THRESHOLD,
        edge_threshold=DEFAULT_EDGE_THRESHOLD, color_nodes=DEFAULT_COLOR_NODES):
    profile.prune(node_threshold / 100.0, edge_threshold / 100.0, color_nodes)
    filelike = StringIO()
    dot = gprof2dot.DotWriter(filelike)
    dot.graph(profile, gprof2dot.TEMPERATURE_COLORMAP)
    return filelike.getvalue()
