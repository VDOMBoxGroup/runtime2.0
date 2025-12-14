
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestClasses(VScriptTestCase):

    def test_constructor(self):
        assert self.execute("""
            class object
                sub class_initialize
                    result=3
                end
            end
            set instance=new object""").is_integer(3)

    def test_destructor(self):
        assert self.execute("""
            class object
                sub class_terminate
                    result=3
                end
            end
            set instance=new object
            set instance=nothing""").is_integer(3)
