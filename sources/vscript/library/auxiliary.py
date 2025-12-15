
from .. import version
from ..subtypes import integer, string


def v_vartype(value):
    return integer(value.subtype.code)


def v_typename(value):
    return string(value.subtype.name)


def v_scriptengine():
    return string(u"VScript")


def v_scriptenginebuildversion():
    return integer(version.build)


def v_scriptenginemajorversion():
    return integer(version.major)


def v_scriptengineminorversion():
    return integer(version.minor)
