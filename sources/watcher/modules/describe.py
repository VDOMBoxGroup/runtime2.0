import codecs
import gc
from collections import defaultdict

from utils.tracing import describe_object, describe_reference
from utils.checkinterval import maximal_check_interval
from .. import auxiliary
from ..auxiliary import select_objects, get_type_name


REFERENCE_LIMIT = 800
REFERENCE_DEPTH = 16


def describe(options):
    gc.collect()

    source = options.get("source", use=auxiliary.verificators.objects_source)
    filter_by_server = options.get("filter", use=auxiliary.verificators.server_filter)

    reference = defaultdict(list)
    with maximal_check_interval:
        objects = select_objects(server=filter_by_server, source=source)
        exclude = objects,
        for object in objects:
            description = describe_reference(
                object, limit=REFERENCE_LIMIT, depth=REFERENCE_DEPTH, exclude=exclude)
            if description:
                reference[get_type_name(target_type=type(object))].append(
                    (describe_object(object), description))

    yield "<reply>"
    yield "<descriptions>"
    for name, items in reference.items():
        yield "<subgroup name=\"%s\">" % codecs.encode(name, "xml")
        for description, reference in items:
            yield "<description object=\"%s\">%s</description>" % (
                codecs.encode(description, "xml"), codecs.encode(reference, "xml"))
        yield "</subgroup>"
    yield "</descriptions>"
    yield "</reply>"
