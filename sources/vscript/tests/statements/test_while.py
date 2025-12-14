
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestWhileStatement(VScriptTestCase):

    def test_for_each_statement(self):
        assert self.execute("""
            while result<3
                result=result+1
            wend""").is_integer(3)
        