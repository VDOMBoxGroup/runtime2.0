
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestBooleanAddition(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("true+empty").is_integer(-1)
        assert self.evaluate("false+empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("true+null").is_null
        assert self.evaluate("false+null").is_null

    def test_integer(self):
        assert self.evaluate("true+123").is_integer(122)
        assert self.evaluate("false+123").is_integer(123)

    def test_double(self):
        assert self.evaluate("true+123.456").is_double(122.456)
        assert self.evaluate("false+123.456").is_double(123.456)

    def test_date(self):
        assert self.evaluate("true+#02.05.1900 10:56:38#").is_date(1900, 5, 1, 10, 56, 38)
        assert self.evaluate("false+#02.05.1900 10:56:38#").is_date(1900, 5, 2, 10, 56, 38)

    def test_string(self):
        assert self.evaluate("true+\"123\"").is_double(122)
        assert self.evaluate("false+\"123\"").is_double(123)
        assert self.evaluate("true+\"123.456\"").is_double(122.456)
        assert self.evaluate("false+\"123.456\"").is_double(123.456)
        with raises(errors.type_mismatch):
            assert self.evaluate("true+\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("false+\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true+new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true+nothing")

    def test_boolean(self):
        assert self.evaluate("true+true").is_integer(-2)
        assert self.evaluate("true+false").is_integer(-1)
        assert self.evaluate("false+true").is_integer(-1)
        assert self.evaluate("false+false").is_integer(0)
        
class TestBooleanSubtraction(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("true-empty").is_integer(-1)
        assert self.evaluate("false-empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("true-null").is_null
        assert self.evaluate("false-null").is_null

    def test_integer(self):
        assert self.evaluate("true-123").is_integer(-124)
        assert self.evaluate("false-123").is_integer(-123)

    def test_double(self):
        assert self.evaluate("true-123.456").is_double(-124.456)
        assert self.evaluate("false-123.456").is_double(-123.456)

    def test_date(self):
        assert self.evaluate("true-#02.05.1900 10:56:38#").is_date(1899, 8, 28, 10, 56, 38)
        assert self.evaluate("false-#02.05.1900 10:56:38#").is_date(1899, 8, 29, 10, 56, 38)

    def test_string(self):
        assert self.evaluate("true-\"123\"").is_double(-124)
        assert self.evaluate("false-\"123\"").is_double(-123)
        assert self.evaluate("true-\"123.456\"").is_double(-124.456)
        assert self.evaluate("false-\"123.456\"").is_double(-123.456)
        with raises(errors.type_mismatch):
            assert self.evaluate("true-\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("false-\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true-new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true-nothing")

    def test_boolean(self):
        assert self.evaluate("true-true").is_integer(0)
        assert self.evaluate("true-false").is_integer(-1)
        assert self.evaluate("false-true").is_integer(1)
        assert self.evaluate("false-false").is_integer(0)

class TestBooleanMultiplication(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("true*empty").is_integer(0)
        assert self.evaluate("false*empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("true*null").is_null
        assert self.evaluate("false*null").is_null

    def test_integer(self):
        assert self.evaluate("true*123").is_integer(-123)
        assert self.evaluate("false*123").is_integer(0)

    def test_double(self):
        assert self.evaluate("true*123.456").is_double(-123.456)
        assert self.evaluate("false*123.456").is_double(0.0)

    def test_date(self):
        assert self.evaluate("true*#02.05.1900 10:56:38#").is_double(-123.45599537037)
        assert self.evaluate("false*#02.05.1900 10:56:38#").is_double(0.0)

    def test_string(self):
        assert self.evaluate("true*\"123\"").is_double(-123)
        assert self.evaluate("false*\"123\"").is_double(0)
        assert self.evaluate("true*\"123.456\"").is_double(-123.456)
        assert self.evaluate("false*\"123.456\"").is_double(0.0)
        with raises(errors.type_mismatch):
            assert self.evaluate("true*\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("false*\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true*new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true*nothing")

    def test_boolean(self):
        assert self.evaluate("true*true").is_integer(1)
        assert self.evaluate("true*false").is_integer(0)
        assert self.evaluate("false*true").is_integer(0)
        assert self.evaluate("false*false").is_integer(0)

class TestBooleanDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("true/empty")
        with raises(errors.division_by_zero):
            self.evaluate("false/empty")
            
    def test_null(self):
        assert self.evaluate("true/null").is_null
        assert self.evaluate("false/null").is_null

    def test_integer(self):
        assert self.evaluate("true/123").is_double(-8.13008130081301E-03)
        assert self.evaluate("false/123").is_double(0.0)
        with raises(errors.division_by_zero):
            self.evaluate("true/0")
        with raises(errors.division_by_zero):
            self.evaluate("false/0")

    def test_double(self):
        assert self.evaluate("true/123.456").is_double(-8.10005184033178E-03)
        assert self.evaluate("false/123.456").is_double(0.0)
        with raises(errors.division_by_zero):
            self.evaluate("true/0.0")
        with raises(errors.division_by_zero):
            self.evaluate("false/0.0")

    def test_date(self):
        assert self.evaluate("true/#02.05.1900 10:56:38#").is_double(-8.10005214408568E-03)
        assert self.evaluate("false/#02.05.1900 10:56:38#").is_double(0.0)
        with raises(errors.division_by_zero):
            self.evaluate("true/#30.12.1899#")
        with raises(errors.division_by_zero):
            self.evaluate("false/#30.12.1899#")

    def test_string(self):
        assert self.evaluate("true/\"123\"").is_double(-8.13008130081301E-03)
        assert self.evaluate("false/\"123\"").is_double(0.0)
        with raises(errors.division_by_zero):
            self.evaluate("true/\"0\"")
        with raises(errors.division_by_zero):
            self.evaluate("false/\"0\"")
        assert self.evaluate("true/\"123.456\"").is_double(-8.10005184033178E-03)
        assert self.evaluate("false/\"123.456\"").is_double(0.0)
        with raises(errors.division_by_zero):
            self.evaluate("true/\"0.0\"")
        with raises(errors.division_by_zero):
            self.evaluate("false/\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("true/\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("true/\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true/new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true/nothing")

    def test_boolean(self):
        assert self.evaluate("true/true").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("true/false")
        assert self.evaluate("false/true").is_double(0.0)
        with raises(errors.division_by_zero):
            self.evaluate("false/false")

class TestBooleanIntegerDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("true\\empty")
        with raises(errors.division_by_zero):
            self.evaluate("false\\empty")
            
    def test_null(self):
        assert self.evaluate("true\\null").is_null
        assert self.evaluate("false\\null").is_null

    def test_integer(self):
        assert self.evaluate("true\\123").is_integer(0)
        assert self.evaluate("false\\123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true\\0")
        with raises(errors.division_by_zero):
            self.evaluate("false\\0")

    def test_double(self):
        assert self.evaluate("true\\123.456").is_integer(0)
        assert self.evaluate("false\\123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true\\0.0")
        with raises(errors.division_by_zero):
            self.evaluate("false\\0.0")

    def test_date(self):
        assert self.evaluate("true\\#02.05.1900 10:56:38#").is_integer(0)
        assert self.evaluate("false\\#02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true\\#30.12.1899#")
        with raises(errors.division_by_zero):
            self.evaluate("false\\#30.12.1899#")

    def test_string(self):
        assert self.evaluate("true\\\"123\"").is_integer(0)
        assert self.evaluate("false\\\"123\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true\\\"0\"")
        with raises(errors.division_by_zero):
            self.evaluate("false\\\"0\"")
        assert self.evaluate("true\\\"123.456\"").is_integer(0)
        assert self.evaluate("false\\\"123.456\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true\\\"0.0\"")
        with raises(errors.division_by_zero):
            self.evaluate("false\\\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("true\\\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("true\\\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true\\new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true\\nothing")

    def test_boolean(self):
        assert self.evaluate("true\\true").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("true\\false")
        assert self.evaluate("false\\true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("false\\false")

class TestBooleanRemainder(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("true mod empty")
        with raises(errors.division_by_zero):
            self.evaluate("false mod empty")
            
    def test_null(self):
        assert self.evaluate("true mod null").is_null
        assert self.evaluate("false mod null").is_null

    def test_integer(self):
        assert self.evaluate("true mod 123").is_integer(-1)
        assert self.evaluate("false mod 123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true mod 0")
        with raises(errors.division_by_zero):
            self.evaluate("false mod 0")

    def test_double(self):
        assert self.evaluate("true mod 123.456").is_integer(-1)
        assert self.evaluate("false mod 123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true mod 0.0")
        with raises(errors.division_by_zero):
            self.evaluate("false mod 0.0")

    def test_date(self):
        assert self.evaluate("true mod #02.05.1900 10:56:38#").is_integer(-1)
        assert self.evaluate("false mod #02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true mod #30.12.1899#")
        with raises(errors.division_by_zero):
            self.evaluate("false mod #30.12.1899#")

    def test_string(self):
        assert self.evaluate("true mod \"123\"").is_integer(-1)
        assert self.evaluate("false mod \"123\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true mod \"0\"")
        with raises(errors.division_by_zero):
            self.evaluate("false mod \"0\"")
        assert self.evaluate("true mod \"123.456\"").is_integer(-1)
        assert self.evaluate("false mod \"123.456\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true mod \"0.0\"")
        with raises(errors.division_by_zero):
            self.evaluate("false mod \"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("true mod \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("true mod \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true mod new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true mod nothing")

    def test_boolean(self):
        assert self.evaluate("true mod true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("true mod false")
        assert self.evaluate("false mod true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("false mod false")

class TestBooleanExponentiation(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true^empty").is_double(1.0)
        assert self.evaluate("false^empty").is_double(1.0)

    def test_null(self):
        assert self.evaluate("true^null").is_null
        assert self.evaluate("false^null").is_null

    def test_integer(self):
        assert self.evaluate("true^3").is_double(-1.0)
        assert self.evaluate("false^3").is_double(0.0)
        assert self.evaluate("true^1").is_double(-1.0)
        assert self.evaluate("false^1").is_double(0.0)
        assert self.evaluate("true^0").is_double(1.0)
        assert self.evaluate("false^0").is_double(1.0)

    def test_double(self):
        with raises(errors.invalid_procedure_call):
            self.evaluate("true^3.456")
        assert self.evaluate("false^3.456").is_double(0.0)
        assert self.evaluate("true^1.0").is_double(-1.0)
        assert self.evaluate("false^1.0").is_double(0.0)
        assert self.evaluate("true^0.0").is_double(1.0)
        assert self.evaluate("false^0.0").is_double(1.0)

    def test_date(self):
        with raises(errors.invalid_procedure_call):
            self.evaluate("true^#02.01.1900 10:56:38#")
        assert self.evaluate("false^#02.01.1900 10:56:38#").is_double(0.0)
        assert self.evaluate("true^#31.12.1899#").is_double(-1.0)
        assert self.evaluate("false^#31.12.1899#").is_double(0.0)
        assert self.evaluate("true^#30.12.1899#").is_double(1.0)
        assert self.evaluate("false^#30.12.1899#").is_double(1.0)

    def test_string(self):
        assert self.evaluate("true^\"3\"").is_double(-1.0)
        assert self.evaluate("false^\"3\"").is_double(0.0)
        assert self.evaluate("true^\"1\"").is_double(-1.0)
        assert self.evaluate("false^\"1\"").is_double(0.0)
        assert self.evaluate("true^\"0\"").is_double(1.0)
        assert self.evaluate("false^\"0\"").is_double(1.0)
        with raises(errors.invalid_procedure_call):
            self.evaluate("true^\"3.456\"")
        assert self.evaluate("false^\"3.456\"").is_double(0.0)
        assert self.evaluate("true^\"1.0\"").is_double(-1.0)
        assert self.evaluate("false^\"1.0\"").is_double(0.0)
        assert self.evaluate("true^\"0.0\"").is_double(1.0)
        assert self.evaluate("false^\"0.0\"").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("true^\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("false^\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true^new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true^nothing")

    def test_boolean(self):
        assert self.evaluate("true^true").is_double(-1.0)
        assert self.evaluate("true^false").is_double(1.0)
        with raises(errors.invalid_procedure_call):
            self.evaluate("false^true")
        assert self.evaluate("false^false").is_double(1.0)
