
import types
from importlib import import_module
import random
import re
from . import errors
from .primitives import subtype, variable
from .subtypes import string, integer, double, null, empty, nothing, v_empty, generic
from .variables import variant


subtype.byref = property(lambda self: variant(self))
subtype.byval = property(lambda self: variant(self.copy))
variable.byref = property(lambda self: self)
variable.byval = property(lambda self: variant(self.subtype.copy))


def check(value):
    if isinstance(value, (types.FunctionType, types.MethodType)):
        try:
            return value()
        except TypeError as error:
            match = re.search(
                r"(.+)\(\) (?:takes no arguments)|(?:takes exactly \d+ arguments) \(\d+ given\)", getattr(error, "message", str(error)))
            if match:
                raise errors.wrong_number_of_arguments(name=match.group(1))
            else:
                raise
    else:
        return value


def randomize(seed=None):
    random.seed(seed)


def echo(*arguments):
    debug(" ".join([str(argument.as_simple)
          for argument in arguments]), console=True)


def concat(*arguments):
    return string(u"".join(str(argument.as_simple) for argument in arguments))


# VAILS — court-circuit logique de `And`/`Or` (amélioration VScript : en VBScript
# classique les deux opérandes sont toujours évalués). `right` est un thunk : il
# n'est appelé que si la gauche ne détermine pas déjà le résultat.
#
# Le court-circuit est limité aux gauches NUMÉRIQUES déterminantes :
#   And : gauche integer/double valant 0, ou empty  -> 0 & x == 0       => 0
#   Or  : gauche integer/double valant -1            -> -1 | x == -1     => -1
# Null, booléens et chaînes passent par l'évaluation complète, ce qui préserve
# la logique à trois valeurs (`False And Null` => False, `Null And 5` => Null,
# etc.) — cf. tests subtypes/*/test_logic.

def vand(left, right):
    s = left.as_simple
    t = type(s)
    if (t is integer and s.value == 0) or (t is double and s.value == 0.0):
        return integer(0)
    return left & right()


def vor(left, right):
    s = left.as_simple
    t = type(s)
    if (t is integer and s.value == -1) or (t is double and s.value == -1.0):
        return integer(-1)
    return left | right()


# VAILS — coalescing `??` : renvoie `left`, sauf s'il est Null ou Empty → `right`
# (thunk, évalué à la demande). Modernisation (cf. TODO/vscript-modern.md).
def vcoalesce(left, right):
    t = type(left.as_simple)
    if t is null or t is empty:
        return right()
    return left


# VAILS — optional chaining `obj?.member` (Tier 3). Renvoie Empty si `obj` est
# Null/Empty/Nothing (court-circuit nullish), sinon accès membre normal (unwrap via
# variant.__getattr__ + auto-appel d'un membre 0-arg, comme `check(obj).membre`).
# Chaînable : `a?.b?.c` compose en `vget(vget(a, "v_b"), "v_c")`.
def vget(obj, name):
    # On teste le subtype SANS coercition : `as_simple` sur un objet (generic) appellerait
    # sa propriété par défaut (et lèverait). `subtype` renvoie le subtype sous-jacent
    # (variant -> contenu ; subtype -> lui-même).
    sub = obj.subtype
    if isinstance(sub, (null, empty, nothing)):
        return v_empty
    return check(getattr(obj, name))


# VAILS — `For Each k, v In dict` (Tier 3) : yield les paires (clé, valeur) d'un
# dictionnaire, sous forme de variants. Erreur si la collection n'est pas un dictionnaire.
def vitems(coll):
    sub = coll.subtype
    items = getattr(sub, "_items", None)
    if not isinstance(items, dict):
        raise errors.type_mismatch()
    for key, value in items.items():
        yield variant(key), variant(value)


# VAILS — `Enum … End Enum` (Tier 3). `venum` : objet exposant `Color.Red` (membre -> entier).
class venum(generic):
    def __init__(self, members):
        self._members = members  # {nom_minuscule: integer}

    # Objet : se renvoie lui-même à la coercition (sinon generic.as_simple ferait self()).
    as_simple = property(lambda self: self)
    as_complex = property(lambda self: self)

    def __getattr__(self, attr):
        if attr.startswith(u"v_"):
            m = object.__getattribute__(self, "_members").get(attr[2:])
            if m is not None:
                return lambda: m  # callable -> auto-appelé par check(), renvoie l'entier
        raise AttributeError(attr)

    def __call__(self, *arguments, **keywords):
        # accès par nom : Color("red") -> valeur (en plus de Color.Red)
        if len(arguments) == 1:
            m = self._members.get(arguments[0].as_string.lower())
            if m is not None:
                return m
        return self


# VAILS — fonctions de première classe (Tier 3). `AddressOf nom` -> `vfuncref(v_nom)` :
# objet appelable tenant une fonction VScript, stockable dans une variable et invocable
# (`set f = AddressOf add` puis `f(2, 3)`). variant.__call__ délègue à `_value(*args)`.
class vfuncref(generic):
    def __init__(self, func):
        self._func = func

    as_simple = property(lambda self: self)
    as_complex = property(lambda self: self)

    def __call__(self, *arguments, **keywords):
        return self._func(*arguments, **keywords)


# VAILS — `f()` à ZÉRO argument (Tier 4). En VScript classique `f()` (parenthèses vides)
# renvoyait le nom nu (pas d'invocation), donc une fonction-VALEUR stockée (lambda inline ou
# `AddressOf`) ne s'appelait pas. `vcall0` invoque si la valeur est appelable, sinon la renvoie
# inchangée — `x()` sur un non-appelable reste `x` (compat). Les fonctions NOMMÉES (FunctionType,
# déjà auto-appelées par `check`) sont aussi couvertes.
def vcall0(value):
    if isinstance(value, (types.FunctionType, types.MethodType)):
        return value()
    if isinstance(getattr(value, "subtype", None), vfuncref):
        return value()                       # variant tenant une vfuncref -> variant.__call__()
    return value


def venum_build(pairs):
    # pairs : [(nom_minuscule, valeur_ou_None)] ; auto-incrément (0, puis +1), valeur explicite override.
    members = {}
    counter = -1
    for name, value in pairs:
        if value is None:
            counter += 1
            members[name] = integer(counter)
        else:
            iv = int(value)
            members[name] = integer(iv)
            counter = iv
    return venum(members)


class exitloop(Exception):
    pass


class exitdo(exitloop):
    pass


class exitfor(exitloop):
    pass


def vimport(package, name, namespace, names):
    """Import a VScript library into the caller's namespace.

    "use" emitted "from <name> import ..." with the BARE library name. The
    scripting finder cannot resolve that: a plugin library is registered as
    "<application>:<context>.<name>", and a bare name matches its regex not at
    all - the lookup returns None and the import fails. It only ever worked for
    modules importable under their own name.

    Emitting the qualified name is not an option either: it holds ":" and "-",
    so "from <application>:<context>.<name> import x" is a syntax error. Hence
    a call - import_module takes the name as a string, where the statement
    could not.
    """
    module = import_module("%s.%s" % (package, name) if package else name)
    for each in names:
        namespace[each] = getattr(module, each)
