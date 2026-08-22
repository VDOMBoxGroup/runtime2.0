"""Extensions de langage VAILS pour VScript (fonctions utilitaires).

`IIf(condition, truepart, falsepart)` — if inline (manquant dans le cœur). Évalue les
**deux** branches (sémantique VBScript) ; pour une évaluation paresseuse utiliser `If/Then`
ou le coalescing `??`. Cf. TODO/vscript-modern.md.
"""


def v_iif(condition, truepart, falsepart):
    return truepart if condition.as_boolean else falsepart
