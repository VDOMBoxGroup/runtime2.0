
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestCreation(VScriptTestCase):

    def test_integer_creation(self):
        assert integer(123).is_integer(123)

    def test_double_creation(self):
        assert double(123.456).is_double(123.456)

    def test_date_creation(self):
        assert date(0.0).is_date(0.0)
        assert date("02.05.1900 02:57:18").is_date(1900, 5, 2, 2, 57, 18)

    def test_string_creation(self):
        assert string(u"abc").is_string("abc")

    def test_boolean_creation(self):
        assert boolean(true).is_boolean(true)
        assert boolean(false).is_boolean(false)
