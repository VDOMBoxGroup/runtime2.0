
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestDateAddition(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("#02.05.1900 10:56:38#+empty").is_date(1900, 5, 2, 10, 56, 38)

    def test_null(self):
        assert self.evaluate("#02.05.1900 10:56:38#+null").is_null

    def test_integer(self):
        assert self.evaluate("#02.05.1900 10:56:38#+123").is_date(1900, 9, 2, 10, 56, 38)

    def test_double(self):
        assert self.evaluate("#02.05.1900 10:56:38#+123.456").is_date(1900, 9, 2, 21, 53, 16)

    def test_date(self):
        assert self.evaluate("#02.05.1900 10:56:38#+#02.05.1900 10:56:38#").is_date(1900, 9, 2, 21, 53, 16)

    def test_string(self):
        assert self.evaluate("#02.05.1900 10:56:38#+\"123\"").is_date(1900, 9, 2, 10, 56, 38)
        assert self.evaluate("#02.05.1900 10:56:38#+\"123.456\"").is_date(1900, 9, 2, 21, 53, 16)
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 10:56:38#+\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 10:56:38#+\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 10:56:38#+new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 10:56:38#+nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900 10:56:38#+true").is_date(1900, 5, 1, 10, 56, 38)
        assert self.evaluate("#02.05.1900 10:56:38#+false").is_date(1900, 5, 2, 10, 56, 38)
        
class TestDateSubtraction(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("#02.05.1900 10:56:38#-empty").is_date(1900, 5, 2, 10, 56, 38)

    def test_null(self):
        assert self.evaluate("#02.05.1900 10:56:38#-null").is_null

    def test_integer(self):
        assert self.evaluate("#02.05.1900 10:56:38#-123").is_date(1899, 12, 30, 10, 56, 38)

    def test_double(self):
        assert self.evaluate("#02.05.1900 10:56:38#-123.456").is_date(1899, 12, 30, 0, 0, 0)

    def test_date(self):
        assert self.evaluate("#02.05.1900 10:56:38#-#02.05.1900 10:56:38#").is_double(0.0)

    def test_string(self):
        assert self.evaluate("#02.05.1900 10:56:38#-\"123\"").is_date(1899, 12, 30, 10, 56, 38)
        assert self.evaluate("#02.05.1900 10:56:38#-\"123.456\"").is_date(1899, 12, 30, 0, 0, 0)
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 10:56:38#-\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 10:56:38#-\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 10:56:38#-new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 10:56:38#-nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900 10:56:38#-true").is_date(1900, 5, 3, 10, 56, 38)
        assert self.evaluate("#02.05.1900 10:56:38#-false").is_date(1900, 5, 2, 10, 56, 38)

class TestDateMultiplication(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("#02.05.1900 10:56:38#*empty").is_double(0.0)

    def test_null(self):
        assert self.evaluate("#02.05.1900 10:56:38#*null").is_null

    def test_integer(self):
        assert self.evaluate("#02.05.1900 10:56:38#*123").is_double(15185.0874305556)

    def test_double(self):
        assert self.evaluate("#02.05.1900 10:56:38#*123.456").is_double(15241.3833644444)

    def test_date(self):
        assert self.evaluate("#02.05.1900 10:56:38#*#02.05.1900 10:56:38#").is_double(15241.3827928889)

    def test_string(self):
        assert self.evaluate("#02.05.1900 10:56:38#*\"123\"").is_double(15185.0874305556)
        assert self.evaluate("#02.05.1900 10:56:38#*\"123.456\"").is_double(15241.3833644444)
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38#*\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38#*\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 10:56:38#*new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 10:56:38#*nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900 10:56:38#*true").is_double(-123.45599537037)
        assert self.evaluate("#02.05.1900 10:56:38#*false").is_double(0.0)

class TestDateDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#/empty")
            
    def test_null(self):
        assert self.evaluate("#02.05.1900 10:56:38#/null").is_null

    def test_integer(self):
        assert self.evaluate("#31.03.1901 18:56:10#/123").is_double(3.71373174495634)
        assert self.evaluate("#02.05.1900 10:56:38#/123").is_double(1.00370727943391)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#/0")

    def test_double(self):
        assert self.evaluate("#31.03.1901 18:56:10#/123.456").is_double(3.70001461759355)
        assert self.evaluate("#02.05.1900 10:56:38#/123.456").is_double(0.99999996249976)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#/0.0")

    def test_date(self):
        assert self.evaluate("#31.03.1901 18:56:10#/#02.05.1900 10:56:38#").is_double(3.70001475634499)
        assert self.evaluate("#02.05.1900 10:56:38#/#02.05.1900 10:56:38#").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#/#30.12.1899#")

    def test_string(self):
        assert self.evaluate("#31.03.1901 18:56:10#/\"123\"").is_double(3.71373174495634)
        assert self.evaluate("#02.05.1900 10:56:38#/\"123\"").is_double(1.00370727943391)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#/\"0\"")
        assert self.evaluate("#31.03.1901 18:56:10#/\"123.456\"").is_double(3.70001461759355)
        assert self.evaluate("#02.05.1900 10:56:38#/\"123.456\"").is_double(0.99999996249976)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#/\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38#/\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38#/\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 10:56:38#/new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 10:56:38#/nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900 10:56:38#/true").is_double(-123.45599537037)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#/false")

class TestDateIntegerDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#\\empty")

    def test_null(self):
        assert self.evaluate("#02.05.1900 10:56:38#\\null").is_null

    def test_integer(self):
        assert self.evaluate("#31.03.1901 18:56:10#\\123").is_integer(3)
        assert self.evaluate("#02.05.1900 10:56:38#\\123").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#\\0")

    def test_double(self):
        assert self.evaluate("#31.03.1901 18:56:10#\\123.456").is_integer(3)
        assert self.evaluate("#02.05.1900 10:56:38#\\123.456").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#\\0.0")

    def test_date(self):
        assert self.evaluate("#31.03.1901 18:56:10#\\#02.05.1900 10:56:38#").is_integer(3)
        assert self.evaluate("#02.05.1900 10:56:38#\\#02.05.1900 10:56:38#").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#\\#30.12.1899#")

    def test_string(self):
        assert self.evaluate("#31.03.1901 18:56:10#\\\"123\"").is_integer(3)
        assert self.evaluate("#02.05.1900 10:56:38#\\\"123\"").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#\\\"0\"")
        assert self.evaluate("#31.03.1901 18:56:10#\\\"123.456\"").is_integer(3)
        assert self.evaluate("#02.05.1900 10:56:38#\\\"123.456\"").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#\\\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38#\\\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38#\\\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 10:56:38#\\new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 10:56:38#\\nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900 10:56:38#\\true").is_integer(-123)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38#\\false")

class TestDateRemainder(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38# mod empty")

    def test_null(self):
        assert self.evaluate("#02.05.1900 10:56:38# mod null").is_null

    def test_integer(self):
        assert self.evaluate("#31.03.1901 18:56:10# mod 123").is_integer(88)
        assert self.evaluate("#02.05.1900 10:56:38# mod 123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38# mod 0")

    def test_double(self):
        assert self.evaluate("#31.03.1901 18:56:10# mod 123.456").is_integer(88)
        assert self.evaluate("#02.05.1900 10:56:38# mod 123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38# mod 0.0")

    def test_date(self):
        assert self.evaluate("#31.03.1901 18:56:10# mod #02.05.1900 10:56:38#").is_integer(88)
        assert self.evaluate("#02.05.1900 10:56:38# mod #02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38# mod #30.12.1899#")

    def test_string(self):
        assert self.evaluate("#31.03.1901 18:56:10# mod \"123\"").is_integer(88)
        assert self.evaluate("#02.05.1900 10:56:38# mod \"123\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38# mod \"0\"")
        assert self.evaluate("#31.03.1901 18:56:10# mod \"123.456\"").is_integer(88)
        assert self.evaluate("#02.05.1900 10:56:38# mod \"123.456\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38# mod \"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38# mod \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38# mod \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 10:56:38# mod new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 10:56:38# mod nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900 10:56:38# mod true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("#02.05.1900 10:56:38# mod false")

class TestDateExponentiation(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("#02.05.1900 10:56:38#^empty").is_double(1.0)

    def test_null(self):
        assert self.evaluate("#02.05.1900 10:56:38#^null").is_null

    def test_integer(self):
        assert self.evaluate("#31.03.1901 18:56:10#^3").is_double(95311855.5098998)
        assert self.evaluate("#02.05.1900 10:56:38#^3").is_double(1881640.08351694)
        assert self.evaluate("#02.05.1900 10:56:38#^1").is_double(123.45599537037)
        assert self.evaluate("#02.05.1900 10:56:38#^0").is_double(1.0)

    def test_double(self):
        assert self.evaluate("#31.03.1901 18:56:10#^3.456").is_double(1555884150.9868)
        assert self.evaluate("#02.05.1900 10:56:38#^3.456").is_double(16914770.6127272)
        assert self.evaluate("#02.05.1900 10:56:38#^1.0").is_double(123.45599537037)
        assert self.evaluate("#02.05.1900 10:56:38#^0.0").is_double(1.0)

    def test_date(self):
        assert self.evaluate("#31.03.1901 18:56:10#^#02.01.1900 10:56:38#").is_double(1555840037.81909)
        assert self.evaluate("#02.05.1900 10:56:38#^#02.01.1900 10:56:38#").is_double(16914393.4892168)
        assert self.evaluate("#02.05.1900 10:56:38#^#31.12.1899#").is_double(123.45599537037)
        assert self.evaluate("#02.05.1900 10:56:38#^#30.12.1899#").is_double(1.0)

    def test_string(self):
        assert self.evaluate("#31.03.1901 18:56:10#^\"3.456\"").is_double(1555884150.9868)
        assert self.evaluate("#02.05.1900 10:56:38#^\"3.456\"").is_double(16914770.6127272)
        assert self.evaluate("#02.05.1900 10:56:38#^\"1.0\"").is_double(123.45599537037)
        assert self.evaluate("#02.05.1900 10:56:38#^\"0.0\"").is_double(1.0)

        assert self.evaluate("#31.03.1901 18:56:10#^\"3.456\"").is_double(1555884150.9868)
        assert self.evaluate("#02.05.1900 10:56:38#^\"3.456\"").is_double(16914770.6127272)
        assert self.evaluate("#02.05.1900 10:56:38#^\"1.0\"").is_double(123.45599537037)
        assert self.evaluate("#02.05.1900 10:56:38#^\"0.0\"").is_double(1.0)

        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38#^\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("#02.05.1900 10:56:38#^\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 10:56:38#^new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 10:56:38#^nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900 10:56:38#^true").is_double(8.10005214408568E-03)
        assert self.evaluate("#02.05.1900 10:56:38#^false").is_double(1.0)
