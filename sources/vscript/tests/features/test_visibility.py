
from ...testing import raises, VScriptTestCase
from ... import errors


# Classe de référence : champ privé encapsulé par une propriété get/let avec
# validation, + un champ public explicite.
ACCOUNT = """
    class account
        private m_balance
        public owner
        public property get balance
            balance = m_balance
        end property
        public property let balance(v)
            if v < 0 then v = 0
            m_balance = v
        end property
    end
"""


class TestFieldVisibility(VScriptTestCase):

    # ── champ privé : accessible en interne via la propriété ─────────
    def test_private_via_property(self):
        assert self.execute(ACCOUNT + """
            set a = new account
            a.balance = 100
            result = a.balance""").is_integer(100)

    def test_private_property_validates(self):
        assert self.execute(ACCOUNT + """
            set a = new account
            a.balance = 0 - 50
            result = a.balance""").is_integer(0)

    # ── champ privé : INACCESSIBLE de l'extérieur (lecture + écriture) ─
    def test_private_external_read_blocked(self):
        with raises(errors.object_has_no_property):
            self.execute(ACCOUNT + """
                set a = new account
                a.balance = 100
                result = a.m_balance""")

    def test_private_external_write_blocked(self):
        with raises(errors.object_has_no_property):
            self.execute(ACCOUNT + """
                set a = new account
                a.m_balance = 999""")

    # ── champ public : accessible en lecture/écriture ────────────────
    def test_public_field_readwrite(self):
        assert self.execute(ACCOUNT + """
            set a = new account
            a.owner = "Alice"
            result = a.owner""").is_string(u"Alice")

    # ── `Dim` reste public par défaut (rétro-compatibilité) ──────────
    def test_dim_field_still_public(self):
        assert self.execute("""
            class point
                dim x, y
            end
            set p = new point
            p.x = 7
            result = p.x""").is_integer(7)

    # ── plusieurs champs privés sur une même ligne ───────────────────
    def test_multiple_private_on_one_line(self):
        with raises(errors.object_has_no_property):
            self.execute("""
                class box
                    private a, b, c
                end
                set x = new box
                result = x.b""")

    # ── accès interne entre méthodes (champ privé partagé) ───────────
    def test_private_shared_across_methods(self):
        assert self.execute("""
            class counter
                private m_n
                sub class_initialize
                    m_n = 0
                end sub
                public sub bump
                    m_n = m_n + 1
                end sub
                public property get value
                    value = m_n
                end property
            end
            set c = new counter
            c.bump
            c.bump
            result = c.value""").is_integer(2)


class TestPrivateInheritance(VScriptTestCase):

    BASE = """
        class base
            private m_secret
            public property let secret(v)
                m_secret = v
            end property
            public property get secret
                secret = m_secret
            end property
        end
        class derived
            inherits base
            private m_own
        end
    """

    def test_inherited_public_property(self):
        assert self.execute(self.BASE + """
            set d = new derived
            d.secret = 42
            result = d.secret""").is_integer(42)

    def test_parent_private_hidden_on_child(self):
        with raises(errors.object_has_no_property):
            self.execute(self.BASE + """
                set d = new derived
                result = d.m_secret""")

    def test_child_private_hidden(self):
        with raises(errors.object_has_no_property):
            self.execute(self.BASE + """
                set d = new derived
                result = d.m_own""")
