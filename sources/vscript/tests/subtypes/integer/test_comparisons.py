
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestIntegerEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123=empty").is_boolean(false)
        assert self.evaluate("0=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("123=null").is_null

    def test_integer(self):
        assert self.evaluate("123=456").is_boolean(false)
        assert self.evaluate("123=123").is_boolean(true)

    def test_double(self):
        assert self.evaluate("123=456.0").is_boolean(false)
        assert self.evaluate("123=123.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("123=#31.03.1901#").is_boolean(false)
        assert self.evaluate("123=#02.05.1900#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("123=\"456\"").is_boolean(false)
        assert self.evaluate("123=\"123\"").is_boolean(true)
        assert self.evaluate("123=\"456.0\"").is_boolean(false)
        assert self.evaluate("123=\"123.0\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("123=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123=nothing")

    def test_boolean(self):
        assert self.evaluate("0=true").is_boolean(false)
        assert self.evaluate("-1=true").is_boolean(true)
        assert self.evaluate("-1=false").is_boolean(false)
        assert self.evaluate("0=false").is_boolean(true)

class TestIntegerNonEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123<>empty").is_boolean(true)
        assert self.evaluate("0<>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("123<>null").is_null

    def test_integer(self):
        assert self.evaluate("123<>456").is_boolean(true)
        assert self.evaluate("123<>123").is_boolean(false)

    def test_double(self):
        assert self.evaluate("123<>456.0").is_boolean(true)
        assert self.evaluate("123<>123.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("123<>#31.03.1901#").is_boolean(true)
        assert self.evaluate("123<>#02.05.1900#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("123<>\"456\"").is_boolean(true)
        assert self.evaluate("123<>\"123\"").is_boolean(false)
        assert self.evaluate("123<>\"456.0\"").is_boolean(true)
        assert self.evaluate("123<>\"123.0\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("123<>\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123<>\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123<>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123<>nothing")

    def test_boolean(self):
        assert self.evaluate("0<>true").is_boolean(true)
        assert self.evaluate("-1<>true").is_boolean(false)
        assert self.evaluate("-1<>false").is_boolean(true)
        assert self.evaluate("0<>false").is_boolean(false)

class TestIntegerLessThanComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123<empty").is_boolean(false)
        assert self.evaluate("0<empty").is_boolean(false)
        assert self.evaluate("-123<empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("123<null").is_null

    def test_integer(self):
        assert self.evaluate("456<123").is_boolean(false)
        assert self.evaluate("123<123").is_boolean(false)
        assert self.evaluate("123<456").is_boolean(true)

    def test_double(self):
        assert self.evaluate("456<123.0").is_boolean(false)
        assert self.evaluate("123<123.0").is_boolean(false)
        assert self.evaluate("123<456.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("456<#02.05.1900#").is_boolean(false)
        assert self.evaluate("123<#02.05.1900#").is_boolean(false)
        assert self.evaluate("123<#31.03.1901#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("456<\"123\"").is_boolean(false)
        assert self.evaluate("123<\"123\"").is_boolean(false)
        assert self.evaluate("123<\"456\"").is_boolean(true)
        assert self.evaluate("456<\"123.0\"").is_boolean(false)
        assert self.evaluate("123<\"123.0\"").is_boolean(false)
        assert self.evaluate("123<\"456.0\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("123<\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123<\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123<new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123<nothing")

    def test_boolean(self):
        assert self.evaluate("123<true").is_boolean(false)
        assert self.evaluate("-1<true").is_boolean(false)
        assert self.evaluate("-123<true").is_boolean(true)
        assert self.evaluate("123<false").is_boolean(false)
        assert self.evaluate("0<false").is_boolean(false)
        assert self.evaluate("-123<false").is_boolean(true)

class TestIntegerGreatThenComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123>empty").is_boolean(true)
        assert self.evaluate("0>empty").is_boolean(false)
        assert self.evaluate("-123>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("123>null").is_null

    def test_integer(self):
        assert self.evaluate("456>123").is_boolean(true)
        assert self.evaluate("123>123").is_boolean(false)
        assert self.evaluate("123>456").is_boolean(false)

    def test_double(self):
        assert self.evaluate("456>123.0").is_boolean(true)
        assert self.evaluate("123>123.0").is_boolean(false)
        assert self.evaluate("123>456.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("456>#02.05.1900#").is_boolean(true)
        assert self.evaluate("123>#02.05.1900#").is_boolean(false)
        assert self.evaluate("123>#31.03.1901#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("456>\"123\"").is_boolean(true)
        assert self.evaluate("123>\"123\"").is_boolean(false)
        assert self.evaluate("123>\"456\"").is_boolean(false)
        assert self.evaluate("456>\"123.0\"").is_boolean(true)
        assert self.evaluate("123>\"123.0\"").is_boolean(false)
        assert self.evaluate("123>\"456.0\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("123>\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123>\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123>nothing")

    def test_boolean(self):
        assert self.evaluate("123>true").is_boolean(true)
        assert self.evaluate("-1>true").is_boolean(false)
        assert self.evaluate("-123>true").is_boolean(false)
        assert self.evaluate("123>false").is_boolean(true)
        assert self.evaluate("0>false").is_boolean(false)
        assert self.evaluate("-123>false").is_boolean(false)

class TestIntegerLessThanOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123<=empty").is_boolean(false)
        assert self.evaluate("0<=empty").is_boolean(true)
        assert self.evaluate("-123<=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("123<=null").is_null

    def test_integer(self):
        assert self.evaluate("456<=123").is_boolean(false)
        assert self.evaluate("123<=123").is_boolean(true)
        assert self.evaluate("123<=456").is_boolean(true)

    def test_double(self):
        assert self.evaluate("456<=123.0").is_boolean(false)
        assert self.evaluate("123<=123.0").is_boolean(true)
        assert self.evaluate("123<=456.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("456<=#02.05.1900#").is_boolean(false)
        assert self.evaluate("123<=#02.05.1900#").is_boolean(true)
        assert self.evaluate("123<=#31.03.1901#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("456<=\"123\"").is_boolean(false)
        assert self.evaluate("123<=\"123\"").is_boolean(true)
        assert self.evaluate("123<=\"456\"").is_boolean(true)
        assert self.evaluate("456<=\"123.0\"").is_boolean(false)
        assert self.evaluate("123<=\"123.0\"").is_boolean(true)
        assert self.evaluate("123<=\"456.0\"").is_boolean(true)
        with raises(errors.type_mismatch):
            assert self.evaluate("123<=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123<=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123<=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123<=nothing")

    def test_boolean(self):
        assert self.evaluate("123<=true").is_boolean(false)
        assert self.evaluate("-1<=true").is_boolean(true)
        assert self.evaluate("-123<=true").is_boolean(true)
        assert self.evaluate("123<=false").is_boolean(false)
        assert self.evaluate("0<=false").is_boolean(true)
        assert self.evaluate("-123<=false").is_boolean(true)

class TestIntegerGreatThenOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("123>=empty").is_boolean(true)
        assert self.evaluate("0>=empty").is_boolean(true)
        assert self.evaluate("-123>=empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("123>=null").is_null

    def test_integer(self):
        assert self.evaluate("456>=123").is_boolean(true)
        assert self.evaluate("123>=123").is_boolean(true)
        assert self.evaluate("123>=456").is_boolean(false)

    def test_double(self):
        assert self.evaluate("456>=123.0").is_boolean(true)
        assert self.evaluate("123>=123.0").is_boolean(true)
        assert self.evaluate("123>=456.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("456>=#02.05.1900#").is_boolean(true)
        assert self.evaluate("123>=#02.05.1900#").is_boolean(true)
        assert self.evaluate("123>=#31.03.1901#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("456>=\"123\"").is_boolean(true)
        assert self.evaluate("123>=\"123\"").is_boolean(true)
        assert self.evaluate("123>=\"456\"").is_boolean(false)
        assert self.evaluate("456>=\"123.0\"").is_boolean(true)
        assert self.evaluate("123>=\"123.0\"").is_boolean(true)
        assert self.evaluate("123>=\"456.0\"").is_boolean(false)
        with raises(errors.type_mismatch):
            assert self.evaluate("123>=\"abc\"")
        with raises(errors.type_mismatch):
            assert self.evaluate("123>=\"\"")

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123>=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("123>=nothing")

    def test_boolean(self):
        assert self.evaluate("123>=true").is_boolean(true)
        assert self.evaluate("-1>=true").is_boolean(true)
        assert self.evaluate("-123>=true").is_boolean(false)
        assert self.evaluate("123>=false").is_boolean(true)
        assert self.evaluate("0>=false").is_boolean(true)
        assert self.evaluate("-123>=false").is_boolean(false)
