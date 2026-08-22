"""VAILS — VScript Tier 4 : méthodes fonctionnelles `arr.map/filter/reduce`.

Débloquées par les fonctions-valeurs (lambdas inline + AddressOf). Sémantique 1-D.
Cf. vscript/subtypes/array.py (v_map/v_filter/v_reduce).
"""

from ...testing import VScriptTestCase


class TestMap(VScriptTestCase):

    def test_map_double(self):
        assert self.execute(
            "a = [1, 2, 3]\n"
            "b = a.map(Function(x) Return x * 2 End Function)\n"
            "result = b(0) + b(1) + b(2)").is_integer(12)

    def test_map_preserves_length(self):
        assert self.execute(
            "a = [5, 6, 7, 8]\n"
            "b = a.map(Function(x) Return x + 1 End Function)\n"
            "result = b.count").is_integer(4)

    def test_map_to_strings(self):
        assert self.execute(
            'a = [1, 2]\n'
            'b = a.map(Function(x) Return "n" & x End Function)\n'
            'result = b(1)').is_string(u"n2")

    def test_map_with_addressof(self):
        # fonction-valeur non-lambda : AddressOf d'une fonction nommée.
        assert self.execute(
            "Function dbl(x)\n"
            "  Return x * 2\n"
            "End Function\n"
            "a = [10, 20]\n"
            "b = a.map(AddressOf dbl)\n"
            "result = b(0) + b(1)").is_integer(60)


class TestFilter(VScriptTestCase):

    def test_filter_evens(self):
        assert self.execute(
            "a = [1, 2, 3, 4, 5, 6]\n"
            "b = a.filter(Function(x) Return x mod 2 = 0 End Function)\n"
            "result = b.count").is_integer(3)

    def test_filter_keeps_values(self):
        assert self.execute(
            "a = [1, 2, 3, 4]\n"
            "b = a.filter(Function(x) Return x > 2 End Function)\n"
            "result = b(0) * 10 + b(1)").is_integer(34)  # [3, 4]

    def test_filter_none_match(self):
        assert self.execute(
            "a = [1, 2, 3]\n"
            "b = a.filter(Function(x) Return x > 100 End Function)\n"
            "result = b.count").is_integer(0)


class TestReduce(VScriptTestCase):

    def test_reduce_sum_with_init(self):
        assert self.execute(
            "a = [1, 2, 3, 4]\n"
            "result = a.reduce(Function(acc, x) Return acc + x End Function, 0)").is_integer(10)

    def test_reduce_sum_no_init_uses_first(self):
        assert self.execute(
            "a = [10, 20, 30]\n"
            "result = a.reduce(Function(acc, x) Return acc + x End Function)").is_integer(60)

    def test_reduce_init_offsets(self):
        assert self.execute(
            "a = [1, 2, 3]\n"
            "result = a.reduce(Function(acc, x) Return acc + x End Function, 100)").is_integer(106)

    def test_reduce_string_concat(self):
        assert self.execute(
            'a = ["a", "b", "c"]\n'
            'result = a.reduce(Function(acc, x) Return acc & x End Function, "")').is_string(u"abc")


class TestChaining(VScriptTestCase):

    def test_filter_then_map(self):
        # garde les pairs, puis les triple : [2,4,6] -> [6,12,18] -> somme 36
        assert self.execute(
            "a = [1, 2, 3, 4, 5, 6]\n"
            "b = a.filter(Function(x) Return x mod 2 = 0 End Function) _\n"
            "     .map(Function(x) Return x * 3 End Function)\n"
            "result = b(0) + b(1) + b(2)").is_integer(36)

    def test_closure_capture_in_map(self):
        # le facteur est capturé (closure) par la lambda passée à map.
        assert self.execute(
            "dim factor\n"
            "factor = 10\n"
            "a = [1, 2, 3]\n"
            "b = a.map(Function(x) Return x * factor End Function)\n"
            "result = b(0) + b(1) + b(2)").is_integer(60)
