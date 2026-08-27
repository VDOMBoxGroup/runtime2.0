
from copy import deepcopy
from .. import errors
from ..primitives import subtype
from .empty import v_empty
from ..variables import variant
from functools import reduce


def measure(items):
    subscripts = []
    while True:
        subscripts.insert(0, len(items) - 1)
        if not items:
            break
        items = items[0]
        if not isinstance(items, list):
            break
    return subscripts


def dim(subscripts):
    array = [v_empty] * (subscripts[0] + 1)
    for subscript in subscripts[1:]:
        item = array
        array = [item]
        for index in range(subscript):
            array.append(deepcopy(item))
    return array


def copylist(items):
    return [copylist(item) for item in items] \
        if items and isinstance(items[0], list) \
        else [item.copy for item in items]


def redim(items, subscripts, index):
    subscript = subscripts[index]
    if index > 0:
        if subscript != len(items) - 1:
            raise errors.subscript_out_of_range
        for item in items:
            redim(item, subscripts, index - 1)
    else:
        if subscript < 0:
            raise errors.subscript_out_of_range
        elif subscript < len(items) - 1:
            del items[subscript + 1:]
        elif subscript > len(items) - 1:
            items.extend([v_empty] * (subscript + 1 - len(items)))


def erase(items):
    if items and isinstance(items[0], list):
        for item in items:
            erase(item)
    else:
        items[:] = [v_empty] * len(items)


class array(subtype):

    def __init__(self, items=None, subscripts=None, static=None):
        if items is not None:
            if not isinstance(items, list):
                items = list(items)
            self._items = items
            self._subscripts = measure(items)
            self._static = static
        elif subscripts is not None:
            if not isinstance(subscripts, list):
                items = list(items)
            self._items = dim(subscripts)
            self._subscripts = subscripts
            self._static = static
        else:
            self._items = []
            self._subscripts = [-1]
            self._static = static

    def __call__(self, *arguments, **keywords):
        if "let" in keywords:
            if len(arguments) != len(self._subscripts):
                raise errors.wrong_number_of_arguments
            simple, items = keywords["let"].as_simple, self._items
            try:
                for index in arguments[-1:0:-1]:
                    items = items[index.as_integer]
                items[arguments[0].as_integer] = simple
            except IndexError:
                raise errors.subscript_out_of_range
        elif "set" in keywords:
            if len(arguments) != len(self._subscripts):
                raise errors.wrong_number_of_arguments
            complex, items = keywords["set"].as_complex, self._items
            try:
                for index in arguments[-1:0:-1]:
                    items = items[index.as_integer]
                items[arguments[0].as_integer] = complex
            except IndexError:
                raise errors.subscript_out_of_range
        else:
            if len(arguments) != len(self._subscripts):
                raise errors.wrong_number_of_arguments
            result = self._items
            try:
                for index in reversed(arguments):
                    result = result[index.as_integer]
                return result
            except IndexError:
                raise errors.subscript_out_of_range

    copy = property(lambda self: array(copylist(self._items),
                                       subscripts=deepcopy(self._subscripts), static=self._static))

    code = property(lambda self: 8204)
    name = property(lambda self: "Array")

    def redim(self, preserve, *subscripts):
        if self._static:
            raise errors.static_array
        if subscripts:
            self._subscripts = [
                subscript.as_integer for subscript in subscripts]
            if preserve:
                redim(self._items, self._subscripts, len(self._subscripts) - 1)
            else:
                self._items = dim(self._subscripts)
        else:
            self._items = []
            self._subscripts = [-1]

    def erase(self, *arguments):
        if self._static:
            if arguments:
                if len(arguments) > len(self._subscripts):
                    raise errors.wrong_number_of_arguments
                elif len(arguments) < len(self._subscripts):
                    items = self._items
                    try:
                        for index in reversed(arguments):
                            items = items[index.as_integer]
                    except IndexError:
                        raise errors.subscript_out_of_range
                    erase(items)
                else:
                    items = self._items
                    try:
                        for index in arguments[-1:0:-1]:
                            items = items[index.as_integer]
                        items[arguments[0].as_integer] = v_empty
                    except IndexError:
                        raise errors.subscript_out_of_range
            else:
                erase(self._items)
        else:
            if arguments:
                if len(arguments) > 1:
                    raise errors.wrong_number_of_arguments
                try:
                    del self._items[arguments[0].as_integer]
                except KeyError:
                    raise errors.subscript_out_of_range
                self._subscripts[0] -= 1
            else:
                del self._items[:]
                self._subscripts = []

    as_simple = property(lambda self: self)
    as_array = property(lambda self: self)
    # VAILS — autorise l'accès membre `a.method` (variant.__getattr__ -> as_complex).
    as_complex = property(lambda self: self)

    def is_array(self, *arguments, **keywords):
        if keywords:
            if "length" in keywords:
                if len(self._items) != keywords.pop("length"):
                    return False
            if keywords:
                raise TypeError(
                    "is_array got an unexpected keyword argument %r" % next(iter(keywords)))
        if arguments:
            if len(arguments) > 1:
                return len(self._items) == len(arguments) and \
                    all(function(item)
                        for function, item in zip(arguments, self._items))
            elif isinstance(arguments[0], tuple):
                return len(self._items) == len(arguments[0]) and \
                    all(function(item)
                        for function, item in zip(arguments[0], self._items))
            else:
                if arguments[0].__code__.co_argcount > 1:
                    return all((arguments[0](index, item) for index, item in enumerate(self._items)))
                else:
                    return arguments[0](self._items)
        return True

    dimension = property(lambda self: len(self._subscripts))
    items = property(lambda self: self._items)

    # VAILS — méthodes membres fluides (Tier 2 #7). `a.count`/`a.contains(x)`/…
    def v_count(self):
        from .integer import integer
        return integer(len(self))

    def v_contains(self, item):
        from .boolean import boolean, true, false
        target = item.as_string
        for el in self:
            if el.as_string == target:
                return boolean(true)
        return boolean(false)

    def v_indexof(self, item):
        from .integer import integer
        target = item.as_string
        i = 1
        for el in self:
            if el.as_string == target:
                return integer(i)
            i += 1
        return integer(0)            # 0 si absent (cohérent avec InStr)

    def v_join(self, delimiter=None):
        from ..library.arrays import v_join
        return v_join(self) if delimiter is None else v_join(self, delimiter)

    def v_first(self):
        for el in self:
            return el.subtype
        return v_empty

    def v_last(self):
        last = None
        for el in self:
            last = el
        return last.subtype if last is not None else v_empty

    # VAILS — méthodes FONCTIONNELLES (Tier 4). Prennent une fonction-valeur (`vfuncref`,
    # issue d'une lambda inline `Function(x)…End Function` ou d'`AddressOf`) et l'appliquent.
    # `func(el)` invoque la fonction (variant.__call__ -> vfuncref) et renvoie un subtype.
    # Sémantique 1-D : un tableau multi-dim est parcouru à plat ; le résultat est 1-D.
    def v_map(self, func):
        # nouveau tableau : func appliquée à chaque élément.
        return array([func(el).as_simple for el in self])

    def v_filter(self, func):
        # sous-tableau des éléments pour lesquels le prédicat func est vrai (vérité VScript).
        return array([el.as_simple for el in self if bool(func(el))])

    def v_reduce(self, func, init=None):
        # repli (fold) : func(accumulateur, élément). Sans `init`, le 1er élément sert
        # d'amorce ; tableau vide sans `init` -> Empty.
        acc = init
        started = init is not None
        for el in self:
            if started:
                acc = func(acc, el)
            else:
                acc, started = el, True
        return acc.subtype if started else v_empty

    def v_tojson(self, pretty=None):
        from ..extensions.jsons import v_tojson as _tojson
        return _tojson(self, pretty)

    def subarray(self, *indices):
        if len(indices) >= len(self._subscripts):
            raise errors.wrong_number_of_arguments
        items = self._items
        try:
            for index in reversed(indices):
                items = items[index]
        except IndexError:
            raise errors.subscript_out_of_range
        return copylist(items)

    def flatten(self):
        if len(self._subscripts) == 1:
            return list(self._items)
        else:
            return list(self)

    def lbound(self, dimension):
        if dimension < 1 or dimension > len(self._subscripts):
            raise errors.subscript_out_of_range
        # NOTE: VBScript returns zero
        # if self._subscripts[dimension-1]<0:
        #   raise errors.subscript_out_of_range
        return 0

    def ubound(self, dimension):
        if dimension < 1 or dimension > len(self._subscripts):
            raise errors.subscript_out_of_range
        # An empty array has an upper bound of -1, which is what VBScript
        # answers and what makes the ordinary idiom work by itself:
        #
        #     rows = Database("X").Query("select …")
        #     For i = 0 To UBound(rows)      ' no rows -> 0 to -1 -> no turn
        #
        # This used to raise subscript_out_of_range instead, so every caller
        # that might get no rows had to wrap UBound in a Try purely to learn
        # that a list was empty - and one that forgot died on a query that
        # simply matched nothing, which is not an error anywhere else in the
        # language. LBound already returns 0 for the same array, so the pair
        # 0 / -1 is the signature of "empty" that VBScript code tests for.
        #
        # `Dim a()` - declared, never dimensioned - answers -1 here too, where
        # VBScript raises. The two are the same value in this representation
        # (`_subscripts == [-1]`) and telling them apart would mean a third
        # state on every array, for a case where -1 only makes the loop above
        # do nothing.
        return self._subscripts[dimension - 1]

    def append(self, value):
        if len(self._subscripts) != 1:
            raise errors.invalid_procedure_call
        if self._static:
            raise errors.static_array
        self._items.append(value.as_simple)
        self._subscripts[0] += 1

    def remove(self, value):
        if len(self._subscripts) != 1:
            raise errors.invalid_procedure_call
        if self._static:
            raise errors.static_array
        simple = value.as_simple
        self._items = [item for item in self._items if item != simple]
        self._subscripts = [len(self._items) - 1]

    def __iter__(self):
        edge = len(self._subscripts) - 1
        if edge < 0:
            return
        iterators = [None] * len(self._subscripts)
        iterators[edge] = iter(self._items)
        level = edge
        while level <= edge:
            if level:
                try:
                    array = next(iterators[level])
                except StopIteration:
                    level += 1
                else:
                    level -= 1
                    iterators[level] = iter(array)
            else:
                for item in iterators[level]:
                    yield variant(item)
                level += 1

    def __len__(self):
        return reduce(lambda x, y: x * (y + 1), self._subscripts, 1)

    def __repr__(self):
        return "ARRAY@%08X:%r" % (id(self), self._items)
