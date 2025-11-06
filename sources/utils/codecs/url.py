


import codecs
import urllib.request, urllib.parse, urllib.error


class UrlCodec(codecs.Codec):

    def encode(self, input, errors='strict'):
        output = urllib.parse.quote_plus(input)
        return output, len(output)

    def decode(self, input, errors='strict'):
        output = urllib.parse.unquote(input)
        return output, len(output)


class UrlIncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        raise NotImplementedError


class UrlIncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        raise NotImplementedError


class UrlStreamReader(UrlCodec, codecs.StreamReader):
    pass


class UrlStreamWriter(UrlCodec, codecs.StreamWriter):
    pass


def search(encoding):
    if encoding == 'url':
        return codecs.CodecInfo(name='url',
                encode=UrlCodec().encode,
                decode=UrlCodec().decode,
                incrementalencoder=UrlIncrementalEncoder,
                incrementaldecoder=UrlIncrementalDecoder,
                streamreader=UrlStreamReader,
                streamwriter=UrlStreamWriter)
    return None
