
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestFunctionStatement(VScriptTestCase):

    def test_function_statement(self):
        assert self.execute("""
            function myfunction
                myfunction=3
            end
            result=myfunction""").is_integer(3)
        assert self.execute("""
            function myfunction
                myfunction=3
            end function
            result=myfunction""").is_integer(3)

    def test_function_with_arguments_statement(self):
        assert self.execute("""
            function myfunction(x, y)
                myfunction=x+y
            end
            result=myfunction(1, 2)""").is_integer(3)
        assert self.execute("""
            function myfunction(x, y)
                myfunction=x+y
            end function
            result=myfunction(1, 2)""").is_integer(3)

    def test_class_function_statement(self):
        assert self.execute("""
            class object
                function myclassfunction
                    myclassfunction=3
                end
            end
            set instance=new object
            result=instance.myclassfunction""").is_integer(3)
        assert self.execute("""
            class object
                function myclassfunction
                    myclassfunction=3
                end function
            end class
            set instance=new object
            result=instance.myclassfunction""").is_integer(3)

    def test_class_function_with_arguments_statement(self):
        assert self.execute("""
            class object
                function myclassfunction(x, y)
                    myclassfunction=x+y
                end
            end
            set instance=new object
            result=instance.myclassfunction(1, 2)""").is_integer(3)
        assert self.execute("""
            class object
                function myclassfunction(x, y)
                    myclassfunction=x+y
                end function
            end class
            set instance=new object
            result=instance.myclassfunction(1, 2)""").is_integer(3)

    def test_class_default_function_statement(self):
        assert self.execute("""
            class object
                default function myclassfunction
                    myclassfunction=3
                end
            end
            set instance=new object
            result=instance""").is_integer(3)
        assert self.execute("""
            class object
                default function myclassfunction
                    myclassfunction=3
                end function
            end class
            set instance=new object
            result=instance""").is_integer(3)
        