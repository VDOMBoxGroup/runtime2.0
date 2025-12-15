
from .. import errors
from ..subtypes import generic, string
from ..variables import shadow
from ..conversions import as_string, as_array


class vdomtypewrapper(generic):

    def __init__(self, objecttype):
        generic.__init__(self)
        self.__objecttype = objecttype

    def v_id(self, let=None, set=None):
        if let is not None or set is not None:
            raise errors.object_has_no_property("id")
        else:
            return string(self.__objecttype.id)

    def v_name(self, let=None, set=None):
        if let is not None or set is not None:
            raise errors.object_has_no_property("name")
        else:
            return string(self.__objecttype.name)

    def __repr__(self):
        return "VDOMTYPEWRAPPER@%s:%s" % (object.__repr__(self)[-9:-1], repr(self.__object))


class vdomobjectwrapper(generic):

    def __init__(self, object):
        generic.__init__(self)
        self.__object = object

    def __getattr__(self, name):
        if name.startswith("v_"):
            name = name[2:]
            if name in self.__object.attributes:
                return shadow(self, "wrapper_%s" % name)
            elif name in self.__object.objects:
                return vdomobjectwrapper(self.__object.objects[name])
            else:
                raise errors.object_has_no_property(name)
        elif name.startswith("wrapper_"):
            name = name[8:]
            return string(getattr(self.__object, name))
        else:
            raise errors.object_has_no_property(name)

    def __setattr__(self, name, value):
        if name.startswith("v_"):
            name = name[2:]
            if name in self.__object.attributes:
                setattr(self.__object, name, as_string(value))
            elif name in self.__object.objects:
                raise errors.type_mismatch
            generic.__setattr__(self, "v_%s" % name, value)
        elif name.startswith("wrapper_"):
            name = name[8:]
            setattr(self.__object, name, as_string(value))
        else:
            generic.__setattr__(self, name, value)

    def v_id(self, let=None, set=None):
        if let is not None or set is not None:
            raise errors.object_has_no_property("id")
        else:
            return string(self.__object.id)

    def v_name(self, let=None, set=None):
        if let is not None or set is not None:
            raise errors.object_has_no_property("name")
        else:
            return string(self.__object.name)

    def v_type(self, let=None, set=None):
        if let is not None or set is not None:
            raise errors.object_has_no_property("type")
        else:
            return vdomtypewrapper(self.__object.type)

    def v_update(self, *arguments):
        self.__object.update(*(as_string(argument).lower()
                             for argument in arguments))

    def v_action(self, name, parameters=None, source=None):
        parameters = [] if parameters is None else as_array(parameters)
        self.__object.action(as_string(name),
                             tuple(as_string(parameter)
                                   for parameter in parameters),
                             as_string(source) if source is not None else None)

    def __repr__(self):
        return "VDOMOBJECTWRAPPER@%s:%s" % (object.__repr__(self)[-9:-1], repr(self.__object))
