
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestNullEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null=null").is_null

    def test_null(self):
        assert self.evaluate("null=null").is_null

    def test_integer(self):
        assert self.evaluate("null=123").is_null
        assert self.evaluate("null=0").is_null

    def test_double(self):
        assert self.evaluate("null=1.23").is_null
        assert self.evaluate("null=0.0").is_null

    def test_date(self):
        assert self.evaluate("null=#01.01.2011 01:01:01#").is_null
        assert self.evaluate("null=#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null=\"abc\"").is_null
        assert self.evaluate("null=\"123\"").is_null
        assert self.evaluate("null=\"1.23\"").is_null
        assert self.evaluate("null=\"0\"").is_null
        assert self.evaluate("null=\"0.0\"").is_null
        assert self.evaluate("null=\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null=nothing")

    def test_boolean(self):
        assert self.evaluate("null=true").is_null
        assert self.evaluate("null=false").is_null

class TestNullNonEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null<>empty").is_null

    def test_null(self):
        assert self.evaluate("null<>null").is_null

    def test_integer(self):
        assert self.evaluate("null<>123").is_null
        assert self.evaluate("null<>0").is_null

    def test_double(self):
        assert self.evaluate("null<>1.23").is_null
        assert self.evaluate("null<>0.0").is_null

    def test_date(self):
        assert self.evaluate("null<>#01.01.2011 01:01:01#").is_null
        assert self.evaluate("null<>#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null<>\"abc\"").is_null
        assert self.evaluate("null<>\"123\"").is_null
        assert self.evaluate("null<>\"1.23\"").is_null
        assert self.evaluate("null<>\"0\"").is_null
        assert self.evaluate("null<>\"0.0\"").is_null
        assert self.evaluate("null<>\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null<>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null<>nothing")

    def test_boolean(self):
        assert self.evaluate("null<>true").is_null
        assert self.evaluate("null<>false").is_null

class TestNullLessThanComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null<empty").is_null

    def test_null(self):
        assert self.evaluate("null<null").is_null

    def test_integer(self):
        assert self.evaluate("null<123").is_null
        assert self.evaluate("null<0").is_null

    def test_double(self):
        assert self.evaluate("null<1.23").is_null
        assert self.evaluate("null<0.0").is_null

    def test_date(self):
        assert self.evaluate("null<#01.01.2011 01:01:01#").is_null
        assert self.evaluate("null<#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null<\"abc\"").is_null
        assert self.evaluate("null<\"123\"").is_null
        assert self.evaluate("null<\"1.23\"").is_null
        assert self.evaluate("null<\"0\"").is_null
        assert self.evaluate("null<\"0.0\"").is_null
        assert self.evaluate("null<\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null<new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null<nothing")

    def test_boolean(self):
        assert self.evaluate("null<true").is_null
        assert self.evaluate("null<false").is_null

class TestNullGreatThenComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null>empty").is_null

    def test_null(self):
        assert self.evaluate("null>null").is_null

    def test_integer(self):
        assert self.evaluate("null>123").is_null
        assert self.evaluate("null>0").is_null

    def test_double(self):
        assert self.evaluate("null>1.23").is_null
        assert self.evaluate("null>0.0").is_null

    def test_date(self):
        assert self.evaluate("null>#01.01.2011 01:01:01#").is_null
        assert self.evaluate("null>#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null>\"abc\"").is_null
        assert self.evaluate("null>\"123\"").is_null
        assert self.evaluate("null>\"1.23\"").is_null
        assert self.evaluate("null>\"0\"").is_null
        assert self.evaluate("null>\"0.0\"").is_null
        assert self.evaluate("null>\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null>nothing")

    def test_boolean(self):
        assert self.evaluate("null>true").is_null
        assert self.evaluate("null>false").is_null

class TestNullLessThanOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null<=null").is_null

    def test_null(self):
        assert self.evaluate("null<=null").is_null

    def test_integer(self):
        assert self.evaluate("null<=123").is_null
        assert self.evaluate("null<=0").is_null

    def test_double(self):
        assert self.evaluate("null<=1.23").is_null
        assert self.evaluate("null<=0.0").is_null

    def test_date(self):
        assert self.evaluate("null<=#01.01.2011 01:01:01#").is_null
        assert self.evaluate("null<=#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null<=\"abc\"").is_null
        assert self.evaluate("null<=\"123\"").is_null
        assert self.evaluate("null<=\"1.23\"").is_null
        assert self.evaluate("null<=\"0\"").is_null
        assert self.evaluate("null<=\"0.0\"").is_null
        assert self.evaluate("null<=\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null<=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null<=nothing")

    def test_boolean(self):
        assert self.evaluate("null<=true").is_null
        assert self.evaluate("null<=false").is_null

class TestNullGreatThenOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("null>=null").is_null

    def test_null(self):
        assert self.evaluate("null>=null").is_null

    def test_integer(self):
        assert self.evaluate("null>=123").is_null
        assert self.evaluate("null>=0").is_null

    def test_double(self):
        assert self.evaluate("null>=1.23").is_null
        assert self.evaluate("null>=0.0").is_null

    def test_date(self):
        assert self.evaluate("null>=#01.01.2011 01:01:01#").is_null
        assert self.evaluate("null>=#30.12.1899#").is_null

    def test_string(self):
        assert self.evaluate("null>=\"abc\"").is_null
        assert self.evaluate("null>=\"123\"").is_null
        assert self.evaluate("null>=\"1.23\"").is_null
        assert self.evaluate("null>=\"0\"").is_null
        assert self.evaluate("null>=\"0.0\"").is_null
        assert self.evaluate("null>=\"\"").is_null

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "null>=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("null>=nothing")

    def test_boolean(self):
        assert self.evaluate("null>=true").is_null
        assert self.evaluate("null>=false").is_null
