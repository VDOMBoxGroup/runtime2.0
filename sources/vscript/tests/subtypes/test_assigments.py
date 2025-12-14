
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestAssigments(VScriptTestCase):

    def test_integer_assigment(self):
        assert self.evaluate("1").is_integer(1)

    def test_string_assigment(self):
        assert self.evaluate("\"abc\"").is_string(u"abc")

    def test_double_assigment(self):
        assert self.evaluate("1.23").is_double(1.23)

    def test_nan_assigment(self):
        assert self.evaluate("nan").is_double(nan)

    def test_infinity_assigment(self):
        assert self.evaluate("infinity").is_double(infinity)

    def test_true_assigment(self):
        assert self.evaluate("true").is_boolean(true)

    def test_false_assigment(self):
        assert self.evaluate("false").is_boolean(false)

    def test_date_assigment(self):
        assert self.evaluate("#02.05.1900 02:57:18#").is_date(1900, 5, 2, 2, 57, 18)

    def test_empty_assigment(self):
        assert self.evaluate("empty").is_empty

    def test_null_assigment(self):
        assert self.evaluate("null").is_null

    def test_generic_assigment(self):
        assert self.evaluate("class object end", set="new object").is_generic

    def test_nothing_assigment(self):
        assert self.evaluate(set="nothing").is_nothing

class TestWrongAssigments(VScriptTestCase):

    def test_wrong_integer_assigment(self):
        with raises(errors.object_required):
            self.evaluate(set="1")

    def test_wrong_generic_assigment(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", let="new object")

    def test_wrong_nothing_assigment(self):
        with raises(errors.object_variable_not_set):
            self.evaluate(let="nothing")
