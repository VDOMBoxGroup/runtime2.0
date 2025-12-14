
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestClassStatement(VScriptTestCase):

    def test_class(self):
        assert self.execute("""
            class object
            end
            set result=new object""").is_generic
        assert self.execute("""
            class object
            end class
            set result=new object""").is_generic
