
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestDimStatement(VScriptTestCase):

    def test_dim_statement(self):
        assert self.execute("""
            dim myvariable
            result=myvariable""").is_empty

    def test_dim_static_array_statement(self):
        assert self.execute("""
            dim myarray(2)
            if len(myarray)<>3 then result=3
            for each item in myarray
                if not isempty(item) then result=3
            next""").is_empty

    def test_dim_dynamic_array_statement(self):
        assert self.execute("""
            dim myarray()
            result=myarray""").is_array(length=0)
