
from .. import errors
from .scripting import scripting_dictionary


def v_createobject(name):
    name = name.as_string
    if name == "Scripting.Dictionary":
        return scripting_dictionary()
    else:
        return errors.invalid_procedure_call
