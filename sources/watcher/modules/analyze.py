import codecs
import gc
from collections import defaultdict

from utils.checkinterval import maximal_check_interval
from .. import auxiliary
from ..auxiliary import select_objects, get_type_name


def analyze(options):
    gc.collect()

    source = options.get("source", use=auxiliary.verificators.objects_source)
    filter_by_server = options.get("filter", use=auxiliary.verificators.server_filter)
    group_by_name = options.get("group", use=auxiliary.verificators.objects_grouping)

    with maximal_check_interval:
        reference = defaultdict(int)
        for item in select_objects(server=filter_by_server, source=source):
            reference[type(item)] += 1

    if group_by_name:
        name_reference = defaultdict(list)
        for item, counter in reference.items():
            name_reference[get_type_name(target_type=item)].append(counter)
        iterator = ((name, "%d (%d)" % (sum(counters), len(counters)) if len(counters) > 1 else counters[0])
            for name, counters in name_reference.items())
    else:
        iterator = ((get_type_name(target_type=item), counter) for item, counter in reference.items())

    yield "<reply>"
    yield "<counters>"
    for name, counter in iterator:
        yield "<counter object=\"%s\">%s</counter>" % (codecs.encode(name, "xml"), counter)
    yield "</counters>"
    yield "</reply>"
