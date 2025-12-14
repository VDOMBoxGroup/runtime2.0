
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestBooleanEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true=empty").is_boolean(false)
        assert self.evaluate("false=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("true=null").is_null
        assert self.evaluate("false=null").is_null

    def test_integer(self):
        assert self.evaluate("true=123").is_boolean(false)
        assert self.evaluate("true=-1").is_boolean(true)
        assert self.evaluate("false=123").is_boolean(false)
        assert self.evaluate("false=0").is_boolean(true)

    def test_double(self):
        assert self.evaluate("true=123.456").is_boolean(false)
        assert self.evaluate("true=-1.0").is_boolean(true)
        assert self.evaluate("false=123.456").is_boolean(false)
        assert self.evaluate("false=0.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("true=#02.05.1900#").is_boolean(false)
        assert self.evaluate("true=#29.12.1899#").is_boolean(true)
        assert self.evaluate("false=#02.05.1900#").is_boolean(false)
        assert self.evaluate("false=#30.12.1899#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("true=\"abc\"").is_boolean(false)
        assert self.evaluate("true=\"True\"").is_boolean(true)
        assert self.evaluate("false=\"abc\"").is_boolean(false)
        assert self.evaluate("false=\"False\"").is_boolean(true)
        assert self.evaluate("true=\"-1\"").is_boolean(false)
        assert self.evaluate("false=\"0.0\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true=nothing")

    def test_boolean(self):
        assert self.evaluate("true=true").is_boolean(true)
        assert self.evaluate("true=false").is_boolean(false)
        assert self.evaluate("false=true").is_boolean(false)
        assert self.evaluate("false=false").is_boolean(true)

class TestBooleanNonEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true<>empty").is_boolean(true)
        assert self.evaluate("false<>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("true<>null").is_null
        assert self.evaluate("false<>null").is_null

    def test_integer(self):
        assert self.evaluate("true<>123").is_boolean(true)
        assert self.evaluate("true<>-1").is_boolean(false)
        assert self.evaluate("false<>123").is_boolean(true)
        assert self.evaluate("false<>0").is_boolean(false)

    def test_double(self):
        assert self.evaluate("true<>123.456").is_boolean(true)
        assert self.evaluate("true<>-1.0").is_boolean(false)
        assert self.evaluate("false<>123.456").is_boolean(true)
        assert self.evaluate("false<>0.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("true<>#02.05.1900#").is_boolean(true)
        assert self.evaluate("true<>#29.12.1899#").is_boolean(false)
        assert self.evaluate("false<>#02.05.1900#").is_boolean(true)
        assert self.evaluate("false<>#30.12.1899#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("true<>\"abc\"").is_boolean(true)
        assert self.evaluate("true<>\"True\"").is_boolean(false)
        assert self.evaluate("false<>\"abc\"").is_boolean(true)
        assert self.evaluate("false<>\"False\"").is_boolean(false)
        assert self.evaluate("true<>\"-1\"").is_boolean(true)
        assert self.evaluate("false<>\"0.0\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "true<>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true<>nothing")

    def test_boolean(self):
        assert self.evaluate("true<>true").is_boolean(false)
        assert self.evaluate("true<>false").is_boolean(true)
        assert self.evaluate("false<>true").is_boolean(true)
        assert self.evaluate("false<>false").is_boolean(false)

class TestBooleanLessThanComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true<empty").is_boolean(true)
        assert self.evaluate("false<empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("true<null").is_null
        assert self.evaluate("false<null").is_null

    def test_integer(self):
        assert self.evaluate("true<-123").is_boolean(false)
        assert self.evaluate("true<-1").is_boolean(false)
        assert self.evaluate("true<123").is_boolean(true)
        assert self.evaluate("false<-123").is_boolean(false)
        assert self.evaluate("false<0").is_boolean(false)
        assert self.evaluate("false<123").is_boolean(true)

    def test_double(self):
        assert self.evaluate("true<-123.456").is_boolean(false)
        assert self.evaluate("true<-1.0").is_boolean(false)
        assert self.evaluate("true<123.456").is_boolean(true)
        assert self.evaluate("false<-123.456").is_boolean(false)
        assert self.evaluate("false<0.0").is_boolean(false)
        assert self.evaluate("false<123.456").is_boolean(true)

    def test_date(self):
        assert self.evaluate("true<#29.08.1899#").is_boolean(false)
        assert self.evaluate("true<#29.12.1899#").is_boolean(false)
        assert self.evaluate("true<#02.05.1900#").is_boolean(true)
        assert self.evaluate("false<#29.08.1899#").is_boolean(false)
        assert self.evaluate("false<#30.12.1899#").is_boolean(false)
        assert self.evaluate("false<#02.05.1900#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("true<\"S\"").is_boolean(false)
        assert self.evaluate("true<\"True\"").is_boolean(false)
        assert self.evaluate("true<\"U\"").is_boolean(true)
        assert self.evaluate("false<\"E\"").is_boolean(false)
        assert self.evaluate("false<\"False\"").is_boolean(false)
        assert self.evaluate("false<\"G\"").is_boolean(true)
        assert self.evaluate("true<\"-1\"").is_boolean(false)
        assert self.evaluate("false<\"0.0\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123<new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true<nothing")

    def test_boolean(self):
        assert self.evaluate("true<true").is_boolean(false)
        assert self.evaluate("true<false").is_boolean(true)
        assert self.evaluate("false<true").is_boolean(false)
        assert self.evaluate("false<false").is_boolean(false)

class TestBooleanGreatThenComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true>empty").is_boolean(false)
        assert self.evaluate("false>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("true>null").is_null
        assert self.evaluate("false>null").is_null

    def test_integer(self):
        assert self.evaluate("true>-123").is_boolean(true)
        assert self.evaluate("true>-1").is_boolean(false)
        assert self.evaluate("true>123").is_boolean(false)
        assert self.evaluate("false>-123").is_boolean(true)
        assert self.evaluate("false>0").is_boolean(false)
        assert self.evaluate("false>123").is_boolean(false)

    def test_double(self):
        assert self.evaluate("true>-123.456").is_boolean(true)
        assert self.evaluate("true>-1.0").is_boolean(false)
        assert self.evaluate("true>123.456").is_boolean(false)
        assert self.evaluate("false>-123.456").is_boolean(true)
        assert self.evaluate("false>0.0").is_boolean(false)
        assert self.evaluate("false>123.456").is_boolean(false)

    def test_date(self):
        assert self.evaluate("true>#29.08.1899#").is_boolean(true)
        assert self.evaluate("true>#29.12.1899#").is_boolean(false)
        assert self.evaluate("true>#02.05.1900#").is_boolean(false)
        assert self.evaluate("false>#29.08.1899#").is_boolean(true)
        assert self.evaluate("false>#30.12.1899#").is_boolean(false)
        assert self.evaluate("false>#02.05.1900#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("true>\"S\"").is_boolean(true)
        assert self.evaluate("true>\"True\"").is_boolean(false)
        assert self.evaluate("true>\"U\"").is_boolean(false)
        assert self.evaluate("false>\"E\"").is_boolean(true)
        assert self.evaluate("false>\"False\"").is_boolean(false)
        assert self.evaluate("false>\"G\"").is_boolean(false)
        assert self.evaluate("true>\"-1\"").is_boolean(true)
        assert self.evaluate("false>\"0.0\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true>nothing")

    def test_boolean(self):
        assert self.evaluate("true>true").is_boolean(false)
        assert self.evaluate("true>false").is_boolean(false)
        assert self.evaluate("false>true").is_boolean(true)
        assert self.evaluate("false>false").is_boolean(false)

class TestBooleanLessThanOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true<=empty").is_boolean(true)
        assert self.evaluate("false<=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("true<=null").is_null
        assert self.evaluate("false<=null").is_null

    def test_integer(self):
        assert self.evaluate("true<=-123").is_boolean(false)
        assert self.evaluate("true<=-1").is_boolean(true)
        assert self.evaluate("true<=123").is_boolean(true)
        assert self.evaluate("false<=-123").is_boolean(false)
        assert self.evaluate("false<=0").is_boolean(true)
        assert self.evaluate("false<=123").is_boolean(true)

    def test_double(self):
        assert self.evaluate("true<=-123.456").is_boolean(false)
        assert self.evaluate("true<=-1.0").is_boolean(true)
        assert self.evaluate("true<=123.456").is_boolean(true)
        assert self.evaluate("false<=-123.456").is_boolean(false)
        assert self.evaluate("false<=0.0").is_boolean(true)
        assert self.evaluate("false<=123.456").is_boolean(true)

    def test_date(self):
        assert self.evaluate("true<=#29.08.1899#").is_boolean(false)
        assert self.evaluate("true<=#29.12.1899#").is_boolean(true)
        assert self.evaluate("true<=#02.05.1900#").is_boolean(true)
        assert self.evaluate("false<=#29.08.1899#").is_boolean(false)
        assert self.evaluate("false<=#30.12.1899#").is_boolean(true)
        assert self.evaluate("false<=#02.05.1900#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("true<=\"S\"").is_boolean(false)
        assert self.evaluate("true<=\"True\"").is_boolean(true)
        assert self.evaluate("true<=\"U\"").is_boolean(true)
        assert self.evaluate("false<=\"E\"").is_boolean(false)
        assert self.evaluate("false<=\"False\"").is_boolean(true)
        assert self.evaluate("false<=\"G\"").is_boolean(true)
        assert self.evaluate("true<=\"-1\"").is_boolean(false)
        assert self.evaluate("false<=\"0.0\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123<=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true<=nothing")

    def test_boolean(self):
        assert self.evaluate("true<=true").is_boolean(true)
        assert self.evaluate("true<=false").is_boolean(true)
        assert self.evaluate("false<=true").is_boolean(false)
        assert self.evaluate("false<=false").is_boolean(true)

class TestBooleanGreatThenOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("true>=empty").is_boolean(false)
        assert self.evaluate("false>=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("true>=null").is_null
        assert self.evaluate("false>=null").is_null

    def test_integer(self):
        assert self.evaluate("true>=-123").is_boolean(true)
        assert self.evaluate("true>=-1").is_boolean(true)
        assert self.evaluate("true>=123").is_boolean(false)
        assert self.evaluate("false>=-123").is_boolean(true)
        assert self.evaluate("false>=0").is_boolean(true)
        assert self.evaluate("false>=123").is_boolean(false)

    def test_double(self):
        assert self.evaluate("true>=-123.456").is_boolean(true)
        assert self.evaluate("true>=-1.0").is_boolean(true)
        assert self.evaluate("true>=123.456").is_boolean(false)
        assert self.evaluate("false>=-123.456").is_boolean(true)
        assert self.evaluate("false>=0.0").is_boolean(true)
        assert self.evaluate("false>=123.456").is_boolean(false)

    def test_date(self):
        assert self.evaluate("true>=#29.08.1899#").is_boolean(true)
        assert self.evaluate("true>=#29.12.1899#").is_boolean(true)
        assert self.evaluate("true>=#02.05.1900#").is_boolean(false)
        assert self.evaluate("false>=#29.08.1899#").is_boolean(true)
        assert self.evaluate("false>=#30.12.1899#").is_boolean(true)
        assert self.evaluate("false>=#02.05.1900#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("true>=\"S\"").is_boolean(true)
        assert self.evaluate("true>=\"True\"").is_boolean(true)
        assert self.evaluate("true>=\"U\"").is_boolean(false)
        assert self.evaluate("false>=\"E\"").is_boolean(true)
        assert self.evaluate("false>=\"False\"").is_boolean(true)
        assert self.evaluate("false>=\"G\"").is_boolean(false)
        assert self.evaluate("true>=\"-1\"").is_boolean(true)
        assert self.evaluate("false>=\"0.0\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "123>=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("true>=nothing")

    def test_boolean(self):
        assert self.evaluate("true>=true").is_boolean(true)
        assert self.evaluate("true>=false").is_boolean(false)
        assert self.evaluate("false>=true").is_boolean(true)
        assert self.evaluate("false>=false").is_boolean(true)
