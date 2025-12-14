
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestEmptyConjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty and empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("empty and null").is_integer(0)

    def test_integer(self):
        assert self.evaluate("empty and 456").is_integer(0)
        assert self.evaluate("empty and 123").is_integer(0)
        assert self.evaluate("empty and 0").is_integer(0)

    def test_double(self):
        assert self.evaluate("empty and 456.789").is_integer(0)
        assert self.evaluate("empty and 123.456").is_integer(0)
        assert self.evaluate("empty and 0.0").is_integer(0)

    def test_date(self):
        assert self.evaluate("empty and #31.03.1901 18:56:10#").is_integer(0)
        assert self.evaluate("empty and #02.05.1900 10:56:38#").is_integer(0)
        assert self.evaluate("empty and #30.12.1899#").is_integer(0)

    def test_string(self):
        assert self.evaluate("empty and \"456\"").is_integer(0)
        assert self.evaluate("empty and \"123\"").is_integer(0)
        assert self.evaluate("empty and \"0\"").is_integer(0)
        assert self.evaluate("empty and \"456.789\"").is_integer(0)
        assert self.evaluate("empty and \"123.456\"").is_integer(0)
        assert self.evaluate("empty and \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("empty and \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty and \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty and new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty and nothing")

    def test_boolean(self):
        assert self.evaluate("empty and true").is_integer(0)
        assert self.evaluate("empty and false").is_integer(0)

class TestEmptyDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty or empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("empty or null").is_null

    def test_integer(self):
        assert self.evaluate("empty or 456").is_integer(456)
        assert self.evaluate("empty or 123").is_integer(123)
        assert self.evaluate("empty or 0").is_integer(0)

    def test_double(self):
        assert self.evaluate("empty or 456.789").is_integer(457)
        assert self.evaluate("empty or 123.456").is_integer(123)
        assert self.evaluate("empty or 0.0").is_integer(0)

    def test_date(self):
        assert self.evaluate("empty or #31.03.1901 18:56:10#").is_integer(457)
        assert self.evaluate("empty or #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("empty or #30.12.1899#").is_integer(0)

    def test_string(self):
        assert self.evaluate("empty or \"456\"").is_integer(456)
        assert self.evaluate("empty or \"123\"").is_integer(123)
        assert self.evaluate("empty or \"0\"").is_integer(0)
        assert self.evaluate("empty or \"456.789\"").is_integer(457)
        assert self.evaluate("empty or \"123.456\"").is_integer(123)
        assert self.evaluate("empty or \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("empty or \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty or \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty or new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty or nothing")

    def test_boolean(self):
        assert self.evaluate("empty or true").is_integer(-1)
        assert self.evaluate("empty or false").is_integer(0)

class TestEmptyExclusiveDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty xor empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("empty xor null").is_null

    def test_integer(self):
        assert self.evaluate("empty xor 456").is_integer(456)
        assert self.evaluate("empty xor 123").is_integer(123)
        assert self.evaluate("empty xor 0").is_integer(0)

    def test_double(self):
        assert self.evaluate("empty xor 456.789").is_integer(457)
        assert self.evaluate("empty xor 123.456").is_integer(123)
        assert self.evaluate("empty xor 0.0").is_integer(0)

    def test_date(self):
        assert self.evaluate("empty xor #31.03.1901 18:56:10#").is_integer(457)
        assert self.evaluate("empty xor #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("empty xor #30.12.1899#").is_integer(0)

    def test_string(self):
        assert self.evaluate("empty xor \"456\"").is_integer(456)
        assert self.evaluate("empty xor \"123\"").is_integer(123)
        assert self.evaluate("empty xor \"0\"").is_integer(0)
        assert self.evaluate("empty xor \"456.789\"").is_integer(457)
        assert self.evaluate("empty xor \"123.456\"").is_integer(123)
        assert self.evaluate("empty xor \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("empty xor \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty xor \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty xor new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty xor nothing")

    def test_boolean(self):
        assert self.evaluate("empty xor true").is_integer(-1)
        assert self.evaluate("empty xor false").is_integer(0)
