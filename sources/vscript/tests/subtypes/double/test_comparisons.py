
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestDoubleEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123.456=empty").is_boolean(false)
        assert self.evaluate("0.0=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("123.456=null").is_null

    def test_integer(self):
        assert self.evaluate("123.0=456").is_boolean(false)
        assert self.evaluate("123.0=123").is_boolean(true)

    def test_double(self):
        assert self.evaluate("123.456=456.789").is_boolean(false)
        assert self.evaluate("123.456=123.456").is_boolean(true)

    def test_date(self):
        assert self.evaluate("123.0=#31.03.1901#").is_boolean(false)
        assert self.evaluate("123.0=#02.05.1900#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("123.0=\"456\"").is_boolean(false)
        assert self.evaluate("123.0=\"123\"").is_boolean(true)
        assert self.evaluate("123.456=\"456.789\"").is_boolean(false)
        assert self.evaluate("123.456=\"123.456\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456=nothing")

    def test_boolean(self):
        assert self.evaluate("0.0=true").is_boolean(false)
        assert self.evaluate("-1.0=true").is_boolean(true)
        assert self.evaluate("-1.0=false").is_boolean(false)
        assert self.evaluate("0.0=false").is_boolean(true)

class TestDoubleNonEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123.456<>empty").is_boolean(true)
        assert self.evaluate("0.0<>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("123.456<>null").is_null

    def test_integer(self):
        assert self.evaluate("123.0<>456").is_boolean(true)
        assert self.evaluate("123.0<>123").is_boolean(false)

    def test_double(self):
        assert self.evaluate("123.456<>456.789").is_boolean(true)
        assert self.evaluate("123.456<>123.456").is_boolean(false)

    def test_date(self):
        assert self.evaluate("123.0<>#31.03.1901#").is_boolean(true)
        assert self.evaluate("123.0<>#02.05.1900#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("123.0<>\"456\"").is_boolean(true)
        assert self.evaluate("123.0<>\"123\"").is_boolean(false)
        assert self.evaluate("123.456<>\"456.789\"").is_boolean(true)
        assert self.evaluate("123.456<>\"123.456\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456<>\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456<>\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456<>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456<>nothing")

    def test_boolean(self):
        assert self.evaluate("0.0<>true").is_boolean(true)
        assert self.evaluate("-1.0<>true").is_boolean(false)
        assert self.evaluate("-1.0<>false").is_boolean(true)
        assert self.evaluate("0.0<>false").is_boolean(false)

class TestDoubleLessThanComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123.456<empty").is_boolean(false)
        assert self.evaluate("0.0<empty").is_boolean(false)
        assert self.evaluate("-123.456<empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("123.456<null").is_null

    def test_integer(self):
        assert self.evaluate("456.0<123").is_boolean(false)
        assert self.evaluate("123.0<123").is_boolean(false)
        assert self.evaluate("123.0<456").is_boolean(true)

    def test_double(self):
        assert self.evaluate("456.789<123.456").is_boolean(false)
        assert self.evaluate("123.456<123.456").is_boolean(false)
        assert self.evaluate("123.456<456.789").is_boolean(true)

    def test_date(self):
        assert self.evaluate("456.0<#02.05.1900#").is_boolean(false)
        assert self.evaluate("123.0<#02.05.1900#").is_boolean(false)
        assert self.evaluate("123.0<#31.03.1901#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("456.0<\"123\"").is_boolean(false)
        assert self.evaluate("123.0<\"123\"").is_boolean(false)
        assert self.evaluate("123.0<\"456\"").is_boolean(true)
        assert self.evaluate("456.789<\"123.456\"").is_boolean(false)
        assert self.evaluate("123.456<\"123.456\"").is_boolean(false)
        assert self.evaluate("123.456<\"456.789\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456<\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456<\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456<new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456<nothing")

    def test_boolean(self):
        assert self.evaluate("123.456<true").is_boolean(false)
        assert self.evaluate("-1.0<true").is_boolean(false)
        assert self.evaluate("-123.456<true").is_boolean(true)
        assert self.evaluate("123.456<false").is_boolean(false)
        assert self.evaluate("0.0<false").is_boolean(false)
        assert self.evaluate("-123.456<false").is_boolean(true)

class TestDoubleGreatThenComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123.456>empty").is_boolean(true)
        assert self.evaluate("0.0>empty").is_boolean(false)
        assert self.evaluate("-123.456>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("123.456>null").is_null

    def test_integer(self):
        assert self.evaluate("456.0>123").is_boolean(true)
        assert self.evaluate("123.0>123").is_boolean(false)
        assert self.evaluate("123.0>456").is_boolean(false)

    def test_double(self):
        assert self.evaluate("456.789>123.456").is_boolean(true)
        assert self.evaluate("123.456>123.456").is_boolean(false)
        assert self.evaluate("123.456>456.789").is_boolean(false)

    def test_date(self):
        assert self.evaluate("456.0>#02.05.1900#").is_boolean(true)
        assert self.evaluate("123.0>#02.05.1900#").is_boolean(false)
        assert self.evaluate("123.0>#31.03.1901#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("456.0>\"123\"").is_boolean(true)
        assert self.evaluate("123.0>\"123\"").is_boolean(false)
        assert self.evaluate("123.0>\"456\"").is_boolean(false)
        assert self.evaluate("456.789>\"123.456\"").is_boolean(true)
        assert self.evaluate("123.456>\"123.456\"").is_boolean(false)
        assert self.evaluate("123.456>\"456.789\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456>\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456>\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456>nothing")

    def test_boolean(self):
        assert self.evaluate("123.456>true").is_boolean(true)
        assert self.evaluate("-1.0>true").is_boolean(false)
        assert self.evaluate("-123.456>true").is_boolean(false)
        assert self.evaluate("123.456>false").is_boolean(true)
        assert self.evaluate("0.0>false").is_boolean(false)
        assert self.evaluate("-123.456>false").is_boolean(false)

class TestDoubleLessThanOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123.456<=empty").is_boolean(false)
        assert self.evaluate("0.0<=empty").is_boolean(true)
        assert self.evaluate("-123.456<=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("123.456<=null").is_null

    def test_integer(self):
        assert self.evaluate("456.0<=123").is_boolean(false)
        assert self.evaluate("123.0<=123").is_boolean(true)
        assert self.evaluate("123.0<=456").is_boolean(true)

    def test_double(self):
        assert self.evaluate("456.789<=123.456").is_boolean(false)
        assert self.evaluate("123.456<=123.456").is_boolean(true)
        assert self.evaluate("123.456<=456.789").is_boolean(true)

    def test_date(self):
        assert self.evaluate("456.0<=#02.05.1900#").is_boolean(false)
        assert self.evaluate("123.0<=#02.05.1900#").is_boolean(true)
        assert self.evaluate("123.0<=#31.03.1901#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("456.0<=\"123\"").is_boolean(false)
        assert self.evaluate("123.0<=\"123\"").is_boolean(true)
        assert self.evaluate("123.0<=\"456\"").is_boolean(true)
        assert self.evaluate("456.789<=\"123.456\"").is_boolean(false)
        assert self.evaluate("123.456<=\"123.456\"").is_boolean(true)
        assert self.evaluate("123.456<=\"456.789\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456<=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456<=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456<=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456<=nothing")

    def test_boolean(self):
        assert self.evaluate("123.456<=true").is_boolean(false)
        assert self.evaluate("-1.0<=true").is_boolean(true)
        assert self.evaluate("-123.456<=true").is_boolean(true)
        assert self.evaluate("123.456<=false").is_boolean(false)
        assert self.evaluate("0.0<=false").is_boolean(true)
        assert self.evaluate("-123.456<=false").is_boolean(true)

class TestDoubleGreatThenOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123.456>=empty").is_boolean(true)
        assert self.evaluate("0.0>=empty").is_boolean(true)
        assert self.evaluate("-123.456>=empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("123.456>=null").is_null

    def test_integer(self):
        assert self.evaluate("456.0>=123").is_boolean(true)
        assert self.evaluate("123.0>=123").is_boolean(true)
        assert self.evaluate("123.0>=456").is_boolean(false)

    def test_double(self):
        assert self.evaluate("456.789>=123.456").is_boolean(true)
        assert self.evaluate("123.456>=123.456").is_boolean(true)
        assert self.evaluate("123.456>=456.789").is_boolean(false)

    def test_date(self):
        assert self.evaluate("456.0>=#02.05.1900#").is_boolean(true)
        assert self.evaluate("123.0>=#02.05.1900#").is_boolean(true)
        assert self.evaluate("123.0>=#31.03.1901#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("456.0>=\"123\"").is_boolean(true)
        assert self.evaluate("123.0>=\"123\"").is_boolean(true)
        assert self.evaluate("123.0>=\"456\"").is_boolean(false)
        assert self.evaluate("456.789>=\"123.456\"").is_boolean(true)
        assert self.evaluate("123.456>=\"123.456\"").is_boolean(true)
        assert self.evaluate("123.456>=\"456.789\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456>=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123.456>=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123.456>=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123.456>=nothing")

    def test_boolean(self):
        assert self.evaluate("123.456>=true").is_boolean(true)
        assert self.evaluate("-1.0>=true").is_boolean(true)
        assert self.evaluate("-123.456>=true").is_boolean(false)
        assert self.evaluate("123.456>=false").is_boolean(true)
        assert self.evaluate("0.0>=false").is_boolean(true)
        assert self.evaluate("-123.456>=false").is_boolean(false)
