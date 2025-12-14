
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestWithStatement(VScriptTestCase):

    def test_with_statement(self):
        assert self.execute("""
            class object
                dim value
                sub class_initialize
                    value=3
                end
            end
            set instance=new object
            with instance
                result=.value
            end""").is_integer(3)
        