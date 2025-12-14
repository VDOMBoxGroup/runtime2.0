
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestIntegerAddition(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("123+empty").is_integer(123)

    def test_null(self):
        assert self.evaluate("123+null").is_null

    def test_integer(self):
        assert self.evaluate("123+123").is_integer(246)

    def test_double(self):
        assert self.evaluate("123+123.456").is_double(246.456)

    def test_date(self):
        assert self.evaluate("123+#02.05.1900 10:56:38#").is_date(1900, 9, 2, 10, 56, 38)

    def test_string(self):
        assert self.evaluate("123+\"123\"").is_double(246)
        assert self.evaluate("123+\"123.456\"").is_double(246.456)
        with raises(errors.type_mismatch):
            assert self.evaluate("123+\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123+\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123+new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123+nothing")

    def test_boolean(self):
        assert self.evaluate("123+true").is_integer(122)
        assert self.evaluate("123+false").is_integer(123)
        
class TestIntegerSubtraction(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("123-empty").is_integer(123)

    def test_null(self):
        assert self.evaluate("123-null").is_null

    def test_integer(self):
        assert self.evaluate("123-123").is_integer(0)

    def test_double(self):
        assert self.evaluate("123-123.456").is_double(-0.456)

    def test_date(self):
        assert self.evaluate("123-#02.05.1900 10:56:38#").is_date(1899, 12, 30, 10, 56, 38)

    def test_string(self):
        assert self.evaluate("123-\"123\"").is_double(0)
        assert self.evaluate("123-\"123.456\"").is_double(-0.456)
        with raises(errors.type_mismatch):
            assert self.evaluate("123-\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123-\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123-new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123-nothing")

    def test_boolean(self):
        assert self.evaluate("123-true").is_integer(124)
        assert self.evaluate("123-false").is_integer(123)

class TestIntegerMultiplication(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123*empty").is_integer(0)

    def test_null(self):
        assert self.evaluate("123*null").is_null

    def test_integer(self):
        assert self.evaluate("123*123").is_integer(15129)

    def test_double(self):
        assert self.evaluate("123*123.456").is_double(15185.088)

    def test_date(self):
        assert self.evaluate("123*#02.05.1900 10:56:38#").is_double(15185.0874305556)

    def test_string(self):
        assert self.evaluate("123*\"123\"").is_double(15129)
        assert self.evaluate("123*\"123.456\"").is_double(15185.088)
        with raises(errors.type_mismatch):
            self.evaluate("123*\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123*\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123*new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123*nothing")

    def test_boolean(self):
        assert self.evaluate("123*true").is_integer(-123)
        assert self.evaluate("123*false").is_integer(0)

class TestIntegerDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("123/empty")
            
    def test_null(self):
        assert self.evaluate("123/null").is_null

    def test_integer(self):
        assert self.evaluate("456/123").is_double(3.70731707317073)
        assert self.evaluate("123/123").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("123/0")

    def test_double(self):
        assert self.evaluate("456/123.456").is_double(3.69362363919129)
        assert self.evaluate("123/123.456").is_double(0.996306376360809)
        with raises(errors.division_by_zero):
            self.evaluate("123/0.0")

    def test_date(self):
        assert self.evaluate("456/#02.05.1900 10:56:38#").is_double(3.69362377770307)
        assert self.evaluate("123/#02.05.1900 10:56:38#").is_double(0.996306413722538)
        with raises(errors.division_by_zero):
            self.evaluate("123/#30.12.1899#")

    def test_string(self):
        assert self.evaluate("456/\"123\"").is_double(3.70731707317073)
        assert self.evaluate("123/\"123\"").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("123/\"0\"")
        assert self.evaluate("456/\"123.456\"").is_double(3.69362363919129)
        assert self.evaluate("123/\"123.456\"").is_double(0.996306376360809)
        with raises(errors.division_by_zero):
            self.evaluate("123/\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("123/\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123/\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123/new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123/nothing")

    def test_boolean(self):
        assert self.evaluate("123/true").is_double(-123.0)
        with raises(errors.division_by_zero):
            self.evaluate("123/false")

class TestIntegerIntegerDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("123\\empty")

    def test_null(self):
        assert self.evaluate("123\\null").is_null

    def test_integer(self):
        assert self.evaluate("456\\123").is_integer(3)
        assert self.evaluate("123\\123").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123\\0")

    def test_double(self):
        assert self.evaluate("456\\123.456").is_integer(3)
        assert self.evaluate("123\\123.456").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123\\0.0")

    def test_date(self):
        assert self.evaluate("456\\#02.05.1900 10:56:38#").is_integer(3)
        assert self.evaluate("123\\#02.05.1900 10:56:38#").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123\\#30.12.1899#")

    def test_string(self):
        assert self.evaluate("456\\\"123\"").is_integer(3)
        assert self.evaluate("123\\\"123\"").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123\\\"0\"")
        assert self.evaluate("456\\\"123.456\"").is_integer(3)
        assert self.evaluate("123\\\"123.456\"").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("123\\\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("123\\\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123\\\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123\\new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123\\nothing")

    def test_boolean(self):
        assert self.evaluate("123\\true").is_integer(-123)
        with raises(errors.division_by_zero):
            self.evaluate("123\\false")

class TestIntegerRemainder(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("123 mod empty")

    def test_null(self):
        assert self.evaluate("123 mod null").is_null

    def test_integer(self):
        assert self.evaluate("456 mod 123").is_integer(87)
        assert self.evaluate("123 mod 123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123 mod 0")

    def test_double(self):
        assert self.evaluate("456 mod 123.456").is_integer(87)
        assert self.evaluate("123 mod 123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123 mod 0.0")

    def test_date(self):
        assert self.evaluate("456 mod #02.05.1900 10:56:38#").is_integer(87)
        assert self.evaluate("123 mod #02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123 mod #30.12.1899#")

    def test_string(self):
        assert self.evaluate("456 mod \"123\"").is_integer(87)
        assert self.evaluate("123 mod \"123\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123 mod \"0\"")
        assert self.evaluate("456 mod \"123.456\"").is_integer(87)
        assert self.evaluate("123 mod \"123.456\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123 mod \"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("123 mod \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123 mod \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123 mod new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123 mod nothing")

    def test_boolean(self):
        assert self.evaluate("123 mod true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("123 mod false")

class TestIntegerExponentiation(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123^empty").is_double(1.0)

    def test_null(self):
        assert self.evaluate("123^null").is_null

    def test_integer(self):
        assert self.evaluate("456^3").is_double(94818816.0)
        assert self.evaluate("123^3").is_double(1860867.0)
        assert self.evaluate("123^1").is_double(123.0)
        assert self.evaluate("123^0").is_double(1.0)

    def test_double(self):
        assert self.evaluate("456^3.456").is_double(1546615991.21912)
        assert self.evaluate("123^3.456").is_double(16699830.5756869)
        assert self.evaluate("123^1.0").is_double(123.0)
        assert self.evaluate("123^0.0").is_double(1.0)

    def test_date(self):
        assert self.evaluate("456^#02.01.1900 10:56:38#").is_double(1546572153.20483)
        assert self.evaluate("123^#02.01.1900 10:56:38#").is_double(16699458.5304636)
        assert self.evaluate("123^#31.12.1899#").is_double(123.0)
        assert self.evaluate("123^#30.12.1899#").is_double(1.0)

    def test_string(self):
        assert self.evaluate("456^\"3\"").is_double(94818816.0)
        assert self.evaluate("123^\"3\"").is_double(1860867.0)
        assert self.evaluate("123^\"1\"").is_double(123.0)
        assert self.evaluate("123^\"0\"").is_double(1.0)
        assert self.evaluate("456^\"3.456\"").is_double(1546615991.21912)
        assert self.evaluate("123^\"3.456\"").is_double(16699830.5756869)
        assert self.evaluate("123^\"1.0\"").is_double(123.0)
        assert self.evaluate("123^\"0.0\"").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("123^\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("123^\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123^new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123^nothing")

    def test_boolean(self):
        assert self.evaluate("123^true").is_double(8.13008130081301E-03)
        assert self.evaluate("123^false").is_double(1.0)
