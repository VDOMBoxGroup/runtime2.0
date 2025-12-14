
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestThrowStatement(VScriptTestCase):

    def test_throw_statement(self):
        with raises(errors.division_by_zero):
            assert self.execute("""
                throw divisionbyzero""")

    def test_throw_statement_in_catch(self):
        with raises(errors.division_by_zero):
            assert self.execute("""
                try
                    print 1/0
                catch divisionbyzero
                    throw
                end""")
