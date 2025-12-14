
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestParameters(VScriptTestCase):

    def test_parameters_by_default(self):
        assert self.execute("""
            result=1
            sub mysub(parameter)
                parameter=3
            end
            mysub(result)
            """).is_integer(3)

    def test_parameters_by_value(self):
        assert self.execute("""
            result=1
            sub mysub(byval parameter)
                parameter=3
            end
            mysub(result)
            """).is_integer(1)

    def test_parameters_by_reference(self):
        assert self.execute("""
            result=1
            sub mysub(byref parameter)
                parameter=3
            end
            mysub(result)
            """).is_integer(3)
        