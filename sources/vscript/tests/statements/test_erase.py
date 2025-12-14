
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestEraseStatement(VScriptTestCase):

    def test_redim_static_array_statement(self):
        assert self.execute("""
            result=array(1, 2, 3)
            erase result""").is_array(lambda index, item: item.is_empty)

    def test_redim_dynamic_array_statement(self):
        assert self.execute("""
            result=array(1, 2, 3)
            erase result""").is_array(length=0)

class TestWrongRedimStatement(VScriptTestCase):

    def test_erase_variable_statement(self):
        with raises(errors.type_mismatch):
            assert self.execute("""
                dim myvariable
                erase myvariable""")
