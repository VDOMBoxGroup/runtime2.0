
from builtins import map
import re
import codecs


unsafe_symbols = " &+-*/%,;<=>^\b\f\n\r\t\v\0\'\"\\"
encode_regex = re.compile("(%s)" % "|".join(map(re.escape, unsafe_symbols)))


class JavaScriptCodec(codecs.Codec):

    def encode(self, input, errors="strict"):
        output = encode_regex.sub(lambda match: "\{0:03o}".format(ord(match.group(0))), input)
        return output, len(output)

    def decode(self, input, errors="strict"):
        raise NotImplementedError


class JavaScriptIncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        raise NotImplementedError


class JavaScriptIncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        raise NotImplementedError


class JavaScriptStreamReader(JavaScriptCodec, codecs.StreamReader):
    pass


class JavaScriptStreamWriter(JavaScriptCodec, codecs.StreamWriter):
    pass


def search(encoding):
    if encoding in ("js", "javascript"):
        return codecs.CodecInfo(name="javascript",
                encode=JavaScriptCodec().encode,
                decode=JavaScriptCodec().decode,
                incrementalencoder=JavaScriptIncrementalEncoder,
                incrementaldecoder=JavaScriptIncrementalDecoder,
                streamreader=JavaScriptStreamReader,
                streamwriter=JavaScriptStreamWriter)
    return None
