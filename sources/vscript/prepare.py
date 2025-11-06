
import ply.lex
import ply.yacc
import settings

from . import lexemes, syntax


LEXER_TABLE_NAME = "vscript.tables.lexer"
PARSER_TABLE_NAME = "vscript.tables.parser"


if settings.DISABLE_VSCRIPT:
    print("VScript are disabled through configuration")
    lexer = None
    parser = None
else:
    lexer = ply.lex.lex(module=lexemes, debug=False,
        optimize=settings.OPTIMIZE_VSCRIPT_PARSER, lextab=LEXER_TABLE_NAME)
    parser = ply.yacc.yacc(module=syntax, debug=False, start="source",
        optimize=settings.OPTIMIZE_VSCRIPT_PARSER, tabmodule=PARSER_TABLE_NAME)
