
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestMathematicsRoutines(VScriptTestCase):

    def test_abs_function(self):
        assert self.evaluate("abs(empty)").is_integer(0)
        assert self.evaluate("abs(null)").is_null
        assert self.evaluate("abs(123)").is_integer(123)
        assert self.evaluate("abs(-123)").is_integer(123)
        assert self.evaluate("abs(123.456)").is_double(123.456)
        assert self.evaluate("abs(-123.456)").is_double(123.456)
        assert self.evaluate("abs(#29.08.1899 10:56:38#)").is_date(1900, 5, 2, 10, 56, 38)
        assert self.evaluate("abs(\"-123\")").is_double(123)
        assert self.evaluate("abs(\"-123.456\")").is_double(123.456)
        with raises(errors.type_mismatch):
            self.evaluate("abs(\"abc\")")
        with raises(errors.object_has_no_property):
            self.evaluate("class object end", "abs(new object)")
        with raises(errors.object_variable_not_set):
            self.evaluate("abs(nothing)")
        assert self.evaluate("abs(true)").is_integer(1)
        assert self.evaluate("abs(false)").is_integer(0)

    def test_sgn_function(self):
        assert self.evaluate("sgn(empty)").is_integer(0)
        assert self.evaluate("sgn(123)").is_integer(1)
        assert self.evaluate("sgn(0)").is_integer(0)
        assert self.evaluate("sgn(-123)").is_integer(-1)
        assert self.evaluate("sgn(123.456)").is_integer(1)
        assert self.evaluate("sgn(0.0)").is_integer(0)
        assert self.evaluate("sgn(-123.456)").is_integer(-1)
        assert self.evaluate("sgn(\"123\")").is_integer(1)
        assert self.evaluate("sgn(\"123.456\")").is_integer(1)

    def test_round_function(self):
        assert self.evaluate("round(empty)").is_integer(0)
        assert self.evaluate("round(123)").is_integer(123)
        assert self.evaluate("round(0)").is_integer(0)
        assert self.evaluate("round(-123)").is_integer(-123)
        assert self.evaluate("round(123.456)").is_double(123.0)
        assert self.evaluate("round(0.0)").is_double(0.0)
        assert self.evaluate("round(-123.456)").is_double(-123.0)
        assert self.evaluate("round(\"123\")").is_double(123.0)
        assert self.evaluate("round(\"123.456\")").is_double(123.0)

    def test_exp_function(self):
        assert self.evaluate("exp(empty)").is_double(1.0)
        assert self.evaluate("exp(123)").is_double(2.61951731874906E+53)
        assert self.evaluate("exp(0)").is_double(1.0)
        assert self.evaluate("exp(-123)").is_double(3.81749718867117E-54)
        assert self.evaluate("exp(123.456)").is_double(4.13294435277811E+53)
        assert self.evaluate("exp(0.0)").is_double(1.0)
        assert self.evaluate("exp(-123.456)").is_double(2.41958254126459E-54)
        assert self.evaluate("exp(\"123\")").is_double(2.61951731874906E+53)
        assert self.evaluate("exp(\"123.456\")").is_double(4.13294435277811E+53)

    def test_int_function(self):
        assert self.evaluate("int(empty)").is_integer(0)
        assert self.evaluate("int(123)").is_integer(123)
        assert self.evaluate("int(0)").is_integer(0)
        assert self.evaluate("int(-123)").is_integer(-123)
        assert self.evaluate("int(123.456)").is_double(123.0)
        assert self.evaluate("int(0.0)").is_double(0.0)
        assert self.evaluate("int(-123.456)").is_double(-124.0)
        assert self.evaluate("int(\"123\")").is_double(123.0)
        assert self.evaluate("int(\"123.456\")").is_double(123.0)

    def test_fix_function(self):
        assert self.evaluate("fix(empty)").is_integer(0)
        assert self.evaluate("fix(123)").is_integer(123)
        assert self.evaluate("fix(0)").is_integer(0)
        assert self.evaluate("fix(-123)").is_integer(-123)
        assert self.evaluate("fix(123.456)").is_double(123.0)
        assert self.evaluate("fix(0.0)").is_double(0.0)
        assert self.evaluate("fix(-123.456)").is_double(-123.0)
        assert self.evaluate("fix(\"123\")").is_double(123.0)
        assert self.evaluate("fix(\"123.456\")").is_double(123.0)

    def test_log_function(self):
        with raises(errors.invalid_procedure_call):
            self.evaluate("log(empty)")
        assert self.evaluate("log(123)").is_double(4.81218435537242)
        with raises(errors.invalid_procedure_call):
            self.evaluate("log(0)")
        with raises(errors.invalid_procedure_call):
            self.evaluate("log(-123)")
        assert self.evaluate("log(123.456)").is_double(4.81588481728326)
        with raises(errors.invalid_procedure_call):
            self.evaluate("log(0.0)")
        with raises(errors.invalid_procedure_call):
            self.evaluate("log(-123.456)")
        assert self.evaluate("log(\"123\")").is_double(4.81218435537242)
        assert self.evaluate("log(\"123.456\")").is_double(4.81588481728326)

    def test_sqr_function(self):
        assert self.evaluate("sqr(empty)").is_double(0.0)
        assert self.evaluate("sqr(123)").is_double(11.0905365064094)
        assert self.evaluate("sqr(0)").is_double(0.0)
        with raises(errors.invalid_procedure_call):
            self.evaluate("sqr(-123)")
        assert self.evaluate("sqr(123.456)").is_double(11.1110755554987)
        assert self.evaluate("sqr(0.0)").is_double(0.0)
        with raises(errors.invalid_procedure_call):
            self.evaluate("sqr(-123.456)")
        assert self.evaluate("sqr(\"123\")").is_double(11.0905365064094)
        assert self.evaluate("sqr(\"123.456\")").is_double(11.1110755554987)
