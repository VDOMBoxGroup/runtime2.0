
from ...testing import raises, VScriptTestCase
from ... import errors


class TestArrays(VScriptTestCase):

    def test_static_array_enumeration(self):
        assert self.execute("""
            dim myarray(2)
            myarray(0)=1
            myarray(1)=2
            myarray(2)=3
            result=len(myarray)
            for each item in myarray
                result=result+item
            next""").is_integer(9)

    def test_static_multidimensional_array_enumeration(self):
        assert self.execute("""
            dim myarray(1, 1, 1)
            myarray(0, 0, 0)=1
            myarray(0, 0, 1)=2
            myarray(0, 1, 0)=3
            myarray(0, 1, 1)=4
            myarray(1, 0, 0)=5
            myarray(1, 0, 1)=6
            myarray(1, 1, 0)=7
            myarray(1, 1, 1)=8
            for index1=0 to 1
                for index2=0 to 1
                    for index3=0 to 1
                        result=result+myarray(index1, index2, index3)
                    next
                next
            next""").is_integer(36)

    def test_static_array_ubound(self):
        self.evaluate("dim a(0)", let="ubound(a)").is_integer(0)
        self.evaluate("dim a(3)", let="ubound(a)").is_integer(3)

    def test_dynamic_array_enumeration(self):
        assert self.execute("""
            for each item in array(1, 2, 3)
                result=result+item
            next""").is_integer(6)

    def test_dynamic_array_ubound(self):
        # An empty array bounds 0 to -1, as in VBScript. UBound used to raise
        # subscript_out_of_range on it, which made every caller that could get
        # no rows wrap the call in a Try just to learn that a list was empty.
        # LBound still answers 0, so `for i = 0 to ubound(a)` runs no turn.
        assert self.evaluate("a=array()", let="ubound(a)").is_integer(-1)
        assert self.evaluate("a=array()", let="lbound(a)").is_integer(0)
        assert self.evaluate("dim a()", let="ubound(a)").is_integer(-1)
        # The three lines below carried no assert, so nothing checked them and
        # the last one expected 3 for a three-element array. UBound is the
        # highest index, not the count.
        assert self.evaluate("a=array(1)", let="ubound(a)").is_integer(0)
        assert self.evaluate("a=array(1, 2, 3)", let="ubound(a)").is_integer(2)
