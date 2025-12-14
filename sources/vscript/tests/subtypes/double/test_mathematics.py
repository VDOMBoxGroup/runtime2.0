
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestDoubleAddition(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("123.456+empty").is_double(123.456)

    def test_null(self):
        assert self.evaluate("123.456+null").is_null

    def test_integer(self):
        assert self.evaluate("123.456+123").is_double(246.456)

    def test_double(self):
        assert self.evaluate("123.456+123.456").is_double(246.912)

    def test_date(self):
        assert self.evaluate("123.456+#02.05.1900 10:56:38#").is_date(1900, 9, 2, 21, 53, 16)

    def test_string(self):
        assert self.evaluate("123.456+\"123\"").is_double(246.456)
        assert self.evaluate("123.456+\"123.456\"").is_double(246.912)
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456+\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456+\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456+new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456+nothing")

    def test_boolean(self):
        assert self.evaluate("123.456+true").is_double(122.456)
        assert self.evaluate("123.456+false").is_double(123.456)
        
class TestDoubleSubtraction(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("123.456-empty").is_double(123.456)

    def test_null(self):
        assert self.evaluate("123.456-null").is_null

    def test_integer(self):
        assert self.evaluate("123.456-123").is_double(0.456000000000003)

    def test_double(self):
        assert self.evaluate("123.456-123.456").is_double(0.0)

    def test_date(self):
        assert self.evaluate("123.456-#02.05.1900 10:56:38#").is_date(1899, 12, 30, 0, 0, 0)

    def test_string(self):
        assert self.evaluate("123.456-\"123\"").is_double(0.456000000000003)
        assert self.evaluate("123.456-\"123.456\"").is_double(0.0)
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456-\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456-\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456-new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456-nothing")

    def test_boolean(self):
        assert self.evaluate("123.456-true").is_double(124.456)
        assert self.evaluate("123.456-false").is_double(123.456)

class TestDoubleMultiplication(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123.456*empty").is_double(0.0)

    def test_null(self):
        assert self.evaluate("123.456*null").is_null

    def test_integer(self):
        assert self.evaluate("123.456*123").is_double(15185.088)

    def test_double(self):
        assert self.evaluate("123.456*123.456").is_double(15241.383936)

    def test_date(self):
        assert self.evaluate("123.456*#02.05.1900 10:56:38#").is_double(15241.3833644444)

    def test_string(self):
        assert self.evaluate("123.456*\"123\"").is_double(15185.088)
        assert self.evaluate("123.456*\"123.456\"").is_double(15241.383936)
        with raises(errors.type_mismatch):
            self.evaluate("123.456*\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123.456*\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456*new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456*nothing")

    def test_boolean(self):
        assert self.evaluate("123.456*true").is_double(-123.456)
        assert self.evaluate("123.456*false").is_double(0.0)

class TestDoubleDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("123.456/empty")
            
    def test_null(self):
        assert self.evaluate("123.456/null").is_null

    def test_integer(self):
        assert self.evaluate("456.789/123").is_double(3.71373170731707)
        assert self.evaluate("123.456/123").is_double(1.00370731707317)
        with raises(errors.division_by_zero):
            self.evaluate("123.456/0")

    def test_double(self):
        assert self.evaluate("456.789/123.456").is_double(3.70001458009331)
        assert self.evaluate("123.456/123.456").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("123.456/0.0")

    def test_date(self):
        assert self.evaluate("456.789/#02.05.1900 10:56:38#").is_double(3.70001471884475)
        assert self.evaluate("123.456/#02.05.1900 10:56:38#").is_double(1.00000003750024)
        with raises(errors.division_by_zero):
            self.evaluate("123.456/#30.12.1899#")

    def test_string(self):
        assert self.evaluate("456.789/\"123\"").is_double(3.71373170731707)
        assert self.evaluate("123.456/\"123\"").is_double(1.00370731707317)
        with raises(errors.division_by_zero):
            self.evaluate("123.456/\"0\"")
        assert self.evaluate("456.789/\"123.456\"").is_double(3.70001458009331)
        assert self.evaluate("123.456/\"123.456\"").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("123.456/\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("123.456/\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123.456/\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456/new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456/nothing")

    def test_boolean(self):
        assert self.evaluate("123.456/true").is_double(-123.456)
        with raises(errors.division_by_zero):
            self.evaluate("123.456/false")

class TestDoubleIntegerDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("123.456\\empty")

    def test_null(self):
        assert self.evaluate("123.456\\null").is_null

    def test_integer(self):
        assert self.evaluate("456.789\\123").is_integer(3)
        assert self.evaluate("123.456\\123").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123.456\\0")

    def test_double(self):
        assert self.evaluate("456.789\\123.456").is_integer(3)
        assert self.evaluate("123.456\\123.456").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123.456\\0.0")

    def test_date(self):
        assert self.evaluate("456.789\\#02.05.1900 10:56:38#").is_integer(3)
        assert self.evaluate("123.456\\#02.05.1900 10:56:38#").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123.456\\#30.12.1899#")

    def test_string(self):
        assert self.evaluate("456.789\\\"123\"").is_integer(3)
        assert self.evaluate("123.456\\\"123\"").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123.456\\\"0\"")
        assert self.evaluate("456.789\\\"123.456\"").is_integer(3)
        assert self.evaluate("123.456\\\"123.456\"").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123.456\\\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("123.456\\\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123.456\\\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456\\new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456\\nothing")

    def test_boolean(self):
        assert self.evaluate("123.456\\true").is_integer(-123)
        with raises(errors.division_by_zero):
            self.evaluate("123.456\\false")

class TestDoubleRemainder(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("123.456 mod empty")

    def test_null(self):
        assert self.evaluate("123.456 mod null").is_null

    def test_integer(self):
        assert self.evaluate("456.789 mod 123").is_integer(88)
        assert self.evaluate("123.456 mod 123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123.456 mod 0")

    def test_double(self):
        assert self.evaluate("456.789 mod 123.456").is_integer(88)
        assert self.evaluate("123.456 mod 123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123.456 mod 0.0")

    def test_date(self):
        assert self.evaluate("456.789 mod #02.05.1900 10:56:38#").is_integer(88)
        assert self.evaluate("123.456 mod #02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123.456 mod #30.12.1899#")

    def test_string(self):
        assert self.evaluate("456.789 mod \"123\"").is_integer(88)
        assert self.evaluate("123.456 mod \"123\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123.456 mod \"0\"")
        assert self.evaluate("456.789 mod \"123.456\"").is_integer(88)
        assert self.evaluate("123.456 mod \"123.456\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123.456 mod \"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("123.456 mod \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123.456 mod \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456 mod new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456 mod nothing")

    def test_boolean(self):
        assert self.evaluate("123.456 mod true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123.456 mod false")

class TestDoubleExponentiation(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123.456^empty").is_double(1.0)

    def test_null(self):
        assert self.evaluate("123.456^null").is_null

    def test_integer(self):
        assert self.evaluate("456.789^3").is_double(95311852.6118971)
        assert self.evaluate("123.456^3").is_double(1881640.29520282)
        assert self.evaluate("123.456^1").is_double(123.456)
        assert self.evaluate("123.456^0").is_double(1.0)

    def test_double(self):
        assert self.evaluate("456.789^3.456").is_double(1555884096.48867)
        assert self.evaluate("123.456^3.456").is_double(16914772.8048957)
        assert self.evaluate("123.456^1.0").is_double(123.456)
        assert self.evaluate("123.456^0.0").is_double(1.0)

    def test_date(self):
        assert self.evaluate("456.789^#02.01.1900 10:56:38#").is_double(1555839983.32258)
        assert self.evaluate("123.456^#02.01.1900 10:56:38#").is_double(16914395.6813334)
        assert self.evaluate("123.456^#31.12.1899#").is_double(123.456)
        assert self.evaluate("123.456^#30.12.1899#").is_double(1.0)

    def test_string(self):
        assert self.evaluate("456.789^\"3\"").is_double(95311852.6118971)
        assert self.evaluate("123.456^\"3\"").is_double(1881640.29520282)
        assert self.evaluate("123.456^\"1\"").is_double(123.456)
        assert self.evaluate("123.456^\"0\"").is_double(1.0)
        assert self.evaluate("456.789^\"3.456\"").is_double(1555884096.48867)
        assert self.evaluate("123.456^\"3.456\"").is_double(16914772.8048957)
        assert self.evaluate("123.456^\"1.0\"").is_double(123.456)
        assert self.evaluate("123.456^\"0.0\"").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("123.456^\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123.456^\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456^new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456^nothing")

    def test_boolean(self):
        assert self.evaluate("123.456^true").is_double(8.10005184033178E-03)
        assert self.evaluate("123.456^false").is_double(1.0)
