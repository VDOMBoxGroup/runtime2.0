
from builtins import chr
import re
import codecs


decode_table = {"&lt;": "<", "&gt;": ">", "&quot;": "\"", "&apos;": "'", "&amp;": "&"}
decode_regex = re.compile("(?:&#(\d{1,5});)|(?:&#x(\d{1,5});)|(&\w{1,8};)")


class XmlCodec(codecs.Codec):

    def encode(self, input, errors='strict'):
        output = input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")
        return output, len(output)

    def decode(self, input, errors='strict'):
        def substitute(match):
            code, xcode, entity = match.group(1, 2, 3)
            return chr(int(code)) if code else chr(int(xcode, 16)) if xcode else decode_table.get(entity, entity)
        output = decode_regex.sub(substitute, input)
        return output, len(output)


class XmlIncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        raise NotImplementedError


class XmlIncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        raise NotImplementedError


class XmlStreamReader(XmlCodec, codecs.StreamReader):
    pass


class XmlStreamWriter(XmlCodec, codecs.StreamWriter):
    pass


def search(encoding):
    if encoding == 'xml':
        return codecs.CodecInfo(name='xml',
                encode=XmlCodec().encode,
                decode=XmlCodec().decode,
                incrementalencoder=XmlIncrementalEncoder,
                incrementaldecoder=XmlIncrementalDecoder,
                streamreader=XmlStreamReader,
                streamwriter=XmlStreamWriter)
    return None
