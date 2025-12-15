from ..primitives import variable


class shadow(variable):

    def __init__(self, owner=None, name=None):
        self._owner = owner
        self._name = name

    def __call__(self, *arguments, **keywords):
        if "let" in keywords:
            if arguments:
                getattr(self._owner, self._name)(*arguments, **keywords)
            else:
                setattr(self._owner, self._name, keywords["let"].as_simple)
        elif "set" in keywords:
            if arguments:
                getattr(self._owner, self._name)(*arguments, **keywords)
            else:
                setattr(self._owner, self._name, keywords["let"].as_complex)
        else:
            getattr(self._owner, self._name)(*arguments, **keywords)

    subtype = property(lambda self: getattr(self._owner, self._name).subtype)
    copy = property(lambda self: getattr(self._owner, self._name).copy)
    exception = property(lambda self: getattr(
        self._owner, self._name).exception)
    value = property(lambda self: getattr(self._owner, self._name).value)

    def __repr__(self):
        return "SHADOW@%08X:%r" % (id(self), getattr(self._owner, self._name))
