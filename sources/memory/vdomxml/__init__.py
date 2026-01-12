from sources import settings
from .dumps import dumps

try:
    if not settings.BINARY_LOADS_EXTENSION:
        raise ImportError

    from ._loads import loads, BaseException as ParsingException

except ImportError:
    from .loads import loads, BaseException as ParsingException
