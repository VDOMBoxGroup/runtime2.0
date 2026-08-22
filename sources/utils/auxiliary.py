
def enquote(value):
    # encode() answers bytes in py3, and replacing str inside bytes raises
    # TypeError - so come back to text first, the way representation.py does.
    return "\"%s\"" % value.encode("unicode_escape").decode("ascii").replace("\"", "\\\"")


def headline(value):
    return value[:1].upper() + value[1:]


def forfeit(value):
    return value[:1].lower() + value[1:]


def lfill(pattern, length):
    pattern_length = len(pattern)
    return pattern * (length // pattern_length) + pattern[:length % pattern_length]


def rfill(pattern, length):
    pattern_length = len(pattern)
    return pattern[len(pattern) - length % pattern_length:] + pattern * (length // pattern_length)


def ljust(value, width, filler):
    if len(value) < width:
        return value + rfill(filler, width - len(value))
    else:
        return value


def rjust(value, width, filler):
    if len(value) < width:
        return lfill(filler, width - len(value)) + value
    else:
        return value


fill = lfill
just = ljust


def lfit(value, width):
    if width < 0:
        return value
    elif value:
        return value[:width - 3] + "..." if len(value) > width else value
    else:
        return ""


def rfit(value, width, start=0):
    if width < 0:
        return value
    elif value:
        return value[:start] + "..." + value[width - start - 3:] if len(value) > width else value
    else:
        return ""


fit = lfit


def align(value, width, separator=" ", indent="", filler=" ", padding=" ", hint="...", stretch=0):
    if width < 0:
        return value
    elif width < len(separator) + len(hint):
        return rfill(filler, min(0, width - len(separator))) + separator[:max(len(separator), width)]
    elif value:
        value = indent + value.strip()
        if len(value) + len(separator) > width:
            if stretch:
                return value + separator
            else:
                return value[:width - len(separator) - len(hint)] + hint + separator
        else:
            return ljust(value + padding[:width - len(value) - len(separator)], width - len(separator), filler) + separator
    else:
        return rfill(filler, width - len(separator)) + separator
