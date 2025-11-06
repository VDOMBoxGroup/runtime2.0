
from ..exceptions import UnexpectedElementError
from ..auxiliary import subparser, lower


@subparser
def value(self, selector, iterator):
    """
    Gather and return element's value
    """

    context = \
        self._parser.StartElementHandler, \
        self._parser.EndElementHandler
    chunks = []

    def data(chunk):
        # HACK: There's a could be a problem with reading files logic but this workaround is good enough for now
        if isinstance(chunk, str) and chunk.startswith("b'") and chunk.endswith("'"):
            chunk = chunk[2:-1]
        chunks.append(chunk)

    def element(name, attributes):
        if self._unexpected_element_handler:
            self._unexpected_element_handler(name, attributes)
        else:
            raise UnexpectedElementError(name, attributes)

        context = \
            self._parser.CharacterDataHandler, \
            self._parser.StartElementHandler, \
            self._parser.EndElementHandler

        def element(name, attributes):
            context = self._parser.EndElementHandler

            def close_element(name):
                self._parser.EndElementHandler = context

            self._parser.EndElementHandler = close_element

        def close_element(name):
            self._parser.CharacterDataHandler, \
                self._parser.StartElementHandler, \
                self._parser.EndElementHandler = context

        self._parser.CharacterDataHandler = None
        self._parser.StartElementHandler = element
        self._parser.EndElementHandler = close_element

    def close_element(name):
        self._parser.CharacterDataHandler = None
        self._parser.StartElementHandler, \
            self._parser.EndElementHandler = context

        if iterator:
            try:
                iterator.send(u"".join(chunks).strip())
            except StopIteration:
                pass

    self._parser.CharacterDataHandler = data
    self._parser.StartElementHandler = lower(element) if self._lower else element
    self._parser.EndElementHandler = close_element


VALUE = value
