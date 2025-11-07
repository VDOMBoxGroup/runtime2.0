


REASONABLE_WIDTH = 7
REASONABLE_OBJECT_WIDTH = 10

NOTHING = "NOTHING"


def represent(value, width=None, limit=None, ellipsis="..."):
    if width < 0:
        width = None

    def sequence(opening, ending, separator=", ", ellipsis="..."):
        if width is None:
            return "".join((
                opening,
                separator.join((represent(subvalue, -1) for subvalue in value)),
                ending))

        iterator = iter(value)
        subvalue = next(iterator, NOTHING)
        if subvalue is NOTHING:
            result = opening + ending
        else:
            parts = []
            space = width - len(opening) - len(ending)
            extra = 0 if limit is None else (limit - width)
            while space + extra > 0:
                following = next(iterator, NOTHING)
                reserve = 0 if following is NOTHING else len(separator) + len(ellipsis)
                if space < reserve:
                    break

                part_width = space - reserve
                part = represent(subvalue, part_width, limit=part_width + extra)
                if part is None:
                    break

                parts.append(part)
                space -= len(part)

                subvalue = following
                if subvalue is NOTHING:
                    break

                space -= len(separator)

            if subvalue is not NOTHING:
                while parts and space < len(ellipsis):
                    deleted = parts.pop(-1)
                    space += len(deleted)
                    if parts:
                        space += len(separator)
                parts.append(ellipsis)

            result = "".join((opening, separator.join(parts), ending))

        if len(result) > (limit or width):
            return result[:width] if limit is None else None
        else:
            return result

    def mapping(opening, ending, colon=": ", separator=", ", ellipsis="..."):
        if width is None:
            return "".join((
                opening,
                separator.join((colon.join((represent(subkey), represent(subvalue)))
                    for subkey, subvalue in value.items())),
                ending))

        iterator = iter(value.items())
        subvalue = next(iterator, NOTHING)
        if subvalue is NOTHING:
            result = opening + ending
        else:
            parts = []
            space = width - len(opening) - len(ending)
            extra = 0 if limit is None else (limit - width)
            while space + extra > 0:
                following = next(iterator, NOTHING)
                reserve = (0 if following is NOTHING else len(separator) + len(ellipsis))
                if space < reserve:
                    break

                part_width = space - reserve
                key_width = part_width - part_width // 2
                key_part = represent(subvalue[0], key_width, limit=key_width + extra)
                if key_part is None:
                    break

                value_width = part_width - len(colon) - len(key_part)
                if value_width < 0:
                    break

                value_part = represent(subvalue[1], value_width, limit=value_width + extra)
                if value_part is None:
                    if value_width >= len(ellipsis):
                        key_width = part_width - len(colon) - len(ellipsis)
                        key_part = represent(subvalue[0], key_width, limit=key_width + extra)
                        value_part = ellipsis
                    else:
                        break

                part = colon.join((key_part, value_part))
                parts.append(part)
                space -= len(part)

                subvalue = following
                if subvalue is NOTHING:
                    break

                space -= len(separator)

            if subvalue is not NOTHING:
                while parts and space < len(ellipsis):
                    deleted = parts.pop(-1)
                    space += len(deleted)
                    if parts:
                        space += len(separator)
                parts.append(ellipsis)

            result = "".join((opening, separator.join(parts), ending))

        if len(result) > (limit or width):
            return result[:width] if limit is None else None
        else:
            return result

    def string(ellipsis="..."):
        if isinstance(value, str):
            prefix, extra = "u", 3
            encoding = "unicode-escape"
        else:
            prefix, extra = "", 2
            encoding = "string_escape"

        result = value.encode(encoding).replace("\"", "\\\"")

        if width is None or len(result) + extra <= width:
            return "%s\"%s\"" % (prefix, result)
        else:
            length = width - extra - len(ellipsis)
            if length <= 0:
                return (("%s\"\"%s" if length == 0 else "%s\"%s")
                    % (prefix, ellipsis))[:width] if limit is None else None
            else:
                return "%s\"%s\"%s" % (prefix, result[:length], ellipsis)

    if isinstance(value, tuple) and getattr(type(value), "__repr__") is tuple.__repr__:
        return sequence("(", ")", ellipsis=ellipsis)
    elif isinstance(value, list) and getattr(type(value), "__repr__") is list.__repr__:
        return sequence("[", "]", ellipsis=ellipsis)
    elif isinstance(value, dict) and getattr(type(value), "__repr__") is dict.__repr__:
        return mapping("{", "}", ellipsis=ellipsis)
    elif isinstance(value, set) and getattr(type(value), "__repr__") is set.__repr__:
        return sequence("set(", ")", ellipsis=ellipsis)
    elif isinstance(value, frozenset) and getattr(type(value), "__repr__") is frozenset.__repr__:
        return sequence("frozenset(", ")", ellipsis=ellipsis)
    elif isinstance(value, bytes):
        return string(ellipsis=ellipsis)
    else:
        try:
            result = repr(value)
        except Exception as error:
            try:
                message = str(error)
            except Exception:
                message = type(error).__name__
            return "Unable to represent: %s" % message
        length = len(result)
        if width is None or length <= width:
            return result
        else:
            if result.startswith("<") and result.endswith(">"):
                overhead = len(ellipsis) + 2
                if limit is None:
                    if width < overhead:
                        return ("<" + ellipsis)[:width]
                    else:
                        return result[:width - overhead + 1] + ellipsis + ">"
                else:
                    minimal = min(length, REASONABLE_OBJECT_WIDTH)
                    if limit < minimal + overhead:
                        return None
                    else:
                        if width < minimal + overhead:
                            return result[:minimal + 1] + ellipsis + ">"
                        else:
                            return result[:width - overhead + 1] + ellipsis + ">"
            else:
                overhead = len(ellipsis)
                if limit is None:
                    if width < overhead:
                        return ellipsis[:width]
                    else:
                        return result[:width - overhead] + ellipsis
                else:
                    minimal = min(length, REASONABLE_WIDTH)
                    if limit < minimal + overhead:
                        return None
                    else:
                        if width < minimal + overhead:
                            return result[:minimal] + ellipsis
                        else:
                            return result[:width - overhead] + ellipsis
