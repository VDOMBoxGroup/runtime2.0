
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestStringConjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"123\" and empty").is_integer(0)
        assert self.evaluate("\"0\" and empty").is_integer(0)
        assert self.evaluate("\"123.456\" and empty").is_integer(0)
        assert self.evaluate("\"0.0\" and empty").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" and empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" and empty")

    def test_null(self):
        assert self.evaluate("\"123\" and null").is_null
        assert self.evaluate("\"0\" and null").is_integer(0)
        assert self.evaluate("\"123.456\" and null").is_null
        assert self.evaluate("\"0.0\" and null").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" and null")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" and null")

    def test_integer(self):
        assert self.evaluate("\"123\" and 456").is_integer(72)
        assert self.evaluate("\"123\" and 123").is_integer(123)
        assert self.evaluate("\"123\" and 0").is_integer(0)
        assert self.evaluate("\"123.456\" and 456").is_integer(72)
        assert self.evaluate("\"123.456\" and 123").is_integer(123)
        assert self.evaluate("\"123.456\" and 0").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" and 123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" and 123")

    def test_double(self):
        assert self.evaluate("\"123\" and 456.789").is_integer(73)
        assert self.evaluate("\"123\" and 123.456").is_integer(123)
        assert self.evaluate("\"123\" and 0.0").is_integer(0)
        assert self.evaluate("\"123.456\" and 456.789").is_integer(73)
        assert self.evaluate("\"123.456\" and 123.456").is_integer(123)
        assert self.evaluate("\"123.456\" and 0.0").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" and 123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" and 123.456")

    def test_date(self):
        assert self.evaluate("\"123\" and #31.03.1901 18:56:10#").is_integer(73)
        assert self.evaluate("\"123\" and #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("\"123\" and #30.12.1899#").is_integer(0)
        assert self.evaluate("\"123.456\" and #31.03.1901 18:56:10#").is_integer(73)
        assert self.evaluate("\"123.456\" and #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("\"123.456\" and #30.12.1899#").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" and #02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" and #02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"123\" and \"456\"").is_integer(72)
        assert self.evaluate("\"123\" and \"123\"").is_integer(123)
        assert self.evaluate("\"123\" and \"0\"").is_integer(0)
        assert self.evaluate("\"123.456\" and \"456.789\"").is_integer(73)
        assert self.evaluate("\"123.456\" and \"123.456\"").is_integer(123)
        assert self.evaluate("\"123.456\" and \"0.0\"").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" and \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" and \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\" and new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\" and nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\" and true").is_integer(123)
        assert self.evaluate("\"123\" and false").is_integer(0)
        assert self.evaluate("\"123.456\" and true").is_integer(123)
        assert self.evaluate("\"123.456\" and false").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" and true")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" and false")

class TestStringDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"123\" or empty").is_integer(123)
        assert self.evaluate("\"0\" or empty").is_integer(0)
        assert self.evaluate("\"123.456\" or empty").is_integer(123)
        assert self.evaluate("\"0.0\" or empty").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" or empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" or empty")

    def test_null(self):
        assert self.evaluate("\"123\" or null").is_integer(123)
        assert self.evaluate("\"0\" or null").is_null
        assert self.evaluate("\"123.456\" or null").is_integer(123)
        assert self.evaluate("\"0.0\" or null").is_null
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" or null")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" or null")

    def test_integer(self):
        assert self.evaluate("\"123\" or 456").is_integer(507)
        assert self.evaluate("\"123\" or 123").is_integer(123)
        assert self.evaluate("\"123\" or 0").is_integer(123)
        assert self.evaluate("\"123.456\" or 456").is_integer(507)
        assert self.evaluate("\"123.456\" or 123").is_integer(123)
        assert self.evaluate("\"123.456\" or 0").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" or 123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" or 123")

    def test_double(self):
        assert self.evaluate("\"123\" or 456.789").is_integer(507)
        assert self.evaluate("\"123\" or 123.456").is_integer(123)
        assert self.evaluate("\"123\" or 0.0").is_integer(123)
        assert self.evaluate("\"123.456\" or 456.789").is_integer(507)
        assert self.evaluate("\"123.456\" or 123.456").is_integer(123)
        assert self.evaluate("\"123.456\" or 0.0").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" or 123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" or 123.456")

    def test_date(self):
        assert self.evaluate("\"123\" or #31.03.1901 18:56:10#").is_integer(507)
        assert self.evaluate("\"123\" or #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("\"123\" or #30.12.1899#").is_integer(123)
        assert self.evaluate("\"123.456\" or #31.03.1901 18:56:10#").is_integer(507)
        assert self.evaluate("\"123.456\" or #02.05.1900 10:56:38#").is_integer(123)
        assert self.evaluate("\"123.456\" or #30.12.1899#").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" or #02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" or #02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"123\" or \"456\"").is_integer(507)
        assert self.evaluate("\"123\" or \"123\"").is_integer(123)
        assert self.evaluate("\"123\" or \"0\"").is_integer(123)
        assert self.evaluate("\"123.456\" or \"456.789\"").is_integer(507)
        assert self.evaluate("\"123.456\" or \"123.456\"").is_integer(123)
        assert self.evaluate("\"123.456\" or \"0.0\"").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" or \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" or \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\" or new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\" or nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\" or true").is_integer(-1)
        assert self.evaluate("\"123\" or false").is_integer(123)
        assert self.evaluate("\"123.456\" or true").is_integer(-1)
        assert self.evaluate("\"123.456\" or false").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" or true")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" or false")
            
class TestStringExclusiveDisjunction(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"123\" xor empty").is_integer(123)
        assert self.evaluate("\"0\" xor empty").is_integer(0)
        assert self.evaluate("\"123.456\" xor empty").is_integer(123)
        assert self.evaluate("\"0.0\" xor empty").is_integer(0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" xor empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" xor empty")

    def test_null(self):
        assert self.evaluate("\"123\" xor null").is_null
        assert self.evaluate("\"0\" xor null").is_null
        assert self.evaluate("\"123.456\" xor null").is_null
        assert self.evaluate("\"0.0\" xor null").is_null
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" xor null")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" xor null")

    def test_integer(self):
        assert self.evaluate("\"123\" xor 456").is_integer(435)
        assert self.evaluate("\"123\" xor 123").is_integer(0)
        assert self.evaluate("\"123\" xor 0").is_integer(123)
        assert self.evaluate("\"123.456\" xor 456").is_integer(435)
        assert self.evaluate("\"123.456\" xor 123").is_integer(0)
        assert self.evaluate("\"123.456\" xor 0").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" xor 123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" xor 123")

    def test_double(self):
        assert self.evaluate("\"123\" xor 456.789").is_integer(434)
        assert self.evaluate("\"123\" xor 123.456").is_integer(0)
        assert self.evaluate("\"123\" xor 0.0").is_integer(123)
        assert self.evaluate("\"123.456\" xor 456.789").is_integer(434)
        assert self.evaluate("\"123.456\" xor 123.456").is_integer(0)
        assert self.evaluate("\"123.456\" xor 0.0").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" xor 123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" xor 123.456")

    def test_date(self):
        assert self.evaluate("\"123\" xor #31.03.1901 18:56:10#").is_integer(434)
        assert self.evaluate("\"123\" xor #02.05.1900 10:56:38#").is_integer(0)
        assert self.evaluate("\"123\" xor #30.12.1899#").is_integer(123)
        assert self.evaluate("\"123.456\" xor #31.03.1901 18:56:10#").is_integer(434)
        assert self.evaluate("\"123.456\" xor #02.05.1900 10:56:38#").is_integer(0)
        assert self.evaluate("\"123.456\" xor #30.12.1899#").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" xor #02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" xor #02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"123\" xor \"456\"").is_integer(435)
        assert self.evaluate("\"123\" xor \"123\"").is_integer(0)
        assert self.evaluate("\"123\" xor \"0\"").is_integer(123)
        assert self.evaluate("\"123.456\" xor \"456.789\"").is_integer(434)
        assert self.evaluate("\"123.456\" xor \"123.456\"").is_integer(0)
        assert self.evaluate("\"123.456\" xor \"0.0\"").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" xor \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" xor \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\" xor new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\" xor nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\" xor true").is_integer(-124)
        assert self.evaluate("\"123\" xor false").is_integer(123)
        assert self.evaluate("\"123.456\" xor true").is_integer(-124)
        assert self.evaluate("\"123.456\" xor false").is_integer(123)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" xor true")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" xor false")