
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestDoStatement(VScriptTestCase):

    def test_do_loop_statement(self):
        assert self.execute("""
            do
                result=result+1
                exit do
            loop""").is_integer(1)

    def test_do_while_loop_statement(self):
        assert self.execute("""
            do while result<3
                result=result+1
            loop""").is_integer(3)
        assert self.execute("""
            do while result=0
                result=result+1
            loop""").is_integer(1)

    def test_do_until_loop_statement(self):
        assert self.execute("""
            do until result>3
                result=result+1
            loop""").is_integer(4)
        assert self.execute("""
            do until result=0
                result=result+1
            loop""").is_empty

    def test_do_loop_while_statement(self):
        assert self.execute("""
            do
                result=result+1
            loop while result<3""").is_integer(3)
        assert self.execute("""
            do
                result=result+1
            loop while result=1""").is_integer(2)

    def test_do_loop_until_statement(self):
        assert self.execute("""
            do
                result=result+1
            loop until result>3""").is_integer(4)
        assert self.execute("""
            do
                result=result+1
            loop until result=1""").is_integer(1)
        