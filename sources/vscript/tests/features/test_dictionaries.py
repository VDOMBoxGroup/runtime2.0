
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestDictionaries(VScriptTestCase):

    def test_dictionary_enumeration(self):
        assert self.execute("""
            mydictionary=dictionary(1, "a", 2, "b", 3, "c")
            for each item in mydictionary
                result=result+item
            next""").is_integer(6)
