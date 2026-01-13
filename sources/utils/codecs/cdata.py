import codecs


class XmlCodec(codecs.Codec):
    def encode(self, input, errors="strict"):
        output = "<![CDATA[%s]]>" % input.replace("]]>", "]]]]><![CDATA[>")
        return output, len(output)

    def decode(self, input, errors="strict"):
        raise NotImplementedError


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
    if encoding == "cdata":
        return codecs.CodecInfo(
            name="cdata",
            encode=XmlCodec().encode,
            decode=XmlCodec().decode,
            incrementalencoder=XmlIncrementalEncoder,
            incrementaldecoder=XmlIncrementalDecoder,
            streamreader=XmlStreamReader,
            streamwriter=XmlStreamWriter,
        )
    return None
