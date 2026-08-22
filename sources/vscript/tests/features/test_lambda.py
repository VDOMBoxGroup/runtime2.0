"""VAILS — modernisation VScript (Tier 4) : lambdas inline + closures.

`Function(args) ... End Function` en position expression. Hissée en def Python
imbriqué (closures lecture+écriture via boîtes variant), valeur = `vfuncref(...)`.
Cf. TODO/vscript-modern.md, vscript/source.py::vlambda. Ajout purement additif,
0 conflit LALR (vérifié).
"""

from ...testing import VScriptTestCase


class TestLambdaBasics(VScriptTestCase):

    def test_store_and_call(self):
        assert self.execute(
            "set f = Function(x) Return x * x End Function\n"
            "result = f(5)").is_integer(25)

    def test_no_args_call(self):
        # `f()` (zéro argument) invoque désormais la fonction-valeur (vcall0).
        assert self.execute(
            "set f = Function() Return 42 End Function\n"
            "result = f()").is_integer(42)

    def test_two_args(self):
        assert self.execute(
            "set g = Function(a, b) Return a + b End Function\n"
            "result = g(20, 22)").is_integer(42)

    def test_multi_statement_body(self):
        assert self.execute(
            "set f = Function(x)\n"
            "  dim t\n"
            "  t = x * 2\n"
            "  Return t + 1\n"
            "End Function\n"
            "result = f(10)").is_integer(21)

    def test_string_body(self):
        assert self.execute(
            'set greet = Function(name) Return "hi " & name End Function\n'
            'result = greet("sam")').is_string(u"hi sam")


class TestLambdaClosure(VScriptTestCase):

    def test_capture_module_global(self):
        # `base` est un global de module capturé en lecture par la lambda.
        assert self.execute(
            "base = 100\n"
            "set f = Function(x) Return x + base End Function\n"
            "result = f(5)").is_integer(105)

    def test_closure_over_procedure_local(self):
        # Le vrai test : `n` est un param de make_adder, capturé par le def imbriqué.
        assert self.execute(
            "Function make_adder(n)\n"
            "  set make_adder = Function(x) Return x + n End Function\n"
            "End Function\n"
            "set add10 = make_adder(10)\n"
            "result = add10(5)").is_integer(15)

    def test_distinct_closures_keep_their_own_capture(self):
        assert self.execute(
            "Function make_adder(n)\n"
            "  set make_adder = Function(x) Return x + n End Function\n"
            "End Function\n"
            "set a2 = make_adder(2)\n"
            "set a100 = make_adder(100)\n"
            "result = a2(1) + a100(1)").is_integer(104)  # 3 + 101

    def test_mutable_closure_state_persists(self):
        # Capture EN ÉCRITURE : la boîte variant `c` est mutée à travers les appels
        # (état persistant, upvalue mutable à la Lua) — pas seulement de la lecture.
        assert self.execute(
            "Function counter()\n"
            "  dim c\n"
            "  c = 0\n"
            "  set counter = Function(inc)\n"
            "    c = c + inc\n"
            "    Return c\n"
            "  End Function\n"
            "End Function\n"
            "set f = counter()\n"
            "dim a, b\n"
            "a = f(5)\n"           # c : 0 -> 5
            "b = f(3)\n"           # c : 5 -> 8
            "result = a * 100 + b").is_integer(508)


class TestLambdaHigherOrder(VScriptTestCase):

    def test_pass_lambda_as_argument(self):
        # apply_twice reçoit la lambda et l'invoque deux fois.
        assert self.execute(
            "Function apply_twice(f, x)\n"
            "  apply_twice = f(f(x))\n"
            "End Function\n"
            "set dbl = Function(x) Return x * 2 End Function\n"
            "result = apply_twice(dbl, 3)").is_integer(12)


class TestLambdaNoRegression(VScriptTestCase):

    def test_named_function_still_works(self):
        assert self.execute(
            "Function add(a, b)\n"
            "  Return a + b\n"
            "End Function\n"
            "result = add(40, 2)").is_integer(42)

    def test_addressof_still_works(self):
        assert self.execute(
            "Function dbl(x)\n"
            "  Return x * 2\n"
            "End Function\n"
            "set f = AddressOf dbl\n"
            "result = f(21)").is_integer(42)
