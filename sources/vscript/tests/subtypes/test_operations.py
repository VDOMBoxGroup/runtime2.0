
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestOperations(VScriptTestCase):

    def test_empty_operations(self):
        assert self.evaluate("not empty").is_integer(-1)
        assert self.evaluate("-(empty)").is_integer(0)
        assert self.evaluate("+(empty)").is_empty

    def test_null_operations(self):
        assert self.evaluate("not null").is_null
        assert self.evaluate("-(null)").is_null
        assert self.evaluate("+(null)").is_null

    def test_integer_operations(self):
        assert self.evaluate("not 123").is_integer(-124)
        assert self.evaluate("-(123)").is_integer(-123)
        assert self.evaluate("+(123)").is_integer(123)

    def test_double_operations(self):
        assert self.evaluate("not 123.456").is_integer(-124)
        assert self.evaluate("-(123.456)").is_double(-123.456)
        assert self.evaluate("+(123.456)").is_double(123.456)

    def test_date_operations(self):
        assert self.evaluate("not #02.05.1900 10:56:38#").is_integer(-124)
        assert self.evaluate("-(#02.05.1900 10:56:38#)").is_date(1899, 8, 29, 10, 56, 38)
        assert self.evaluate("+(#02.05.1900 10:56:38#)").is_date(1900, 5, 2, 10, 56, 38)

    def test_string_operations(self):
        assert self.evaluate("not \"123\"").is_integer(-124)
        assert self.evaluate("-(\"123\")").is_double(-123.0)
        assert self.evaluate("+(\"123\")").is_double(123.0)
        assert self.evaluate("not \"123.456\"").is_integer(-124)
        assert self.evaluate("-(\"123.456\")").is_double(-123.456)
        assert self.evaluate("+(\"123.456\")").is_double(123.456)
        with raises(errors.type_mismatch):
            self.evaluate("not \"abc\"")
        with raises(errors.type_mismatch):
            self.evaluate("-(\"abc\")")
        with raises(errors.type_mismatch):
            self.evaluate("+(\"abc\")")

    def test_generic_operations(self):
        with raises(errors.object_has_no_property):
            assert self.evaluate("class object end", "not new object")
        with raises(errors.object_has_no_property):
            assert self.evaluate("class object end", "-(new object)")
        with raises(errors.object_has_no_property):
            assert self.evaluate("class object end", "+(new object)")

    def test_nothing_operations(self):
        with raises(errors.object_variable_not_set):
            assert self.evaluate("not nothing")
        with raises(errors.object_variable_not_set):
            assert self.evaluate("-(nothing)")
        with raises(errors.object_variable_not_set):
            assert self.evaluate("+(nothing)")

    def test_boolean_operations(self):
        assert self.evaluate("not true").is_boolean(false)
        assert self.evaluate("-(true)").is_integer(1)
        assert self.evaluate("+(true)").is_integer(-1)
        assert self.evaluate("not false").is_boolean(true)
        assert self.evaluate("-(false)").is_integer(0)
        assert self.evaluate("+(false)").is_integer(0)
