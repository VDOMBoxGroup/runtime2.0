
import inspect
from ..exceptions import UnexpectedAttributeError
from ..auxiliary import subparser, lower


@subparser
def native(self, selector, iterator):
    """
    Native subparser to do manunal element and attributes handling
    """

    context = \
        self._parser.StartElementHandler, \
        self._parser.EndElementHandler

    def element(name, attributes):
        if inspect.isgeneratorfunction(selector):
            inner_iterator = selector(name, attributes)
            inner_handlers = next(inner_iterator)
        else:
            inner_iterator = None
            inner_handlers = selector(name, attributes)

        for attribute_name in attributes:
            if self._unexpected_attribute_handler:
                self._unexpected_attribute_handler(attribute_name)
            else:
                raise UnexpectedAttributeError(attribute_name)

        self._handle(inner_handlers, inner_iterator)

    def close_element(name):
        self._parser.StartElementHandler, \
            self._parser.EndElementHandler = context

        if iterator:
            try:
                next(iterator)
            except StopIteration:
                pass

    self._parser.StartElementHandler = lower(element) if self._lower else element
    self._parser.EndElementHandler = close_element
