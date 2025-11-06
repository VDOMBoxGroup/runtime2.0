from __future__ import unicode_literals

import codecs
import re
from utils.properties import lazy, weak, roproperty, rwproperty
from ..generic import MemoryBase


@weak("_collection")
class MemoryTypeAttributeSketch(MemoryBase):

    @lazy
    def _regex(self):
        return re.compile("^%s$" % self._validation_pattern, re.DOTALL)

    _name = None
    _display_name = None
    _description = ""
    _default_value = ""
    _validation_pattern = ".*"
    _validation_error_message = ""
    _visible = 1
    _interface_type = 0
    _code_interface = "TextField(99)"
    _color_group = 1
    _complexity = 0

    def __init__(self, collection):
        self._collection = collection

    def _set_validation_pattern(self, value):
        self._validation_pattern = value
        if "_regex" in self.__dict__:
            del self._regex

    owner = property(lambda self: self._collection.owner)

    name = rwproperty("_name")
    display_name = rwproperty("_display_name")
    description = rwproperty("_description")
    default_value = rwproperty("_default_value")
    validation_pattern = rwproperty("_validation_pattern", _set_validation_pattern)
    validation_error_message = rwproperty("_validation_error_message")
    visible = rwproperty("_visible")
    interface_type = rwproperty("_interface_type")
    code_interface = rwproperty("_code_interface")
    color_group = rwproperty("_color_group")
    complexity = rwproperty("_complexity")

    def __invert__(self):
        if self._name is None:
            raise Exception("Attribute require name")
        if self._display_name is None:
            self._display_name = self._name

        self.__class__ = MemoryTypeAttribute
        self._collection.on_complete(self)
        return self

    def __str__(self):
        return " ".join([_f for _f in ("attribute", "\"%s\"" % self._name,
            "sketch of %s" % self._collection.owner if self._collection else None) if _f])


class MemoryTypeAttribute(MemoryTypeAttributeSketch):

    def __init__(self):
        raise Exception("Use 'new' to create new attribute")

    name = roproperty("_name")
    display_name = roproperty("_display_name")
    description = roproperty("_description")
    default_value = roproperty("_default_value")
    validation_pattern = roproperty("_validation_pattern")
    validation_error_message = roproperty("_validation_error_message")
    visible = roproperty("_visible")
    interface_type = roproperty("_interface_type")
    code_interface = roproperty("_code_interface")
    color_group = roproperty("_color_group")
    complexity = roproperty("_complexity")

    # unsafe
    def compose(self, ident="", file=None):
        file.write("%s<Attribute>\n" % ident)
        file.write("%s\t<Name>%s</Name>\n" % (ident, self._name))
        if self._display_name:
            file.write("%s\t<DisplayName>%s</DisplayName>\n" % (ident, codecs.encode(self._display_name, "xml")))
        if self._description:
            file.write("%s\t<Description>%s</Description>\n" % (ident, codecs.encode(self._description, "xml")))
        file.write("%s\t<DefaultValue>%s</DefaultValue>\n" % (ident, codecs.encode(self._default_value, "xml")))
        file.write("%s\t<RegularExpressionValidation>%s</RegularExpressionValidation>\n" % (ident, codecs.encode(self._validation_pattern, "xml")))
        if self._validation_error_message:
            file.write("%s\t<ErrorValidationMessage>%s</ErrorValidationMessage>\n" % (ident, codecs.encode(self._validation_error_message, "xml")))
        file.write("%s\t<Visible>%s</Visible>\n" % (ident, self._visible))
        file.write("%s\t<InterfaceType>%s</InterfaceType>\n" % (ident, self._interface_type))
        file.write("%s\t<CodeInterface>%s</CodeInterface>\n" % (ident, codecs.encode(self._code_interface, "xml")))
        file.write("%s\t<ColorGroup>%s</ColorGroup>\n" % (ident, self._color_group))
        file.write("%s</Attribute>\n" % ident)

    def verify(self, value):
        if not self._regex.match(value):
            raise ValueError

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join([_f for _f in ("attribute", "\"%s\"" % self._name,
            "of %s" % self._collection.owner if self._collection else None) if _f])
