
import re
from ..exceptions import UnexpectedElementError
from ..auxiliary import subparser, lower


SPACES = re.compile(r"[\r\n\s\t]+", re.IGNORECASE | re.MULTILINE)


@subparser
def words(self, selector, iterator):
    """
    Gather and return element's value with cleanup negligible spaces
    """

    context = \
        self._parser.StartElementHandler, \
        self._parser.EndElementHandler
    chunks, chunks2clean = [], []

    def data(chunk):
        chunks2clean.append(chunk)

    def cdata(chunk):
        chunks.append(u" ".join([_f for _f in SPACES.split(u"".join(chunks2clean)) if _f]))
        del chunks2clean[:]
        chunks.append(chunk)

    def cdata_section():
        self._parser.CharacterDataHandler = cdata

    def close_cdata_section():
        self._parser.CharacterDataHandler = data

    def element(name, attributes):
        if self._unexpected_element_handler:
            self._unexpected_element_handler(name, attributes)
        else:
            raise UnexpectedElementError(name, attributes)

        context = \
            self._parser.CharacterDataHandler, \
            self._parser.StartCdataSectionHandler, \
            self._parser.EndCdataSectionHandler, \
            self._parser.StartElementHandler, \
            self._parser.EndElementHandler

        def element(name, attributes):
            context = self._parser.EndElementHandler

            def close_element(name):
                self._parser.EndElementHandler = context

            self._parser.EndElementHandler = close_element

        def close_element(name):
            self._parser.CharacterDataHandler, \
                self._parser.StartCdataSectionHandler, \
                self._parser.EndCdataSectionHandler, \
                self._parser.StartElementHandler, \
                self._parser.EndElementHandler = context

        self._parser.CharacterDataHandler = None
        self._parser.StartCdataSectionHandler = None
        self._parser.EndCdataSectionHandler = None
        self._parser.StartElementHandler = element
        self._parser.EndElementHandler = close_element

    def close_element(name):
        self._parser.CharacterDataHandler = None
        self._parser.StartCdataSectionHandler = None
        self._parser.EndCdataSectionHandler = None
        self._parser.StartElementHandler, \
            self._parser.EndElementHandler = context

        if iterator:
            chunks.append(u" ".join([_f for _f in SPACES.split(u"".join(chunks2clean)) if _f]))
            try:
                iterator.send(u"".join(chunks))
            except StopIteration:
                pass

    self._parser.CharacterDataHandler = data
    self._parser.StartCdataSectionHandler = cdata_section
    self._parser.EndCdataSectionHandler = close_cdata_section
    self._parser.StartElementHandler = lower(element) if self._lower else element
    self._parser.EndElementHandler = close_element


WORDS = words
