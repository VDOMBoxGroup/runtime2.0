from json import JSONDecoder, JSONEncoder
from json.decoder import JSONObject, JSONArray
from json.scanner import py_make_scanner
from collections import OrderedDict
from .. import errors
from ..subtypes import array, boolean, date, dictionary, double, \
    empty, error, generic, integer, mismatch, nothing, null, string, \
    v_null, ordereddictionary


def wrap(value):
    def unknown(value):
        raise errors.system_error(u"Unexpected %s object" %
                                  value.__class__.__name__)
    return {
        array: lambda value: value,
        dictionary: lambda value: value,
        type(None): lambda value: v_null,
        bool: lambda value: boolean(value),
        float: lambda value: double(value),
        int: lambda value: integer(value),
        str: lambda value: string(value)} \
        .get(type(value), unknown)(value)


def vscript_parse_object(*arguments):
    subject, position = JSONObject(*arguments)
    # TODO: Remove this after upgrade to Python 2.7.11
    if isinstance(subject, list):
        subject = {}
    return dictionary({string(key): wrap(value) for key, value in subject.items()}), position


def vscript_parse_array(*arguments):
    subject, position = JSONArray(*arguments)
    return array([wrap(item) for item in subject]), position


class VScriptJSONDecoder(JSONDecoder):

    def __init__(self, *arguments, **keywords):
        JSONDecoder.__init__(self, *arguments, **keywords)
        self.parse_object = vscript_parse_object
        self.parse_array = vscript_parse_array
        self.scan_once = py_make_scanner(self)


class VScriptJSONEncoder(JSONEncoder):

    def default(self, value):
        def unknown(value):
            raise errors.system_error(
                u"Unexpected %s object" % value.__class__.__name__)
        return {
            array: lambda value: value.items,
            boolean: lambda value: bool(value.value),
            date: lambda value: str(value),
            dictionary: lambda value: {key.as_string: value
                                       for key, value in value.items.items()},
            double: lambda value: value.value,
            empty: lambda value: value.name,
            error: lambda value: value.name,
            generic: lambda value: value.name,
            integer: lambda value: value.value,
            mismatch: lambda value: str(value),
            nothing: lambda value: value.name,
            null: lambda value: None,
            ordereddictionary: lambda value: OrderedDict(
                [(k.as_string, v) for k, v in value.items.items()]
            ),
            string: lambda value: value.value
        }.get(type(value), unknown)(value)


def v_asjson(value):
    value = VScriptJSONDecoder().decode(value.as_string)
    return value if isinstance(value, (array, dictionary)) else wrap(value)


def v_tojson(value):
    return string(VScriptJSONEncoder().encode(value.subtype))
