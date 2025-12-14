from __future__ import absolute_import


import ply.lex as lex
from . import errors, lexemes
from .source import *


tokens = lexemes.tokens


def p_empty(p):
    'empty :'
    pass


def p_newline_continues(p):
    """newline : newline NEWLINE"""
    p[0] = None


def p_newline_starts(p):
    """newline : NEWLINE"""
    p[0] = None


def p_arguments_starts_empty(p):
    """arguments : empty"""
    p[0] = varguments()


def p_arguments_starts_argument(p):
    """arguments : argument"""
    p[0] = varguments().join(p[1])


def p_arguments_continues_with_argument(p):
    """arguments : arguments ',' argument"""
    p[0] = p[1].join(p[3])


def p_argument_starts_name(p):
    """argument : NAME"""
    p[0] = (p[1][1], u"byref")


def p_argument_starts_array(p):
    """argument : NAME '(' ')'"""
    p[0] = (p[1][1], u"byref")


def p_argument_starts_byval_name(p):
    """argument : BYVAL NAME"""
    p[0] = (p[2][1], u"byval")


def p_argument_starts_byval_array(p):
    """argument : BYVAL NAME '(' ')'"""
    p[0] = (p[2][1], u"byval")


def p_argument_starts_byref_name(p):
    """argument : BYREF NAME"""
    p[0] = (p[2][1], u"byref")


def p_argument_starts_byref_array(p):
    """argument : BYREF NAME '(' ')'"""
    p[0] = (p[2][1], u"byref")


def p_names_start(p):
    """names : NAME"""
    p[0] = vnames(line=p[1][0]).join(p[1][1])


def p_names_continues(p):
    """names : names ',' NAME"""
    p[0] = p[1].join(p[3][1])


def p_call_continues_with_expressions(p):
    """call : call '(' expressions ')'"""
    p[0] = p[1].join(p[3])


def p_call_continues_with_empty_expressions(p):
    """call : call '(' ')'"""
    p[0] = p[1].join(p[3])


def p_name_continues_with_dot_name(p):
    """name : name '.' NAME"""
    p[0] = p[1].join(p[3][1])


def p_name_continues_with_dot_call(p):
    """name : call '.' NAME"""
    p[0] = p[1].join(p[3][1])


def p_call_continues_with_dot_name_expressions(p):
    """call : name '.' NAME '(' expressions ')'"""
    p[0] = p[1].join(p[3][1]).join(p[5])


def p_call_continues_with_dot_name_empty_expressions(p):
    """call : name '.' NAME '(' ')'"""
    p[0] = p[1].join(p[3][1])


def p_call_continues_with_dot_call_expressions(p):
    """call : call '.' NAME '(' expressions ')'"""
    p[0] = p[1].join(p[3][1]).join(p[5])


def p_call_continues_with_dot_call_empty_expressions(p):
    """call : call '.' NAME '(' ')'"""
    p[0] = p[1].join(p[3][1])


def p_name_starts_with_name(p):
    """name : NAME"""
    p[0] = vname(p[1][1], line=p[1][0])


def p_name_starts_with_mybase(p):
    """name : MYBASE"""
    p[0] = vmybase(line=p[1][0])


def p_name_starts_with_me(p):
    """name : ME"""
    p[0] = vme(line=p[1][0])


def p_name_starts_with_myclass(p):
    """name : MYCLASS"""
    p[0] = vmyclass(line=p[1][0])


def p_call_starts_with_name_expressions(p):
    """call : NAME '(' expressions ')'"""
    p[0] = vname(p[1][1], line=p[1][0]).join(p[3])


def p_call_starts_with_name_empty_expressions(p):
    """call : NAME '(' ')'"""
    p[0] = vname(p[1][1], line=p[1][0])


def p_name_starts_with_dot_name(p):
    """name : '.' NAME"""
    p[0] = vname(None, line=p[2][0]).join(p[2][1])

# def p_name_starts_with_expression(p):
#    """name : '(' expression ')'"""
#    p[0]=vname("", line=p[1][0]).join(p[2])


def p_exponentiation_continues(p):
    """exponentiation : value '^' exponentiation"""
    p[0] = p[1].join(u"%s**%s", p[3])


def p_exponentiation_starts(p):
    """exponentiation : value"""
    p[0] = p[1]


def p_unary_continues_with_plus(p):
    """unary : '+' unary"""
    p[0] = p[2].apply(u"+(%s)")


def p_unary_continues_with_minus(p):
    """unary : '-' unary"""
    p[0] = p[2].apply(u"-(%s)")


def p_unary_starts(p):
    """unary : exponentiation"""
    p[0] = p[1]


def p_multiplication_continues_with_asterix(p):
    """multiplication : multiplication '*' unary"""
    p[0] = p[1].join(u"%s*%s", p[3])


def p_multiplication_continues_with_slash(p):
    """multiplication : multiplication '/' unary"""
    p[0] = p[1].join(u"%s/%s", p[3])


def p_multiplication_starts(p):
    """multiplication : unary"""
    p[0] = p[1]


def p_integer_division_continues(p):
    """integer_division : integer_division '\\\\' multiplication"""
    p[0] = p[1].join(u"%s//%s", p[3])


def p_integer_division_starts(p):
    """integer_division : multiplication"""
    p[0] = p[1]


def p_modulus_continues(p):
    """modulus : modulus MOD integer_division"""
    p[0] = p[1].join(u"%s%%%%%s", p[3])


def p_modulus_starts(p):
    """modulus : integer_division"""
    p[0] = p[1]


def p_addition_continues_with_plus(p):
    """addition : addition '+' modulus"""
    p[0] = p[1].join(u"%s+%s", p[3])


def p_addition_continues_with_minus(p):
    """addition : addition '-' modulus"""
    p[0] = p[1].join(u"%s-%s", p[3])


def p_addition_starts(p):
    """addition : modulus"""
    p[0] = p[1]


def p_rconcatenation_continues(p):
    """rconcatenation : rconcatenation '&' addition"""
    expression, expressions = p[1]
    p[0] = expression, expressions.join(p[3])


def p_rconcatenation_starts(p):
    """rconcatenation : addition '&' addition"""
    expression, expressions = p[1], vexpressions()
    p[0] = expression, expressions.join(p[3])


def p_concatenation_addition(p):
    """concatenation : addition"""
    p[0] = p[1]


def p_concatenation_rconcatenation(p):
    """concatenation : rconcatenation"""
    expression, expressions = p[1]
    p[0] = expression.join(u"concat(%s, %s)", expressions)


def p_equality_continues_with_equals(p):
    """equality : equality '=' concatenation"""
    p[0] = p[1].join(u"%s==%s", p[3])


def p_equality_continues_with_inequal(p):
    """equality : equality NE concatenation"""
    p[0] = p[1].join(u"%s!=%s", p[3])


def p_equality_continues_with_less(p):
    """equality : equality '<' concatenation"""
    p[0] = p[1].join(u"%s<%s", p[3])


def p_equality_continues_with_greater(p):
    """equality : equality '>' concatenation"""
    p[0] = p[1].join(u"%s>%s", p[3])


def p_equality_continues_with_less_or_equal(p):
    """equality : equality LE concatenation"""
    p[0] = p[1].join(u"%s<=%s", p[3])


def p_equality_continues_with_greater_or_equal(p):
    """equality : equality GE concatenation"""
    p[0] = p[1].join(u"%s>=%s", p[3])


def p_equality_continues_with_is(p):
    """equality : equality IS concatenation"""
    p[0] = p[1].join(u"%s is %s", p[3])


def p_equality_continues_with_is_not(p):
    """equality : equality IS NOT concatenation"""
    p[0] = p[1].join(u"%s is not %s", p[3])


def p_equality_starts(p):
    """equality : concatenation"""
    p[0] = p[1]


def p_negation_continues(p):
    """negation : NOT negation"""
    p[0] = p[2].apply(u"~%s")


def p_negation_starts(p):
    """negation : equality"""
    p[0] = p[1]


def p_conjunction_continues(p):
    """conjunction : conjunction AND negation"""
    p[0] = p[1].join(u"(%s) & (%s)", p[3])


def p_conjunction_starts(p):
    """conjunction : negation"""
    p[0] = p[1]


def p_disjunction_continues(p):
    """disjunction : disjunction OR conjunction"""
    p[0] = p[1].join(u"(%s) | (%s)", p[3])


def p_disjunction_starts(p):
    """disjunction : conjunction"""
    p[0] = p[1]


def p_exclusion_continues(p):
    """exclusion : exclusion XOR disjunction"""
    p[0] = p[1].join(u"(%s) ^ (%s)", p[3])


def p_exclusion_starts(p):
    """exclusion : disjunction"""
    p[0] = p[1]


def p_inclusion_continues(p):
    """inclusion : inclusion IN exclusion"""
    p[0] = p[1].join(u"boolean((%s) in (%s))", p[3])


def p_inclusion_starts(p):
    """inclusion : exclusion"""
    p[0] = p[1]


def p_expression(p):
    """expression : inclusion"""
    p[0] = p[1]


def p_value_number(p):
    """value : NUMBER"""
    p[0] = vexpression(u"integer(%s)" % p[1][1], line=p[1][0])


def p_value_double(p):
    """value : DOUBLE"""
    p[0] = vexpression(u"double(%s)" % p[1][1], line=p[1][0])


def p_value_date(p):
    """value : DATE"""
    p[0] = vexpression(u"date(\"%s\")" % p[1][1], line=p[1][0])


def p_value_string(p):
    """value : STRING"""
    p[0] = vexpression(u"string(%s)" % repr(
        p[1][1]).replace("%", "%%"), line=p[1][0])


def p_value_true(p):
    """value : TRUE"""
    p[0] = vexpression(u"boolean(true)", line=p[1][0])


def p_value_false(p):
    """value : FALSE"""
    p[0] = vexpression(u"boolean(false)", line=p[1][0])


def p_value_empty(p):
    """value : EMPTY"""
    p[0] = vexpression(u"v_empty", line=p[1][0])


def p_value_nothing(p):
    """value : NOTHING"""
    p[0] = vexpression(u"v_nothing", line=p[1][0])


def p_value_null(p):
    """value : NULL"""
    p[0] = vexpression(u"v_null", line=p[1][0])


def p_value_nan(p):
    """value : NAN"""
    p[0] = vexpression(u"double(nan)", line=p[1][0])


def p_value_infinity(p):
    """value : INFINITY"""
    p[0] = vexpression(u"double(infinity)", line=p[1][0])


def p_value_new(p):
    """value : NEW NAME"""
    name = vname(p[2][1], line=p[1][0]).join(vexpressions())
    p[0] = vexpression(u"%s", values=(name, ), line=name.line)


def p_value_name(p):
    """value : name"""
    p[0] = vexpression(u"%s", values=(p[1], ), line=p[1].line)


def p_value_call(p):
    """value : call"""
    p[0] = vexpression(u"%s", values=(p[1], ), line=p[1].line)


def p_value_parenthesis(p):
    """value : '(' expression ')'"""
    p[0] = p[2].apply(u"(%s)")


def p_value_constants(p):
    """value : VCRLF
             | VCR
             | VLF
             | VFORMFEED
             | VNEWLINE
             | VNULLCHAR
             | VNULLSTRING
             | VTAB
             | VVERTICALTAB
             | VBINARYCOMPARE
             | VTEXTCOMPARE
             | VDATABASECOMPARE
             | VGENERALDATE
             | VLONGDATE
             | VSHORTDATE
             | VLONGTIME
             | VSHORTTIME
             | VUSEDEFAULT
             | VTRUE
             | VFALSE
             | VUSESYSTEMDAYOFWEEK
             | VSUNDAY
             | VMONDAY
             | VTUESDAY
             | VWEDNESDAY
             | VTHURSDAY
             | VFRIDAY
             | VSATURDAY
             | VUSESYSTEM
             | VFIRSTJAN1
             | VFIRSTFOURDAYS
             | VFIRSTFULLWEEK
             """
    p[0] = vexpression(p[1][1], line=p[1][0])


def p_expressions_continues_with_expression(p):
    """expressions : expressions ',' expression"""
    p[0] = p[1].join(p[3])


def p_expressions_continues_with_comma_expression(p):
    """expressions : expressions ','"""
    p[0] = p[1].join(vexpression(u"variant(integer(0))", line=p[2][0]))


def p_expressions_starts_expression(p):
    """expressions : expression"""
    p[0] = vexpressions(line=p[1].line).join(p[1])

# def p_expressions_starts_empty(p):
#    """expressions : empty"""
#    p[0]=vexpressions()


# def p_use_start(p):
#    """use : USE NAME"""
#    p[0]=vnames(line=p[1][0]).join(p[1][1])

# def p_use_continues(p):
#    """use : use ',' NAME"""
#    p[0]=p[1].join(p[3][1])


def p_cases_starts(p):
    """cases : CASE expressions statements"""
    p[0] = vselectcases().join(vselectcase(p[2], p[3], line=p[1][0]))


def p_cases_continues(p):
    """cases : cases CASE expressions statements"""
    p[0] = p[1].join(vselectcase(p[3], p[4], line=p[2][0]))


def p_elseifs_starts(p):
    """elseifs : ELSEIF expression THEN statements"""
    p[0] = velseifs().join(velseif(p[2], p[4], line=p[1][0]))


def p_elseifs_continues(p):
    """elseifs : elseifs ELSEIF expression THEN statements"""
    p[0] = p[1].join(velseif(p[3], p[5], line=p[2][0]))


def p_catches_start_with_name(p):
    """catches : CATCH NAME statements"""
    p[0] = vtrycatches().join(vtrycatch(p[3], exceptions=vnames(
        line=p[2][0]).join(p[2][1]), line=p[1][0]))


def p_catches_start_with_names(p):
    """catches : CATCH names statements"""
    p[0] = vtrycatches().join(vtrycatch(p[3], exceptions=p[2], line=p[1][0]))


def p_catches_start_as_name(p):
    """catches : CATCH NAME AS NAME statements"""
    p[0] = vtrycatches().join(vtrycatch(p[5], exceptions=vnames(
        line=p[2][0]).join(p[2][1]), name=p[4][1], line=p[1][0]))


def p_catches_start_as_names(p):
    """catches : CATCH names AS NAME statements"""
    p[0] = vtrycatches().join(
        vtrycatch(p[5], exceptions=p[2], name=p[4][1], line=p[1][0]))


def p_catches_continue_with_name(p):
    """catches : catches CATCH NAME statements"""
    p[0] = p[1].join(vtrycatch(p[4], exceptions=vnames(
        line=p[3][0]).join(p[3][1]), line=p[2][0]))


def p_catches_continue_with_names(p):
    """catches : catches CATCH names statements"""
    p[0] = p[1].join(vtrycatch(p[4], exceptions=p[3], line=p[2][0]))


def p_catches_continue_as_name(p):
    """catches : catches CATCH NAME AS NAME statements"""
    p[0] = p[1].join(vtrycatch(p[6], exceptions=vnames(
        line=p[3][0]).join(p[3][1]), name=p[5][1], line=p[2][0]))


def p_catches_continue_as_names(p):
    """catches : catches CATCH names AS NAME statements"""
    p[0] = p[1].join(vtrycatch(p[6], exceptions=p[3],
                     name=p[5][1], line=p[2][0]))


# def p_statement_expression(p):
#    """statement : expression"""
#    raise errors.expected_statement(p[1].line)

def p_statement_python(p):
    """statement : PYTHON"""
    p[0] = vpython(p[1][1], line=p[1][0])


def p_statement_remark(p):
    """statement : REM"""
    pass


def p_statement_use(p):
    """statement : USE NAME"""
    p[0] = vuse(p[2][1], line=p[2][0], package=p.parser.package,
                environment=p.parser.environment)


def p_statement_declaration(p):
    """statement : declarations"""
    p[0] = p[1]


def p_statement_constant(p):
    """statement : CONST NAME '=' expression"""
    p[0] = vconstant(vname(p[2][1], line=p[2][0]), p[4], line=p[1][0])


def p_statement_redim(p):
    """statement : redim"""
    p[0] = p[1]


def p_statement_erase(p):
    """statement : ERASE NAME"""
    p[0] = verase(vname(p[2][1], line=p[2][0]), line=p[1][0])


def p_statement_erase_with_expressions(p):
    """statement : ERASE NAME '(' expressions ')'"""
    p[0] = verase(vname(p[2][1], line=p[2][0]), expressions=p[4], line=p[1][0])


def p_statement_assigment_name(p):
    """statement : name '=' expression"""
    p[0] = vlet(p[1], p[3], line=p[1].line)


def p_statement_assigment_call(p):
    """statement : call '=' expression"""
    p[0] = vcall(p[1].let(p[3]), line=p[1].line)


def p_statement_assigment_set_name(p):
    """statement : SET name '=' expression"""
    p[0] = vset(p[2], p[4], line=p[1][0])


def p_statement_assigment_set_call(p):
    """statement : SET call '=' expression"""
    p[0] = vcall(p[2].set(p[4]), line=p[1][0])


def p_statement_invoke_name(p):
    """statement : name"""
    p[0] = vcall(p[1].join(vexpressions()), line=p[1].line)


def p_statement_invoke_call(p):
    """statement : call"""
    p[0] = vcall(p[1], line=p[1].line)


def p_statement_invoke_name_expression(p):
    """statement : name expressions"""
    p[0] = vcall(p[1].join(p[2]), line=p[1].line)


def p_statement_invoke_call_expression(p):
    """statement : call expressions"""
    p[0] = vcall(p[1].join(p[2]), line=p[1].line)


def p_statement_invoke_ex_name(p):
    """statement : CALL name"""
    p[0] = vcall(p[2].join(vexpressions()), line=p[1][0])


def p_statement_invoke_ex_call(p):
    """statement : CALL call"""
    p[0] = vcall(p[2], line=p[1][0])


def p_statement_invoke_ex_name_expression(p):
    """statement : CALL name expressions"""
    p[0] = vcall(p[2].join(p[3]), line=p[1][0])


def p_statement_invoke_ex_call_expression(p):
    """statement : CALL call expressions"""
    p[0] = vcall(p[2].join(p[3]), line=p[1][0])


def p_statement_if_then_single_statement(p):
    """statement : IF expression THEN statement"""
    p[0] = vifthen(p[2], p[4], line=p[1][0])


def p_statement_if_then_else_single_statement(p):
    """statement : IF expression THEN statement ELSE statement"""
    p[0] = vifthenelse(p[2], p[4], p[6], line=p[1][0])


def p_statement_if_then(p):
    """statement : IF expression THEN statements END
                 | IF expression THEN statements END IF"""
    p[0] = vifthen(p[2], p[4], line=p[1][0])


def p_statement_if_then_elseifs(p):
    """statement : IF expression THEN statements elseifs END
                 | IF expression THEN statements elseifs END IF"""
    p[0] = vifthen(p[2], p[4], elseifs=p[5], line=p[1][0])


def p_statement_if_then_else(p):
    """statement : IF expression THEN statements ELSE statements END
                 | IF expression THEN statements ELSE statements END IF"""
    p[0] = vifthenelse(p[2], p[4], p[6], line=p[1][0])


def p_statement_if_then_elseifs_else(p):
    """statement : IF expression THEN statements elseifs ELSE statements END
                 | IF expression THEN statements elseifs ELSE statements END IF"""
    p[0] = vifthenelse(p[2], p[4], p[7], elseifs=p[5], line=p[1][0])


def p_statement_select(p):
    """statement : SELECT CASE expression newline cases END
                 | SELECT CASE expression newline cases END SELECT"""
    p[0] = vselect(p[3], p[5], line=p[1][0])


def p_statement_select_else(p):
    """statement : SELECT CASE expression newline cases CASE ELSE statements END
                 | SELECT CASE expression newline cases CASE ELSE statements END SELECT"""
    p[0] = vselectelse(p[3], p[5], p[8], line=p[1][0])


def p_statement_do_loop(p):
    """statement : DO statements LOOP"""
    p[0] = vdoloop(p[2], line=p[1][0])


def p_statement_do_while_loop(p):
    """statement : DO WHILE expression newline statements LOOP"""
    p[0] = vdowhileloop(p[3], p[5], line=p[1][0])


def p_statement_do_until_loop(p):
    """statement : DO UNTIL expression newline statements LOOP"""
    p[0] = vdountilloop(p[3], p[5], line=p[1][0])


def p_statement_do_loop_while(p):
    """statement : DO statements LOOP WHILE expression"""
    p[0] = vdoloopwhile(p[5], p[2], line=p[1][0])


def p_statement_do_loop_until(p):
    """statement : DO statements LOOP UNTIL expression"""
    p[0] = vdoloopuntil(p[5], p[2], line=p[1][0])


def p_statement_for_each(p):
    """statement : FOR EACH NAME IN expression statements NEXT"""
    p[0] = vforeach(vname(p[3][1], line=p[3][0]), p[5], p[6], line=p[1][0])


def p_statement_for(p):
    """statement : FOR NAME '=' expression TO expression statements NEXT"""
    p[0] = vfor(vname(p[2][1], line=p[2][0]), (p[4], p[6]), p[7], line=p[1][0])


def p_statement_for_step(p):
    """statement : FOR NAME '=' expression TO expression STEP expression statements NEXT"""
    p[0] = vforstep(vname(p[2][1], line=p[2][0]),
                    (p[4], p[6]), p[8], p[9], line=p[1][0])


def p_statement_while(p):
    """statement : WHILE expression newline statements WEND"""
    p[0] = vdowhileloop(p[2], p[4], line=p[1][0])


def p_statement_try(p):
    """statement : TRY statements END
                 | TRY statements END TRY"""
    p[0] = vtry(p[2], vtrycatches(), line=p[1][0])


def p_statement_try_catch(p):
    """statement : TRY statements CATCH statements END
                 | TRY statements CATCH statements END TRY"""
    p[0] = vtry(p[2], vtrycatches().join(
        vtrycatch(p[4], line=p[3][0])), line=p[1][0])


def p_statement_try_catches(p):
    """statement : TRY statements catches END
                 | TRY statements catches END TRY"""
    p[0] = vtry(p[2], p[3], line=p[1][0])


def p_statement_try_catches_catch(p):
    """statement : TRY statements catches CATCH statements END
                 | TRY statements catches CATCH statements END TRY"""
    p[0] = vtry(p[2], p[3].join(vtrycatch(p[5], line=p[4][0])), line=p[1][0])


def p_statement_try_finally(p):
    """statement : TRY statements FINALLY statements END
                 | TRY statements FINALLY statements END TRY"""
    p[0] = vtryfinally(p[2], vtrycatches(), p[4], line=p[1][0])


def p_statement_try_catch_finally(p):
    """statement : TRY statements CATCH statements FINALLY statements END
                 | TRY statements CATCH statements FINALLY statements END TRY"""
    p[0] = vtryfinally(p[2], vtrycatches().join(
        vtrycatch(p[4], line=p[3][0])), p[6], line=p[1][0], finally_line=p[5][0])


def p_statement_try_catches_finally(p):
    """statement : TRY statements catches FINALLY statements END
                 | TRY statements catches FINALLY statements END TRY"""
    p[0] = vtryfinally(p[2], p[3], p[5], line=p[1][0])


def p_statement_try_catches_catch_finally(p):
    """statement : TRY statements catches CATCH statements FINALLY statements END
                 | TRY statements catches CATCH statements FINALLY statements END TRY"""
    p[0] = vtryfinally(p[2], p[3].join(
        vtrycatch(p[5], line=p[4][0])), p[7], line=p[1][0], finally_line=p[6][0])


def p_statement_throw(p):
    """statement : THROW"""
    p[0] = vthrow(line=p[1][0])


def p_statement_throw_name(p):
    """statement : THROW NAME"""
    p[0] = vthrow(p[2][1], line=p[1][0])


def p_statement_with(p):
    """statement : WITH NAME statements END
                 | WITH NAME statements END WITH"""
    p[0] = vwith(p[2][1], p[3], line=p[1][0])


def p_statement_exit_function(p):
    """statement : EXIT FUNCTION"""
    p[0] = vexitfunction(line=p[1][0])


def p_statement_exit_sub(p):
    """statement : EXIT SUB"""
    p[0] = vexitsub(line=p[1][0])


def p_statement_exit_property(p):
    """statement : EXIT PROPERTY"""
    p[0] = vexitproperty(line=p[1][0])


def p_statement_exit_do(p):
    """statement : EXIT DO"""
    p[0] = vexitdo(line=p[1][0])


def p_statement_exit_for(p):
    """statement : EXIT FOR"""
    p[0] = vexitfor(line=p[1][0])


def p_statement_randomize(p):
    """statement : RANDOMIZE"""
    p[0] = vrandomize(line=p[1][0])


def p_statement_randomize_number(p):
    """statement : RANDOMIZE NUMBER"""
    p[0] = vrandomize(seed=p[2][1], line=p[1][0])


def p_statement_print(p):
    """statement : PRINT expressions"""
    p[0] = vprint(p[2], line=p[1][0])


def p_statement_touch(p):
    """statement : TOUCH expressions"""
    p[0] = vtouch(p[2], line=p[1][0])


def p_statements_m_starts_empty(p):
    """statements_m : empty"""
    p[0] = vstatements()


def p_statements_m_starts_newline(p):
    """statements_m : newline"""
    p[0] = vstatements()


def p_statements_m_starts_statement(p):
    """statements_m : cstatements_m"""
    p[0] = p[1]


def p_statements_m_starts_newline_statement(p):
    """statements_m : newline cstatements_m"""
    p[0] = p[2]


def p_statements_m_starts_statement_newline(p):
    """statements_m : cstatements_m newline"""
    p[0] = p[1]


def p_statements_m_starts_newline_statement_newline(p):
    """statements_m : newline cstatements_m newline"""
    p[0] = p[2]


def p_cstatements_m_starts_statement(p):
    """cstatements_m : statement"""
    p[0] = vstatements().join(p[1])


def p_cstatements_m_starts_procedure(p):
    """cstatements_m : procedure"""
    p[0] = vstatements().join(p[1])


def p_cstatements_m_starts_class_declaration(p):
    """cstatements_m : class"""
    p[0] = vstatements().join(p[1])


def p_cstatements_m_continues_with_colon_statement(p):
    """cstatements_m : cstatements_m ':' statement"""
    p[0] = p[1].join(p[3])


def p_cstatements_m_continues_with_newline_statement(p):
    """cstatements_m : cstatements_m newline statement"""
    p[0] = p[1].join(p[3])


def p_cstatements_m_continues_with_colon_procedure(p):
    """cstatements_m : cstatements_m ':' procedure"""
    p[0] = p[1].join(p[3])


def p_cstatements_m_continues_with_newline_procedure(p):
    """cstatements_m : cstatements_m newline procedure"""
    p[0] = p[1].join(p[3])


def p_cstatements_m_continues_with_colon_class(p):
    """cstatements_m : cstatements_m ':' class"""
    p[0] = p[1].join(p[3])


def p_cstatements_m_continues_with_newline_class(p):
    """cstatements_m : cstatements_m newline class"""
    p[0] = p[1].join(p[3])


def p_class(p):
    """class : CLASS NAME statements_c END
             | CLASS NAME statements_c END CLASS"""
    p[0] = vclass(p[2][1], p[3], line=p[1][0])


def p_statements_continues_with_starts_empty(p):
    """statements_c : empty"""
    p[0] = vstatements()


def p_statements_continues_with_starts_newline(p):
    """statements_c : newline"""
    p[0] = vstatements()


def p_statements_continues_with_starts_statement(p):
    """statements_c : cstatements_c"""
    p[0] = p[1]


def p_statements_continues_with_starts_newline_statement(p):
    """statements_c : newline cstatements_c"""
    p[0] = p[2]


def p_statements_continues_with_starts_statement_newline(p):
    """statements_c : cstatements_c newline"""
    p[0] = p[1]


def p_statements_continues_with_starts_newline_statement_newline(p):
    """statements_c : newline cstatements_c newline"""
    p[0] = p[2]


def p_cstatements_starts_empty(p):
    """cstatements_c : empty"""
    p[0] = vstatements().join(p[1])


def p_cstatements_starts_inherits(p):
    """cstatements_c : inherits"""
    p[0] = vstatements().join(p[1])


def p_cstatements_starts_declarations(p):
    """cstatements_c : declarations"""
    p[0] = vstatements().join(p[1])


def p_cstatements_starts_procedure(p):
    """cstatements_c : procedure"""
    p[0] = vstatements().join(p[1])


def p_cstatements_starts_property(p):
    """cstatements_c : property"""
    p[0] = vstatements().join(p[1])


def p_cstatements_continues_with_inherits(p):
    """cstatements_c : cstatements_c ':' inherits
                     | cstatements_c newline inherits"""
    p[0] = p[1].join(p[3])


def p_cstatements_continues_with_declaration(p):
    """cstatements_c : cstatements_c ':' declarations
                     | cstatements_c newline declarations"""
    p[0] = p[1].join(p[3])


def p_cstatements_continues_with_procedure(p):
    """cstatements_c : cstatements_c ':' procedure
                     | cstatements_c newline procedure"""
    p[0] = p[1].join(p[3])


def p_cstatements_continues_with_property(p):
    """cstatements_c : cstatements_c ':' property
                     | cstatements_c newline property"""
    p[0] = p[1].join(p[3])


def p_inherits(p):
    """inherits : INHERITS NAME"""
    p[0] = vinherits(name=p[2][1], line=p[1][0])


def p_function_without_agruments(p):
    """procedure : FUNCTION NAME statements END
                 | FUNCTION NAME statements END FUNCTION"""
    p[0] = vfunction(p[2][1], varguments(), p[3], line=p[1][0])


def p_function_with_agruments(p):
    """procedure : FUNCTION NAME '(' arguments ')' statements END
                 | FUNCTION NAME '(' arguments ')' statements END FUNCTION"""
    p[0] = vfunction(p[2][1], p[4], p[6], line=p[1][0])


def p_sub_without_agruments(p):
    """procedure : SUB NAME statements END
                 | SUB NAME statements END SUB"""
    p[0] = vsub(p[2][1], varguments(), p[3], line=p[1][0])


def p_sub_with_agruments(p):
    """procedure : SUB NAME '(' arguments ')' statements END
                 | SUB NAME '(' arguments ')' statements END SUB"""
    p[0] = vsub(p[2][1], p[4], p[6], line=p[1][0])


def p_property_get_without_agruments(p):
    """property : PROPERTY GET NAME statements END
                | PROPERTY GET NAME statements END PROPERTY"""
    p[0] = vpropertyget(p[3][1], varguments(), p[4], line=p[1][0])


def p_property_get_with_agruments(p):
    """property : PROPERTY GET NAME '(' arguments ')' statements END
                | PROPERTY GET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertyget(p[3][1], p[5], p[7], line=p[1][0])


def p_property_let_without_agruments(p):
    """property : PROPERTY LET NAME statements END
                | PROPERTY LET NAME statements END PROPERTY"""
    p[0] = vpropertylet(p[3][1], varguments(), p[4], line=p[1][0])


def p_property_let_with_agruments(p):
    """property : PROPERTY LET NAME '(' arguments ')' statements END
                | PROPERTY LET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertylet(p[3][1], p[5], p[7], line=p[1][0])


def p_property_set_without_agruments(p):
    """property : PROPERTY SET NAME statements END
                | PROPERTY SET NAME statements END PROPERTY"""
    p[0] = vpropertyset(p[3][1], varguments(), p[4], line=p[1][0])


def p_property_set_with_agruments(p):
    """property : PROPERTY SET NAME '(' arguments ')' statements END
                | PROPERTY SET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertyset(p[3][1], p[5], p[7], line=p[1][0])


def p_function_default_without_agruments(p):
    """procedure : DEFAULT FUNCTION NAME statements END
                 | DEFAULT FUNCTION NAME statements END FUNCTION"""
    p[0] = vpropertyget(p[3][1], varguments(), p[4],
                        default=True, line=p[1][0])


def p_function_default_with_agruments(p):
    """procedure : DEFAULT FUNCTION NAME '(' arguments ')' statements END
                 | DEFAULT FUNCTION NAME '(' arguments ')' statements END FUNCTION"""
    p[0] = vpropertyget(p[3][1], p[5], p[7], default=True, line=p[1][0])


def p_property_get_default_without_agruments(p):
    """property : DEFAULT PROPERTY GET NAME statements END
                | DEFAULT PROPERTY GET NAME statements END PROPERTY"""
    p[0] = vpropertyget(p[4][1], varguments(), p[5],
                        default=True, line=p[1][0])


def p_property_get_default_with_agruments(p):
    """property : DEFAULT PROPERTY GET NAME '(' arguments ')' statements END
                | DEFAULT PROPERTY GET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertyget(p[4][1], p[6], p[8], default=True, line=p[1][0])


def p_function_public_without_agruments(p):
    """procedure : PUBLIC FUNCTION NAME statements END
                 | PUBLIC FUNCTION NAME statements END FUNCTION"""
    p[0] = vfunction(p[3][1], varguments(), p[4], line=p[1][0])


def p_function_public_with_agruments(p):
    """procedure : PUBLIC FUNCTION NAME '(' arguments ')' statements END
                 | PUBLIC FUNCTION NAME '(' arguments ')' statements END FUNCTION"""
    p[0] = vfunction(p[3][1], p[5], p[7], line=p[1][0])


def p_sub_public_without_agruments(p):
    """procedure : PUBLIC SUB NAME statements END
                 | PUBLIC SUB NAME statements END SUB"""
    p[0] = vsub(p[3][1], varguments(), p[4], line=p[1][0])


def p_sub_public_with_agruments(p):
    """procedure : PUBLIC SUB NAME '(' arguments ')' statements END
                 | PUBLIC SUB NAME '(' arguments ')' statements END SUB"""
    p[0] = vsub(p[3][1], p[5], p[7], line=p[1][0])


def p_property_get_public_without_agruments(p):
    """property : PUBLIC PROPERTY GET NAME statements END
                | PUBLIC PROPERTY GET NAME statements END PROPERTY"""
    p[0] = vpropertyget(p[4][1], varguments(), p[5], line=p[1][0])


def p_property_get_public_with_agruments(p):
    """property : PUBLIC PROPERTY GET NAME '(' arguments ')' statements END
                | PUBLIC PROPERTY GET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertyget(p[4][1], p[6], p[8], line=p[1][0])


def p_property_let_public_without_agruments(p):
    """property : PUBLIC PROPERTY LET NAME statements END
                | PUBLIC PROPERTY LET NAME statements END PROPERTY"""
    p[0] = vpropertylet(p[4][1], varguments(), p[5], line=p[1][0])


def p_property_let_public_with_agruments(p):
    """property : PUBLIC PROPERTY LET NAME '(' arguments ')' statements END
                | PUBLIC PROPERTY LET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertylet(p[4][1], p[6], p[8], line=p[1][0])


def p_property_set_public_without_agruments(p):
    """property : PUBLIC PROPERTY SET NAME statements END
                | PUBLIC PROPERTY SET NAME statements END PROPERTY"""
    p[0] = vpropertyset(p[4][1], varguments(), p[5], line=p[1][0])


def p_property_set_public_with_agruments(p):
    """property : PUBLIC PROPERTY SET NAME '(' arguments ')' statements END
                | PUBLIC PROPERTY SET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertyset(p[4][1], p[6], p[8], line=p[1][0])


def p_function_public_default_without_agruments(p):
    """procedure : PUBLIC DEFAULT FUNCTION NAME statements END
                 | PUBLIC DEFAULT FUNCTION NAME statements END FUNCTION"""
    p[0] = vpropertyget(p[4][1], varguments(), p[5],
                        default=True, line=p[1][0])


def p_function_public_default_with_agruments(p):
    """procedure : PUBLIC DEFAULT FUNCTION NAME '(' arguments ')' statements END
                 | PUBLIC DEFAULT FUNCTION NAME '(' arguments ')' statements END FUNCTION"""
    p[0] = vpropertyget(p[4][1], p[6], p[8], default=True, line=p[1][0])


def p_property_get_public_default_without_agruments(p):
    """property : PUBLIC DEFAULT PROPERTY GET NAME statements END
                | PUBLIC DEFAULT PROPERTY GET NAME statements END PROPERTY"""
    p[0] = vpropertyget(p[5][1], varguments(), p[6],
                        default=True, line=p[1][0])


def p_property_get_public_default_with_agruments(p):
    """property : PUBLIC DEFAULT PROPERTY GET NAME '(' arguments ')' statements END
                | PUBLIC DEFAULT PROPERTY GET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertyget(p[5][1], p[7], p[9], default=True, line=p[1][0])


def p_function_private_without_agruments(p):
    """procedure : PRIVATE FUNCTION NAME statements END
                 | PRIVATE FUNCTION NAME statements END FUNCTION"""
    p[0] = vfunction(p[3][1], varguments(), p[4], line=p[1][0])


def p_function_private_with_agruments(p):
    """procedure : PRIVATE FUNCTION NAME '(' arguments ')' statements END
                 | PRIVATE FUNCTION NAME '(' arguments ')' statements END FUNCTION"""
    p[0] = vfunction(p[3][1], p[5], p[7], line=p[1][0])


def p_sub_private_without_agruments(p):
    """procedure : PRIVATE SUB NAME statements END
                 | PRIVATE SUB NAME statements END SUB"""
    p[0] = vsub(p[3][1], varguments(), p[4], line=p[1][0])


def p_sub_private_with_agruments(p):
    """procedure : PRIVATE SUB NAME '(' arguments ')' statements END
                 | PRIVATE SUB NAME '(' arguments ')' statements END SUB"""
    p[0] = vsub(p[3][1], p[5], p[7], line=p[1][0])


def p_property_get_private_without_agruments(p):
    """property : PRIVATE PROPERTY GET NAME statements END
                | PRIVATE PROPERTY GET NAME statements END PROPERTY"""
    p[0] = vpropertyget(p[4][1], varguments(), p[5], line=p[1][0])


def p_property_get_private_with_agruments(p):
    """property : PRIVATE PROPERTY GET NAME '(' arguments ')' statements END
                | PRIVATE PROPERTY GET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertyget(p[4][1], p[6], p[8], line=p[1][0])


def p_property_let_private_without_agruments(p):
    """property : PRIVATE PROPERTY LET NAME statements END
                | PRIVATE PROPERTY LET NAME statements END PROPERTY"""
    p[0] = vpropertylet(p[4][1], varguments(), p[5], line=p[1][0])


def p_property_let_private_with_agruments(p):
    """property : PRIVATE PROPERTY LET NAME '(' arguments ')' statements END
                | PRIVATE PROPERTY LET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertylet(p[4][1], p[6], p[8], line=p[1][0])


def p_property_set_private_without_agruments(p):
    """property : PRIVATE PROPERTY SET NAME statements END
                | PRIVATE PROPERTY SET NAME statements END PROPERTY"""
    p[0] = vpropertyset(p[4][1], varguments(), p[5], line=p[1][0])


def p_property_set_private_with_agruments(p):
    """property : PRIVATE PROPERTY SET NAME '(' arguments ')' statements END
                | PRIVATE PROPERTY SET NAME '(' arguments ')' statements END PROPERTY"""
    p[0] = vpropertyset(p[4][1], p[6], p[8], line=p[1][0])


def p_statements_starts_empty(p):
    """statements : empty"""
    p[0] = vstatements()


def p_statements_starts_newline(p):
    """statements : newline"""
    p[0] = vstatements()


def p_statements_starts_statement(p):
    """statements : cstatements"""
    p[0] = p[1]


def p_statements_starts_newline_statement(p):
    """statements : newline cstatements"""
    p[0] = p[2]


def p_statements_starts_statement_newline(p):
    """statements : cstatements newline"""
    p[0] = p[1]


def p_statements_starts_newline_statement_newline(p):
    """statements : newline cstatements newline"""
    p[0] = p[2]


def p_cstatements_starts_statement(p):
    """cstatements : statement"""
    p[0] = vstatements().join(p[1])


def p_cstatements_continues_with_colon_statement(p):
    """cstatements : cstatements ':' statement"""
    p[0] = p[1].join(p[3])


def p_cstatements_continues_with_newline_statement(p):
    """cstatements : cstatements newline statement"""
    p[0] = p[1].join(p[3])


def p_redim_starts_array(p):
    """redim : REDIM NAME '(' expressions ')'"""
    p[0] = vredim(0, line=p[1][0]).join(vname(p[2][1], line=p[1][0]), p[4])


def p_redim_starts_array_with_preserve(p):
    """redim : REDIM PRESERVE NAME '(' expressions ')'"""
    p[0] = vredim(1, line=p[1][0]).join(vname(p[3][1], line=p[1][0]), p[5])


def p_redim_continues_with_array(p):
    """redim : redim ',' NAME '(' expressions ')'"""
    p[0] = p[1].join(vname(p[3][1], line=p[3][0]), p[5])


def p_declarations_starts_variable(p):
    """declarations : DIM NAME"""
    p[0] = vdeclarations(line=p[1][0]).join(p[2][1], u"variant()")


def p_declarations_starts_empty_array(p):
    """declarations : DIM NAME '(' ')'"""
    p[0] = vdeclarations(line=p[1][0]).join(p[2][1], u"variant(array())")


def p_declarations_starts_array(p):
    """declarations : DIM NAME '(' subscripts ')'"""
    p[0] = vdeclarations(line=p[1][0]).join(
        p[2][1], u"permanent(array(subscripts=%s, static=1))" % p[4])


def p_declarations_continues_with_variable(p):
    """declarations : declarations ',' NAME"""
    p[0] = p[1].join(p[3][1], u"variant()")


def p_declarations_continues_with_empty_array(p):
    """declarations : declarations ',' NAME '(' ')'"""
    p[0] = p[1].join(p[3][1], u"variant(array())")


def p_declarations_continues_with_array(p):
    """declarations : declarations ',' NAME '(' subscripts ')'"""
    p[0] = p[1].join(p[3][1], u"variant(array(subscripts=%s))" % p[5])


def p_subscripts_starts(p):
    """subscripts : NUMBER"""
    p[0] = vsubscripts().join(int(p[1][1]))


def p_subscripts_continues(p):
    """subscripts : subscripts ',' NUMBER"""
    p[0] = p[1].join(int(p[3][1]))


def p_source(p):
    """source : statements_m"""
    p[0] = vsource(p[1], package=p.parser.package,
                   environment=p.parser.environment)


def p_error(p):
    if isinstance(p, tuple):
        raise errors.syntax_error(p.value[1], p.lexer.lineno)
    elif isinstance(p, bytes):
        raise errors.syntax_error(p.value)
    elif isinstance(p, lex.LexToken):
        if p.type == "NEWLINE":
            raise errors.syntax_error("CR/LF", p.lineno)
        elif isinstance(p.value, tuple):
            raise errors.syntax_error(p.value[1], p.lineno)
        elif isinstance(p.value, bytes):
            raise errors.syntax_error(p.value, p.lineno)
        else:
            debug("!!! STRANGE LEXTOKEN VALUE !!!", console=True)
            raise errors.syntax_error(p.value, p.lineno)
        raise errors.syntax_error(p.value, p.lineno)
    else:
        raise errors.unknown_syntax_error
