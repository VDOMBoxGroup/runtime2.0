
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestSubStatement(VScriptTestCase):

    def test_sub_statement(self):
        assert self.execute("""
            sub mysub
                result=3
            end
            mysub""").is_integer(3)
        assert self.execute("""
            sub mysub
                result=3
            end sub
            mysub""").is_integer(3)

    def test_sub_with_arguments_statement(self):
        assert self.execute("""
            sub mysub(x, y)
                result=x+y
            end
            mysub(1, 2)""").is_integer(3)
        assert self.execute("""
            sub mysub(x, y)
                result=x+y
            end sub
            mysub(1, 2)""").is_integer(3)

    def test_class_sub_statement(self):
        assert self.execute("""
            class object
                sub myclasssub
                    result=3
                end
            end
            set instance=new object
            instance.myclasssub""").is_integer(3)
        assert self.execute("""
            class object
                sub myclasssub
                    result=3
                end sub
            end class
            set instance=new object
            instance.myclasssub""").is_integer(3)

    def test_class_sub_with_arguments_statement(self):
        assert self.execute("""
            class object
                sub myclasssub(x, y)
                    result=x+y
                end
            end
            set instance=new object
            instance.myclasssub(1, 2)""").is_integer(3)
        assert self.execute("""
            class object
                sub myclasssub(x, y)
                    result=x+y
                end sub
            end class
            set instance=new object
            instance.myclasssub(1, 2)""").is_integer(3)

class TestWrongSubStatement(VScriptTestCase):

    def test_class_default_function_statement(self):
        with raises(errors.syntax_error):
            assert self.execute("""
                class object
                    default sub myclasssub
                    end
                end""")
        with raises(errors.syntax_error):
            assert self.execute("""
                class object
                    default sub myclasssub
                    end sub
                end class""")
        