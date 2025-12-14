
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestInheritsStatement(VScriptTestCase):

    def test_inherits(self):
        assert self.execute("""
            class ancestor
                function mark
                    result=3
                end
            end
            class descendant
                inherits ancestor
            end
            set instance=new descendant
            instance.mark""").is_integer(3)

