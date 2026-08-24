
from builtins import chr
from . import errors


prefix = u"v_"

reserved = (u"DIM", u"MOD", u"IS", u"NOT", u"AND", u"OR", u"XOR", u"TRUE", u"FALSE", u"USE", u"ADDRESSOF",
            u"BYVAL", u"BYREF", u"CALL", u"PROPERTY", u"GET", u"LET", u"SET", u"SUB", u"FUNCTION",
            u"CLASS", u"PUBLIC", u"PRIVATE", u"DEFAULT", u"NEW", u"WITH", u"INHERITS", u"MYBASE", u"MYCLASS", u"ME",
            # u"PROTECTED", u"FRIEND",
            # u"NOTINHERITABLE", u"MUSTINHERIT",
            # u"OVERRIDABLE", u"OVERRIDES", u"NOTOVERRIDABLE", u"MUSTOVERRIDE",
            u"IF", u"THEN", u"ELSE", u"ELSEIF", u"SELECT", u"CASE", u"DO", u"LOOP", u"WHILE", u"UNTIL", u"WEND",
            u"FOR", u"EACH", u"IN", u"TO", u"STEP", u"NEXT", u"TRY", u"CATCH", u"AS", u"FINALLY", u"THROW",
            u"END", u"EXIT", u"RETURN", u"ENUM", u"CONST", u"REDIM", u"PRESERVE", u"ERASE", u"RANDOMIZE", u"PRINT", u"TOUCH",
            u"EMPTY", u"NOTHING", u"NULL", u"NAN", u"INFINITY")
tokens = reserved + (u"PYTHON",
                     u"VCR", u"VCRLF", u"VFORMFEED", u"VLF", u"VNEWLINE", u"VNULLCHAR", u"VNULLSTRING",
                     u"VTAB", u"VVERTICALTAB", u"VBINARYCOMPARE", u"VTEXTCOMPARE", u"VDATABASECOMPARE",
                     u"VGENERALDATE", u"VLONGDATE", u"VSHORTDATE", u"VLONGTIME", u"VSHORTTIME", u"VUSEDEFAULT", u"VTRUE", u"VFALSE",
                     u"VUSESYSTEMDAYOFWEEK", u"VSUNDAY", u"VMONDAY", u"VTUESDAY", u"VWEDNESDAY", u"VTHURSDAY", u"VFRIDAY", u"VSATURDAY",
                     u"VUSESYSTEM", u"VFIRSTJAN1", u"VFIRSTFOURDAYS", u"VFIRSTFULLWEEK",
                     u"REM", u"NE", u"LE", u"GE", u"NUMBER", u"DOUBLE", u"DATE", u"STRING", u"NAME", u"NEWLINE",
                     # VAILS — modernisation : coalescing + assignations composées
                     u"COALESCE", u"PLUSEQ", u"MINUSEQ", u"STAREQ", u"SLASHEQ", u"BACKSLASHEQ", u"AMPEQ",
                     u"OPTDOT")
literals = [u'&', u'(', u')', u'*', u'+', u',', u'-', u'.',
            u'/', u':', u'<', u'=', u'>', u'\\', u'^',
            u'[', u']', u'{', u'}']   # VAILS — littéraux tableau/dictionnaire


words = reserved
reserved = {}
for word in words:
    reserved[word.lower()] = word
del words


def t_vcrlf(t):
    r'[Vv][Bb]?[Cc][Rr][Ll][Ff]'
    t.type = u"VCRLF"
    t.value = (t.lexer.lineno, "string(u\"\\r\\n\")")
    return t


def t_vcr(t):
    r'[Vv][Bb]?[Cc][Rr]'
    t.type = u"VCR"
    t.value = (t.lexer.lineno, "string(u\"\\r\")")
    return t


def t_vlf(t):
    r'[Vv][Bb]?[Ll][Ff]'
    t.type = u"VLF"
    t.value = (t.lexer.lineno, "string(u\"\\n\")")
    return t


def t_vformfeed(t):
    r'[Vv][Bb]?[Ff][Oo][Rr][Mm][Ff][Ee][Ee][Dd]'
    t.type = u"VFORMFEED"
    t.value = (t.lexer.lineno, "string(u\"\\f\")")
    return t


def t_vnewline(t):
    r'[Vv][Bb]?[Nn][Ee][Ww][Ll][Ii][Nn][Ee]'
    t.type = u"VNEWLINE"
    # string(u\"\\r\\n\") FOR WINDOWS
    t.value = (t.lexer.lineno, "string(u\"\\n\")")
    return t


def t_vnullchar(t):
    r'[Vv][Bb]?[Nn][Uu][Ll][Ll][Cc][Hh][Aa][Rr]'
    t.type = u"VNULLCHAR"
    t.value = (t.lexer.lineno, "string(u\"\\0\")")
    return t


def t_vnullstring(t):
    r'[Vv][Bb]?[Nn][Uu][Ll][Ll][Ss][Tt][Rr][Ii][Nn][Gg]'
    t.type = u"VNULLSTRING"
    t.value = (t.lexer.lineno, "string(u\"\\0\")")
    return t


def t_vtab(t):
    r'[Vv][Bb]?[Tt][Aa][Bb]'
    # r'(?:^|[^A-Za-z])[Vv][Bb]?[Tt][Aa][Bb](?:[^0-9A-Za-z]|$)'
    t.type = u"VTAB"
    t.value = (t.lexer.lineno, "string(u\"\\t\")")
    return t


def t_vverticaltab(t):
    r'[Vv][Bb]?[Vv][Ee][Rr][Tt][Ii][Cc][Aa][Ll][Tt][Aa][Bb]'
    t.type = u"VVERTICALTAB"
    t.value = (t.lexer.lineno, "string(u\"\\v\")")
    return t


def t_vbinarycompare(t):
    r'[Vv][Bb]?[Bb][Ii][Nn][Aa][Rr][Yy][Cc][Oo][Mm][Pp][Aa][Rr][Ee]'
    t.type = u"VBINARYCOMPARE"
    t.value = (t.lexer.lineno, "integer(0)")
    return t


def t_vtextcompare(t):
    r'[Vv][Bb]?[Tt][Ee][Xx][Tt][Cc][Oo][Mm][Pp][Aa][Rr][Ee]'
    t.type = u"VTEXTCOMPARE"
    t.value = (t.lexer.lineno, "integer(1)")
    return t


def t_vdatabasecompare(t):
    r'[Vv][Bb]?[Dd][Aa][Tt][Aa][Bb][Aa][Ss][Ee][Cc][Oo][Mm][Pp][Aa][Rr][Ee]'
    t.type = u"VDATABASECOMPARE"
    t.value = (t.lexer.lineno, "integer(2)")
    return t


def t_vgeneraldate(t):
    r'[Vv][Bb]?[Gg][Ee][Nn][Ee][Rr][Aa][Ll][Dd][Aa][Tt][Ee]'
    t.type = u"VGENERALDATE"
    t.value = (t.lexer.lineno, "integer(0)")
    return t


def t_vlongdate(t):
    r'[Vv][Bb]?[Ll][Oo][Nn][Gg][Dd][Aa][Tt][Ee]'
    t.type = u"VLONGDATE"
    t.value = (t.lexer.lineno, "integer(1)")
    return t


def t_vshortdate(t):
    r'[Vv][Bb]?[Ss][Hh][Oo][Rr][Tt][Dd][Aa][Tt][Ee]'
    t.type = u"VSHORTDATE"
    t.value = (t.lexer.lineno, "integer(2)")
    return t


def t_vlongtime(t):
    r'[Vv][Bb]?[Ll][Oo][Nn][Gg][Tt][Ii][Mm][Ee]'
    t.type = u"VLONGTIME"
    t.value = (t.lexer.lineno, "integer(3)")
    return t


def t_vshorttime(t):
    r'[Vv][Bb]?[Ss][Hh][Oo][Rr][Tt][Tt][Ii][Mm][Ee]'
    t.type = u"VSHORTTIME"
    t.value = (t.lexer.lineno, "integer(4)")
    return t


def t_vusedefault(t):
    r'[Vv][Bb]?[Uu][Ss][Ee][Dd][Ee][Ff][Aa][Uu][Ll][Tt]'
    t.type = u"VUSEDEFAULT"
    t.value = (t.lexer.lineno, "integer(-2)")
    return t


def t_vtrue(t):
    r'[Vv][Bb]?[Tt][Rr][Uu][Ee]'
    t.type = u"VTRUE"
    t.value = (t.lexer.lineno, "integer(-1)")
    return t


def t_vfalse(t):
    r'[Vv][Bb]?[Ff][Aa][Ll][Ss][Ee]'
    t.type = u"VFALSE"
    t.value = (t.lexer.lineno, "integer(0)")
    return t


def t_vusesystemdayofweek(t):
    r'[Vv][Bb]?[Uu][Ss][Ee][Ss][Yy][Ss][Tt][Ee][Mm][Dd][Aa][Yy][Oo][Ff][Ww][Ee][Ee][Kk]'
    t.type = u"VUSESYSTEMDAYOFWEEK"
    t.value = (t.lexer.lineno, "integer(0)")
    return t


def t_vsunday(t):
    r'[Vv][Bb]?[Ss][Uu][Nn][Dd][Aa][Yy]'
    t.type = u"VSUNDAY"
    t.value = (t.lexer.lineno, "integer(1)")
    return t


def t_vmonday(t):
    r'[Vv][Bb]?[Mm][Oo][Nn][Dd][Aa][Yy]'
    t.type = u"VMONDAY"
    t.value = (t.lexer.lineno, "integer(2)")
    return t


def t_vtuesday(t):
    r'[Vv][Bb]?[Tt][Uu][Ee][Ss][Dd][Aa][Yy]'
    t.type = u"VTUESDAY"
    t.value = (t.lexer.lineno, "integer(3)")
    return t


def t_vwednesday(t):
    r'[Vv][Bb]?[Ww][Ee][Dd][Nn][Ee][Ss][Dd][Aa][Yy]'
    t.type = u"VWEDNESDAY"
    t.value = (t.lexer.lineno, "integer(4)")
    return t


def t_vthursday(t):
    r'[Vv][Bb]?[Tt][Hh][Uu][Rr][Ss][Dd][Aa][Yy]'
    t.type = u"VTHURSDAY"
    t.value = (t.lexer.lineno, "integer(5)")
    return t


def t_vfriday(t):
    r'[Vv][Bb]?[Ff][Rr][Ii][Dd][Aa][Yy]'
    t.type = u"VFRIDAY"
    t.value = (t.lexer.lineno, "integer(6)")
    return t


def t_vsaturday(t):
    r'[Vv][Bb]?[Ss][Aa][Tt][Uu][Rr][Dd][Aa][Yy]'
    t.type = u"VSATURDAY"
    t.value = (t.lexer.lineno, "integer(7)")
    return t


def t_vusesystem(t):
    r'[Vv][Bb]?[Uu][Ss][Ee][Ss][Yy][Ss][Tt][Ee][Mm]'
    t.type = u"VUSESYSTEM"
    t.value = (t.lexer.lineno, "integer(0)")
    return t


def t_vfirstjan1(t):
    r'[Vv][Bb]?[Ff][Ii][Rr][Ss][Tt][Jj][Aa][Nn]1'
    t.type = u"VFIRSTJAN1"
    t.value = (t.lexer.lineno, "integer(1)")
    return t


def t_vfirstfourdays(t):
    r'[Vv][Bb]?[Ff][Ii][Rr][Ss][Tt][Ff][Oo][Uu][Rr][Dd][Aa][Yy][Ss]'
    t.type = u"VFIRSTFOURDAYS"
    t.value = (t.lexer.lineno, "integer(2)")
    return t


def t_vfirstfullweek(t):
    r'[Vv][Bb]?[Ff][Ii][Rr][Ss][Tt][Ff][Uu][Ll][Ll][Ww][Ee][Ee][Kk]'
    t.type = u"VFIRSTFULLWEEK"
    t.value = (t.lexer.lineno, "integer(3)")
    return t


def t_ne(t):
    r'<>'
    t.type = u"NE"
    t.value = (t.lexer.lineno, u"<>")
    return t


def t_le(t):
    r'<='
    t.type = u"LE"
    t.value = (t.lexer.lineno, u"<=")
    return t


def t_ge(t):
    r'>='
    t.type = u"GE"
    t.value = (t.lexer.lineno, ">=")
    return t


# VAILS — opérateurs composés (fonctions = prioritaires sur les littéraux `+ - * / \ & ?`)
def t_coalesce(t):
    r'\?\?'
    t.type = u"COALESCE"; t.value = (t.lexer.lineno, u"??"); return t


def t_optdot(t):
    r'\?\.'
    t.type = u"OPTDOT"; t.value = (t.lexer.lineno, u"?."); return t


def t_pluseq(t):
    r'\+='
    t.type = u"PLUSEQ"; t.value = (t.lexer.lineno, u"+="); return t


def t_minuseq(t):
    r'-='
    t.type = u"MINUSEQ"; t.value = (t.lexer.lineno, u"-="); return t


def t_stareq(t):
    r'\*='
    t.type = u"STAREQ"; t.value = (t.lexer.lineno, u"*="); return t


def t_slasheq(t):
    r'/='
    t.type = u"SLASHEQ"; t.value = (t.lexer.lineno, u"/="); return t


def t_backslasheq(t):
    r'\\='
    t.type = u"BACKSLASHEQ"; t.value = (t.lexer.lineno, u"\\="); return t


def t_ampeq(t):
    r'&='
    t.type = u"AMPEQ"; t.value = (t.lexer.lineno, u"&="); return t


def t_comment(t):
    r'\'[^\n]*'
    pass


def t_rem(t):
    r'rem\s.*'
    t.type = u"REM"
    t.value = (t.lexer.lineno, str(t.value))
    return t


def t_multiline(t):
    r'_\r?\n'
    t.lexer.lineno += 1
    pass


def t_double(t):
    r'\d+\.\d+([Ee][+-]?\d+)? | [+-]?\d+[Ee][+-]?\d+'
    t.type = u"DOUBLE"
    t.value = (t.lexer.lineno, str(t.value))
    return t


def t_number(t):
    r'\d+'
    t.type = u"NUMBER"
    t.value = (t.lexer.lineno, str(t.value))
    return t


def t_date(t):
    r'\#[^#]+\#'
    t.type = u"DATE"
    t.value = (t.lexer.lineno, str(t.value[1:-1]))
    return t


# VAILS — modernisation : interpolation de chaîne `$"… {expr} …"`.
# Expansion au niveau LEXER (aucun changement de grammaire → zéro conflit PLY) :
# la chaîne interpolée est réécrite en source VScript équivalente
#   `("" & "litéral" & (expr) & …)`   (le `&` compose déjà en `concat(...)`)
# puis re-lue en place par le pipeline normal. Échappements `\n \t \r \\ \" {{ }}`
# pris en charge UNIQUEMENT dans `$"…"` (les `"…"` classiques sont inchangés, donc
# les chemins Windows `"C:\dir"` restent littéraux).
def _split_pipes(s):
    u"""Découpe `expr | f | g(args)` sur les `|` de niveau supérieur (hors parenthèses/
    crochets/accolades et hors chaînes `"…"`). `|` n'est utilisé par aucun opérateur
    VScript → libre comme séparateur de pipe."""
    out, cur, depth, instr = [], [], 0, False
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if instr:
            cur.append(c)
            if c == u"\"":
                if i + 1 < n and s[i + 1] == u"\"":
                    cur.append(u"\"")
                    i += 2
                    continue
                instr = False
            i += 1
            continue
        if c == u"\"":
            instr = True
            cur.append(c)
            i += 1
            continue
        if c in u"([{":
            depth += 1
        elif c in u")]}":
            depth -= 1
        elif c == u"|" and depth == 0:
            out.append(u"".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    out.append(u"".join(cur))
    return out


def _compose_interp(content):
    u"""Compose une interpolation `{ expr | f | g(a) }` : la valeur est passée en
    PREMIER argument de chaque étage de pipe (chaînable). `f` → `f((acc))`,
    `g(a)` → `g((acc), a)`."""
    segs = _split_pipes(content)
    acc = u"(" + segs[0].strip() + u")"
    for stage in segs[1:]:
        stage = stage.strip()
        if stage.endswith(u")") and u"(" in stage:
            k = stage.index(u"(")
            fname = stage[:k].strip()
            inner = stage[k + 1:-1].strip()
            acc = fname + u"(" + acc + (u", " + inner if inner else u"") + u")"
        else:
            acc = stage + u"(" + acc + u")"
    return acc


def _expand_fstring(raw):
    parts = []
    lit = []

    def flush():
        if lit:
            parts.append(u'"' + u"".join(lit) + u'"')
            del lit[:]

    i, n = 0, len(raw)
    while i < n:
        c = raw[i]
        if c == u"{":
            if i + 1 < n and raw[i + 1] == u"{":
                lit.append(u"{")
                i += 2
                continue
            j = raw.find(u"}", i + 1)
            if j == -1:
                raise errors.syntax_error(u"Unterminated '{' in interpolated string")
            flush()
            parts.append(_compose_interp(raw[i + 1:j]))
            i = j + 1
            continue
        if c == u"}":
            if i + 1 < n and raw[i + 1] == u"}":
                lit.append(u"}")
                i += 2
                continue
            lit.append(u"}")
            i += 1
            continue
        if c == u"\\" and i + 1 < n:
            nxt = raw[i + 1]
            ctrl = {u"n": u"vblf", u"t": u"vbtab", u"r": u"vbcr"}
            if nxt in ctrl:
                flush()
                parts.append(ctrl[nxt])
                i += 2
                continue
            if nxt == u"\\":
                lit.append(u"\\")
                i += 2
                continue
            if nxt == u"\"":
                lit.append(u"\"\"")
                i += 2
                continue
            if nxt in (u"{", u"}"):
                lit.append(nxt)
                i += 2
                continue
            lit.append(u"\\")
            i += 1
            continue
        lit.append(c)
        i += 1
    flush()
    return (u'("" & ' + u" & ".join(parts) + u")") if parts else u'("")'


def expand_fstrings(src):
    u"""Pré-passage source→source : étend `$"… {expr} …"` en concaténation VScript
    `("" & "lit" & (expr) & …)` AVANT le lexing. Respecte les frontières — on saute
    les chaînes classiques `"…"` (avec `""` échappé) et les commentaires `'…` — donc
    un `$` à l'intérieur d'une chaîne/commentaire n'est jamais pris pour un f-string.
    Les `"` à l'intérieur d'un `{…}` interpolé sont tolérés (on saute jusqu'au `}`)."""
    if u"$\"" not in src:
        return src
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == u"\"":                       # chaîne classique — copiée telle quelle
            j = i + 1
            while j < n:
                if src[j] == u"\"":
                    if j + 1 < n and src[j + 1] == u"\"":
                        j += 2
                        continue
                    j += 1
                    break
                if src[j] == u"\n":
                    break
                j += 1
            out.append(src[i:j])
            i = j
            continue
        if c == u"'":                        # commentaire jusqu'à la fin de ligne
            j = src.find(u"\n", i)
            j = n if j == -1 else j
            out.append(src[i:j])
            i = j
            continue
        if c == u"$" and i + 1 < n and src[i + 1] == u"\"":   # f-string
            j = i + 2
            while j < n:
                if src[j] == u"\"":
                    if j + 1 < n and src[j + 1] == u"\"":
                        j += 2
                        continue
                    break
                if src[j] == u"{":           # saute l'interpolation (peut contenir des ")
                    k = src.find(u"}", j + 1)
                    if k == -1:
                        break
                    j = k + 1
                    continue
                if src[j] == u"\n":
                    break
                j += 1
            out.append(_expand_fstring(src[i + 2:j]))
            i = j + 1
            continue
        out.append(c)
        i += 1
    return u"".join(out)


def t_verbatim_string(t):
    # A string that may span lines, written @"...". The ordinary literal
    # cannot: its pattern excludes a newline on purpose, so a missing closing
    # quote stays a one-line mistake instead of swallowing the rest of the
    # file. That protection is worth keeping, so this is a separate, opt-in
    # form rather than a loosening of the existing one.
    #
    # "@" was free: it appears in no other rule and in no literal.
    #
    # Triple quotes were the obvious choice and are not available. Four quotes
    # is already how a lone double-quote is written, and this repository uses
    # it - lib_vails.vb and lib_console.vb both do. A triple-quote delimiter
    # would have re-read that as an opening delimiter and broken working code.
    #
    # Escaping is the same as everywhere else in the language - two quotes are
    # one quote - so there is one rule to know rather than two. The alternation
    # cannot cross a lone closing quote, which is what stops a literal that
    # ends in a quote from being cut one character short. That exact mistake is
    # live in the VAILS parser today, in its << >> rule.
    r'@\"([^\"]|(\"\"))*\"'
    t.type = u"STRING"
    start = t.lexer.lineno
    t.lexer.lineno += t.value.count(u"\n")
    t.value = (start, str(t.value[2:-1].replace(u"\"\"", u"\"")))
    return t


def t_string(t):
    r'\"([^\"\n]|(\"\"))*\"'
    t.type = u"STRING"
    t.value = (t.lexer.lineno, str(t.value[1:-1].replace(u"\"\"", u"\"")))
    return t


def t_character(t):
    # VAILS — littéral hexadécimal NUMÉRIQUE `&H1F` -> 31 (avant : caractère chr(),
    # divergence vs VBScript). Aucun test cœur ne dépendait de l'ancien comportement.
    r'\&[Hh][0-9A-Fa-f]+'
    t.type = u"NUMBER"
    t.value = (t.lexer.lineno, str(int(t.value[2:], 16)))
    return t


def t_binary_literal(t):
    # VAILS — littéral binaire numérique `&B1010` -> 10.
    r'\&[Bb][01]+'
    t.type = u"NUMBER"
    t.value = (t.lexer.lineno, str(int(t.value[2:], 2)))
    return t


def t_python(t):
    r'`[^\n]*'
    value = str(t.value[1:])
    value = value.replace(u"\\n", u"\n")
    t.type = u"PYTHON"
    t.value = (t.lexer.lineno, str(value))
    return t


def t_name(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    value = str(t.value.lower())
    t.type = reserved.get(value, u"NAME")
    t.value = (t.lexer.lineno, prefix + value) if t.type == u"NAME" else (t.lexer.lineno, value)
    return t


def t_newline(t):
    r'(\r?\n)+'
    t.lexer.lineno += t.value.count(u"\n")
    t.type = u"NEWLINE"
    t.value = (t.lexer.lineno, str(t.value))
    return t


t_ignore = " \t"


def t_error(t):
    raise errors.invalid_character(
        t.value[0] if t is not None else "Unknown", line=t.lexer.lineno)
    t.lexer.skip(1)
