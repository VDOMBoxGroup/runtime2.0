"""VAILS — modernisation VScript (Tier 1) : littéraux [..]/{..}, ??, op=, IIf.

Cf. TODO/vscript-modern.md. Ajouts purement additifs.
"""

from ...testing import VScriptTestCase


class TestLiterals(VScriptTestCase):

    def test_array_index(self):
        assert self.execute("a = [10, 20, 30]\nresult = a(1)").is_integer(20)

    def test_array_ubound(self):
        assert self.execute("a = [10, 20, 30]\nresult = UBound(a)").is_integer(2)

    def test_empty_array_parses(self):
        assert self.execute("a = []\nresult = 1").is_integer(1)

    def test_dict_string_value(self):
        assert self.execute('d = {"id": 7, "name": "z"}\nresult = d("name")').is_string(u"z")

    def test_dict_int_value(self):
        assert self.execute('d = {"id": 7}\nresult = d("id")').is_integer(7)

    def test_nested_dict_array(self):
        assert self.execute('d = {"items": [1, 2, 3]}\nresult = d("items")(2)').is_integer(3)

    def test_array_of_records(self):
        assert self.execute('a = [{"id": 1}, {"id": 2}]\nresult = a(1)("id")').is_integer(2)

    def test_dict_iteration_keys(self):
        assert self.execute('d = {"a": 1, "b": 2}\nr = ""\nfor each k in d\n r = r & k\nnext\nresult = r') \
            .is_string(u"ab")


class TestCoalesce(VScriptTestCase):

    def test_null(self):
        assert self.evaluate("null ?? 42").is_integer(42)

    def test_empty(self):
        assert self.evaluate("empty ?? 42").is_integer(42)

    def test_present(self):
        assert self.evaluate('"x" ?? 42').is_string(u"x")

    def test_chain(self):
        assert self.evaluate("null ?? empty ?? 7").is_integer(7)

    def test_lazy_right_not_evaluated(self):
        # `1 \ 0` lèverait division_by_zero s'il était évalué
        assert self.evaluate('"x" ?? (1 \\ 0)').is_string(u"x")


class TestCompoundAssign(VScriptTestCase):

    def test_plus(self):
        assert self.execute("x = 10\nx += 5\nresult = x").is_integer(15)

    def test_minus_keeps_precedence(self):
        assert self.execute("x = 10\nx -= 2 + 3\nresult = x").is_integer(5)

    def test_star(self):
        assert self.execute("x = 6\nx *= 7\nresult = x").is_integer(42)

    def test_slash(self):
        # `/` est la division flottante en VScript -> double 5.0
        assert self.execute("x = 20\nx /= 4\nresult = x").is_double(5.0)

    def test_integer_division(self):
        assert self.execute("x = 17\nx \\= 5\nresult = x").is_integer(3)

    def test_concat(self):
        assert self.execute('s = "a"\ns &= "b" & "c"\nresult = s').is_string(u"abc")


class TestIIf(VScriptTestCase):

    def test_true_branch(self):
        assert self.evaluate('IIf(2 > 1, "yes", "no")').is_string(u"yes")

    def test_false_branch(self):
        assert self.evaluate('IIf(1 > 2, "yes", "no")').is_string(u"no")
