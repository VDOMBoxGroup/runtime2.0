

import codecs
import time
import datetime
from struct import Struct
from io import StringIO


ENCODING = "utf8"

TIMESTAMP_CODE = "d"
LENGTH_CODE = "L"


_encode = codecs.getencoder(ENCODING)
_decode = codecs.getdecoder(ENCODING)


def create_packer(format):
    name = "%sPacker" % format
    struct = Struct("=" + format.replace("S", LENGTH_CODE).replace("T", TIMESTAMP_CODE))
    pairs = tuple(("value%d" % index, symbol) for index, symbol in enumerate(format))

    formatting = {
        "name": name,
        "arguments": ", ".join(name for name, symbol in pairs),
        "strings": ", ".join(name for name, symbol in pairs if symbol == "S"),
        "encoding": ", ".join("str(%s).encode()" % name
            for name, symbol in pairs if symbol == "S"),
        "pack": ", ".join(("mktime(%s.timetuple())" % name if symbol == "T"
            else "len(%s)" % name if symbol == "S"
            else name)
            for name, symbol in pairs),
        "write": "\n".join("        stream.write(%s)" % name
            for name, symbol in pairs if symbol == "S"),
        "size": struct.size,
        "unpack": ", ".join(("%s_timestamp" % name if symbol == "T"
            else "%s_length" % name if symbol == "S"
            else name)
            for name, symbol in pairs),
        "decode": ", ".join(("fromtimestamp(%s_timestamp)" % name if symbol == "T"
            else "decode(stream.read(%s_length))[0]" % name if symbol == "S"
            else name)
            for name, symbol in pairs)}

    source = """
class %(name)s(object):
    def pack(self, %(arguments)s):
        %(strings)s=%(encoding)s
        return \"\".join((struct.pack(%(pack)s), %(strings)s))
    def pack_into(self, stream, %(arguments)s):
        %(strings)s=%(encoding)s
        stream.write(struct.pack(%(pack)s))
%(write)s
    def unpack(self, data):
        stream=StringIO(data[%(size)d:])
        %(unpack)s=struct.unpack_from(data)
        return %(decode)s
    def unpack_from(self, stream):
        data = stream.read(%(size)d)
        if data is None: return
        %(unpack)s=struct.unpack(data)
        return %(decode)s
        """ if "S" in format else """
class %(name)s(object):
    def pack(self, %(arguments)s):
        return struct.pack(%(pack)s)
    def pack_into(self, stream, %(arguments)s):
        stream.write(struct.pack(%(pack)s))
    def unpack(self, data):
        %(unpack)s=struct.unpack(data)
        return %(decode)s
    def unpack_from(self, stream):
        data = stream.read(%(size)d)
        if data is None: return
        %(unpack)s=struct.unpack(data)
        return %(decode)s
        """ if "T" in format else """
class %(name)s(object):
    def pack(self, %(arguments)s):
        return struct.pack(%(arguments)s)
    def pack_into(self, stream, %(arguments)s):
        stream.write(struct.pack(%(arguments)s))
    def unpack(self, data):
        return struct.unpack(data)
    def unpack_from(self, stream):
        data = stream.read(%(size)d)
        if data is None: return
        return struct.unpack(data)
        """

    namespace = {
        "struct": struct,
        "StringIO": StringIO,
        "encode": _encode,
        "decode": _decode,
        "mktime": time.mktime,
        "fromtimestamp": datetime.datetime.fromtimestamp}

    exec(source % formatting, namespace)
    return namespace[name]()
