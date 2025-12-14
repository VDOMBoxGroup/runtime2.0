
import re
from .. import levels
from .multiline import MultilineLogFormatter


class LevelingLogFormatter(MultilineLogFormatter):

    PREFIXES = levels.PREFIXES
    PREFIXES_REGEX = re.compile(r"|".join("(^%s)" % prefix or "$" for prefix in PREFIXES))

    def _make_caption(self, level, *values):
        return super(LevelingLogFormatter, self)._make_caption(*values) + self.PREFIXES[level]

    def parse(self, data):
        values = super(LevelingLogFormatter, self).parse(data)
        fields, message = values[:-1], values[-1]
        match = self.PREFIXES_REGEX.match(message)
        if match:
            level, message = match.lastindex, message[match.end():]
        else:
            level = levels.MESSAGE
        return (level,) + fields + (message,)
