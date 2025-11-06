
from ..auxiliary import subparser, lower


def encode_data(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")


def encode_cdata(value):
    return value.replace("]]>", "]]]]><![CDATA[>")


@subparser
def contents(self, selector, iterator):
    context = \
        self._parser.StartElementHandler, \
        self._parser.EndElementHandler
    chunks = []

    def data(chunk):
        chunks.append(encode_data(chunk))

    def cdata(chunk):
        chunks.append(chunk)

    def cdata_section():
        chunks.append("<![CDATA[")
        self._parser.CharacterDataHandler = cdata

    def close_cdata_section():
        chunks.append("]]>")
        self._parser.CharacterDataHandler = data

    def default(data):
        chunks.append(data)

    def element(name, attributes):
        chunks.append("<%s" % name)
        for name, value in attributes.items():
            chunks.append(" %s=\"%s\"" % (name, encode_data(value)))
        chunks.append(">")
        context = self._parser.EndElementHandler

        def close_element(name):
            chunks.append("</%s>" % name)
            self._parser.EndElementHandler = context

        self._parser.EndElementHandler = close_element

    def close_element(name):
        self._parser.CharacterDataHandler = None
        self._parser.StartCdataSectionHandler = None
        self._parser.EndCdataSectionHandler = None
        self._parser.DefaultHandler = None
        self._parser.StartElementHandler, \
            self._parser.EndElementHandler = context

        if iterator:
            try:
                iterator.send(u"".join(chunks))
            except StopIteration:
                pass

    self._parser.CharacterDataHandler = data
    self._parser.StartCdataSectionHandler = cdata_section
    self._parser.EndCdataSectionHandler = close_cdata_section
    self._parser.DefaultHandler = default
    self._parser.StartElementHandler = lower(element) if self._lower else element
    self._parser.EndElementHandler = close_element


CONTENTS = contents
