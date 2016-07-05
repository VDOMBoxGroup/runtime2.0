
import gc
from collections import defaultdict
from ..auxiliary import select_objects, get_type_name


SERVER_OPTION = "server"
NAME_OPTION = "name"


def analyze(options):
    if "objects" in options:
        filter_by_server = options.get("filter") == SERVER_OPTION
        group_by_name = options.get("group") == NAME_OPTION

        reference = defaultdict(int)
        for item in select_objects(server=filter_by_server):
            reference[type(item)] += 1

        if group_by_name:
            name_reference = defaultdict(list)
            for item, counter in reference.iteritems():
                name_reference[get_type_name(target_type=item)].append(counter)
            iterator = ((name, "%d (%d)" % (sum(counters), len(counters)) if len(counters) > 1
                else counters[0]) for name, counters in name_reference.iteritems())
        else:
            iterator = ((get_type_name(target_type=item), counter) for item, counter in reference.iteritems())

        yield "<reply>"
        yield "<counters>"
        for name, counter in iterator:
            yield "<counter object=\"%s\">%s</counter>" % (name.encode("xml"), counter)
        yield "</counters>"
        yield "</reply>"
    elif "garbage" in options:
        filter_by_server = options.get("filter") == SERVER_OPTION
        group_by_name = options.get("group") == NAME_OPTION

        reference = defaultdict(int)
        for item in select_objects(server=filter_by_server, source=gc.garbage):
            reference[type(item)] += 1

        if group_by_name:
            name_reference = defaultdict(list)
            for item, counter in reference.iteritems():
                name_reference[get_type_name(target_type=item)].append(counter)
            iterator = ((name, "%d (%d)" % (sum(counters), len(counters)) if len(counters) > 1
                else counters[0]) for name, counters in name_reference.iteritems())
        else:
            iterator = ((get_type_name(target_type=item), counter) for item, counter in reference.iteritems())

        yield "<reply>"
        yield "<counters>"
        for name, counter in iterator:
            yield "<counter object=\"%s\">%s</counter>" % (name.encode("xml"), counter)
        yield "</counters>"
        yield "</reply>"
