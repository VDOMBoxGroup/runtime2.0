
import datetime
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestChronologyRoutines(VScriptTestCase):

    def test_date_function(self):
        assert self.evaluate("date").is_date()

    def test_time_function(self):
        assert self.evaluate("time").is_date()

    def test_now_function(self):
        assert self.evaluate("now").is_date()


    def test_timer_function(self):
        assert self.evaluate("timer").is_integer()


    def test_dateserial_function(self):
        assert self.evaluate("dateserial(1991, 12, 21)").is_date(1991, 12, 21)
        assert self.evaluate("dateserial(91, 12, 21)").is_date(1991, 12, 21)
        with raises(errors.type_mismatch):
            self.execute("""dateserial("abc", 12, 21)""")
        with raises(errors.type_mismatch):
            self.execute("""dateserial(1991, "abc", 21)""")
        with raises(errors.type_mismatch):
            self.execute("""dateserial(1991, 12, "abc")""")

    def test_timeserial_function(self):
        assert self.evaluate("""timeserial(11, 22, 33)""").is_date(hour=11, minute=22, second=33)
        with raises(errors.type_mismatch):
            self.execute("""timeserial("abc", 22, 33)""")
        with raises(errors.type_mismatch):
            self.execute("""timeserial(11, "abc", 33)""")
        with raises(errors.type_mismatch):
            self.execute("""timeserial(11, 22, "abc")""")

    def test_datevalue_function(self):
        assert self.evaluate("""datevalue("1991.12.21")""").is_date(1991, 12, 21)
        with raises(errors.type_mismatch):
            self.execute("""datevalue("abc")""")

    def test_timevalue_function(self):
        assert self.evaluate("""timevalue("11:22:33")""").is_date(hour=11, minute=22, second=33)
        with raises(errors.type_mismatch):
            self.execute("""timevalue("abc")""")

    def test_datepart_function(self):
        assert self.evaluate("""datepart("yyyy", #1991.12.21 11:22:33#)""").is_integer(1991)
        assert self.evaluate("""datepart("m", #1991.12.21 11:22:33#)""").is_integer(12)
        assert self.evaluate("""datepart("d", #1991.12.21 11:22:33#)""").is_integer(21)
        assert self.evaluate("""datepart("h", #1991.12.21 11:22:33#)""").is_integer(11)
        assert self.evaluate("""datepart("n", #1991.12.21 11:22:33#)""").is_integer(22)
        assert self.evaluate("""datepart("s", #1991.12.21 11:22:33#)""").is_integer(33)
        assert self.evaluate("""datepart("w", #1991.12.21 11:22:33#, vmonday)""").is_integer(6)
        assert self.evaluate("""datepart("w", #1991.12.21 11:22:33#)""").is_integer(7)
        assert self.evaluate("""datepart("y", #1991.12.21 11:22:33#)""").is_integer(355)
        assert self.evaluate("""datepart("ww", #1991.12.21 11:22:33#)""").is_integer(51)
        assert self.evaluate("""datepart("q", #1991.12.21 11:22:33#)""").is_integer(4)
        with raises(errors.invalid_procedure_call):
            self.execute("""datepart("abc", #1991.12.21 11:22:33#)""")
        with raises(errors.type_mismatch):
            self.execute("""datepart("yyyy", "abc")""")

    def test_year_function(self):
        assert self.evaluate("""year(#1991.12.21 11:22:33#)""").is_integer(1991)
        with raises(errors.type_mismatch):
            self.execute("""year("abc")""")

    def test_month_function(self):
        assert self.evaluate("""month(#1991.12.21 11:22:33#)""").is_integer(12)
        with raises(errors.type_mismatch):
            self.execute("""month("abc")""")

    def test_day_function(self):
        assert self.evaluate("""day(#1991.12.21 11:22:33#)""").is_integer(21)
        with raises(errors.type_mismatch):
            self.execute("""day("abc")""")

    def test_hour_function(self):
        assert self.evaluate("""hour(#1991.12.21 11:22:33#)""").is_integer(11)
        with raises(errors.type_mismatch):
            self.execute("""hour("abc")""")

    def test_minute_function(self):
        assert self.evaluate("""minute(#1991.12.21 11:22:33#)""").is_integer(22)
        with raises(errors.type_mismatch):
            self.execute("""minute("abc")""")

    def test_second_function(self):
        assert self.evaluate("""second(#1991.12.21 11:22:33#)""").is_integer(33)
        with raises(errors.type_mismatch):
            self.execute("""second("abc")""")

    def test_weekday_function(self):
        assert self.evaluate("""weekday(#1991.12.21 11:22:33#, vmonday)""").is_integer(6)
        assert self.evaluate("""weekday(#1991.12.21 11:22:33#)""").is_integer(7)
        with raises(errors.type_mismatch):
            self.execute("""weekday("abc", vmonday)""")

    def test_dateadd_function(self):
        assert self.evaluate("""dateadd("yyyy", 1, #1991.12.21 11:22:33#)""").is_date(1992, 12, 21, 11, 22, 33)
        assert self.evaluate("""dateadd("m", 1, #1991.12.21 11:22:33#)""").is_date(1992, 1, 21, 11, 22, 33)
        assert self.evaluate("""dateadd("d", 1, #1991.12.21 11:22:33#)""").is_date(1991, 12, 22, 11, 22, 33)
        assert self.evaluate("""dateadd("h", 1, #1991.12.21 11:22:33#)""").is_date(1991, 12, 21, 12, 22, 33)
        assert self.evaluate("""dateadd("n", 1, #1991.12.21 11:22:33#)""").is_date(1991, 12, 21, 11, 23, 33)
        assert self.evaluate("""dateadd("s", 1, #1991.12.21 11:22:33#)""").is_date(1991, 12, 21, 11, 22, 34)
        assert self.evaluate("""dateadd("w", 1, #1991.12.21 11:22:33#)""").is_date(1991, 12, 22, 11, 22, 33)
        assert self.evaluate("""dateadd("y", 1, #1991.12.21 11:22:33#)""").is_date(1991, 12, 22, 11, 22, 33)
        assert self.evaluate("""dateadd("ww", 1, #1991.12.21 11:22:33#)""").is_date(1991, 12, 28, 11, 22, 33)
        assert self.evaluate("""dateadd("q", 1, #1991.12.21 11:22:33#)""").is_date(1992, 3, 21, 11, 22, 33)
        with raises(errors.invalid_procedure_call):
            self.execute("""dateadd("abc", 1, #1991.12.21 11:22:33#)""")
        with raises(errors.type_mismatch):
            self.execute("""dateadd("yyyy", "abc", #1991.12.21 11:22:33#)""")
        with raises(errors.type_mismatch):
            self.execute("""dateadd("yyyy", 1, "abc")""")

    def test_datediff_function(self):
        assert self.evaluate("""datediff("yyyy", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#)""").is_integer(1)
        assert self.evaluate("""datediff("m", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#)""").is_integer(12)
        assert self.evaluate("""datediff("d", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#)""").is_integer(366)
        assert self.evaluate("""datediff("h", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#)""").is_integer(8784)
        assert self.evaluate("""datediff("n", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#)""").is_integer(527040)
        assert self.evaluate("""datediff("s", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#)""").is_integer(31622400)
        assert self.evaluate("""datediff("y", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#)""").is_integer(366)
        assert self.evaluate("""datediff("w", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#, vmonday)""").is_integer(52)
        assert self.evaluate("""datediff("ww", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#, vmonday)""").is_integer(53)
        assert self.evaluate("""datediff("q", #1991.12.21 11:22:33#, #1992.12.21 11:22:33#)""").is_integer(4)
        with raises(errors.invalid_procedure_call):
            self.execute("""datediff("abc", #1991.12.21 11:22:33#, #1992.12.21 22:33:44#)""")
        with raises(errors.type_mismatch):
            self.execute("""datediff("yyyy", "abc", #1992.12.21 22:33:44#)""")
        with raises(errors.type_mismatch):
            self.execute("""datediff("yyyy", #1991.12.21 11:22:33#, "abc")""")

    def test_monthname_function(self):
        assert self.evaluate("""monthname(1)""").is_string()
        with raises(errors.type_mismatch):
            self.execute("""monthname("abc")""")

    def test_weekdayname_function(self):
        assert self.evaluate("""weekdayname(1)""").is_string()
        with raises(errors.type_mismatch):
            self.execute("""weekdayname("abc")""")
            