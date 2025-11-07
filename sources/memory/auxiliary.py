import ast
import re
from io import StringIO
import binascii
import settings


CHUNK_SIZE = (settings.RESOURCE_LINE_LENGTH // 4) * 3
READ_CHUNK_COUNT = 1000

INDEX_LINE_REGEX = re.compile(r"^(?P<uuid>[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})\:(?P<name>[A-Z]\w*)$", re.IGNORECASE)
STRANGE_REGEX = re.compile(r"^\n\t+$")
DEREFERENCE_REGEX = re.compile(r"\#RES\(([A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})\)", re.IGNORECASE)


def wrapfilelike(function):
    def wrapper(*arguments, **keywords):
        filelike = keywords.get("filelike")
        if not filelike:
            keywords["filelike"] = filelike = StringIO()
            function(*arguments, **keywords)
            return filelike.getvalue()
    return wrapper


def source_is_empty(source):
    tree = ast.parse(source, mode="exec")
    iterator = ast.walk(tree)
    try:
        next(iterator)
        next(iterator)
        return False
    except StopIteration:
        return True


def write_as_base64(file, data, indent=""):
    for position in range(0, len(data), CHUNK_SIZE):
        file.write(indent + binascii.b2a_base64(data[position:position + CHUNK_SIZE]).decode())


def copy_as_base64(target, source, indent=""):
    # target.write(base64.b64encode(source))
    with source:
        while 1:
            chunk = source.read(CHUNK_SIZE * READ_CHUNK_COUNT)
            if chunk:
                write_as_base64(target, chunk, indent=indent)
            else:
                break


def clean_attribute_value(value):
    if STRANGE_REGEX.match(value):
        return u""
    else:
        return DEREFERENCE_REGEX.sub(lambda match: match.group(1), value)


def clean_source_code(source_code):
    clean_source_code = source_code.strip()
    if clean_source_code:
        return source_code
    else:
        return clean_source_code


def parse_index_line(value):
    match = INDEX_LINE_REGEX.match(value.decode('utf-8'))
    if match:
        return match.group("uuid"), match.group("name")
    else:
        raise ValueError(value)
