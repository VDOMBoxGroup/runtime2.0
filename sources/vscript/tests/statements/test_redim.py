
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestRedimStatement(VScriptTestCase):

    def test_redim_statement(self):
        assert self.execute("""
            myarray=array(1, 2, 3)
            redim myarray(5)
            for each item in myarray
                result=result+item
            next""").is_integer(0)
        assert self.execute("""
            myarray=array(1, 2, 3)
            redim myarray(1)
            for each item in myarray
                result=result+item
            next""").is_integer(0)

    def test_redim_preserve_statement(self):
        assert self.execute("""
            myarray=array(1, 2, 3)
            redim preserve myarray(5)
            for each item in myarray
                result=result+item
            next""").is_integer(6)
        assert self.execute("""
            myarray=array(1, 2, 3)
            redim preserve myarray(1)
            for each item in myarray
                result=result+item
            next""").is_integer(3)

class TestWrongRedimStatement(VScriptTestCase):

    def test_redim_variable_statement(self):
        with raises(errors.type_mismatch):
            assert self.execute("""
                dim myvariable
                redim myvariable(1)""")

    def test_redim_static_array_statement(self):
        with raises(errors.static_array):
            assert self.execute("""
                dim myarray(2)
                redim myarray(1)""")
