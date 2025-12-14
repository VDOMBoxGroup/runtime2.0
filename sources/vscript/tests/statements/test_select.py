
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestSelectStatement(VScriptTestCase):

    def test_select_statement(self):
        assert self.execute("""
            select case 1
            case 1
                result=1
            case 2
                result=2
            case 3
                result=3
            end""").is_integer(1)
        assert self.execute("""
            select case 1
            case 1
                result=1
            case 2
                result=2
            case 3
                result=3
            end select""").is_integer(1)
        assert self.execute("""
            select case 2
            case 1
                result=1
            case 2
                result=2
            case 3
                result=3
            end""").is_integer(2)
        assert self.execute("""
            select case 2
            case 1
                result=1
            case 2
                result=2
            case 3
                result=3
            end select""").is_integer(2)
        assert self.execute("""
            select case 3
            case 1
                result=1
            case 2
                result=2
            case 3
                result=3
            end""").is_integer(3)
        assert self.execute("""
            select case 3
            case 1
                result=1
            case 2
                result=2
            case 3
                result=3
            end select""").is_integer(3)

    def test_select_else_statement(self):
        assert self.execute("""
            select case 1
            case 1
                result=1
            case 2
                result=2
            case else
                result=3
            end""").is_integer(1)
        assert self.execute("""
            select case 1
            case 1
                result=1
            case 2
                result=2
            case else
                result=3
            end select""").is_integer(1)
        assert self.execute("""
            select case 2
            case 1
                result=1
            case 2
                result=2
            case else
                result=3
            end""").is_integer(2)
        assert self.execute("""
            select case 2
            case 1
                result=1
            case 2
                result=2
            case else
                result=3
            end select""").is_integer(2)
        assert self.execute("""
            select case 3
            case 1
                result=1
            case 2
                result=2
            case else
                result=3
            end""").is_integer(3)
        assert self.execute("""
            select case 3
            case 1
                result=1
            case 2
                result=2
            case else
                result=3
            end select""").is_integer(3)
        