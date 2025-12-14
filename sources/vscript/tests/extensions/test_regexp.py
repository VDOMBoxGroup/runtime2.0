
from ...testing import VScriptTestCase
from ...subtypes import true, false


class TestRegExpExtension(VScriptTestCase):

    def test_regexp_ignorecase(self):
        assert self.execute("""
            set re=new regexp
            result=re.ignorecase""").is_boolean(false)
        assert self.execute("""
            set re=new regexp
            re.ignorecase=true
            result=re.ignorecase""").is_boolean(true)

    def test_regexp_global(self):
        assert self.execute("""
            set re=new regexp
            result=re.global""").is_boolean(false)
        assert self.execute("""
            set re=new regexp
            re.global=true
            result=re.global""").is_boolean(true)

    def test_regexp_pattern(self):
        assert self.execute("""
            set re=new regexp
            result=re.pattern""").is_string(u"")
        assert self.execute("""
            set re=new regexp
            re.pattern="abc"
            result=re.pattern""").is_string(u"abc")

    def test_regexp_replace(self):
        assert self.execute("""
            set re=new regexp
            re.pattern="abc"
            result=re.replace("def klm uvw", "def")""").is_string(u"def klm uvw")
        assert self.execute("""
            set re=new regexp
            re.pattern="abc"
            result=re.replace("abc def abc", "def")""").is_string(u"def def abc")
        assert self.execute("""
            set re=new regexp
            re.global=false
            re.pattern="abc"
            result=re.replace("abc def abc", "def")""").is_string(u"def def abc")
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="abc"
            result=re.replace("abc def abc", "def")""").is_string(u"def def def")
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.ignorecase=true
            re.pattern="abc"
            result=re.replace("abc ABC abc", "def")""").is_string(u"def def def")

    def test_regexp_execute(self):
        assert self.execute("""
            set re=new regexp
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm uvwdef klm defuvwklm klm")
            for each match in matches
                result=result&match.value
            next""").is_empty
        assert self.execute("""
            set re=new regexp
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcdef klm defabcklm klm")
            for each match in matches
                result=result&match.value
            next""").is_string(u"abcdef")
        assert self.execute("""
            set re=new regexp
            re.global=false
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcdef klm defabcklm klm")
            for each match in matches
                result=result&match.value
            next""").is_string(u"abcdef")
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcdef klm defabcklm klm")
            for each match in matches
                result=result&match.value
            next""").is_string(u"abcdefabcklm")
        assert self.execute("""
            set re=new regexp
            re.ignorecase=true
            re.global=true
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcdef klm defABCklm klm")
            for each match in matches
                result=result&match.value
            next""").is_string(u"abcdefABCklm")

    def test_regexp_test(self):
        assert self.execute("""
            set re=new regexp
            re.pattern="abc"
            result=re.test("adefbklmc")""").is_boolean(false)
        assert self.execute("""
            set re=new regexp
            re.pattern="abc"
            result=re.test("defabcklm")""").is_boolean(true)
        assert self.execute("""
            set re=new regexp
            re.global=false
            re.pattern="abc"
            result=re.test("defabcklm")""").is_boolean(true)
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="abc"
            result=re.test("defabcklm")""").is_boolean(true)
        assert self.execute("""
            set re=new regexp
            re.ignorecase=true
            re.global=true
            re.pattern="abc"
            result=re.test("defABCklm")""").is_boolean(true)

    def test_matches_count(self):
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcd klm defabcklm klm")
            result=matches.count""").is_integer(2)

    def test_matches_item(self):
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcd klm defabcklm klm")
            set result=matches.item(1)""").is_generic

    def test_match_firstindex(self):
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcd klm defabcklm klm")
            set match=matches.item(1)
            result=match.firstindex""").is_integer(16)
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="(abc)([a-z]+)"
            set matches=re.execute("klm abcd klm defabcklm klm")
            set match=matches.item(1)
            result=match.firstindex(2)""").is_integer(19)

    def test_match_length(self):
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcd klm defabcklm klm")
            set match=matches.item(1)
            result=match.length""").is_integer(6)
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="(abc)([a-z]+)"
            set matches=re.execute("klm abcd klm defabcklm klm")
            set match=matches.item(1)
            result=match.length(2)""").is_integer(3)

    def test_match_value(self):
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="abc[a-z]+"
            set matches=re.execute("klm abcd klm defabcklm klm")
            set match=matches.item(1)
            result=match.value""").is_string(u"abcklm")
        assert self.execute("""
            set re=new regexp
            re.global=true
            re.pattern="(abc)([a-z]+)"
            set matches=re.execute("klm abcd klm defabcklm klm")
            set match=matches.item(1)
            result=match.value(2)""").is_string(u"klm")
