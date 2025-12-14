
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestStringEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"abc\"=empty").is_boolean(false)
        assert self.evaluate("\"\"=empty").is_boolean(true)
        assert self.evaluate("\"0\"=empty").is_boolean(false)
        assert self.evaluate("\"0.0\"=empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("\"abc\"=null").is_null
        assert self.evaluate("\"\"=null").is_null
        assert self.evaluate("\"0\"=null").is_null
        assert self.evaluate("\"0.0\"=null").is_null

    def test_integer(self):
        assert self.evaluate("\"123\"=456").is_boolean(false)
        assert self.evaluate("\"123\"=123").is_boolean(true)
        assert self.evaluate("\"123.0\"=456").is_boolean(false)
        assert self.evaluate("\"123.0\"=123").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"=123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"=0")

    def test_double(self):
        assert self.evaluate("\"123.456\"=456.789").is_boolean(false)
        assert self.evaluate("\"123.456\"=123.456").is_boolean(true)
        assert self.evaluate("\"123.456\"=456.789").is_boolean(false)
        assert self.evaluate("\"123.456\"=123.456").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"=123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"=0.0")

    def test_date(self):
        assert self.evaluate("\"123\"=#31.03.1901#").is_boolean(false)
        assert self.evaluate("\"123\"=#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123.0\"=#31.03.1901#").is_boolean(false)
        assert self.evaluate("\"123.0\"=#02.05.1900#").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"=#02.05.1900#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"=#30.12.1899#")

    def test_string(self):
        assert self.evaluate("\"abc\"=\"def\"").is_boolean(false)
        assert self.evaluate("\"abc\"=\"abc\"").is_boolean(true)
        assert self.evaluate("\"0\"=\"\"").is_boolean(false)
        assert self.evaluate("\"0.0\"=\"\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"=nothing")

    def test_boolean(self):
        assert self.evaluate("\"abc\"=false").is_boolean(false)
        assert self.evaluate("\"True\"=true").is_boolean(true)
        assert self.evaluate("\"abc\"=true").is_boolean(false)
        assert self.evaluate("\"False\"=false").is_boolean(true)
        assert self.evaluate("\"-1\"=true").is_boolean(false)
        assert self.evaluate("\"0.0\"=false").is_boolean(false)

class TestStringNonEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"abc\"<>empty").is_boolean(true)
        assert self.evaluate("\"\"<>empty").is_boolean(false)
        assert self.evaluate("\"0\"<>empty").is_boolean(true)
        assert self.evaluate("\"0.0\"<>empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("\"abc\"<>null").is_null
        assert self.evaluate("\"\"<>null").is_null
        assert self.evaluate("\"0\"<>null").is_null
        assert self.evaluate("\"0.0\"<>null").is_null

    def test_integer(self):
        assert self.evaluate("\"123\"<>456").is_boolean(true)
        assert self.evaluate("\"123\"<>123").is_boolean(false)
        assert self.evaluate("\"123.0\"<>456").is_boolean(true)
        assert self.evaluate("\"123.0\"<>123").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<>123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<>0")

    def test_double(self):
        assert self.evaluate("\"123.456\"<>456.789").is_boolean(true)
        assert self.evaluate("\"123.456\"<>123.456").is_boolean(false)
        assert self.evaluate("\"123.456\"<>456.789").is_boolean(true)
        assert self.evaluate("\"123.456\"<>123.456").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<>123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<>0.0")

    def test_date(self):
        assert self.evaluate("\"123\"<>#31.03.1901#").is_boolean(true)
        assert self.evaluate("\"123\"<>#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123.0\"<>#31.03.1901#").is_boolean(true)
        assert self.evaluate("\"123.0\"<>#02.05.1900#").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<>#02.05.1900#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<>#30.12.1899#")

    def test_string(self):
        assert self.evaluate("\"abc\"<>\"def\"").is_boolean(true)
        assert self.evaluate("\"abc\"<>\"abc\"").is_boolean(false)
        assert self.evaluate("\"0\"<>\"\"").is_boolean(true)
        assert self.evaluate("\"0.0\"<>\"\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"<>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"<>nothing")

    def test_boolean(self):
        assert self.evaluate("\"abc\"<>false").is_boolean(true)
        assert self.evaluate("\"True\"<>true").is_boolean(false)
        assert self.evaluate("\"abc\"<>true").is_boolean(true)
        assert self.evaluate("\"False\"<>false").is_boolean(false)
        assert self.evaluate("\"-1\"<>true").is_boolean(true)
        assert self.evaluate("\"0.0\"<>false").is_boolean(true)

class TestStringLessThanComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"123\"<empty").is_boolean(false)
        assert self.evaluate("\"0\"<empty").is_boolean(false)
        assert self.evaluate("\"123.456\"<empty").is_boolean(false)
        assert self.evaluate("\"0.0\"<empty").is_boolean(false)
        assert self.evaluate("\"abc\"<empty").is_boolean(false)
        assert self.evaluate("\"\"<empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("\"123\"<null").is_null
        assert self.evaluate("\"0\"<null").is_null
        assert self.evaluate("\"123.456\"<null").is_null
        assert self.evaluate("\"0.0\"<null").is_null
        assert self.evaluate("\"abc\"<null").is_null
        assert self.evaluate("\"\"<null").is_null

    def test_integer(self):
        assert self.evaluate("\"456\"<123").is_boolean(false)
        assert self.evaluate("\"123\"<123").is_boolean(false)
        assert self.evaluate("\"123\"<456").is_boolean(true)
        assert self.evaluate("\"456.789\"<123").is_boolean(false)
        assert self.evaluate("\"123.456\"<123").is_boolean(false)
        assert self.evaluate("\"123.456\"<456").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<0")

    def test_double(self):
        assert self.evaluate("\"456\"<123.0").is_boolean(false)
        assert self.evaluate("\"123\"<123.0").is_boolean(false)
        assert self.evaluate("\"123\"<456.0").is_boolean(true)
        assert self.evaluate("\"456.789\"<123.456").is_boolean(false)
        assert self.evaluate("\"123.456\"<123.456").is_boolean(false)
        assert self.evaluate("\"123.456\"<456.789").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<0.0")

    def test_date(self):
        assert self.evaluate("\"456\"<#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123\"<#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123\"<#31.03.1901#").is_boolean(true)
        assert self.evaluate("\"456.0\"<#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123.0\"<#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123.0\"<#31.03.1901#").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<#02.05.1900#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<#30.12.1899#")

    def test_string(self):
        assert self.evaluate("\"def\"<\"abc\"").is_boolean(false)
        assert self.evaluate("\"abc\"<\"abc\"").is_boolean(false)
        assert self.evaluate("\"abc\"<\"def\"").is_boolean(true)
        assert self.evaluate("\"0\"<\"\"").is_boolean(false)
        assert self.evaluate("\"0.0\"<\"\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"<new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"<nothing")

    def test_boolean(self):
        assert self.evaluate("\"U\"<true").is_boolean(false)
        assert self.evaluate("\"True\"<true").is_boolean(false)
        assert self.evaluate("\"S\"<true").is_boolean(true)
        assert self.evaluate("\"G\"<false").is_boolean(false)
        assert self.evaluate("\"False\"<false").is_boolean(false)
        assert self.evaluate("\"E\"<false").is_boolean(true)
        assert self.evaluate("\"-1\"<true").is_boolean(true)
        assert self.evaluate("\"0.0\"<false").is_boolean(true)

class TestStringGreatThenComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"123\">empty").is_boolean(true)
        assert self.evaluate("\"0\">empty").is_boolean(true)
        assert self.evaluate("\"123.456\">empty").is_boolean(true)
        assert self.evaluate("\"0.0\">empty").is_boolean(true)
        assert self.evaluate("\"abc\">empty").is_boolean(true)
        assert self.evaluate("\"\">empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("\"123\">null").is_null
        assert self.evaluate("\"0\">null").is_null
        assert self.evaluate("\"123.456\">null").is_null
        assert self.evaluate("\"0.0\">null").is_null
        assert self.evaluate("\"abc\">null").is_null
        assert self.evaluate("\"\">null").is_null

    def test_integer(self):
        assert self.evaluate("\"456\">123").is_boolean(true)
        assert self.evaluate("\"123\">123").is_boolean(false)
        assert self.evaluate("\"123\">456").is_boolean(false)
        assert self.evaluate("\"456.789\">123").is_boolean(true)
        assert self.evaluate("\"123.456\">123").is_boolean(false)
        assert self.evaluate("\"123.456\">456").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\">123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\">0")

    def test_double(self):
        assert self.evaluate("\"456\">123.0").is_boolean(true)
        assert self.evaluate("\"123\">123.0").is_boolean(false)
        assert self.evaluate("\"123\">456.0").is_boolean(false)
        assert self.evaluate("\"456.789\">123.456").is_boolean(true)
        assert self.evaluate("\"123.456\">123.456").is_boolean(false)
        assert self.evaluate("\"123.456\">456.789").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\">123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\">0.0")

    def test_date(self):
        assert self.evaluate("\"456\">#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123\">#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123\">#31.03.1901#").is_boolean(false)
        assert self.evaluate("\"456.0\">#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123.0\">#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123.0\">#31.03.1901#").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\">#02.05.1900#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\">#30.12.1899#")

    def test_string(self):
        assert self.evaluate("\"def\">\"abc\"").is_boolean(true)
        assert self.evaluate("\"abc\">\"abc\"").is_boolean(false)
        assert self.evaluate("\"abc\">\"def\"").is_boolean(false)
        assert self.evaluate("\"0\">\"\"").is_boolean(true)
        assert self.evaluate("\"0.0\">\"\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\">new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\">nothing")

    def test_boolean(self):
        assert self.evaluate("\"U\">true").is_boolean(true)
        assert self.evaluate("\"True\">true").is_boolean(false)
        assert self.evaluate("\"S\">true").is_boolean(false)
        assert self.evaluate("\"G\">false").is_boolean(true)
        assert self.evaluate("\"False\">false").is_boolean(false)
        assert self.evaluate("\"E\">false").is_boolean(false)
        assert self.evaluate("\"-1\">true").is_boolean(false)
        assert self.evaluate("\"0.0\">false").is_boolean(false)

class TestStringLessThanOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"123\"<=empty").is_boolean(false)
        assert self.evaluate("\"0\"<=empty").is_boolean(false)
        assert self.evaluate("\"123.456\"<=empty").is_boolean(false)
        assert self.evaluate("\"0.0\"<=empty").is_boolean(false)
        assert self.evaluate("\"abc\"<=empty").is_boolean(false)
        assert self.evaluate("\"\"<=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("\"123\"<=null").is_null
        assert self.evaluate("\"0\"<=null").is_null
        assert self.evaluate("\"123.456\"<=null").is_null
        assert self.evaluate("\"0.0\"<=null").is_null
        assert self.evaluate("\"abc\"<=null").is_null
        assert self.evaluate("\"\"<=null").is_null

    def test_integer(self):
        assert self.evaluate("\"456\"<=123").is_boolean(false)
        assert self.evaluate("\"123\"<=123").is_boolean(true)
        assert self.evaluate("\"123\"<=456").is_boolean(true)
        assert self.evaluate("\"456.789\"<=123").is_boolean(false)
        assert self.evaluate("\"123.456\"<=123").is_boolean(true)
        assert self.evaluate("\"123.456\"<=456").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<=123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<=0")

    def test_double(self):
        assert self.evaluate("\"456\"<=123.0").is_boolean(false)
        assert self.evaluate("\"123\"<=123.0").is_boolean(true)
        assert self.evaluate("\"123\"<=456.0").is_boolean(true)
        assert self.evaluate("\"456.789\"<=123.456").is_boolean(false)
        assert self.evaluate("\"123.456\"<=123.456").is_boolean(true)
        assert self.evaluate("\"123.456\"<=456.789").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<=123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<=0.0")

    def test_date(self):
        assert self.evaluate("\"456\"<=#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123\"<=#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123\"<=#31.03.1901#").is_boolean(true)
        assert self.evaluate("\"456.0\"<=#02.05.1900#").is_boolean(false)
        assert self.evaluate("\"123.0\"<=#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123.0\"<=#31.03.1901#").is_boolean(true)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\"<=#02.05.1900#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\"<=#30.12.1899#")

    def test_string(self):
        assert self.evaluate("\"def\"<=\"abc\"").is_boolean(false)
        assert self.evaluate("\"abc\"<=\"abc\"").is_boolean(true)
        assert self.evaluate("\"abc\"<=\"def\"").is_boolean(true)
        assert self.evaluate("\"0\"<=\"\"").is_boolean(false)
        assert self.evaluate("\"0.0\"<=\"\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\"<=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\"<=nothing")

    def test_boolean(self):
        assert self.evaluate("\"U\"<=true").is_boolean(false)
        assert self.evaluate("\"True\"<=true").is_boolean(true)
        assert self.evaluate("\"S\"<=true").is_boolean(true)
        assert self.evaluate("\"G\"<=false").is_boolean(false)
        assert self.evaluate("\"False\"<=false").is_boolean(true)
        assert self.evaluate("\"E\"<=false").is_boolean(true)
        assert self.evaluate("\"-1\"<=true").is_boolean(true)
        assert self.evaluate("\"0.0\"<=false").is_boolean(true)

class TestStringGreatThenOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("\"123\">=empty").is_boolean(true)
        assert self.evaluate("\"0\">=empty").is_boolean(true)
        assert self.evaluate("\"123.456\">=empty").is_boolean(true)
        assert self.evaluate("\"0.0\">=empty").is_boolean(true)
        assert self.evaluate("\"abc\">=empty").is_boolean(true)
        assert self.evaluate("\"\">=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("\"123\">=null").is_null
        assert self.evaluate("\"0\">=null").is_null
        assert self.evaluate("\"123.456\">=null").is_null
        assert self.evaluate("\"0.0\">=null").is_null
        assert self.evaluate("\"abc\">=null").is_null
        assert self.evaluate("\"\">=null").is_null

    def test_integer(self):
        assert self.evaluate("\"456\">=123").is_boolean(true)
        assert self.evaluate("\"123\">=123").is_boolean(true)
        assert self.evaluate("\"123\">=456").is_boolean(false)
        assert self.evaluate("\"456.789\">=123").is_boolean(true)
        assert self.evaluate("\"123.456\">=123").is_boolean(true)
        assert self.evaluate("\"123.456\">=456").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\">=123")
        with raises(errors.type_mismatch):
            self.evaluate("\"\">=0")

    def test_double(self):
        assert self.evaluate("\"456\">=123.0").is_boolean(true)
        assert self.evaluate("\"123\">=123.0").is_boolean(true)
        assert self.evaluate("\"123\">=456.0").is_boolean(false)
        assert self.evaluate("\"456.789\">=123.456").is_boolean(true)
        assert self.evaluate("\"123.456\">=123.456").is_boolean(true)
        assert self.evaluate("\"123.456\">=456.789").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\">=123.456")
        with raises(errors.type_mismatch):
            self.evaluate("\"\">=0.0")

    def test_date(self):
        assert self.evaluate("\"456\">=#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123\">=#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123\">=#31.03.1901#").is_boolean(false)
        assert self.evaluate("\"456.0\">=#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123.0\">=#02.05.1900#").is_boolean(true)
        assert self.evaluate("\"123.0\">=#31.03.1901#").is_boolean(false)
        with raises(errors.type_mismatch):
            self.evaluate("\"abc\">=#02.05.1900#")
        with raises(errors.type_mismatch):
            self.evaluate("\"\">=#30.12.1899#")

    def test_string(self):
        assert self.evaluate("\"def\">=\"abc\"").is_boolean(true)
        assert self.evaluate("\"abc\">=\"abc\"").is_boolean(true)
        assert self.evaluate("\"abc\">=\"def\"").is_boolean(false)
        assert self.evaluate("\"0\">=\"\"").is_boolean(true)
        assert self.evaluate("\"0.0\">=\"\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "\"abc\">=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("\"abc\">=nothing")

    def test_boolean(self):
        assert self.evaluate("\"U\">=true").is_boolean(true)
        assert self.evaluate("\"True\">=true").is_boolean(true)
        assert self.evaluate("\"S\">=true").is_boolean(false)
        assert self.evaluate("\"G\">=false").is_boolean(true)
        assert self.evaluate("\"False\">=false").is_boolean(true)
        assert self.evaluate("\"E\">=false").is_boolean(false)
        assert self.evaluate("\"-1\">=true").is_boolean(false)
        assert self.evaluate("\"0.0\">=false").is_boolean(false)
