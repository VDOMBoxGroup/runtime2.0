
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestRandomizeStatement(VScriptTestCase):

    def test_randomize_statement(self):
        assert self.execute("randomize").is_empty

    def test_randomize_with_argument_statement(self):
        assert self.execute("randomize 3").is_empty
        