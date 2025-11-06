
from builtins import next
from builtins import object
from .exceptions import UnexpectedElementError, UnexpectedAttributeError
from .auxiliary import lower
from .subparsers import VALUE, CONTENTS


class LegacyInterface(object):

    def handle_value(self, name, attributes, setter):
        """
        Parse element value and report about all nested elements
        :param name: Element name to parse
        :param attributes: Unhandled attributes to report
        :param setter: Setter to handle value
        """
        for attribute_name in attributes:
            if self._unexpected_attribute_handler:
                self._unexpected_attribute_handler(attribute_name)
            else:
                raise UnexpectedAttributeError(attribute_name)

        def wrapper():
            value = yield
            setter(value)

        iterator = wrapper()
        next(iterator)

        return VALUE(self, None, iterator)

    def handle_contents(self, name, attributes, setter):
        """
        Parse element contents with all nested elements
        :param name: Element name to parse
        :param attributes: Unhandled attributes to report
        :param setter: Setter to handle value
        """
        for attribute_name in attributes:
            if self._unexpected_attribute_handler:
                self._unexpected_attribute_handler(attribute_name)
            else:
                raise UnexpectedAttributeError(attribute_name)

        def wrapper():
            value = yield
            setter(value)

        iterator = wrapper()
        next(iterator)

        return CONTENTS(self, None, iterator)

    def handle_elements(self, name, attributes, handler=None, close_handler=None):
        """
        Parse element contents
        :param name: Element name to parse
        :param attributes: Unhandled attributes to report
        :param handler: Handler for nested elements
        :param close_handler: Close handler
        """
        for attribute_name in attributes:
            if self._unexpected_attribute_handler:
                self._unexpected_attribute_handler(attribute_name)
            else:
                raise UnexpectedAttributeError(attribute_name)

        context = self._parser.StartElementHandler, self._parser.EndElementHandler

        def close_element_handler(name):
            self._parser.StartElementHandler, self._parser.EndElementHandler = context
            if close_handler:
                close_handler(name)

        handler = handler or self.reject_elements
        self._parser.StartElementHandler = lower(handler) if self._lower else handler
        self._parser.EndElementHandler = close_element_handler

    def reject_elements(self, name, attributes):
        """
        Parse unknown element and report about it
        :param name: Element name to report
        :param attributes: Unhandled attributes to report
        """
        if self._unexpected_element_handler:
            self._unexpected_element_handler(name, attributes)
        else:
            raise UnexpectedElementError(name, attributes)

        self.ignore_elements(name, attributes)

    def ignore_elements(self, name, attributes):
        """
        Parse unnecessary element to siletly ignore it
        :param name: Element name
        :param attributes: Element attributes
        """
        context = self._parser.StartElementHandler, self._parser.EndElementHandler

        def element_handler(name, attributes):
            context = self._parser.EndElementHandler

            def close_element_handler(name):
                self._parser.EndElementHandler = context

            self._parser.EndElementHandler = close_element_handler

        def close_element_handler(name):
            self._parser.StartElementHandler, self._parser.EndElementHandler = context

        self._parser.StartElementHandler = lower(element_handler) if self._lower else element_handler
        self._parser.EndElementHandler = close_element_handler
