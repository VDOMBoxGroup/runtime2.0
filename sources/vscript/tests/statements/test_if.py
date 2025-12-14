
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestIfStatement(VScriptTestCase):

    def test_if_then_statement(self):
        assert self.execute("""
            if true then
                result=1
            end""").is_integer(1)
        assert self.execute("""
            if true then
                result=1
            end if""").is_integer(1)

    def test_if_then_singleline_statement(self):
        assert self.execute("if true then result=1").is_integer(1)

    def test_if_then_else_statement(self):
        assert self.execute("""
            if true then
                result=1
            else
                result=2
            end""").is_integer(1)
        assert self.execute("""
            if true then
                result=1
            else
                result=2
            end if""").is_integer(1)
        assert self.execute("""
            if false then
                result=1
            else
                result=2
            end""").is_integer(2)
        assert self.execute("""
            if false then
                result=1
            else
                result=2
            end if""").is_integer(2)

    def test_if_then_else_singleline_statement(self):
        assert self.execute("if true then result=1 else result=2").is_integer(1)
        assert self.execute("if false then result=1 else result=2").is_integer(2)

    def test_if_then_elseif_then_statement(self):
        assert self.execute("""
            if true then
                result=1
            elseif true then
                result=2
            end""").is_integer(1)
        assert self.execute("""
            if true then
                result=1
            elseif true then
                result=2
            end if""").is_integer(1)
        assert self.execute("""
            if false then
                result=1
            elseif true then
                result=2
            end""").is_integer(2)
        assert self.execute("""
            if false then
                result=1
            elseif true then
                result=2
            end if""").is_integer(2)

    def test_if_then_elseif_then_else_statement(self):
        assert self.execute("""
            if true then
                result=1
            elseif true then
                result=2
            else
                result=3
            end""").is_integer(1)
        assert self.execute("""
            if true then
                result=1
            elseif true then
                result=2
            else
                result=3
            end if""").is_integer(1)
        assert self.execute("""
            if false then
                result=1
            elseif true then
                result=2
            else
                result=3
            end""").is_integer(2)
        assert self.execute("""
            if false then
                result=1
            elseif true then
                result=2
            else
                result=3
            end if""").is_integer(2)
        assert self.execute("""
            if false then
                result=1
            elseif false then
                result=2
            else
                result=3
            end""").is_integer(3)
        assert self.execute("""
            if false then
                result=1
            elseif false then
                result=2
            else
                result=3
            end if""").is_integer(3)
