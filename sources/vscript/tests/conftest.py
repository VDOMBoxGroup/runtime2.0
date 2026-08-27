"""Let the VScript tests be collected at all.

`settings.py` reads a builtin named `MANAGE`, which `sources/managers` sets on
import (`builtins.MANAGE = False`). Nothing in the test tree goes through
managers, so importing any test module pulls `settings` in with the name
undefined and collection dies before a single test runs:

    settings.py:112: in <module>
        if MANAGE:
    E   NameError: name 'MANAGE' is not defined

Set it the way the server does. `MANAGE` only overrides logging levels for the
manage utility, so this changes no behaviour - it makes the suite runnable:

    cd sources && python -m pytest vscript/tests -q

Two defects keep most of it red, and neither is VScript's; both are recorded in
BUGs/model-and-macro-engine.md. In short: the engine ends up imported twice,
once as `vscript.*` and once as `sources.vscript.*`, so `raises(errors.X)`
never matches the X that was raised - and the obvious repair, resolving the two
names to one module, then hits a circular import that only the server's import
order avoids.
"""
import builtins

if not hasattr(builtins, "MANAGE"):
    builtins.MANAGE = False
