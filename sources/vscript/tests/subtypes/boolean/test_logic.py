
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestBooleanConjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true and empty").is_integer(0)
        assert self.evaluate("false and empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("true and null").is_null
        assert self.evaluate("false and null").is_boolean(false)

    def test_integer(self):
        assert self.evaluate("true and 456").is_integer(456)
        assert self.evaluate("true and 123").is_integer(123)
        assert self.evaluate("true and 0").is_integer(0)
        assert self.evaluate("false and 456").is_integer(0)
        assert self.evaluate("false and 123").is_integer(0)
        assert self.evaluate("false and 0").is_integer(0)

    def test_double(self):
        assert self.evaluate("true and 456.789").is_integer(457)
        assert self.evaluate("true and 123.456").is_integer(123)
        assert self.evaluate("true and 0.0").is_integer(0)
        assert self.evaluate("false and 456.789").is_integer(0)
        assert self.evaluate("false and 123.456").is_integer(0)
        assert self.evaluate("false and 0.0").is_integer(0)

    def test_date(self):
        assert self.evaluate("true and #31.03.1901 18:56:10#").is_integer(457)
        assert self.evaluate("true and #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("true and #30.12.1899#").is_integer(0)
        assert self.evaluate("false and #31.03.1901 18:56:10#").is_integer(0)
        assert self.evaluate("false and #02.05.1900 10:56:38#").is_integer(0)
        assert self.evaluate("false and #30.12.1899#").is_integer(0)

    def test_string(self):
        assert self.evaluate("true and \"456\"").is_integer(456)
        assert self.evaluate("true and \"123\"").is_integer(123)
        assert self.evaluate("true and \"0\"").is_integer(0)
        assert self.evaluate("false and \"456\"").is_integer(0)
        assert self.evaluate("false and \"123\"").is_integer(0)
        assert self.evaluate("false and \"0\"").is_integer(0)
        assert self.evaluate("true and \"456.789\"").is_integer(457)
        assert self.evaluate("true and \"123.456\"").is_integer(123)
        assert self.evaluate("true and \"0.0\"").is_integer(0)
        assert self.evaluate("false and \"456.789\"").is_integer(0)
        assert self.evaluate("false and \"123.456\"").is_integer(0)
        assert self.evaluate("false and \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("true and \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("false and \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true and new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true and nothing")

    def test_boolean(self):
        assert self.evaluate("true and true").is_boolean(true)
        assert self.evaluate("true and false").is_boolean(false)
        assert self.evaluate("false and true").is_boolean(false)
        assert self.evaluate("false and false").is_boolean(false)

class TestBooleanDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true or empty").is_integer(-1)
        assert self.evaluate("false or empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("true or null").is_boolean(true)
        assert self.evaluate("false or null").is_null

    def test_integer(self):
        assert self.evaluate("true or 456").is_integer(-1)
        assert self.evaluate("true or 123").is_integer(-1)
        assert self.evaluate("true or 0").is_integer(-1)
        assert self.evaluate("false or 456").is_integer(456)
        assert self.evaluate("false or 123").is_integer(123)
        assert self.evaluate("false or 0").is_integer(0)

    def test_double(self):
        assert self.evaluate("true or 456.789").is_integer(-1)
        assert self.evaluate("true or 123.456").is_integer(-1)
        assert self.evaluate("true or 0.0").is_integer(-1)
        assert self.evaluate("false or 456.789").is_integer(457)
        assert self.evaluate("false or 123.456").is_integer(123)
        assert self.evaluate("false or 0.0").is_integer(0)

    def test_date(self):
        assert self.evaluate("true or #31.03.1901 18:56:10#").is_integer(-1)
        assert self.evaluate("true or #02.05.1900 10:56:38#").is_integer(-1)
        assert self.evaluate("true or #30.12.1899#").is_integer(-1)
        assert self.evaluate("false or #31.03.1901 18:56:10#").is_integer(457)
        assert self.evaluate("false or #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("false or #30.12.1899#").is_integer(0)

    def test_string(self):
        assert self.evaluate("true or \"456\"").is_integer(-1)
        assert self.evaluate("true or \"123\"").is_integer(-1)
        assert self.evaluate("true or \"0\"").is_integer(-1)
        assert self.evaluate("false or \"456\"").is_integer(456)
        assert self.evaluate("false or \"123\"").is_integer(123)
        assert self.evaluate("false or \"0\"").is_integer(0)
        assert self.evaluate("true or \"456.789\"").is_integer(-1)
        assert self.evaluate("true or \"123.456\"").is_integer(-1)
        assert self.evaluate("true or \"0.0\"").is_integer(-1)
        assert self.evaluate("false or \"456.789\"").is_integer(457)
        assert self.evaluate("false or \"123.456\"").is_integer(123)
        assert self.evaluate("false or \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("true or \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("false or \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true or new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true or nothing")

    def test_boolean(self):
        assert self.evaluate("true or true").is_boolean(true)
        assert self.evaluate("true or false").is_boolean(true)
        assert self.evaluate("false or true").is_boolean(true)
        assert self.evaluate("false or false").is_boolean(false)

class TestBooleanExclusiveDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true xor empty").is_integer(-1)
        assert self.evaluate("false xor empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("true xor null").is_null
        assert self.evaluate("false xor null").is_null

    def test_integer(self):
        assert self.evaluate("true xor 456").is_integer(-457)
        assert self.evaluate("true xor 123").is_integer(-124)
        assert self.evaluate("true xor 0").is_integer(-1)
        assert self.evaluate("false xor 456").is_integer(456)
        assert self.evaluate("false xor 123").is_integer(123)
        assert self.evaluate("false xor 0").is_integer(0)

    def test_double(self):
        assert self.evaluate("true xor 456.789").is_integer(-458)
        assert self.evaluate("true xor 123.456").is_integer(-124)
        assert self.evaluate("true xor 0.0").is_integer(-1)
        assert self.evaluate("false xor 456.789").is_integer(457)
        assert self.evaluate("false xor 123.456").is_integer(123)
        assert self.evaluate("false xor 0.0").is_integer(0)

    def test_date(self):
        assert self.evaluate("true xor #31.03.1901 18:56:10#").is_integer(-458)
        assert self.evaluate("true xor #02.05.1900 10:56:38#").is_integer(-124)
        assert self.evaluate("true xor #30.12.1899#").is_integer(-1)
        assert self.evaluate("false xor #31.03.1901 18:56:10#").is_integer(457)
        assert self.evaluate("false xor #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("false xor #30.12.1899#").is_integer(0)

    def test_string(self):
        assert self.evaluate("true xor \"456\"").is_integer(-457)
        assert self.evaluate("true xor \"123\"").is_integer(-124)
        assert self.evaluate("true xor \"0\"").is_integer(-1)
        assert self.evaluate("false xor \"456\"").is_integer(456)
        assert self.evaluate("false xor \"123\"").is_integer(123)
        assert self.evaluate("false xor \"0\"").is_integer(0)
        assert self.evaluate("true xor \"456.789\"").is_integer(-458)
        assert self.evaluate("true xor \"123.456\"").is_integer(-124)
        assert self.evaluate("true xor \"0.0\"").is_integer(-1)
        assert self.evaluate("false xor \"456.789\"").is_integer(457)
        assert self.evaluate("false xor \"123.456\"").is_integer(123)
        assert self.evaluate("false xor \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("true xor \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("false xor \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true xor new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true xor nothing")

    def test_boolean(self):
        assert self.evaluate("true xor true").is_boolean(false)
        assert self.evaluate("true xor false").is_boolean(true)
        assert self.evaluate("false xor true").is_boolean(true)
        assert self.evaluate("false xor false").is_boolean(false)
