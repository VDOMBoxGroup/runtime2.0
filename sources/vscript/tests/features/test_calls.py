
from ...testing import VScriptTestCase


class TestCalls(VScriptTestCase):

    def test_invoke_sub(self):
        assert self.execute("""
            sub mysub
                result=3
            end
            mysub""").is_integer(3)

    def test_invoke_sub_with_arguments(self):
        assert self.execute("""
            sub mysub(x, y)
                result=x+y
            end
            mysub(1, 2)""").is_integer(3)

    def test_invoke_sub_with_clear_arguments(self):
        assert self.execute("""
            sub mysub(x, y)
                result=x+y
            end
            mysub 1, 2""").is_integer(3)

    def test_invoke_function(self):
        assert self.execute("""
            function myfunction
                result=3
            end
            myfunction""").is_integer(3)

    def test_invoke_sub_with_arguments2(self):
        assert self.execute("""
            function myfunction(x, y)
                result=x+y
            end
            myfunction(1, 2)""").is_integer(3)

    def test_invoke_sub_with_clear_arguments2(self):
        assert self.execute("""
            function myfunction(x, y)
                result=x+y
            end
            myfunction 1, 2""").is_integer(3)
