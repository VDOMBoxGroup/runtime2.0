# flake8: noqa: E226
from .. import errors
from ..operations import div, mod
from ..primitives import subtype


class string(subtype):

    def __init__(self, value):
        # assert isinstance(value, unicode), "Got %s instead unicode string"%type(value)
        self._value = str(value)

    value = property(lambda self: self._value)

    code = property(lambda self: 8)
    name = property(lambda self: "String")

    as_simple = property(lambda self: self)
    # VAILS — autorise l'accès membre `s.method` (variant.__getattr__ -> as_complex).
    as_complex = property(lambda self: self)
    as_boolean = property(lambda self: bool(self))
    as_date = property(lambda self: float(self))
    as_double = property(lambda self: float(self))
    as_integer = property(lambda self: int(self))
    as_string = property(lambda self: str(self))
    as_number = property(lambda self: float(self))

    def is_string(self, value=None):
        return True if value is None else self._value == value

    def __iter__(self):
        from ..variables import variant
        for character in self._value:
            yield variant(string(character))

    def __len__(self):
        return len(self._value)

    def __invert__(self):
        try:
            return integer(~int(round(float(self._value))))
        except ValueError:
            raise errors.type_mismatch

    def __neg__(self):
        try:
            return double(-float(self._value))
        except ValueError:
            raise errors.type_mismatch

    def __pos__(self):
        try:
            return double(+float(self._value))
        except ValueError:
            raise errors.type_mismatch

    def __abs__(self):
        try:
            return double(abs(float(self._value)))
        except ValueError:
            raise errors.type_mismatch

    def __int__(self):
        try:
            return int(round(float(self._value)))
        except ValueError:
            raise errors.type_mismatch

    def __float__(self):
        try:
            return float(self._value)
        except ValueError:
            raise errors.type_mismatch

    def __str__(self):
        return str(self._value)

    def __bool__(self):
        try:
            return bool(float(self._value))
        except ValueError:
            if self._value.lower() == "true":
                return True
            elif self._value.lower() == "false":
                return False
            else:
                raise errors.type_mismatch

    def __hash__(self):
        return hash(self._value)

    def __repr__(self):
        if hasattr(self, "_value"):
            return "STRING@%08X:%r" % (id(self), self._value)
        else:
            return "STRING@%08X:<UNINITIALIZED>" % (id(self))

    # VAILS — méthodes membres fluides (Tier 2 #7). `s.upper`/`s.trim`/… en plus des
    # fonctions globales (UCase/Trim/…). Le membre 0-arg est auto-appelé par `check`.
    # Délègue à la lib (parité de comportement) ; imports paresseux (cycle subtypes↔library).
    def v_upper(self):
        from ..library.strings import v_ucase
        return v_ucase(self)

    def v_lower(self):
        from ..library.strings import v_lcase
        return v_lcase(self)

    def v_trim(self):
        from ..library.strings import v_trim
        return v_trim(self)

    def v_ltrim(self):
        from ..library.strings import v_ltrim
        return v_ltrim(self)

    def v_rtrim(self):
        from ..library.strings import v_rtrim
        return v_rtrim(self)

    def v_len(self):
        from ..library.strings import v_len
        return v_len(self)

    def v_reverse(self):
        from ..library.strings import v_strreverse
        return v_strreverse(self)

    def v_split(self, delimiter=None):
        from ..library.strings import v_split
        return v_split(self) if delimiter is None else v_split(self, delimiter)

    def v_replace(self, find, replacewith):
        from ..library.strings import v_replace
        return v_replace(self, find, replacewith)

    def v_left(self, length):
        from ..library.strings import v_left
        return v_left(self, length)

    def v_right(self, length):
        from ..library.strings import v_right
        return v_right(self, length)

    def v_indexof(self, sub):
        from ..library.strings import v_instr
        return v_instr(self, sub)            # 1-based, 0 si absent (comme InStr)

    def v_contains(self, sub):
        from .boolean import boolean, true, false
        return boolean(true) if sub.as_string in self._value else boolean(false)

    def v_startswith(self, prefix):
        from .boolean import boolean, true, false
        return boolean(true) if self._value.startswith(prefix.as_string) else boolean(false)

    def v_endswith(self, suffix):
        from .boolean import boolean, true, false
        return boolean(true) if self._value.endswith(suffix.as_string) else boolean(false)

    # JSON — parse la chaîne en array/dictionary/scalaire (réciproque de `d.ToJson`).
    # `s.FromJson` / `s.AsJson` (nom VDOM) / `s.ParseJson` — délègue à l'extension jsons.
    def v_fromjson(self):
        from ..extensions.jsons import v_fromjson as _fromjson
        return _fromjson(self)

    v_asjson = v_fromjson
    v_parsejson = v_fromjson


from .boolean import boolean, true, false  # noqa: E402
from .date import date  # noqa: E402
from .double import double  # noqa: E402
from .empty import empty  # noqa: E402
from .integer import integer  # noqa: E402
from .null import null, v_null  # noqa: E402


string.add_table = {
    empty: lambda self, another: string(str(self)+str(another)),
    null: lambda self, another: v_null,
    integer: lambda self, another: double(float(self)+int(another)),
    double: lambda self, another: double(float(self)+float(another)),
    date: lambda self, another: date(float(self)+float(another)),
    string: lambda self, another: string(str(self)+str(another)),
    boolean: lambda self, another: double(float(self)+int(another))}

string.sub_table = {
    empty: lambda self, another: double(float(self)-0),
    null: lambda self, another: v_null,
    integer: lambda self, another: double(float(self)-int(another)),
    double: lambda self, another: double(float(self)-float(another)),
    date: lambda self, another: date(float(self)-float(another)),
    string: lambda self, another: double(float(self)-float(another)),
    boolean: lambda self, another: double(float(self)-int(another))}

string.mul_table = {
    empty: lambda self, another: double(float(self)*0),
    null: lambda self, another: v_null,
    integer: lambda self, another: double(float(self)*int(another)),
    double: lambda self, another: double(float(self)*float(another)),
    date: lambda self, another: double(float(self)*float(another)),
    string: lambda self, another: double(float(self)*float(another)),
    boolean: lambda self, another: double(float(self)*int(another))}

string.div_table = {
    empty: lambda self, another: double(float(self)/0),
    null: lambda self, another: v_null,
    integer: lambda self, another: double(float(self)/int(another)),
    double: lambda self, another: double(float(self)/float(another)),
    date: lambda self, another: double(float(self)/float(another)),
    string: lambda self, another: double(float(self)/float(another)),
    boolean: lambda self, another: double(float(self)/int(another))}

string.floordiv_table = {
    empty: lambda self, another: integer(div(int(self), 0)),
    null: lambda self, another: v_null,
    integer: lambda self, another: integer(div(int(self), int(another))),
    double: lambda self, another: integer(div(int(self), int(another))),
    date: lambda self, another: integer(div(int(self), int(another))),
    string: lambda self, another: integer(div(int(self), int(another))),
    boolean: lambda self, another: integer(div(int(self), int(another)))}

string.mod_table = {
    empty: lambda self, another: integer(mod(int(self), 0)),
    null: lambda self, another: v_null,
    integer: lambda self, another: integer(mod(int(self), int(another))),
    double: lambda self, another: integer(mod(int(self), int(another))),
    date: lambda self, another: integer(mod(int(self), int(another))),
    string: lambda self, another: integer(mod(int(self), int(another))),
    boolean: lambda self, another: integer(mod(int(self), int(another)))}

string.pow_table = {
    empty: lambda self, another: double(float(self)**0),
    null: lambda self, another: v_null,
    integer: lambda self, another: double(float(self)**int(another)),
    double: lambda self, another: double(float(self)**float(another)),
    date: lambda self, another: double(float(self)**float(another)),
    string: lambda self, another: double(float(self)**float(another)),
    boolean: lambda self, another: double(float(self)**int(another))}


string.eq_table = {
    empty: lambda self, another: boolean(true) if str(self) == "" else boolean(false),
    null: lambda self, another: v_null,
    integer: lambda self, another: boolean(true) if int(self) == int(another) else boolean(false),
    double: lambda self, another: boolean(true) if float(self) == float(another) else boolean(false),
    date: lambda self, another: boolean(true) if float(self) == float(another) else boolean(false),
    string: lambda self, another: boolean(true) if str(self) == str(another) else boolean(false),
    boolean: lambda self, another: boolean(true) if str(self) == str(another) else boolean(false)}

string.ne_table = {
    empty: lambda self, another: boolean(true) if str(self) != "" else boolean(false),
    null: lambda self, another: v_null,
    integer: lambda self, another: boolean(true) if int(self) != int(another) else boolean(false),
    double: lambda self, another: boolean(true) if float(self) != float(another) else boolean(false),
    date: lambda self, another: boolean(true) if float(self) != float(another) else boolean(false),
    string: lambda self, another: boolean(true) if str(self) != str(another) else boolean(false),
    boolean: lambda self, another: boolean(true) if str(self) != str(another) else boolean(false)}

string.lt_table = {
    empty: lambda self, another: boolean(true) if str(self) < "" else boolean(false),
    null: lambda self, another: v_null,
    integer: lambda self, another: boolean(true) if int(self) < int(another) else boolean(false),
    double: lambda self, another: boolean(true) if float(self) < float(another) else boolean(false),
    date: lambda self, another: boolean(true) if float(self) < float(another) else boolean(false),
    string: lambda self, another: boolean(true) if str(self) < str(another) else boolean(false),
    boolean: lambda self, another: boolean(true) if str(self) < str(another) else boolean(false)}

string.gt_table = {
    empty: lambda self, another: boolean(true) if str(self) > "" else boolean(false),
    null: lambda self, another: v_null,
    integer: lambda self, another: boolean(true) if int(self) > int(another) else boolean(false),
    double: lambda self, another: boolean(true) if float(self) > float(another) else boolean(false),
    date: lambda self, another: boolean(true) if float(self) > float(another) else boolean(false),
    string: lambda self, another: boolean(true) if str(self) > str(another) else boolean(false),
    boolean: lambda self, another: boolean(true) if str(self) > str(another) else boolean(false)}

string.le_table = {
    empty: lambda self, another: boolean(true) if str(self) <= "" else boolean(false),
    null: lambda self, another: v_null,
    integer: lambda self, another: boolean(true) if int(self) <= int(another) else boolean(false),
    double: lambda self, another: boolean(true) if float(self) <= float(another) else boolean(false),
    date: lambda self, another: boolean(true) if float(self) <= float(another) else boolean(false),
    string: lambda self, another: boolean(true) if str(self) <= str(another) else boolean(false),
    boolean: lambda self, another: boolean(true) if str(self) <= str(another) else boolean(false)}

string.ge_table = {
    empty: lambda self, another: boolean(true) if str(self) >= "" else boolean(false),
    null: lambda self, another: v_null,
    integer: lambda self, another: boolean(true) if int(self) >= int(another) else boolean(false),
    double: lambda self, another: boolean(true) if float(self) >= float(another) else boolean(false),
    date: lambda self, another: boolean(true) if float(self) >= float(another) else boolean(false),
    string: lambda self, another: boolean(true) if str(self) >= str(another) else boolean(false),
    boolean: lambda self, another: boolean(true) if str(self) >= str(another) else boolean(false)}


string.and_table = {
    empty: lambda self, another: integer(int(self) & 0),
    null: lambda self, another: v_null if int(self) else integer(int(self)),
    integer: lambda self, another: integer(int(self) & int(another)),
    double: lambda self, another: integer(int(self) & int(another)),
    date: lambda self, another: integer(int(self) & int(another)),
    string: lambda self, another: integer(int(self) & int(another)),
    boolean: lambda self, another: integer(int(self) & int(another))}

string.or_table = {
    empty: lambda self, another: integer(int(self) | 0),
    null: lambda self, another: integer(int(self)) if int(self) else v_null,
    integer: lambda self, another: integer(int(self) | int(another)),
    double: lambda self, another: integer(int(self) | int(another)),
    date: lambda self, another: integer(int(self) | int(another)),
    string: lambda self, another: integer(int(self) | int(another)),
    boolean: lambda self, another: integer(int(self) | int(another))}

string.xor_table = {
    empty: lambda self, another: integer(int(self) ^ 0),
    null: lambda self, another: v_null if int(self) else v_null,
    integer: lambda self, another: integer(int(self) ^ int(another)),
    double: lambda self, another: integer(int(self) ^ int(another)),
    date: lambda self, another: integer(int(self) ^ int(another)),
    string: lambda self, another: integer(int(self) ^ int(another)),
    boolean: lambda self, another: integer(int(self) ^ int(another))}
