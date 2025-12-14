
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestForStatement(VScriptTestCase):

    def test_for_each_statement(self):
        assert self.execute("""
            for each item in array(1, 2, 3)
                result=result+item
            next""").is_integer(6)

    def test_for_to_statement(self):
        assert self.execute("""
            for index=1 to 3
                result=result+index
            next""").is_integer(6)

    def test_for_to_step_statement(self):
        assert self.execute("""
            for index=1 to 6 step 2
                result=result+index
            next""").is_integer(9)
        