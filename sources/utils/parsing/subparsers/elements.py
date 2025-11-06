
from builtins import next
from builtins import zip
import inspect
from itertools import chain
from ..exceptions import UnexpectedElementError, UnexpectedAttributeError, MissingAttributeError, UnexpectedAttributeValueError
from ..auxiliary import subparser, uncover, lower
from .nothing import nothing


@subparser
def elements(self, selector, iterator):
    """
    Handle element and control attributes
    """

    context = \
        self._parser.StartElementHandler, \
        self._parser.EndElementHandler

    def element(name, attributes):
        handler = selector(name)

        if handler is None:
            if self._unexpected_element_handler:
                self._unexpected_element_handler(name, attributes)
            else:
                raise UnexpectedElementError(name, attributes)
            return nothing(self, selector, iterator)
        else:
            subuparser = getattr(handler, "subparser", None)
            if subuparser:
                subuparser(self, handler, iterator)

        names, arguments, keywords, defaults = inspect.getargspec(handler)
        index = len(names) - (len(defaults) if defaults else 0)

        names = getattr(handler, "names", names)

        try:
            parameters = tuple(chain(
                (attributes.pop(uncover(name)) for name in names[:index]),
                (attributes.pop(uncover(name), default) for name, default in zip(names[index:], defaults or ()))))
        except KeyError as error:
            raise MissingAttributeError(error)

        verificators = getattr(handler, "verificators", None)
        if verificators is not None:
            try:
                for attribute_name, parameter, verificator in zip(names, parameters, verificators):
                    verificator(parameter)
            except:
                raise UnexpectedAttributeValueError(attribute_name)

        if not keywords:
            for attribute_name in attributes:
                if self._unexpected_attribute_handler:
                    self._unexpected_attribute_handler(attribute_name)
                else:
                    raise UnexpectedAttributeError(attribute_name)
            attributes.clear()

        if inspect.isgeneratorfunction(handler):
            inner_iterator = handler(*parameters, **attributes)
            inner_handlers = next(inner_iterator)
        else:
            inner_iterator = None
            inner_handlers = handler(*parameters, **attributes)

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
