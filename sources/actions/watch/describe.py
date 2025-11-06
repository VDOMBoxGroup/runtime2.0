
from logs import console
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ..auxiliary import section, show
from .auxiliary import query


REQUEST = "<action name=\"describe\">%s</action>"
SOURCE_OBJECTS_OPTION = "<option name=\"source\">objects</option>"
SOURCE_GARBAGE_OPTION = "<option name=\"source\">garbage</option>"
SOURCE_CHANGES_OPTION = "<option name=\"source\">changes</option>"
FILTER_BY_SERVER_OPTION = "<option name=\"filter\">server</option>"

SORT_BY_NAME = "SORT BY NAME"
SORT_BY_COUNTER = "SORT BY COUNTYER"
SORT_VALUES = {
    "n": SORT_BY_NAME,
    "name": SORT_BY_NAME,
    "c": SORT_BY_COUNTER,
    "counter": SORT_BY_COUNTER
}

ORDER_BY_ASCENDING = "ORDER BY ASCENDING"
ORDER_BY_DESCENDING = "ORDER BY DESCENDING"
ORDER_VALUES = {
    "a": ORDER_BY_ASCENDING,
    "asc": ORDER_BY_ASCENDING,
    "ascending": ORDER_BY_ASCENDING,
    "d": ORDER_BY_DESCENDING,
    "desc": ORDER_BY_DESCENDING,
    "descending": ORDER_BY_DESCENDING
}


def sort_by_name(x):
    return x[0]


def sort_by_counter(x):
    return x[1], -x[2], x[0]


def builder(parser):
    # <reply>
    def reply():
        result = Structure(entries=None)
        # <descriptions>
        def descriptions():
            result.entries = []
            # <subgroup>
            def subgroup(name):
                subgroup = []
                result.entries.append((name, subgroup))
                # <description>
                def description(object):
                    value = yield VALUE
                    subgroup.append((object, value))
                # </description>
                return description
            # </subgroup>
            return subgroup
        # </descriptions>
        yield descriptions
        parser.accept(result)
    # </reply>
    return reply


def run(address=None, port=None, timeout=None,
        all=False, sort=None, order=None, limit=None,
        objects=False, garbage=False, changes=False):
    """
    describe server object changes
    :param address: specifies server address
    :key int port: specifies server port
    :key float timeout: specifies timeout to wait for reply
    :key switch all: disable objects filtering
    :key sort: sort entries by "name" or by "counter"
    :key order: sort entries "asc"ending or "desc"ending
    :key int limit: limit output
    :key switch objects: use all objects
    :key switch garbage: use objects from garbage
    :key switch changes: use changes
    """
    try:
        if sum((objects, garbage, changes)) > 1:
            raise Exception("Options \"objects\", \"garbage\" and \"changes\" are mutually exclusive")

        sort = SORT_VALUES.get((sort or "").lower(), SORT_BY_NAME)
        if sort is SORT_BY_COUNTER and order is None:
            order = "desc"
        order = ORDER_VALUES.get((order or "").lower(), ORDER_BY_ASCENDING)

        options = "".join([_f for _f in (
            SOURCE_OBJECTS_OPTION if objects else None,
            SOURCE_GARBAGE_OPTION if garbage else None,
            SOURCE_CHANGES_OPTION if changes else None,
            None if all else FILTER_BY_SERVER_OPTION,) if _f])
        request = REQUEST % options

        message = query("describe objects", address, port, request, timeout=timeout)
        parser = Parser(builder=builder, notify=True, supress=True)
        result = parser.parse(message)
        if not result:
            raise Exception("Incorrect response")
    except ParsingException as error:
        console.error("unable to parse, line %s: %s" % (error.lineno, error))
    except Exception as error:
        console.error(error)
    else:
        console.write()
        with section("objects"):
            if result.entries:
                key = sort_by_counter if sort is SORT_BY_COUNTER else sort_by_name
                reverse = order is ORDER_BY_DESCENDING
                entries = sorted(result.entries, key=key, reverse=reverse)
                if limit is not None:
                    entries = entries[:limit]
                for name, subgroup in entries:
                    with section(name):
                        for object, description in subgroup:
                            with section(object, lazy=False):
                                for part in description.split(" < "):
                                    show(part, longer=True)
            else:
                show("no objects")
