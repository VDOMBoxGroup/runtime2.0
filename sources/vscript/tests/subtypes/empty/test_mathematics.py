
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestEmptyAddition(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("empty+empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("empty+null").is_null

    def test_integer(self):
        assert self.evaluate("empty+123").is_integer(123)

    def test_double(self):
        assert self.evaluate("empty+123.456").is_double(123.456)

    def test_date(self):
        assert self.evaluate("empty+#02.05.1900 10:56:38#").is_date(1900, 5, 2, 10, 56, 38)

    def test_string(self):
        assert self.evaluate("empty+\"123\"").is_string(u"123")
        assert self.evaluate("empty+\"123.456\"").is_string(u"123.456")
        assert self.evaluate("empty+\"abc\"").is_string(u"abc")
        assert self.evaluate("empty+\"\"").is_string(u"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty+new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty+nothing")

    def test_boolean(self):
        assert self.evaluate("empty+true").is_integer(-1)
        assert self.evaluate("empty+false").is_integer(0)
        
class TestEmptySubtraction(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("empty-empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("empty-null").is_null

    def test_integer(self):
        assert self.evaluate("empty-123").is_integer(-123)

    def test_double(self):
        assert self.evaluate("empty-123.456").is_double(-123.456)

    def test_date(self):
        assert self.evaluate("empty-#02.05.1900 10:56:38#").is_date(1899, 8, 29, 10, 56, 38)

    def test_string(self):
        assert self.evaluate("empty-\"123\"").is_double(-123.0)
        assert self.evaluate("empty-\"123.456\"").is_double(-123.456)
        with raises(errors.type_mismatch):
            assert self.evaluate("empty-\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("empty-\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty-new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty-nothing")

    def test_boolean(self):
        assert self.evaluate("empty-true").is_integer(1)
        assert self.evaluate("empty-false").is_integer(0)

class TestEmptyMultiplication(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty*empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("empty*null").is_null

    def test_integer(self):
        assert self.evaluate("empty*123").is_integer(0)

    def test_double(self):
        assert self.evaluate("empty*123.456").is_double(0.0)

    def test_date(self):
        assert self.evaluate("empty*#02.05.1900 10:56:38#").is_double(0.0)

    def test_string(self):
        assert self.evaluate("empty*\"123\"").is_double(0.0)
        assert self.evaluate("empty*\"123.456\"").is_double(0.0)
        with raises(errors.type_mismatch):
            self.evaluate("empty*\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty*\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty*new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty*nothing")

    def test_boolean(self):
        assert self.evaluate("empty*true").is_integer(0)
        assert self.evaluate("empty*false").is_integer(0)

class TestEmptyDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.overflow):
            self.evaluate("empty/empty")
            
    def test_null(self):
        assert self.evaluate("empty/null").is_null

    def test_integer(self):
        assert self.evaluate("empty/123").is_double(0.0)
        with raises(errors.overflow):
            self.evaluate("empty/0")

    def test_double(self):
        assert self.evaluate("empty/123.456").is_double(0.0)
        with raises(errors.overflow):
            self.evaluate("empty/0.0")

    def test_date(self):
        assert self.evaluate("empty/#02.05.1900 10:56:38#").is_double(0.0)
        with raises(errors.overflow):
            self.evaluate("empty/#30.12.1899#")

    def test_string(self):
        assert self.evaluate("empty/\"123\"").is_double(0.0)
        with raises(errors.overflow):
            self.evaluate("empty/\"0\"")
        assert self.evaluate("empty/\"123.456\"").is_double(0.0)
        with raises(errors.overflow):
            self.evaluate("empty/\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty/\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty/\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty/new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty/nothing")

    def test_boolean(self):
        assert self.evaluate("empty/true").is_double(0.0)
        with raises(errors.overflow):
            self.evaluate("empty/false")

class TestEmptyIntegerDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("empty\\empty")

    def test_null(self):
        assert self.evaluate("empty\\null").is_null

    def test_integer(self):
        assert self.evaluate("empty\\123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty\\0")

    def test_double(self):
        assert self.evaluate("empty\\123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty\\0.0")

    def test_date(self):
        assert self.evaluate("empty\\#02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty\\#30.12.1899#")

    def test_string(self):
        assert self.evaluate("empty\\\"123\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty\\\"0\"")
        assert self.evaluate("empty\\\"123.456\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty\\\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty\\\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty\\\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty\\new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty\\nothing")

    def test_boolean(self):
        assert self.evaluate("empty\\true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty\\false")

class TestEmptyRemainder(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("empty mod empty")

    def test_null(self):
        assert self.evaluate("empty mod null").is_null

    def test_integer(self):
        assert self.evaluate("empty mod 123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty mod 0")

    def test_double(self):
        assert self.evaluate("empty mod 123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty mod 0.0")

    def test_date(self):
        assert self.evaluate("empty mod #02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty mod #30.12.1899#")

    def test_string(self):
        assert self.evaluate("empty mod \"123\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty mod \"0\"")
        assert self.evaluate("empty mod \"123.456\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty mod \"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty mod \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty mod \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty mod new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty mod nothing")

    def test_boolean(self):
        assert self.evaluate("empty mod true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("empty mod false")

class TestEmptyExponentiation(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty^empty").is_double(1.0)

    def test_null(self):
        assert self.evaluate("empty^null").is_null

    def test_integer(self):
        assert self.evaluate("empty^3").is_double(0.0)
        assert self.evaluate("empty^1").is_double(0.0)
        assert self.evaluate("empty^0").is_double(1.0)

    def test_double(self):
        assert self.evaluate("empty^3.456").is_double(0.0)
        assert self.evaluate("empty^1.0").is_double(0.0)
        assert self.evaluate("empty^0.0").is_double(1.0)

    def test_date(self):
        assert self.evaluate("empty^#02.01.1900 10:56:38#").is_double(0.0)
        assert self.evaluate("empty^#31.12.1899#").is_double(0.0)
        assert self.evaluate("empty^#30.12.1899#").is_double(1.0)

    def test_string(self):
        assert self.evaluate("empty^\"3\"").is_double(0.0)
        assert self.evaluate("empty^\"1\"").is_double(0.0)
        assert self.evaluate("empty^\"0\"").is_double(1.0)
        assert self.evaluate("empty^\"3.456\"").is_double(0.0)
        assert self.evaluate("empty^\"1.0\"").is_double(0.0)
        assert self.evaluate("empty^\"0.0\"").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("empty^\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("empty^\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty^new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty^nothing")

    def test_boolean(self):
        with raises(errors.invalid_procedure_call):
            self.evaluate("empty^true")
        assert self.evaluate("empty^false").is_double(1.0)
