
def empty_builder(parser, object):

    def document_handler(name, attributes):
        parser.reject_elements(name, attributes)

    return document_handler


def subparser(function):
    function.subparser = function
    return function


def uncover(name):
    return (name[1:] if name[0] == "_" else name).replace("_", "-")


def lower(handler):

    def wrapper(name, attributes):
        name = name.lower()
        attributes = {key.lower(): value for key, value in attributes.items()}
        return handler(name, attributes)

    return wrapper
