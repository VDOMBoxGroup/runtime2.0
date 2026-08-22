"""VAILS — court-circuit logique de And/Or (amélioration VScript).

En VBScript classique les deux opérandes de And/Or sont toujours évalués. VScript
court-circuite : la droite n'est pas évaluée quand la gauche détermine déjà le
résultat (gauche integer/double valant 0 pour And, -1 pour Or). Null/booléens/
chaînes restent en évaluation complète (logique à 3 valeurs préservée — cf.
subtypes/*/test_logic).
"""

from ...testing import VScriptTestCase, raises
from ... import errors


class TestShortCircuit(VScriptTestCase):

    def test_and_skips_right(self):
        # `1 \ 0` lèverait division_by_zero s'il était évalué
        assert self.evaluate("0 and (1 \\ 0)").is_integer(0)

    def test_and_evaluates_right_when_left_nonzero(self):
        with raises(errors.division_by_zero):
            self.evaluate("1 and (1 \\ 0)")

    def test_or_skips_right(self):
        assert self.evaluate("-1 or (1 \\ 0)").is_integer(-1)

    def test_or_evaluates_right_when_left_not_minus_one(self):
        with raises(errors.division_by_zero):
            self.evaluate("0 or (1 \\ 0)")

    def test_and_side_effect_skipped(self):
        assert self.execute(
            "dim hit\nhit = 0\n"
            "function bump()\n hit = hit + 1\n bump = 1\nend function\n"
            "dim x\nx = 0 and bump()\n"
            "result = hit").is_integer(0)

    def test_and_side_effect_runs_when_left_nonzero(self):
        assert self.execute(
            "dim hit\nhit = 0\n"
            "function bump()\n hit = hit + 1\n bump = 1\nend function\n"
            "dim x\nx = 1 and bump()\n"
            "result = hit").is_integer(1)

    def test_chained_and(self):
        # 0 and b and c : ni b ni c ne sont évalués
        assert self.evaluate("0 and (1 \\ 0) and (2 \\ 0)").is_integer(0)
