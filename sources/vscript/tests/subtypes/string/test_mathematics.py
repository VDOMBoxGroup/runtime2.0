
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestStringAddition(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("\"123\"+empty").is_string(u"123")
        assert self.evaluate("\"123.456\"+empty").is_string(u"123.456")
        assert self.evaluate("\"abc\"+empty").is_string(u"abc")
        assert self.evaluate("\"\"+empty").is_string(u"")

    def test_null(self):
        assert self.evaluate("\"123\"+null").is_null
        assert self.evaluate("\"123.456\"+null").is_null
        assert self.evaluate("\"abc\"+null").is_null
        assert self.evaluate("\"\"+null").is_null

    def test_integer(self):
        assert self.evaluate("\"123\"+123").is_double(246.0)
        assert self.evaluate("\"123.456\"+123").is_double(246.456)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"+123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"+123")

    def test_double(self):
        assert self.evaluate("\"123\"+123.456").is_double(246.456)
        assert self.evaluate("\"123.456\"+123.456").is_double(246.912)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"+123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"+123.456")

    def test_date(self):
        assert self.evaluate("\"123\"+#02.05.1900 10:56:38#").is_date(1900, 9, 2, 10, 56, 38)
        assert self.evaluate("\"123.456\"+#02.05.1900 10:56:38#").is_date(1900, 9, 2, 21, 53, 16)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"+#02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"+#02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"123\"+\"123\"").is_string(u"123123")
        assert self.evaluate("\"123.456\"+\"123.456\"").is_string(u"123.456123.456")
        assert self.evaluate("\"abc\"+\"abc\"").is_string(u"abcabc")
        assert self.evaluate("\"\"+\"\"").is_string(u"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"+new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"+nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\"+true").is_double(122.0)
        assert self.evaluate("\"123.456\"+false").is_double(123.456)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"+true")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"+false")
        
class TestStringSubtraction(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("\"123\"-empty").is_double(123.0)
        assert self.evaluate("\"123.456\"-empty").is_double(123.456)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"-empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"-empty")

    def test_null(self):
        assert self.evaluate("\"123\"-null").is_null
        assert self.evaluate("\"123.456\"-null").is_null
        assert self.evaluate("\"abc\"-null").is_null
        assert self.evaluate("\"\"-null").is_null

    def test_integer(self):
        assert self.evaluate("\"123\"-123").is_double(0.0)
        assert self.evaluate("\"123.456\"-123").is_double(0.456)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"-123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"-123")

    def test_double(self):
        assert self.evaluate("\"123\"-123.456").is_double(-0.456)
        assert self.evaluate("\"123.456\"-123.456").is_double(0.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"-123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"-123.456")

    def test_date(self):
        assert self.evaluate("\"123\"-#02.05.1900 10:56:38#").is_date(1899, 12, 30, 10, 56, 38)
        assert self.evaluate("\"123.456\"-#02.05.1900 10:56:38#").is_date(1899, 12, 30, 0, 0, 0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"-#02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"-#02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"123\"-\"123\"").is_double(0.0)
        assert self.evaluate("\"123.456\"-\"123.456\"").is_double(0.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"-\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"-\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"-new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"-nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\"-true").is_double(124.0)
        assert self.evaluate("\"123.456\"-false").is_double(123.456)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"-true")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"-false")

class TestStringMultiplication(VScriptTestCase):
    
    def test_empty(self):
        assert self.evaluate("\"123\"*empty").is_double(0.0)
        assert self.evaluate("\"123.456\"*empty").is_double(0.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"*empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"*empty")

    def test_null(self):
        assert self.evaluate("\"123\"*null").is_null
        assert self.evaluate("\"123.456\"*null").is_null
        assert self.evaluate("\"abc\"*null").is_null
        assert self.evaluate("\"\"*null").is_null

    def test_integer(self):
        assert self.evaluate("\"123\"*123").is_double(15129.0)
        assert self.evaluate("\"123.456\"*123").is_double(15185.088)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"*123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"*123")

    def test_double(self):
        assert self.evaluate("\"123\"*123.456").is_double(15185.088)
        assert self.evaluate("\"123.456\"*123.456").is_double(15241.383936)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"*123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"*123.456")

    def test_date(self):
        assert self.evaluate("\"123\"*#02.05.1900 10:56:38#").is_double(15185.0874305556)
        assert self.evaluate("\"123.456\"*#02.05.1900 10:56:38#").is_double(15241.3833644444)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"*#02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"*#02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"123\"*\"123\"").is_double(15129.0)
        assert self.evaluate("\"123.456\"*\"123.456\"").is_double(15241.383936)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"*\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"*\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"*new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"*nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\"*true").is_double(-123.0)
        assert self.evaluate("\"123.456\"*false").is_double(0.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"*true")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"*false")

class TestStringDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"/empty")
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"/empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"/empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"/empty")
            
    def test_null(self):
        assert self.evaluate("\"123\"/null").is_null
        assert self.evaluate("\"123.456\"/null").is_null
        assert self.evaluate("\"abc\"/null").is_null
        assert self.evaluate("\"\"/null").is_null

    def test_integer(self):
        assert self.evaluate("\"456\"/123").is_double(3.70731707317073)
        assert self.evaluate("\"123\"/123").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"/0")
        assert self.evaluate("\"456.789\"/123").is_double(3.71373170731707)
        assert self.evaluate("\"123.456\"/123").is_double(1.00370731707317)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"/0")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"/123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"/123")

    def test_double(self):
        assert self.evaluate("\"456\"/123.456").is_double(3.69362363919129)
        assert self.evaluate("\"123\"/123.456").is_double(0.996306376360809)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"/0.0")
        assert self.evaluate("\"456.789\"/123.456").is_double(3.70001458009331)
        assert self.evaluate("\"123.456\"/123.456").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"/0.0")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"/123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"/123.456")

    def test_date(self):
        assert self.evaluate("\"456\"/#02.05.1900 10:56:38#").is_double(3.69362377770307)
        assert self.evaluate("\"123\"/#02.05.1900 10:56:38#").is_double(0.996306413722538)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"/#30.12.1899#")
        assert self.evaluate("\"456.789\"/#02.05.1900 10:56:38#").is_double(3.70001471884475)
        assert self.evaluate("\"123.456\"/#02.05.1900 10:56:38#").is_double(1.00000003750024)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"/#30.12.1899#")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"/#02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"/#02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"456\"/\"123\"").is_double(3.70731707317073)
        assert self.evaluate("\"123\"/\"123\"").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"/\"0\"")
        assert self.evaluate("\"456.789\"/\"123.456\"").is_double(3.70001458009331)
        assert self.evaluate("\"123.456\"/\"123.456\"").is_double(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"/\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"123\"/\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"123.456\"/\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"/new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"/nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\"/true").is_double(-123.0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"/false")
        assert self.evaluate("\"123.456\"/true").is_double(-123.456)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"/false")

class TestStringIntegerDivision(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"\\empty")
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"\\empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"\\empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"\\empty")
            
    def test_null(self):
        assert self.evaluate("\"123\"\\null").is_null
        assert self.evaluate("\"123.456\"\\null").is_null
        assert self.evaluate("\"abc\"\\null").is_null
        assert self.evaluate("\"\"\\null").is_null

    def test_integer(self):
        assert self.evaluate("\"456\"\\123").is_integer(3)
        assert self.evaluate("\"123\"\\123").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"\\0")
        assert self.evaluate("\"456.789\"\\123").is_integer(3)
        assert self.evaluate("\"123.456\"\\123").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"\\0")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"\\123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"\\123")

    def test_double(self):
        assert self.evaluate("\"456\"\\123.456").is_integer(3)
        assert self.evaluate("\"123\"\\123.456").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"\\0.0")
        assert self.evaluate("\"456.789\"\\123.456").is_integer(3)
        assert self.evaluate("\"123.456\"\\123.456").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"\\0.0")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"\\123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"\\123.456")

    def test_date(self):
        assert self.evaluate("\"456\"\\#02.05.1900 10:56:38#").is_integer(3)
        assert self.evaluate("\"123\"\\#02.05.1900 10:56:38#").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"\\#30.12.1899#")
        assert self.evaluate("\"456.789\"\\#02.05.1900 10:56:38#").is_integer(3)
        assert self.evaluate("\"123.456\"\\#02.05.1900 10:56:38#").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"\\#30.12.1899#")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"\\#02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"\\#02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"456\"\\\"123\"").is_integer(3)
        assert self.evaluate("\"123\"\\\"123\"").is_integer(1.0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"\\\"0\"")
        assert self.evaluate("\"456.789\"\\\"123.456\"").is_integer(3)
        assert self.evaluate("\"123.456\"\\\"123.456\"").is_integer(1)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"\\\"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"123\"\\\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"123.456\"\\\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"\\new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"\\nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\"\\true").is_integer(-123)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\"\\false")
        assert self.evaluate("\"123.456\"\\true").is_integer(-123)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\"\\false")

class TestStringRemainder(VScriptTestCase):

    def test_empty(self):
        with raises(errors.division_by_zero):
            self.evaluate("\"123\" mod empty")
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\" mod empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" mod empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" mod empty")
            
    def test_null(self):
        assert self.evaluate("\"123\" mod null").is_null
        assert self.evaluate("\"123.456\" mod null").is_null
        assert self.evaluate("\"abc\" mod null").is_null
        assert self.evaluate("\"\" mod null").is_null

    def test_integer(self):
        assert self.evaluate("\"456\" mod 123").is_integer(87)
        assert self.evaluate("\"123\" mod 123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\" mod 0")
        assert self.evaluate("\"456.789\" mod 123").is_integer(88)
        assert self.evaluate("\"123.456\" mod 123").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\" mod 0")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" mod 123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" mod 123")

    def test_double(self):
        assert self.evaluate("\"456\" mod 123.456").is_integer(87)
        assert self.evaluate("\"123\" mod 123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\" mod 0.0")
        assert self.evaluate("\"456.789\" mod 123.456").is_integer(88)
        assert self.evaluate("\"123.456\" mod 123.456").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\" mod 0.0")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" mod 123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" mod 123.456")

    def test_date(self):
        assert self.evaluate("\"456\" mod #02.05.1900 10:56:38#").is_integer(87)
        assert self.evaluate("\"123\" mod #02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\" mod #30.12.1899#")
        assert self.evaluate("\"456.789\" mod #02.05.1900 10:56:38#").is_integer(88)
        assert self.evaluate("\"123.456\" mod #02.05.1900 10:56:38#").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\" mod #30.12.1899#")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\" mod #02.05.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\" mod #02.05.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"456\" mod \"123\"").is_integer(87)
        assert self.evaluate("\"123\" mod \"123\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\" mod \"0\"")
        assert self.evaluate("\"456.789\" mod \"123.456\"").is_integer(88)
        assert self.evaluate("\"123.456\" mod \"123.456\"").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\" mod \"0.0\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"123\" mod \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"123.456\" mod \"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\" mod new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\" mod nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\" mod true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123\" mod false")
        assert self.evaluate("\"123.456\" mod true").is_integer(0)
        with raises(errors.division_by_zero):
            self.evaluate("\"123.456\" mod false")

class TestStringExponentiation(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"123\"^empty").is_double(1.0)
        assert self.evaluate("\"123.456\"^empty").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"^empty")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"^empty")

    def test_null(self):
        assert self.evaluate("\"123\"^null").is_null
        assert self.evaluate("\"123.456\"^null").is_null
        assert self.evaluate("\"abc\"^null").is_null
        assert self.evaluate("\"\"^null").is_null

    def test_integer(self):
        assert self.evaluate("\"456\"^3").is_double(94818816.0)
        assert self.evaluate("\"123\"^3").is_double(1860867.0)
        assert self.evaluate("\"123\"^1").is_double(123.0)
        assert self.evaluate("\"123\"^0").is_double(1.0)
        assert self.evaluate("\"456.789\"^3").is_double(95311852.6118971)
        assert self.evaluate("\"123.456\"^3").is_double(1881640.29520282)
        assert self.evaluate("\"123.456\"^1").is_double(123.456)
        assert self.evaluate("\"123.456\"^0").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"^3")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"^3")

    def test_double(self):
        assert self.evaluate("\"456\"^3.456").is_double(1546615991.21912)
        assert self.evaluate("\"123\"^3.456").is_double(16699830.5756869)
        assert self.evaluate("\"123\"^1.0").is_double(123.0)
        assert self.evaluate("\"123\"^0.0").is_double(1.0)
        assert self.evaluate("\"456.789\"^3.456").is_double(1555884096.48867)
        assert self.evaluate("\"123.456\"^3.456").is_double(16914772.8048957)
        assert self.evaluate("\"123.456\"^1.0").is_double(123.456)
        assert self.evaluate("\"123.456\"^0.0").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"^3.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"^3.456")

    def test_date(self):
        assert self.evaluate("\"456\"^#02.01.1900 10:56:38#").is_double(1546572153.20483)
        assert self.evaluate("\"123\"^#02.01.1900 10:56:38#").is_double(16699458.5304636)
        assert self.evaluate("\"123\"^#31.12.1899#").is_double(123.0)
        assert self.evaluate("\"123\"^#30.12.1899#").is_double(1.0)
        assert self.evaluate("\"456.789\"^#02.01.1900 10:56:38#").is_double(1555839983.32258)
        assert self.evaluate("\"123.456\"^#02.01.1900 10:56:38#").is_double(16914395.6813334)
        assert self.evaluate("\"123.456\"^#31.12.1899#").is_double(123.456)
        assert self.evaluate("\"123.456\"^#30.12.1899#").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"^#02.01.1900 10:56:38#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"^#02.01.1900 10:56:38#")

    def test_string(self):
        assert self.evaluate("\"456\"^\"3\"").is_double(94818816.0)
        assert self.evaluate("\"123\"^\"3\"").is_double(1860867.0)
        assert self.evaluate("\"123\"^\"1\"").is_double(123.0)
        assert self.evaluate("\"123\"^\"0\"").is_double(1.0)
        assert self.evaluate("\"456\"^\"3.456\"").is_double(1546615991.21912)
        assert self.evaluate("\"123\"^\"3.456\"").is_double(16699830.5756869)
        assert self.evaluate("\"123\"^\"1.0\"").is_double(123.0)
        assert self.evaluate("\"123\"^\"0.0\"").is_double(1.0)
        assert self.evaluate("\"456.789\"^\"3\"").is_double(95311852.6118971)
        assert self.evaluate("\"123.456\"^\"3\"").is_double(1881640.29520282)
        assert self.evaluate("\"123.456\"^\"1\"").is_double(123.456)
        assert self.evaluate("\"123.456\"^\"0\"").is_double(1.0)
        assert self.evaluate("\"456.789\"^\"3.456\"").is_double(1555884096.48867)
        assert self.evaluate("\"123.456\"^\"3.456\"").is_double(16914772.8048957)
        assert self.evaluate("\"123.456\"^\"1.0\"").is_double(123.456)
        assert self.evaluate("\"123.456\"^\"0.0\"").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"123\"^\"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"123.456\"^\"\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"^\"123.456\"")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"^\"123\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"123.456\"^new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"123.456\"^nothing")

    def test_boolean(self):
        assert self.evaluate("\"123\"^true").is_double(8.13008130081301E-03)
        assert self.evaluate("\"123\"^false").is_double(1.0)
        assert self.evaluate("\"123.456\"^true").is_double(8.10005184033178E-03)
        assert self.evaluate("\"123.456\"^false").is_double(1.0)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"^true")
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"^false")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"^true")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"^false")
