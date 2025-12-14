
from ....testing import raises, VScriptTestCase
from .... import errors
from ....subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestEmptyEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("empty=null").is_null

    def test_integer(self):
        assert self.evaluate("empty=123").is_boolean(false)
        assert self.evaluate("empty=0").is_boolean(true)

    def test_double(self):
        assert self.evaluate("empty=123.456").is_boolean(false)
        assert self.evaluate("empty=0.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("empty=#02.05.1900#").is_boolean(false)
        assert self.evaluate("empty=#30.12.1899#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("empty=\"123\"").is_boolean(false)
        assert self.evaluate("empty=\"0\"").is_boolean(false)
        assert self.evaluate("empty=\"123.456\"").is_boolean(false)
        assert self.evaluate("empty=\"0.0\"").is_boolean(false)
        assert self.evaluate("empty=\"abc\"").is_boolean(false)
        assert self.evaluate("empty=\"\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty=nothing")

    def test_boolean(self):
        assert self.evaluate("empty=true").is_boolean(false)
        assert self.evaluate("empty=false").is_boolean(true)

class TestEmptyNonEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty<>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("empty<>null").is_null

    def test_integer(self):
        assert self.evaluate("empty<>123").is_boolean(true)
        assert self.evaluate("empty<>0").is_boolean(false)

    def test_double(self):
        assert self.evaluate("empty<>123.456").is_boolean(true)
        assert self.evaluate("empty<>0.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("empty<>#02.05.1900#").is_boolean(true)
        assert self.evaluate("empty<>#30.12.1899#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("empty<>\"123\"").is_boolean(true)
        assert self.evaluate("empty<>\"0\"").is_boolean(true)
        assert self.evaluate("empty<>\"123.456\"").is_boolean(true)
        assert self.evaluate("empty<>\"0.0\"").is_boolean(true)
        assert self.evaluate("empty<>\"abc\"").is_boolean(true)
        assert self.evaluate("empty<>\"\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty<>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty<>nothing")

    def test_boolean(self):
        assert self.evaluate("empty<>true").is_boolean(true)
        assert self.evaluate("empty<>false").is_boolean(false)

class TestEmptyLessThanComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty<empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("empty<null").is_null

    def test_integer(self):
        assert self.evaluate("empty<-123").is_boolean(false)
        assert self.evaluate("empty<0").is_boolean(false)
        assert self.evaluate("empty<456").is_boolean(true)

    def test_double(self):
        assert self.evaluate("empty<-123.0").is_boolean(false)
        assert self.evaluate("empty<0.0").is_boolean(false)
        assert self.evaluate("empty<456.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("empty<#29.08.1899#").is_boolean(false)
        assert self.evaluate("empty<#30.12.1899#").is_boolean(false)
        assert self.evaluate("empty<#31.03.1901#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("empty<\"-123\"").is_boolean(true)
        assert self.evaluate("empty<\"0\"").is_boolean(true)
        assert self.evaluate("empty<\"456\"").is_boolean(true)
        assert self.evaluate("empty<\"-123.0\"").is_boolean(true)
        assert self.evaluate("empty<\"0.0\"").is_boolean(true)
        assert self.evaluate("empty<\"456.0\"").is_boolean(true)
        assert self.evaluate("empty<\"abc\"").is_boolean(true)
        assert self.evaluate("empty<\"\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty<new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty<nothing")

    def test_boolean(self):
        assert self.evaluate("empty<true").is_boolean(false)
        assert self.evaluate("empty<false").is_boolean(false)

class TestEmptyGreatThenComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty>empty").is_boolean(false)

    def test_null(self):
        assert self.evaluate("empty>null").is_null

    def test_integer(self):
        assert self.evaluate("empty>-123").is_boolean(true)
        assert self.evaluate("empty>0").is_boolean(false)
        assert self.evaluate("empty>456").is_boolean(false)

    def test_double(self):
        assert self.evaluate("empty>-123.0").is_boolean(true)
        assert self.evaluate("empty>0.0").is_boolean(false)
        assert self.evaluate("empty>456.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("empty>#29.08.1899#").is_boolean(true)
        assert self.evaluate("empty>#30.12.1899#").is_boolean(false)
        assert self.evaluate("empty>#31.03.1901#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("empty>\"-123\"").is_boolean(false)
        assert self.evaluate("empty>\"0\"").is_boolean(false)
        assert self.evaluate("empty>\"456\"").is_boolean(false)
        assert self.evaluate("empty>\"-123.0\"").is_boolean(false)
        assert self.evaluate("empty>\"0.0\"").is_boolean(false)
        assert self.evaluate("empty>\"456.0\"").is_boolean(false)
        assert self.evaluate("empty>\"abc\"").is_boolean(false)
        assert self.evaluate("empty>\"\"").is_boolean(false)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty>new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty>nothing")

    def test_boolean(self):
        assert self.evaluate("empty>true").is_boolean(true)
        assert self.evaluate("empty>false").is_boolean(false)

class TestEmptyLessThanOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty<=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("empty<=null").is_null

    def test_integer(self):
        assert self.evaluate("empty<=-123").is_boolean(false)
        assert self.evaluate("empty<=0").is_boolean(true)
        assert self.evaluate("empty<=456").is_boolean(true)

    def test_double(self):
        assert self.evaluate("empty<=-123.0").is_boolean(false)
        assert self.evaluate("empty<=0.0").is_boolean(true)
        assert self.evaluate("empty<=456.0").is_boolean(true)

    def test_date(self):
        assert self.evaluate("empty<=#29.08.1899#").is_boolean(false)
        assert self.evaluate("empty<=#30.12.1899#").is_boolean(true)
        assert self.evaluate("empty<=#31.03.1901#").is_boolean(true)

    def test_string(self):
        assert self.evaluate("empty<=\"-123\"").is_boolean(true)
        assert self.evaluate("empty<=\"0\"").is_boolean(true)
        assert self.evaluate("empty<=\"456\"").is_boolean(true)
        assert self.evaluate("empty<=\"-123.0\"").is_boolean(true)
        assert self.evaluate("empty<=\"0.0\"").is_boolean(true)
        assert self.evaluate("empty<=\"456.0\"").is_boolean(true)
        assert self.evaluate("empty<=\"abc\"").is_boolean(true)
        assert self.evaluate("empty<=\"\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty<=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty<=nothing")

    def test_boolean(self):
        assert self.evaluate("empty<=true").is_boolean(false)
        assert self.evaluate("empty<=false").is_boolean(true)

class TestEmptyGreatThenOrEqualComparison(VScriptTestCase):

    def test_empty(self):
        assert self.evaluate("empty>=empty").is_boolean(true)

    def test_null(self):
        assert self.evaluate("empty>=null").is_null

    def test_integer(self):
        assert self.evaluate("empty>=-123").is_boolean(true)
        assert self.evaluate("empty>=0").is_boolean(true)
        assert self.evaluate("empty>=456").is_boolean(false)

    def test_double(self):
        assert self.evaluate("empty>=-123.0").is_boolean(true)
        assert self.evaluate("empty>=0.0").is_boolean(true)
        assert self.evaluate("empty>=456.0").is_boolean(false)

    def test_date(self):
        assert self.evaluate("empty>=#29.08.1899#").is_boolean(true)
        assert self.evaluate("empty>=#30.12.1899#").is_boolean(true)
        assert self.evaluate("empty>=#31.03.1901#").is_boolean(false)

    def test_string(self):
        assert self.evaluate("empty>=\"-123\"").is_boolean(false)
        assert self.evaluate("empty>=\"0\"").is_boolean(false)
        assert self.evaluate("empty>=\"456\"").is_boolean(false)
        assert self.evaluate("empty>=\"-123.0\"").is_boolean(false)
        assert self.evaluate("empty>=\"0.0\"").is_boolean(false)
        assert self.evaluate("empty>=\"456.0\"").is_boolean(false)
        assert self.evaluate("empty>=\"abc\"").is_boolean(false)
        assert self.evaluate("empty>=\"\"").is_boolean(true)

    def test_generic(self):
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "empty>=new object")

    def test_nothing(self):
        with raises(errors.object_variable_not_set):
            self.evaluate("empty>=nothing")

    def test_boolean(self):
        assert self.evaluate("empty>=true").is_boolean(true)
        assert self.evaluate("empty>=false").is_boolean(true)
