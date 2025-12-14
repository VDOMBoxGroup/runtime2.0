
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestDateEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("#02.05.1900 02:57:18#=empty").is_boolean(false)
        assert self.evaluate("#30.12.1899#=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("#02.05.1900 02:57:18#=null").is_null

    def test_integer(self):
        assert self.evaluate("#02.05.1900#=456").is_boolean(false)
        assert self.evaluate("#02.05.1900#=123").is_boolean(true)

    def test_double(self):
        assert self.evaluate("#02.05.1900#=456.0").is_boolean(false)
        assert self.evaluate("#02.05.1900#=123.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("#02.05.1900 02:57:18#=#31.03.1901 18:56:10#").is_boolean(false)
        assert self.evaluate("#02.05.1900 02:57:18#=#02.05.1900 02:57:18#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("#02.05.1900#=\"456\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#=\"123\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#=\"456.0\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#=\"123.0\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 02:57:18#=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 02:57:18#=nothing")

    def test_boolean(self):
        assert self.evaluate("#30.12.1899#=true").is_boolean(false)
        assert self.evaluate("#29.12.1899#=true").is_boolean(true)
        assert self.evaluate("#29.12.1899#=false").is_boolean(false)
        assert self.evaluate("#30.12.1899#=false").is_boolean(true)

class TestDateNonEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("#02.05.1900 02:57:18#<>empty").is_boolean(true)
        assert self.evaluate("#30.12.1899#<>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("#02.05.1900 02:57:18#<>null").is_null

    def test_integer(self):
        assert self.evaluate("#02.05.1900#<>456").is_boolean(true)
        assert self.evaluate("#02.05.1900#<>123").is_boolean(false)

    def test_double(self):
        assert self.evaluate("#02.05.1900#<>456.0").is_boolean(true)
        assert self.evaluate("#02.05.1900#<>123.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("#02.05.1900 02:57:18#<>#31.03.1901 18:56:10#").is_boolean(true)
        assert self.evaluate("#02.05.1900 02:57:18#<>#02.05.1900 02:57:18#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("#02.05.1900#<>\"456\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#<>\"123\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#<>\"456.0\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#<>\"123.0\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#<>\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#<>\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 02:57:18#<>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 02:57:18#<>nothing")

    def test_boolean(self):
        assert self.evaluate("#30.12.1899#<>true").is_boolean(true)
        assert self.evaluate("#29.12.1899#<>true").is_boolean(false)
        assert self.evaluate("#29.12.1899#<>false").is_boolean(true)
        assert self.evaluate("#30.12.1899#<>false").is_boolean(false)

class TestDateLessThanComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("#02.05.1900 02:57:18#<empty").is_boolean(false)
        assert self.evaluate("#30.12.1899#<empty").is_boolean(false)
        assert self.evaluate("#29.08.1899 10:56:38#<empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("#02.05.1900 02:57:18#<null").is_null

    def test_integer(self):
        assert self.evaluate("#31.03.1901#<123").is_boolean(false)
        assert self.evaluate("#02.05.1900#<123").is_boolean(false)
        assert self.evaluate("#02.05.1900#<456").is_boolean(true)

    def test_double(self):
        assert self.evaluate("#31.03.1901#<123.0").is_boolean(false)
        assert self.evaluate("#02.05.1900#<123.0").is_boolean(false)
        assert self.evaluate("#02.05.1900#<456.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("#31.03.1901 18:56:10#<#02.05.1900 02:57:18#").is_boolean(false)
        assert self.evaluate("#02.05.1900 02:57:18#<#02.05.1900 02:57:18#").is_boolean(false)
        assert self.evaluate("#02.05.1900 02:57:18#<#31.03.1901 18:56:10#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("#31.03.1901#<\"123\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#<\"123\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#<\"456\"").is_boolean(true)
        assert self.evaluate("#31.03.1901#<\"123.0\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#<\"123.0\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#<\"456.0\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#<\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#<\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 02:57:18#<new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 02:57:18#<nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900#<true").is_boolean(false)
        assert self.evaluate("#29.12.1899#<true").is_boolean(false)
        assert self.evaluate("#29.08.1899#<true").is_boolean(true)
        assert self.evaluate("#02.05.1900#<false").is_boolean(false)
        assert self.evaluate("#30.12.1899#<false").is_boolean(false)
        assert self.evaluate("#29.08.1899#<false").is_boolean(true)

class TestDateGreatThenComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("#02.05.1900 02:57:18#>empty").is_boolean(true)
        assert self.evaluate("#30.12.1899#>empty").is_boolean(false)
        assert self.evaluate("#29.08.1899 10:56:38#>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("#02.05.1900 02:57:18#>null").is_null

    def test_integer(self):
        assert self.evaluate("#31.03.1901#>123").is_boolean(true)
        assert self.evaluate("#02.05.1900#>123").is_boolean(false)
        assert self.evaluate("#02.05.1900#>456").is_boolean(false)

    def test_double(self):
        assert self.evaluate("#31.03.1901#>123.0").is_boolean(true)
        assert self.evaluate("#02.05.1900#>123.0").is_boolean(false)
        assert self.evaluate("#02.05.1900#>456.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("#31.03.1901 18:56:10#>#02.05.1900 02:57:18#").is_boolean(true)
        assert self.evaluate("#02.05.1900 02:57:18#>#02.05.1900 02:57:18#").is_boolean(false)
        assert self.evaluate("#02.05.1900 02:57:18#>#31.03.1901 18:56:10#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("#31.03.1901#>\"123\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#>\"123\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#>\"456\"").is_boolean(false)
        assert self.evaluate("#31.03.1901#>\"123.0\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#>\"123.0\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#>\"456.0\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#>\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#>\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 02:57:18#>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 02:57:18#>nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900#>true").is_boolean(true)
        assert self.evaluate("#29.12.1899#>true").is_boolean(false)
        assert self.evaluate("#29.08.1899#>true").is_boolean(false)
        assert self.evaluate("#02.05.1900#>false").is_boolean(true)
        assert self.evaluate("#30.12.1899#>false").is_boolean(false)
        assert self.evaluate("#29.08.1899#>false").is_boolean(false)

class TestDateLessThanOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("#02.05.1900 02:57:18#<=empty").is_boolean(false)
        assert self.evaluate("#30.12.1899#<=empty").is_boolean(true)
        assert self.evaluate("#29.08.1899 10:56:38#<=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("#02.05.1900 02:57:18#<=null").is_null

    def test_integer(self):
        assert self.evaluate("#31.03.1901#<=123").is_boolean(false)
        assert self.evaluate("#02.05.1900#<=123").is_boolean(true)
        assert self.evaluate("#02.05.1900#<=456").is_boolean(true)

    def test_double(self):
        assert self.evaluate("#31.03.1901#<=123.0").is_boolean(false)
        assert self.evaluate("#02.05.1900#<=123.0").is_boolean(true)
        assert self.evaluate("#02.05.1900#<=456.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("#31.03.1901 18:56:10#<=#02.05.1900 02:57:18#").is_boolean(false)
        assert self.evaluate("#02.05.1900 02:57:18#<=#02.05.1900 02:57:18#").is_boolean(true)
        assert self.evaluate("#02.05.1900 02:57:18#<=#31.03.1901 18:56:10#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("#31.03.1901#<=\"123\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#<=\"123\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#<=\"456\"").is_boolean(true)
        assert self.evaluate("#31.03.1901#<=\"123.0\"").is_boolean(false)
        assert self.evaluate("#02.05.1900#<=\"123.0\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#<=\"456.0\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#<=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#<=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 02:57:18#<=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 02:57:18#<=nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900#<=true").is_boolean(false)
        assert self.evaluate("#29.12.1899#<=true").is_boolean(true)
        assert self.evaluate("#29.08.1899#<=true").is_boolean(true)
        assert self.evaluate("#02.05.1900#<=false").is_boolean(false)
        assert self.evaluate("#30.12.1899#<=false").is_boolean(true)
        assert self.evaluate("#29.08.1899#<=false").is_boolean(true)

class TestDateGreatThenOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("#02.05.1900 02:57:18#>=empty").is_boolean(true)
        assert self.evaluate("#30.12.1899#>=empty").is_boolean(true)
        assert self.evaluate("#29.08.1899 10:56:38#>=empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("#02.05.1900 02:57:18#>=null").is_null

    def test_integer(self):
        assert self.evaluate("#31.03.1901#>=123").is_boolean(true)
        assert self.evaluate("#02.05.1900#>=123").is_boolean(true)
        assert self.evaluate("#02.05.1900#>=456").is_boolean(false)

    def test_double(self):
        assert self.evaluate("#31.03.1901#>=123.0").is_boolean(true)
        assert self.evaluate("#02.05.1900#>=123.0").is_boolean(true)
        assert self.evaluate("#02.05.1900#>=456.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("#31.03.1901 18:56:10#>=#02.05.1900 02:57:18#").is_boolean(true)
        assert self.evaluate("#02.05.1900 02:57:18#>=#02.05.1900 02:57:18#").is_boolean(true)
        assert self.evaluate("#02.05.1900 02:57:18#>=#31.03.1901 18:56:10#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("#31.03.1901#>=\"123\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#>=\"123\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#>=\"456\"").is_boolean(false)
        assert self.evaluate("#31.03.1901#>=\"123.0\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#>=\"123.0\"").is_boolean(true)
        assert self.evaluate("#02.05.1900#>=\"456.0\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#>=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("#02.05.1900 02:57:18#>=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "#02.05.1900 02:57:18#>=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("#02.05.1900 02:57:18#>=nothing")

    def test_boolean(self):
        assert self.evaluate("#02.05.1900#>=true").is_boolean(true)
        assert self.evaluate("#29.12.1899#>=true").is_boolean(true)
        assert self.evaluate("#29.08.1899#>=true").is_boolean(false)
        assert self.evaluate("#02.05.1900#>=false").is_boolean(true)
        assert self.evaluate("#30.12.1899#>=false").is_boolean(true)
        assert self.evaluate("#29.08.1899#>=false").is_boolean(false)
