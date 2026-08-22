"""VAILS — VScript Tier 4, compléments :
  #1 appel `f()` à zéro argument (vcall0) — invoque une fonction-valeur, compat préservée.
  #3 capture « en avant » (local Dim'é après la lambda) — déjà supportée par l'architecture.

Cf. essentials.vcall0, source.vname.__str__, source.vlambda.
"""

from ...testing import VScriptTestCase


class TestZeroArgCall(VScriptTestCase):

    def test_lambda_zero_arg(self):
        assert self.execute(
            "set f = Function() Return 7 End Function\n"
            "result = f()").is_integer(7)

    def test_addressof_zero_arg(self):
        # `AddressOf` d'une fonction nommée 0-arg, appelée via `g()`.
        assert self.execute(
            "Function ping()\n"
            "  Return 99\n"
            "End Function\n"
            "set g = AddressOf ping\n"
            "result = g()").is_integer(99)

    def test_zero_arg_inside_expression(self):
        assert self.execute(
            "set f = Function() Return 20 End Function\n"
            "result = f() + f() + 2").is_integer(42)

    def test_non_callable_paren_is_noop(self):
        # Compat : `x()` sur une valeur NON appelable reste `x` (n'invoque rien, ne lève pas).
        assert self.execute(
            "dim x\n"
            "x = 5\n"
            "result = x()").is_integer(5)

    def test_named_zero_arg_function_still_works(self):
        # Non-régression : appel classique d'une fonction nommée 0-arg.
        assert self.execute(
            "Function answer()\n"
            "  Return 42\n"
            "End Function\n"
            "result = answer()").is_integer(42)


class TestForwardCapture(VScriptTestCase):

    def test_capture_local_declared_after_lambda(self):
        # `total` est Dim'é APRÈS la lambda mais capturé : collect_names voit tous les
        # locaux de la procédure avant le scope, donc le seeding de capture les inclut.
        assert self.execute(
            "Function build()\n"
            "  set build = Function(x) Return x + total End Function\n"
            "  dim total\n"
            "  total = 1000\n"
            "End Function\n"
            "set f = build()\n"
            "result = f(5)").is_integer(1005)
