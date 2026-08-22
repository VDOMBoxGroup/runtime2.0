
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
        
class TestPropertyPairs(VScriptTestCase):
    """Combinaisons d'accesseurs sur un même nom (get+let, get+set, let+set).
    Régression : le contrôle `sum/3` rejetait toute paire (cf. source.vproperty)."""

    def test_get_let_pair(self):
        assert self.execute("""
            class account
                dim m_balance
                public property get balance
                    balance = m_balance
                end property
                public property let balance(v)
                    m_balance = v
                end property
            end
            set a = new account
            a.balance = 42
            result = a.balance""").is_integer(42)

    def test_let_validates(self):
        # L'intérêt d'une propriété vs un champ public : valider dans le Let.
        assert self.execute("""
            class account
                dim m_balance
                public property get balance
                    balance = m_balance
                end property
                public property let balance(v)
                    if v < 0 then v = 0
                    m_balance = v
                end property
            end
            set a = new account
            a.balance = 0 - 50
            result = a.balance""").is_integer(0)

    def test_get_set_pair(self):
        assert self.execute("""
            class box
                dim m_item
                public property get item
                    set item = m_item
                end property
                public property set item(o)
                    set m_item = o
                end property
            end
            class thing
            end
            set b = new box
            set b.item = new thing
            set result = b.item""").is_generic

    def test_indexed_get_let_pair(self):
        # Cohérence des arguments « indices » : get(i) / let(i, v).
        assert self.execute("""
            class table
                dim m_store
                sub class_initialize
                    set m_store = dictionary()
                end sub
                public property get cell(i)
                    cell = m_store(i)
                end property
                public property let cell(i, v)
                    m_store(i) = v
                end property
            end
            set t = new table
            t.cell(1) = 99
            result = t.cell(1)""").is_integer(99)

    def test_inconsistent_arguments_still_rejected(self):
        # get(0 idx) incompatible avec let(2 idx + valeur) -> toujours une erreur.
        with raises(errors.inconsistent_arguments_number):
            self.execute("""
                class bad
                    public property get p
                        p = 1
                    end property
                    public property let p(i, j, v)
                        result = v
                    end property
                end
                set x = new bad""")


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
