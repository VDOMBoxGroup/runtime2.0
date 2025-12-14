
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestRecursion(VScriptTestCase):

    def test_recursion(self):
        assert self.execute("""
            function factorial(value)
                if value=0 then
                    factorial=1
                else
                    factorial=factorial(value-1)*value
                end
            end
            result=factorial(3)""").is_integer(6)
