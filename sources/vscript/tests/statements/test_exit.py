
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestExitStatement(VScriptTestCase):

    def test_exit_function_statement(self):
        assert self.execute("""
            function myfunction
                exit function
                myfunction=3
            end
            result=myfunction""").is_empty

    def test_exit_sub_statement(self):
        assert self.execute("""
            sub mysub
                exit sub
                result=3
            end
            mysub""").is_empty

    def test_exit_property_get_statement(self):
        assert self.execute("""
            class object
                property get myproperty
                    exit property
                    myproperty=3
                end
            end
            set instance=new object
            result=instance.myproperty""").is_empty

    def test_exit_property_let_statement(self):
        assert self.execute("""
            class object
                property let myproperty(value)
                    exit property
                    result=value
                end
            end
            set instance=new object
            instance.myproperty=3""").is_empty

    def test_exit_property_set_statement(self):
        assert self.execute("""
            class object
                property set myproperty(value)
                    exit property
                    set result=value
                end
            end
            set instance=new object
            set instance.myproperty=nothing""").is_empty

    def test_exit_do_loop_statement(self):
        assert self.execute("""
            do
                exit do
                result=3
            loop""").is_empty

    def test_exit_do_while_loop_statement(self):
        assert self.execute("""
            do while true
                exit do
                result=3
            loop""").is_empty

    def test_exit_do_while_loop_statement(self):
        assert self.execute("""
            do until false
                exit do
                result=3
            loop""").is_empty

    def test_exit_do_loop_while_statement(self):
        assert self.execute("""
            do
                exit do
                result=3
            loop while true""").is_empty

    def test_exit_do_loop_while_statement(self):
        assert self.execute("""
            do
                exit do
                result=3
            loop until false""").is_empty

    def test_exit_for_each_statement(self):
        assert self.execute("""
            for each item in array(1, 2, 3)
                exit for
                result=3
            next""").is_empty

    def test_exit_for_to_statement(self):
        assert self.execute("""
            for index=1 to 3
                exit for
                result=3
            next""").is_empty

class TestWrongExitStatement(VScriptTestCase):

    def test_exit_function_statement(self):
        with raises(errors.expected_function):
            self.execute("exit function")
        with raises(errors.expected_function):
            self.execute("""
                sub mysub
                    exit function
                end
                mysub""")

    def test_exit_sub_statement(self):
        with raises(errors.expected_sub):
            self.execute("exit sub")
        with raises(errors.expected_sub):
            self.execute("""
                function myfunction
                    exit sub
                end
                myfunction""")

    def test_exit_property_statement(self):
        with raises(errors.expected_property):
            self.execute("exit property")
        with raises(errors.expected_property):
            self.execute("""
                sub mysub
                    exit property
                end
                mysub""")

    def test_exit_do_statement(self):
        with raises(errors.invalid_exit_statement):
            self.execute("exit do")
        with raises(errors.invalid_exit_statement):
            self.execute("""
                for index=1 to 3
                    exit do
                next""")

    def test_exit_for_statement(self):
        with raises(errors.invalid_exit_statement):
            self.execute("exit for")
        with raises(errors.invalid_exit_statement):
            self.execute("""
                do
                    exit for
                loop""")
