
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestPropertyStatement(VScriptTestCase):

    def test_property_get_statement(self):
        assert self.execute("""
            class object
                property get myproperty
                    myproperty=3
                end
            end
            set instance=new object
            result=instance.myproperty""").is_integer(3)
        assert self.execute("""
            class object
                property get myproperty
                    myproperty=3
                end property
            end class
            set instance=new object
            result=instance.myproperty""").is_integer(3)

    def test_property_let_statement(self):
        assert self.execute("""
            class object
                property let myproperty(value)
                    result=value
                end
            end
            set instance=new object
            instance.myproperty=3""").is_integer(3)
        assert self.execute("""
            class object
                property let myproperty(value)
                    result=value
                end property
            end class
            set instance=new object
            instance.myproperty=3""").is_integer(3)

    def test_property_set_statement(self):
        assert self.execute("""
            class object
                property set myproperty(value)
                    set result=value
                end
            end
            set instance=new object
            set instance.myproperty=nothing""").is_nothing
        assert self.execute("""
            class object
                property set myproperty(value)
                    set result=value
                end property
            end class
            set instance=new object
            set instance.myproperty=nothing""").is_nothing

    def test_default_property_get_statement(self):
        assert self.execute("""
            class object
                default property get myproperty
                    myproperty=3
                end
            end
            set instance=new object
            result=instance""").is_integer(3)
        assert self.execute("""
            class object
                default property get myproperty
                    myproperty=3
                end property
            end class
            set instance=new object
            result=instance""").is_integer(3)
        
class TestWrongPropertyStatement(VScriptTestCase):

    def test_default_property_let_statement(self):
        with raises(errors.syntax_error):
            assert self.execute("""
                class object
                    default property let myproperty
                    end
                end""")
        with raises(errors.syntax_error):
            assert self.execute("""
                class object
                    default property let myproperty
                    end property
                end class""")

    def test_default_property_set_statement(self):
        with raises(errors.syntax_error):
            assert self.execute("""
                class object
                    default property set myproperty
                    end
                end""")
        with raises(errors.syntax_error):
            assert self.execute("""
                class object
                    default property set myproperty
                    end property
                end class""")
