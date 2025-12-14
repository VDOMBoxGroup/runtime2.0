
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestStringsRoutines(VScriptTestCase):

    def test_len_function(self):
        assert self.evaluate("""len("abc")""").is_integer(3)

    def test_strcomp_function(self):
        assert self.evaluate("""strcomp("abc", "abc")""").is_integer(0)
        assert self.evaluate("""strcomp("abc", "ABC", vtextcompare)""").is_integer(0)
        assert self.evaluate("""strcomp("abc", "cde")""").is_integer(-1)
        assert self.evaluate("""strcomp("cde", "abc")""").is_integer(1)
        with raises(errors.invalid_procedure_call):
            self.execute("""strcomp("abc", "abc", 123)""")
        with raises(errors.type_mismatch):
            self.execute("""strcomp("abc", "abc", "abc")""")

    def test_replace_function(self):
        assert self.evaluate("""replace("abcdef", "cd", "dc")""").is_string("abdcef")
        assert self.evaluate("""replace("abcdef", "cd", "dc", 3)""").is_string("dcef")
        assert self.evaluate("""replace("abcdefabcdef", "cd", "dc", 1, 1)""").is_string("abdcefabcdef")
        assert self.evaluate("""replace("abcdef", "CD", "dc", 1, -1, vtextcompare)""").is_string("abdcef")
        assert self.evaluate("""replace("abcdefabcdef", "cd", "dc", 1, 0)""").is_string("abcdefabcdef")
        with raises(errors.invalid_procedure_call):
            self.execute("""replace("abcdef", "CD", "dc", -123, -1, vtextcompare)""")
        with raises(errors.invalid_procedure_call):
            self.execute("""replace("abcdef", "CD", "dc", 1, -123, vtextcompare)""")
        with raises(errors.invalid_procedure_call):
            self.execute("""replace("abcdef", "CD", "dc", 1, -1, 123)""")

    def test_split_function(self):
        assert self.evaluate("""split("abc def abc")""").is_array(lambda items: \
            items[0].is_string("abc") and items[1].is_string("def") \
            and items[2].is_string("abc"), length=3)
        assert self.evaluate("""split("abcsepdefsepabc", "sep")""").is_array(lambda items: \
            items[0].is_string("abc") and items[1].is_string("def") \
            and items[2].is_string("abc"), length=3)
        assert self.evaluate("""split("abcsepdefsepabc", "sep", 2)""").is_array(lambda items: \
            items[0].is_string("abc") and items[1].is_string("defsepabc"), length=2)
        assert self.evaluate("""split("abcSEPdefSEPabc", "sep", 2, vtextcompare)""").is_array(lambda items: \
            items[0].is_string("abc") and items[1].is_string("defSEPabc"), length=2)
        assert self.evaluate("""split("abc def abc", " ", 0)""").is_array(length=0)
        assert self.evaluate("""split("abc def abc", " ", 1)""").is_array(lambda items: \
            items[0].is_string("abc def abc"), length=1)
        with raises(errors.invalid_procedure_call):
            self.execute("""split("abc|def", "|", -123)""")
        with raises(errors.invalid_procedure_call):
            self.execute("""split("abc|def", "|", -1, 123)""")
        with raises(errors.type_mismatch):
            self.execute("""split("abcsepdefsepabc", "sep", "abc")""")
        with raises(errors.type_mismatch):
            self.execute("""split("abcsepdefsepabc", "sep", -1, "abc")""")

    def test_lcase_function(self):
        assert self.evaluate("""lcase("ABC")""").is_string("abc")

    def test_ucase_function(self):
        assert self.evaluate("""ucase("abc")""").is_string("ABC")

    def test_instr_function(self):
        assert self.evaluate("""instr("abcdefabc", "def")""").is_integer(4)
        assert self.evaluate("""instr(5, "abcdefabc", "def")""").is_integer(0)
        assert self.evaluate("""instr(1, "abcDEFabc", "def", vtextcompare)""").is_integer(4)
        with raises(errors.invalid_procedure_call):
            self.execute("""instr(-123, "abcDEFabc", "def", vtextcompare)""")
        with raises(errors.invalid_procedure_call):
            self.execute("""instr(1, "abcDEFabc", "def", 123)""")
        with raises(errors.type_mismatch):
            self.execute("""instr("abc", "abcDEFabc", "def", vtextcompare)""")
        with raises(errors.type_mismatch):
            self.execute("""instr(1, "abcDEFabc", "def", "abc")""")

    def test_instrrev_function(self):
        assert self.evaluate("""instrrev("abcdefabc", "def")""").is_integer(4)
        assert self.evaluate("""instrrev("abcdefabc", "def", 5)""").is_integer(0)
        assert self.evaluate("""instrrev("abcDEFabc", "def", -1, vtextcompare)""").is_integer(4)
        with raises(errors.invalid_procedure_call):
            self.execute("""instrrev("abcDEFabc", "def", -123, vtextcompare)""")
        with raises(errors.invalid_procedure_call):
            self.execute("""instrrev("abcDEFabc", "def", -1, 123)""")
        with raises(errors.type_mismatch):
            self.execute("""instrrev("abcDEFabc", "def", "abc", vtextcompare)""")
        with raises(errors.type_mismatch):
            self.execute("""instrrev("abcDEFabc", "def", -1, "abc")""")

    def test_left_function(self):
        assert self.evaluate("""left("abcdef", 3)""").is_string("abc")
        with raises(errors.invalid_procedure_call):
            self.execute("""left("abcdef", -123)""")
        with raises(errors.type_mismatch):
            self.execute("""left("abcdef", "abc")""")

    def test_right_function(self):
        assert self.evaluate("""right("abcdef", 3)""").is_string("def")
        with raises(errors.invalid_procedure_call):
            self.execute("""right("abcdef", -123)""")
        with raises(errors.type_mismatch):
            self.execute("""right("abcdef", "abc")""")

    def test_mid_function(self):
        assert self.evaluate("""mid("abcdefabc", 4)""").is_string("defabc")
        assert self.evaluate("""mid("abcdefabc", 4, 3)""").is_string("def")
        assert self.evaluate("""mid("abcdefabc", 123)""").is_string("")
        assert self.evaluate("""mid("abcdefabc", 4, 0)""").is_string("")
        with raises(errors.invalid_procedure_call):
            self.execute("""mid("abcdefabc", -123, 3)""")
        with raises(errors.invalid_procedure_call):
            self.execute("""mid("abcdefabc", 4, -123)""")
        with raises(errors.type_mismatch):
            self.execute("""mid("abcdefabc", "abc", 3)""")
        with raises(errors.type_mismatch):
            self.execute("""mid("abcdefabc", 4, "abc")""")

    def test_trim_function(self):
        assert self.evaluate("""trim(" abc ")""").is_string("abc")

    def test_ltrim_function(self):
        assert self.evaluate("""ltrim(" abc ")""").is_string("abc ")

    def test_rtrim_function(self):
        assert self.evaluate("""rtrim(" abc ")""").is_string(" abc")

    def test_space_function(self):
        assert self.evaluate("""space(3)""").is_string("   ")
        with raises(errors.invalid_procedure_call):
            self.execute("""space(-123)""")
        with raises(errors.type_mismatch):
            self.execute("""space("abc")""")

    def test_string_function(self):
        assert self.evaluate("""string(3, "*")""").is_string("***")
        with raises(errors.invalid_procedure_call):
            self.execute("""string(-123, "*")""")
        with raises(errors.type_mismatch):
            self.execute("""string("abc", "*")""")

    def test_strreverse_function(self):
        assert self.evaluate("""strreverse("abc")""").is_string("cba")
