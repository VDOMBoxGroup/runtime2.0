
from builtins import str

from builtins import object
import re
import sys
import codecs

if sys.version_info[0] < 3:
    from collections import Mapping, MutableMapping
else:
    from collections.abc import Mapping, MutableMapping
import settings
import managers
from utils.properties import weak
from logs import log
from ..generic import MemoryBase


FORCE_CDATA_LENGTH = 1024
FORCE_CDATA_REGEX = re.compile(u"[\t\n\r\"<=>]", re.MULTILINE)
PROHIBITED_CHARACTERS = re.compile("[\x00-\x08\x0B\x0C\x0E-\x19]")
DEREFERENCE_REGEX = re.compile(r"\#RES\(([A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})\)", re.IGNORECASE)
LAYOUT_ATTRIBUTES = {"top", "left", "width", "height", "hierarchy"}


@weak("_owner")
class MemoryAttributesSketch(MemoryBase, MutableMapping):

    class CDataLazyProperty(object):

        def __get__(self, instance, owner=None):
            return instance.__dict__.setdefault("_cdata", set())

    class QueryLazyProperty(object):

        def __get__(self, instance, owner=None):
            return instance.__dict__.setdefault("_query", set(instance._items._set))

    _cdata = CDataLazyProperty()
    _query = QueryLazyProperty()

    def __init__(self, owner, values=None):
        self._owner = owner
        self._items = owner.type.attributes.klass()

        if values:
            self.update(values)

    def iternondefault(self):
        return iter(self._items.__dict__)

    def iternondefaultitems(self):
        return iter(self._items.__dict__.items())

    def update(self, values):
        for name, value in values.items():
            value = DEREFERENCE_REGEX.sub(lambda match: match.group(1), value)
            try:
                self._owner.type.attributes[name].verify(value)
            except (AttributeError, KeyError):
                #raise Exception("The %s has no \"%s\" attribute " % (self._owner, name))
                pass
                #del values[name]
            except ValueError:
                # TODO: return ValueError after resolve all issues in applications
                log.warning(u"Unacceptable value for \"%s\" attribute of %s: \"%s\""
                    % (name, self._owner, value.replace('"', '\"')))

        self._query.update(values)
        self._items.__dict__.update(values)

    def __getitem__(self, name):
        try:
            return getattr(self._items, name)
        except AttributeError:
            raise KeyError(name)

    def __setitem__(self, name, value):
        try:
            self._owner.type.attributes[name].verify(value)
        except AttributeError:
            raise Exception("The %s has no \"%s\" attribute " % (self._owner, name))
        except ValueError:
            # TODO: return ValueError after resolve all issues in applications
            log.warning(u"Unacceptable value for \"%s\" attribute of %s: \"%s\""
                % (name, self._owner, value.replace('"', '\"')))

        self._query.add(name)
        self._items.__dict__[name] = value

    def __delitem__(self, name):
        self._query.add(name)
        self._items.__dict__.pop(name, None)

    def __iter__(self):
        return iter(self._items._enumeration)

    def __len__(self):
        return len(self._items._enumeration)

    def __invert__(self):
        self.__class__ = MemoryAttributes
        return self

    def __str__(self):
        return "attributes sketch of %s" % self._owner


class MemoryAttributes(MemoryAttributesSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new attribute")

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False, excess=False):
        skip_defaults = not (settings.STORE_DEFAULT_VALUES or excess)

        for name in self._query:
            value = getattr(self._items, name)
            if value == getattr(self._items.__class__, name):
                self._items.__dict__.pop(name, None)

            if (self._owner.type.attributes[name].complexity
                    or len(value) > FORCE_CDATA_LENGTH or FORCE_CDATA_REGEX.search(value)):
                if name not in self._cdata:
                    self._cdata.add(name)
            else:
                if name in self._cdata:
                    self._cdata.remove(name)

        self._query.clear()

        if not skip_defaults or self._items.__dict__:
            file.write(u"%s<Attributes>\n" % ident)
            for name in self._items.__dict__ if skip_defaults else self._items._enumeration:
                file.write(u"%s\t<Attribute Name=\"%s\">%s</Attribute>\n" %
                    (ident, name, codecs.encode(PROHIBITED_CHARACTERS.sub("?",
                        getattr(self._items, name)), "cdata" if name in self._cdata else "xml")))
            file.write(u"%s</Attributes>\n" % ident)

    def update(self, *arguments, **keywords):
        if arguments:
            collection = arguments[0]
            if isinstance(collection, Mapping):
                values = collection
            elif hasattr(collection, "keys"):
                values = {key: collection[key] for key in list(collection.keys())}
            else:
                values = {key: collection[key] for key, value in collection}
        else:
            values = keywords

        updates = {}
        with self._owner.lock:
            for name, value in values.items():
                if not isinstance(value, str):
                    value = str(value)

                try:
                    current_value = getattr(self._items, name)
                except AttributeError:
                    raise Exception("The %s has no \"%s\" attribute " % (self._owner, name))
                value = DEREFERENCE_REGEX.sub(lambda match: match.group(1), value)
                if current_value != value:
                    updates[name] = value

            if updates:
                managers.dispatcher.dispatch_handler(self._owner, "on_update", updates)

                if updates:
                    layout = False
                    for name, value in updates.items():
                        if not isinstance(value, str):
                            value = str(value)

                        try:
                            self._owner.type.attributes[name].verify(value)
                        except AttributeError:
                            raise Exception("The %s has no \"%s\" attribute " % (self._owner, name))
                        except ValueError:
                            raise ValueError(u"Unacceptable value for \"%s\" attribute of %s: \"%s\"" %
                                (name, self._owner, value.replace('"', '\"')))

                        if settings.DETAILED_LOGGING:
                            log.write("Update %s attrbiute \"%s\" to \"%s\"" % (self._owner, name, value.replace('"', '\"')))
                        self._query.add(name)
                        self._items.__dict__[name] = value

                        if name in LAYOUT_ATTRIBUTES:
                            layout = True

                    self._owner.invalidate(upward=1)
                    if layout:
                        parent = self._owner.parent
                        if parent and parent.virtual == self._owner.virtual:
                            managers.dispatcher.dispatch_handler(parent, "on_layout", self._owner)
                    self._owner.autosave()

    def __setitem__(self, name, value):
        self.update({name: value})

    def __delitem__(self, name):
        managers.dispatcher.dispatch_handler(self._owner, "on_update", {name: self._owner.type.attributes[name].default_value})
        if settings.DETAILED_LOGGING:
            log.write("Reset %s attrbiute \"%s\"" % (self._owner, name))
        self._query.add(name)
        self._items.__dict__.pop(name, None)
        self._owner.invalidate(upward=1)
        self._owner.autosave()

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return "attributes of %s" % self._owner
