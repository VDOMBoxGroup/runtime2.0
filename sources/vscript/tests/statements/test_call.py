
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestCallStatement(VScriptTestCase):

    def test_call_statement(self):
        assert self.execute("""
            sub mysub
                result=3
            end
            call mysub""").is_integer(3)

    def test_call_with_arguments_statement(self):
        assert self.execute("""
            sub mysub(x, y)
                result=x+y
            end
            call mysub(1, 2)""").is_integer(3)

    def test_call_with_clear_arguments_statement(self):
        assert self.execute("""
            sub mysub(x, y)
                result=x+y
            end
            call mysub 1, 2""").is_integer(3)
