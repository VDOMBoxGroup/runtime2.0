
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestNullConjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null and empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("null and null").is_null

    def test_integer(self):
        assert self.evaluate("null and 456").is_null
        assert self.evaluate("null and 123").is_null
        assert self.evaluate("null and 0").is_integer(0)

    def test_double(self):
        assert self.evaluate("null and 456.789").is_null
        assert self.evaluate("null and 123.456").is_null
        assert self.evaluate("null and 0.0").is_integer(0)

    def test_date(self):
        assert self.evaluate("null and #31.03.1901 18:56:10#").is_null
        assert self.evaluate("null and #02.05.1900 10:56:38#").is_null
        assert self.evaluate("null and #30.12.1899#").is_integer(0)

    def test_string(self):
        assert self.evaluate("null and \"456\"").is_null
        assert self.evaluate("null and \"123\"").is_null
        assert self.evaluate("null and \"0\"").is_integer(0)
        assert self.evaluate("null and \"456.789\"").is_null
        assert self.evaluate("null and \"123.456\"").is_null
        assert self.evaluate("null and \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("null and \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("null and \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null and new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null and nothing")

    def test_boolean(self):
        assert self.evaluate("null and true").is_null
        assert self.evaluate("null and false").is_boolean(false)

class TestNullDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null or empty").is_null

    def test_null(self):
        assert self.evaluate("null or null").is_null

    def test_integer(self):
        assert self.evaluate("null or 456").is_integer(456)
        assert self.evaluate("null or 123").is_integer(123)
        assert self.evaluate("null or 0").is_null

    def test_double(self):
        assert self.evaluate("null or 457.456").is_integer(457)
        assert self.evaluate("null or 123.456").is_integer(123)
        assert self.evaluate("null or 0.0").is_null

    def test_date(self):
        assert self.evaluate("null or #31.03.1901 18:56:10#").is_integer(457), self.evaluate("null or #31.03.1901 18:56:10#")
        assert self.evaluate("null or #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("null or #30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null or \"456\"").is_integer(456)
        assert self.evaluate("null or \"123\"").is_integer(123)
        assert self.evaluate("null or \"0\"").is_null
        assert self.evaluate("null or \"456.789\"").is_integer(457)
        assert self.evaluate("null or \"123.456\"").is_integer(123)
        assert self.evaluate("null or \"0.0\"").is_null
        with raises(errors.type_mismatch):
            self.evaluate("null or \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("null or \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null or new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null or nothing")

    def test_boolean(self):
        assert self.evaluate("null or true").is_boolean(true)
        assert self.evaluate("null or false").is_null

class TestNullExclusiveDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null xor empty").is_null

    def test_null(self):
        assert self.evaluate("null xor null").is_null

    def test_integer(self):
        assert self.evaluate("null xor 456").is_null
        assert self.evaluate("null xor 123").is_null
        assert self.evaluate("null xor 0").is_null

    def test_double(self):
        assert self.evaluate("null xor 456.789").is_null
        assert self.evaluate("null xor 123.456").is_null
        assert self.evaluate("null xor 0.0").is_null

    def test_date(self):
        assert self.evaluate("null xor #31.03.1901 18:56:10#").is_null
        assert self.evaluate("null xor #02.05.1900 10:56:38#").is_null
        assert self.evaluate("null xor #30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null xor \"456\"").is_null
        assert self.evaluate("null xor \"123\"").is_null
        assert self.evaluate("null xor \"0\"").is_null
        assert self.evaluate("null xor \"456.789\"").is_null
        assert self.evaluate("null xor \"123.456\"").is_null
        assert self.evaluate("null xor \"0.0\"").is_null
        with raises(errors.type_mismatch):
            self.evaluate("null xor \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("null xor \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null xor new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null xor nothing")

    def test_boolean(self):
        assert self.evaluate("null xor true").is_null
        assert self.evaluate("null xor false").is_null
