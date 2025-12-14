
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestFormattingRoutines(VScriptTestCase):

    def test_formatdatetime_function(self):
        assert self.evaluate("formatdatetime(#00:00:00#)").is_string("00:00:00")
        assert self.evaluate("formatdatetime(#30.12.1899#)").is_string("00:00:00")
        assert self.evaluate("formatdatetime(#01.01.2001#)").is_string("2001-01-01")
        assert self.evaluate("formatdatetime(#01:01:01#)").is_string("01:01:01")
        assert self.evaluate("formatdatetime(#01.01.2001 01:01:01#)").is_string("2001-01-01 01:01:01")
        assert self.evaluate("formatdatetime(#01.01.2001 01:01:01#, vgeneraldate)").is_string("2001-01-01 01:01:01")
        assert self.evaluate("formatdatetime(#01.01.2001 01:01:01#, vlongdate)").is_string("2001-01-01")
        assert self.evaluate("formatdatetime(#01.01.2001 01:01:01#, vshortdate)").is_string("2001-01-01")
        assert self.evaluate("formatdatetime(#01.01.2001 01:01:01#, vlongtime)").is_string("01:01:01")
        assert self.evaluate("formatdatetime(#01.01.2001 01:01:01#, vshorttime)").is_string("01:01")
        with raises(errors.type_mismatch):
            self.evaluate("formatdatetime(\"abc\")")
        with raises(errors.invalid_procedure_call):
            self.evaluate("formatdatetime(#01.01.2001#, 5)")

    def test_formatnumber_function(self):
        assert self.evaluate("formatnumber(0.123)").is_string("0.12")
        assert self.evaluate("formatnumber(123.456)").is_string("123.46")
        assert self.evaluate("formatnumber(-0.123)").is_string("-0.12")
        assert self.evaluate("formatnumber(-123.456)").is_string("-123.46")

        assert self.evaluate("formatnumber(0.123, 0)").is_string("0")
        assert self.evaluate("formatnumber(123.456, 0)").is_string("123")
        assert self.evaluate("formatnumber(-0.123, 0)").is_string("-0")
        assert self.evaluate("formatnumber(-123.456, 0)").is_string("-123")
        assert self.evaluate("formatnumber(0.123, 3)").is_string("0.123")
        assert self.evaluate("formatnumber(123.456, 3)").is_string("123.456")
        assert self.evaluate("formatnumber(-0.123, 3)").is_string("-0.123")
        assert self.evaluate("formatnumber(-123.456, 3)").is_string("-123.456")

        assert self.evaluate("formatnumber(0.567, 0)").is_string("1")
        assert self.evaluate("formatnumber(-0.567, 0)").is_string("-1")

        assert self.evaluate("formatnumber(0.123, 2, vtrue)").is_string("0.12")
        assert self.evaluate("formatnumber(123.456, 2, vtrue)").is_string("123.46")
        assert self.evaluate("formatnumber(-0.123, 2, vtrue)").is_string("-0.12")
        assert self.evaluate("formatnumber(-123.456, 2, vtrue)").is_string("-123.46")
        assert self.evaluate("formatnumber(0.123, 2, vfalse)").is_string(".12")
        assert self.evaluate("formatnumber(123.456, 2, vfalse)").is_string("123.46")
        assert self.evaluate("formatnumber(-0.123, 2, vfalse)").is_string("-.12")
        assert self.evaluate("formatnumber(-123.456, 2, vfalse)").is_string("-123.46")

        assert self.evaluate("formatnumber(0.123, 2, vtrue, vfalse)").is_string("0.12")
        assert self.evaluate("formatnumber(123.456, 2, vtrue, vfalse)").is_string("123.46")
        assert self.evaluate("formatnumber(-0.123, 2, vtrue, vfalse)").is_string("-0.12")
        assert self.evaluate("formatnumber(-123.456, 2, vtrue, vfalse)").is_string("-123.46")
        assert self.evaluate("formatnumber(0.123, 2, vtrue, vtrue)").is_string("0.12")
        assert self.evaluate("formatnumber(123.456, 2, vtrue, vtrue)").is_string("123.46")
        assert self.evaluate("formatnumber(-0.123, 2, vtrue, vtrue)").is_string("(0.12)")
        assert self.evaluate("formatnumber(-123.456, 2, vtrue, vtrue)").is_string("(123.46)")

        assert self.evaluate("formatnumber(123456)").is_string("123456.00")
        assert self.evaluate("formatnumber(-123456)").is_string("-123456.00")
        assert self.evaluate("formatnumber(123456, 2, vtrue, vfalse, vfalse)").is_string("123456.00")
        assert self.evaluate("formatnumber(-123456, 2, vtrue, vfalse, vfalse)").is_string("-123456.00")
        assert self.evaluate("formatnumber(123456, 2, vtrue, vfalse, vtrue)").is_string("123 456.00")
        assert self.evaluate("formatnumber(-123456, 2, vtrue, vfalse, vtrue)").is_string("-123 456.00")

    def test_formatcurrency_function(self):
        assert self.evaluate("formatcurrency(0.123)").is_string("0.12")
        assert self.evaluate("formatcurrency(123.456)").is_string("123.46")
        assert self.evaluate("formatcurrency(-0.123)").is_string("-0.12")
        assert self.evaluate("formatcurrency(-123.456)").is_string("-123.46")

        assert self.evaluate("formatcurrency(123456)").is_string("123456.00")
        assert self.evaluate("formatcurrency(-123456)").is_string("-123456.00")
        assert self.evaluate("formatcurrency(123456, 2, vtrue, vtrue, vtrue)").is_string("123 456.00")
        assert self.evaluate("formatcurrency(-123456, 2, vtrue, vtrue, vtrue)").is_string("(123 456.00)")

    def test_formatpercent_function(self):
        assert self.evaluate("formatpercent(0.123)").is_string("12.30%")
        assert self.evaluate("formatpercent(123.456)").is_string("12345.60%")
        assert self.evaluate("formatpercent(-0.123)").is_string("-12.30%")
        assert self.evaluate("formatpercent(-123.456)").is_string("-12345.60%")

        assert self.evaluate("formatpercent(0.123456)").is_string("12.35%")
        assert self.evaluate("formatpercent(-0.123456)").is_string("-12.35%")
        assert self.evaluate("formatpercent(123.456, 2, vtrue, vtrue, vtrue)").is_string("12 345.60%")
        assert self.evaluate("formatpercent(-123.456, 2, vtrue, vtrue, vtrue)").is_string("(12 345.60%)")
