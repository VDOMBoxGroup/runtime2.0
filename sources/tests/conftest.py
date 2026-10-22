"""Run the server tests without a server:

    cd sources && python -m pytest tests -q

`settings.py` reads the builtin MANAGE, and the modules under test call the
builtin debug; the server sets both at start (managers, startup)."""
import builtins

if not hasattr(builtins, "MANAGE"):
    builtins.MANAGE = False
if not hasattr(builtins, "debug"):
    builtins.debug = lambda *arguments, **keywords: None
