
from logs import log
from utils.parsing import Parser, ParsingException
from .builder import vdomxml_builder


class BaseException(Exception):

    def __init__(self, message, line=None, column=None):
        super(BaseException, self).__init__(message)
        self.message = message
        self.line = line
        self.column = column


def loads(vdomxml, origin, profile=None):
    parser = Parser(builder=vdomxml_builder, lower=True, options=origin, notify=True)
    try:
        object = parser.parse(vdomxml)
        if parser.report:
            log.warning("Loads VDOM XML notifications")
            for lineno, message in parser.report:
                log.warning("    %s at line %s" % (message, lineno))
        return object
    except ParsingException as error:
        raise BaseException(str(error),
            getattr(error, "lineno", None), getattr(error, "column", None))
