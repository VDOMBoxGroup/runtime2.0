
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestNullAddition(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("null+empty").is_null

    def test_null(self):
        assert self.evaluate("null+null").is_null

    def test_integer(self):
        assert self.evaluate("null+123").is_null

    def test_double(self):
        assert self.evaluate("null+123.456").is_null

    def test_date(self):
        assert self.evaluate("null+#02.05.1900 10:56:38#").is_null

    def test_string(self):
        assert self.evaluate("null+\"123\"").is_null
        assert self.evaluate("null+\"123.456\"").is_null
        assert self.evaluate("null+\"abc\"").is_null
        assert self.evaluate("null+\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null+new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null+nothing")

    def test_boolean(self):
        assert self.evaluate("null+true").is_null
        assert self.evaluate("null+false").is_null

class TestNullSubtraction(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("null-empty").is_null

    def test_null(self):
        assert self.evaluate("null-null").is_null

    def test_integer(self):
        assert self.evaluate("null-123").is_null

    def test_double(self):
        assert self.evaluate("null-123.456").is_null

    def test_date(self):
        assert self.evaluate("null-#02.05.1900 10:56:38#").is_null

    def test_string(self):
        assert self.evaluate("null-\"123\"").is_null
        assert self.evaluate("null-\"123.456\"").is_null
        assert self.evaluate("null-\"abc\"").is_null
        assert self.evaluate("null-\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null-new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null-nothing")

    def test_boolean(self):
        assert self.evaluate("null-true").is_null
        assert self.evaluate("null-false").is_null

class TestNullMultiplication(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null*empty").is_null

    def test_null(self):
        assert self.evaluate("null*null").is_null

    def test_integer(self):
        assert self.evaluate("null*123").is_null

    def test_double(self):
        assert self.evaluate("null*123.456").is_null

    def test_date(self):
        assert self.evaluate("null*#02.05.1900 10:56:38#").is_null

    def test_string(self):
        assert self.evaluate("null*\"123\"").is_null
        assert self.evaluate("null*\"123.456\"").is_null
        assert self.evaluate("null*\"abc\"").is_null
        assert self.evaluate("null*\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null*new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null*nothing")

    def test_boolean(self):
        assert self.evaluate("null*true").is_null
        assert self.evaluate("null*false").is_null

class TestNullDivision(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null/empty").is_null
            
    def test_null(self):
        assert self.evaluate("null/null").is_null

    def test_integer(self):
        assert self.evaluate("null/123").is_null
        assert self.evaluate("null/0").is_null

    def test_double(self):
        assert self.evaluate("null/123.456").is_null
        assert self.evaluate("null/0.0").is_null

    def test_date(self):
        assert self.evaluate("null/#02.05.1900 10:56:38#").is_null
        assert self.evaluate("null/#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null/\"123\"").is_null
        assert self.evaluate("null/\"0\"").is_null
        assert self.evaluate("null/\"123.456\"").is_null
        assert self.evaluate("null/\"0.0\"").is_null
        assert self.evaluate("null/\"abc\"").is_null
        assert self.evaluate("null/\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null/new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null/nothing")

    def test_boolean(self):
        assert self.evaluate("null/true").is_null
        assert self.evaluate("null/false").is_null

class TestNullIntegerDivision(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null\\empty").is_null

    def test_null(self):
        assert self.evaluate("null\\null").is_null

    def test_integer(self):
        assert self.evaluate("null\\123").is_null
        assert self.evaluate("null\\0").is_null

    def test_double(self):
        assert self.evaluate("null\\123.456").is_null
        assert self.evaluate("null\\0.0").is_null

    def test_date(self):
        assert self.evaluate("null\\#02.05.1900 10:56:38#").is_null
        assert self.evaluate("null\\#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null\\\"123\"").is_null
        assert self.evaluate("null\\\"0\"").is_null
        assert self.evaluate("null\\\"123.456\"").is_null
        assert self.evaluate("null\\\"0.0\"").is_null
        assert self.evaluate("null\\\"abc\"").is_null
        assert self.evaluate("null\\\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null\\new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null\\nothing")

    def test_boolean(self):
        assert self.evaluate("null\\true").is_null
        assert self.evaluate("null\\false").is_null

class TestNullRemainder(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null mod empty").is_null

    def test_null(self):
        assert self.evaluate("null mod null").is_null

    def test_integer(self):
        assert self.evaluate("null mod 123").is_null
        assert self.evaluate("null mod 0").is_null

    def test_double(self):
        assert self.evaluate("null mod 123.456").is_null
        assert self.evaluate("null mod 0.0").is_null

    def test_date(self):
        assert self.evaluate("null mod #02.05.1900 10:56:38#").is_null
        assert self.evaluate("null mod #30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null mod \"123\"").is_null
        assert self.evaluate("null mod \"0\"").is_null
        assert self.evaluate("null mod \"123.456\"").is_null
        assert self.evaluate("null mod \"0.0\"").is_null
        assert self.evaluate("null mod \"abc\"").is_null
        assert self.evaluate("null mod \"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null mod new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null mod nothing")

    def test_boolean(self):
        assert self.evaluate("null mod true").is_null
        assert self.evaluate("null mod false").is_null

class TestNullExponentiation(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null^empty").is_null

    def test_null(self):
        assert self.evaluate("null^null").is_null

    def test_integer(self):
        assert self.evaluate("null^3").is_null
        assert self.evaluate("null^1").is_null
        assert self.evaluate("null^0").is_null

    def test_double(self):
        assert self.evaluate("null^3.456").is_null
        assert self.evaluate("null^1.0").is_null
        assert self.evaluate("null^0.0").is_null

    def test_date(self):
        assert self.evaluate("null^#02.01.1900 10:56:38#").is_null
        assert self.evaluate("null^#31.12.1899#").is_null
        assert self.evaluate("null^#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null^\"3\"").is_null
        assert self.evaluate("null^\"1\"").is_null
        assert self.evaluate("null^\"0\"").is_null
        assert self.evaluate("null^\"3.456\"").is_null
        assert self.evaluate("null^\"1.0\"").is_null
        assert self.evaluate("null^\"0.0\"").is_null
        assert self.evaluate("null^\"abc\"").is_null
        assert self.evaluate("null^\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null^new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null^nothing")

    def test_boolean(self):
        assert self.evaluate("null^true").is_null
        assert self.evaluate("null^false").is_null
