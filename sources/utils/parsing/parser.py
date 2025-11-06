
#from builtins import str
import types
from weakref import proxy
from xml.parsers.expat import ParserCreate, ExpatError
from utils.properties import roproperty, rwproperty
from utils.decorators import weaker
from .exceptions import AbortingError, ParsingException, \
    UnableToChangeError, OutOfMemoryError, JunkAfterDocumentError
from .subparsers import elements, nothing
from .auxiliary import empty_builder, uncover, lower as lower_decorator
from .legacy import LegacyInterface


MISSING = "MISSING"
DEFAULT_BUFFER_TEXT = True
ERRATIC = {
    1: OutOfMemoryError, # XML_ERROR_NO_MEMORY
    # XML_ERROR_SYNTAX
    # XML_ERROR_NO_ELEMENTS
    # XML_ERROR_INVALID_TOKEN
    # XML_ERROR_UNCLOSED_TOKEN
    # XML_ERROR_PARTIAL_CHAR
    # XML_ERROR_TAG_MISMATCH
    # XML_ERROR_DUPLICATE_ATTRIBUTE
    9: JunkAfterDocumentError, # XML_ERROR_JUNK_AFTER_DOC_ELEMENT
    # XML_ERROR_PARAM_ENTITY_REF
    # XML_ERROR_UNDEFINED_ENTITY
    # XML_ERROR_RECURSIVE_ENTITY_REF
    # XML_ERROR_ASYNC_ENTITY
    # XML_ERROR_BAD_CHAR_REF
    # XML_ERROR_BINARY_ENTITY_REF
    # XML_ERROR_ATTRIBUTE_EXTERNAL_ENTITY_REF
    # XML_ERROR_MISPLACED_XML_PI
    # XML_ERROR_UNKNOWN_ENCODING
    # XML_ERROR_INCORRECT_ENCODING
    # XML_ERROR_UNCLOSED_CDATA_SECTION
    # XML_ERROR_EXTERNAL_ENTITY_HANDLING
    # XML_ERROR_NOT_STANDALONE
    # XML_ERROR_UNEXPECTED_STATE
    # XML_ERROR_ENTITY_DECLARED_IN_PE
    # XML_ERROR_FEATURE_REQUIRES_XML_DTD
    # XML_ERROR_CANT_CHANGE_FEATURE_ONCE_PARSING
    # XML_ERROR_UNBOUND_PREFIX
    # XML_ERROR_UNDECLARING_PREFIX
    # XML_ERROR_INCOMPLETE_PE
    # XML_ERROR_XML_DECL
    # XML_ERROR_TEXT_DECL
    # XML_ERROR_PUBLICID
    # XML_ERROR_SUSPENDED
    # XML_ERROR_NOT_SUSPENDED
    # XML_ERROR_ABORTED
    # XML_ERROR_FINISHED
    # XML_ERROR_SUSPEND_PE
}


class Parser(LegacyInterface):

    def __init__(self, builder=None, lower=False, options=MISSING, result=None, notify=False, supress=False):
        """
        :param builder: Callable that return document handler
        :param options: Optional arguments or keywords for builder
        :param result: Default value for result
        :param notify: Enable default handlers for unknown elements and attributes which notify instead raise exceptions
        :param supress: Suppress parsing exceptions and just notify about them
        """
        self._legacy = builder.__doc__ == "legacy"
        self._lower = lower

        if builder is None:
            builder = empty_builder

        if options is MISSING:
            self._handler = builder(proxy(self))
        elif isinstance(options, tuple):
            self._handler = builder(proxy(self), *options)
        elif isinstance(options, dict):
            self._handler = builder(proxy(self), **options)
        else:
            self._handler = builder(proxy(self), options)

        self._parser = ParserCreate()
        self._parser.buffer_text = DEFAULT_BUFFER_TEXT

        if self._legacy:
            self._parser.StartElementHandler = lower_decorator(self._handler) if lower else self._handler
        else:
            self._handle(self._handler)

        del self._handler

        self._result = result
        self._report = []

        if notify:
            self._unexpected_attribute_handler = weaker(self._unexpected_attribute_handler)
            self._unexpected_element_handler = weaker(self._unexpected_element_handler)
        else:
            self._unexpected_attribute_handler = None
            self._unexpected_element_handler = None

        self._supress = supress

    def _set_cache(self, value):
        if self._parser.CurrentByteIndex >= 0:
            raise UnableToChangeError("cache mode")
        self._parser.buffer_text = value

    def _set_cache_size(self, value):
        if self._parser.CurrentByteIndex >= 0:
            raise UnableToChangeError("cache size")
        self._parser.buffer_size = value

    def _set_unexpected_attribute_handler(self, value):
        if self._parser.CurrentByteIndex >= 0:
            raise UnableToChangeError("unexpected attribute handler")
        self._unexpected_attribute_handler = value

    def _set_unexpected_element_handler(self, value):
        if self._parser.CurrentByteIndex >= 0:
            raise UnableToChangeError("unexpected element handler")
        self._unexpected_element_handler = value

    cache = rwproperty("_parser.buffer_text", _set_cache)
    cache_size = rwproperty("_parser.buffer_size", _set_cache_size)

    position = property(lambda self: self._parser.CurrentByteIndex)
    lineno = property(lambda self: self._parser.CurrentLineNumber)

    unexpected_element_handler = rwproperty("_unexpected_element_handler", _set_unexpected_element_handler)
    unexpected_attribute_handler = rwproperty("_unexpected_attribute_handler", _set_unexpected_attribute_handler)

    result = roproperty("_result")
    report = roproperty("_report")

    def _unexpected_attribute_handler(self, name):
        """
        Default unexpected attribute handler
        """
        self.notify("Ignore \"%s\" attribute" % name)

    def _unexpected_element_handler(self, name, attributes):
        """
        Default element attribute handler
        """
        self.notify("Ignore \"%s\" element" % name)

    def _handle(self, handlers, iterator=None):
        """
        Choose subparser and execute
        """
        if isinstance(handlers, tuple):
            elements(self, {uncover(getattr(handler, "name", handler.__name__)): handler for handler in handlers}.get, iterator)
        elif handlers is None:
            nothing(self, handlers, iterator)
        else:
            subuparser = getattr(handlers, "subparser", None)
            if subuparser:
                subuparser(self, handlers, iterator)
            else:
                elements(self, {uncover(getattr(handlers, "name", handlers.__name__)): handlers}.get, iterator)

    def reset(self, options=MISSING, result=None):
        """
        Reset parser state
        :param options: Optional arguments or keywords for builder
        :param result: Default value for result
        """
        buffer_text = self._parser.buffer_text

        self._parser = ParserCreate()
        self._parser.buffer_text = buffer_text

        if self._legacy:
            self._parser.StartElementHandler = self._handler
        else:
            self._handle(self._handler)

        self._result = result
        self._report = []

    def parse(self, value=None, chunk=None, file=None, filename=None):
        """
        Parse value, file or data chunk
        :param value: Parse string entirely
        :param chunk: Parse string in consecutive calls as chunks, last call must use "value" argument
        :param file: File-like object to read data from
        :param filename: File name of the file to read data from
        """
        try:
            if value is not None:
                self._parser.Parse(value, True)
            elif chunk is not None:
                self._parser.Parse(chunk)
            elif filename is not None:
                with open(filename, "rb") as file:
                    self._parser.ParseFile(file)
            elif file is not None:
                self._parser.ParseFile(file)
            else:
                raise ParsingException("Require value, filename, file or chunk to parse")
        except ExpatError as error:
            try:
                error = ERRATIC[error.code]()
                message = error.args[0]
            except KeyError:
                message = error.args[0].split(":")[0].capitalize()
                error = ParsingException(message)

            error.offset = self._parser.ErrorByteIndex
            error.lineno = self._parser.ErrorLineNumber
            error.column = self._parser.ErrorColumnNumber

            if self._supress:
                self.notify(message)
            else:
                raise error
        except ParsingException as error:
            error.offset = self._parser.CurrentByteIndex
            error.lineno = self._parser.CurrentLineNumber
            error.column = self._parser.CurrentColumnNumber

            if self._supress:
                self.notify(error.message)
            else:
                raise
        except AbortingError as error:
            # message = error.message
            # if message:
            message = error.args[0]
            if message:
                self.notify(message)

        return self._result

    def accept(self, *values):
        """
        Accept result of parsing
        """
        if len(values) == 1:
            self._result = values[0]
        else:
            self._result = values

    def complete(self, *values, **keywords):
        """
        Accept result and immediatelly exit from parsing
        """
        message = keywords.get("message")
        self.accept(*values)
        raise AbortingError(message)

    def abort(self, message=""):
        """
        Abort parsing
        """
        raise AbortingError(message)

    def notify(self, message):
        """
        Add notification to the parsing report
        """
        self._report.append((self._parser.CurrentLineNumber, message))
