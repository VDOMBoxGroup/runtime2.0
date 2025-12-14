
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestConstStatement(VScriptTestCase):

    def test_constant_statement(self):
        assert self.execute("""
            const constant=3
            result=constant""").is_integer(3)

    def test_constant_assigment_statement(self):
        with raises(errors.illegal_assigment):
            self.execute("""
                const constant=3
                constant=1""")
