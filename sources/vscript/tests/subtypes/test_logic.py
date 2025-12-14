
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestLogic(VScriptTestCase):

    def test_empty_operations(self):
        assert self.execute("if empty then result=1 else result=2").is_integer(2)

    def test_null_operations(self):
        assert self.execute("if null then result=1 else result=2").is_integer(2)

    def test_integer_operations(self):
        assert self.execute("if 123 then result=1 else result=2").is_integer(1)
        assert self.execute("if 0.0 then result=1 else result=2").is_integer(2)

    def test_double_operations(self):
        assert self.execute("if 123.456 then result=1 else result=2").is_integer(1)
        assert self.execute("if 0.0 then result=1 else result=2").is_integer(2)

    def test_date_operations(self):
        assert self.execute("if #02.05.1900 10:56:38# then result=1 else result=2").is_integer(1)
        assert self.execute("if #30.12.1899# then result=1 else result=2").is_integer(2)

    def test_string_operations(self):
        assert self.execute("if \"123\" then result=1 else result=2").is_integer(1)
        assert self.execute("if \"0\" then result=1 else result=2").is_integer(2)
        assert self.execute("if \"123.456\" then result=1 else result=2").is_integer(1)
        assert self.execute("if \"0.0\" then result=1 else result=2").is_integer(2)
        assert self.execute("if \"True\" then result=1 else result=2").is_integer(1)
        assert self.execute("if \"False\" then result=1 else result=2").is_integer(2)
        with raises(errors.type_mismatch):
            self.execute("if \"abc\" then result=1 else result=2")
        with raises(errors.type_mismatch):
            self.execute("if \"\" then result=1 else result=2")

    def test_generic_operations(self):
        with raises(errors.object_has_no_property):
            self.execute("class object end", "if new object then result=1 else result=2""")

    def test_nothing_operations(self):
        with raises(errors.object_variable_not_set):
            self.execute("if nothing then result=1 else result=2")

    def test_boolean_operations(self):
        assert self.execute("if true then result=1 else result=2").is_integer(1)
        assert self.execute("if false then result=1 else result=2").is_integer(2)
