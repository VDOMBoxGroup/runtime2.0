
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestTryStatement(VScriptTestCase):

    def test_try_statement(self):
        assert self.execute("""
            try
                result=1
            end""").is_integer(1)
        assert self.execute("""
            try
                result=1
            end try""").is_integer(1)
        with raises(errors.division_by_zero):
            assert self.execute("""
                try
                    result=1/0
                end""")
        with raises(errors.division_by_zero):
            assert self.execute("""
                try
                    result=1/0
                end try""")

    def test_try_catch_statement(self):
        assert self.execute("""
            try
                result=1
            catch overflow
                result=2
            catch divisionbyzero
                result=3
            end""").is_integer(1)
        assert self.execute("""
            try
                result=1
            catch overflow
                result=2
            catch divisionbyzero
                result=3
            end try""").is_integer(1)
        assert self.execute("""
            try
                result=1/0
            catch overflow
                result=2
            catch divisionbyzero
                result=3
            end""").is_integer(3)
        assert self.execute("""
            try
                result=1/0
            catch overflow
                result=2
            catch divisionbyzero
                result=3
            end try""").is_integer(3)

    def test_try_catch_finally_statement(self):
        assert self.execute("""
            try
                result=1
            catch divisionbyzero
                result=2
            finally
                result=3
            end""").is_integer(3)
        assert self.execute("""
            try
                result=1
            catch divisionbyzero
                result=2
            finally
                result=3
            end try""").is_integer(3)
