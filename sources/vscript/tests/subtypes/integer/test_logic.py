
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestIntegerConjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123 and empty").is_integer(0)
        assert self.evaluate("0 and empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("123 and null").is_null
        assert self.evaluate("0 and null").is_integer(0)

    def test_integer(self):
        assert self.evaluate("123 and 456").is_integer(72)
        assert self.evaluate("123 and 123").is_integer(123)
        assert self.evaluate("123 and 0").is_integer(0)

    def test_double(self):
        assert self.evaluate("123 and 456.789").is_integer(73)
        assert self.evaluate("123 and 123.456").is_integer(123)
        assert self.evaluate("123 and 0.0").is_integer(0)

    def test_date(self):
        assert self.evaluate("123 and #31.03.1901 18:56:10#").is_integer(73)
        assert self.evaluate("123 and #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("123 and #30.12.1899#").is_integer(0)

    def test_string(self):
        assert self.evaluate("123 and \"456\"").is_integer(72)
        assert self.evaluate("123 and \"123\"").is_integer(123)
        assert self.evaluate("123 and \"0\"").is_integer(0)
        assert self.evaluate("123 and \"456.789\"").is_integer(73)
        assert self.evaluate("123 and \"123.456\"").is_integer(123)
        assert self.evaluate("123 and \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("123 and \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123 and \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123 and new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123 and nothing")

    def test_boolean(self):
        assert self.evaluate("123 and true").is_integer(123)
        assert self.evaluate("123 and false").is_integer(0)

class TestIntegerDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123 or empty").is_integer(123)
        assert self.evaluate("0 or empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("123 or null").is_integer(123)
        assert self.evaluate("0 or null").is_null

    def test_integer(self):
        assert self.evaluate("123 or 456").is_integer(507)
        assert self.evaluate("123 or 123").is_integer(123)
        assert self.evaluate("123 or 0").is_integer(123)

    def test_double(self):
        assert self.evaluate("123 or 456.789").is_integer(507)
        assert self.evaluate("123 or 123.456").is_integer(123)
        assert self.evaluate("123 or 0.0").is_integer(123)

    def test_date(self):
        assert self.evaluate("123 or #31.03.1901 18:56:10#").is_integer(507)
        assert self.evaluate("123 or #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("123 or #30.12.1899#").is_integer(123)

    def test_string(self):
        assert self.evaluate("123 or \"456\"").is_integer(507)
        assert self.evaluate("123 or \"123\"").is_integer(123)
        assert self.evaluate("123 or \"0\"").is_integer(123)
        assert self.evaluate("123 or \"456.789\"").is_integer(507)
        assert self.evaluate("123 or \"123.456\"").is_integer(123)
        assert self.evaluate("123 or \"0.0\"").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("123 or \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123 or \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123 or new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123 or nothing")

    def test_boolean(self):
        assert self.evaluate("123 or true").is_integer(-1)
        assert self.evaluate("123 or false").is_integer(123)

class TestIntegerExclusiveDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123 xor empty").is_integer(123)
        assert self.evaluate("0 xor empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("123 xor null").is_null
        assert self.evaluate("0 xor null").is_null

    def test_integer(self):
        assert self.evaluate("123 xor 456").is_integer(435)
        assert self.evaluate("123 xor 123").is_integer(0)
        assert self.evaluate("123 xor 0").is_integer(123)

    def test_double(self):
        assert self.evaluate("123 xor 456.789").is_integer(434)
        assert self.evaluate("123 xor 123.456").is_integer(0)
        assert self.evaluate("123 xor 0.0").is_integer(123)

    def test_date(self):
        assert self.evaluate("123 xor #31.03.1901 18:56:10#").is_integer(434)
        assert self.evaluate("123 xor #02.05.1900 10:56:38#").is_integer(0)
        assert self.evaluate("123 xor #30.12.1899#").is_integer(123)

    def test_string(self):
        assert self.evaluate("123 xor \"456\"").is_integer(435)
        assert self.evaluate("123 xor \"123\"").is_integer(0)
        assert self.evaluate("123 xor \"0\"").is_integer(123)
        assert self.evaluate("123 xor \"456.789\"").is_integer(434)
        assert self.evaluate("123 xor \"123.456\"").is_integer(0)
        assert self.evaluate("123 xor \"0.0\"").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("123 xor \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123 xor \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123 xor new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123 xor nothing")

    def test_boolean(self):
        assert self.evaluate("123 xor true").is_integer(-124)
        assert self.evaluate("123 xor false").is_integer(123)
