
from ...testing import raises, VScriptTestCase
from ... import errors
from ...subtypes import mismatch, empty, null, integer, string, double, \
    boolean, error, binary, date, array, dictionary, generic, nothing, \
    nan, infinity, true, false, v_mismatch, v_empty, v_null, v_nothing


class TestConstants(VScriptTestCase):

    def test_vcrlf_constant(self):
        assert self.evaluate("vcrlf").is_string("\r\n")
        assert self.evaluate("vbcrlf").is_string("\r\n")

    def test_vcr_constant(self):
        assert self.evaluate("vcr").is_string("\r")
        assert self.evaluate("vbcr").is_string("\r")

    def test_vlf_constant(self):
        assert self.evaluate("vlf").is_string("\n")
        assert self.evaluate("vblf").is_string("\n")

    def test_vformfeed_constant(self):
        assert self.evaluate("vformfeed").is_string("\f")
        assert self.evaluate("vbformfeed").is_string("\f")

    def test_vnewline_constant(self):
        assert self.evaluate("vnewline").is_string("\n")
        assert self.evaluate("vbnewline").is_string("\n")

    def test_vnullchar_constant(self):
        assert self.evaluate("vnullchar").is_string("\0")
        assert self.evaluate("vbnullchar").is_string("\0")

    def test_vnullstring_constant(self):
        assert self.evaluate("vnullstring").is_string("\0")
        assert self.evaluate("vbnullstring").is_string("\0")

    def test_vtab_constant(self):
        assert self.evaluate("vtab").is_string("\t")
        assert self.evaluate("vbtab").is_string("\t")

    def test_vverticaltab_constant(self):
        assert self.evaluate("vverticaltab").is_string("\v")
        assert self.evaluate("vbverticaltab").is_string("\v")

    def test_vbinarycompare_constant(self):
        assert self.evaluate("vbinarycompare").is_integer(0)
        assert self.evaluate("vbbinarycompare").is_integer(0)

    def test_vtextcompare_constant(self):
        assert self.evaluate("vtextcompare").is_integer(1)
        assert self.evaluate("vbtextcompare").is_integer(1)

    def test_vdatabasecompare_constant(self):
        assert self.evaluate("vdatabasecompare").is_integer(2)
        assert self.evaluate("vbdatabasecompare").is_integer(2)

    def test_vgeneraldate_constant(self):
        assert self.evaluate("vgeneraldate").is_integer(0)
        assert self.evaluate("vbgeneraldate").is_integer(0)

    def test_vlongdate_constant(self):
        assert self.evaluate("vlongdate").is_integer(1)
        assert self.evaluate("vblongdate").is_integer(1)

    def test_vshortdate_constant(self):
        assert self.evaluate("vshortdate").is_integer(2)
        assert self.evaluate("vbshortdate").is_integer(2)

    def test_vlongtime_constant(self):
        assert self.evaluate("vlongtime").is_integer(3)
        assert self.evaluate("vblongtime").is_integer(3)

    def test_vshorttime_constant(self):
        assert self.evaluate("vshorttime").is_integer(4)
        assert self.evaluate("vbshorttime").is_integer(4)

    def test_vusedefault_constant(self):
        assert self.evaluate("vusedefault").is_integer(-2)
        assert self.evaluate("vbusedefault").is_integer(-2)

    def test_vtrue_constant(self):
        assert self.evaluate("vtrue").is_integer(-1)
        assert self.evaluate("vbtrue").is_integer(-1)

    def test_vfalse_constant(self):
        assert self.evaluate("vfalse").is_integer(0)
        assert self.evaluate("vbfalse").is_integer(0)

    def test_vusesystemdayofweek_constant(self):
        assert self.evaluate("vusesystemdayofweek").is_integer(0)
        assert self.evaluate("vbusesystemdayofweek").is_integer(0)

    def test_vsunday_constant(self):
        assert self.evaluate("vsunday").is_integer(1)
        assert self.evaluate("vbsunday").is_integer(1)

    def test_vmonday_constant(self):
        assert self.evaluate("vmonday").is_integer(2)
        assert self.evaluate("vbmonday").is_integer(2)

    def test_vtuesday_constant(self):
        assert self.evaluate("vtuesday").is_integer(3)
        assert self.evaluate("vbtuesday").is_integer(3)

    def test_vwednesday_constant(self):
        assert self.evaluate("vwednesday").is_integer(4)
        assert self.evaluate("vbwednesday").is_integer(4)

    def test_vthursday_constant(self):
        assert self.evaluate("vthursday").is_integer(5)
        assert self.evaluate("vbthursday").is_integer(5)

    def test_vfriday_constant(self):
        assert self.evaluate("vfriday").is_integer(6)
        assert self.evaluate("vbfriday").is_integer(6)

    def test_vsaturday_constant(self):
        assert self.evaluate("vsaturday").is_integer(7)
        assert self.evaluate("vbsaturday").is_integer(7)

    def test_vusesystem_constant(self):
        assert self.evaluate("vusesystem").is_integer(0)
        assert self.evaluate("vbusesystem").is_integer(0)

    def test_vfirstjan1_constant(self):
        assert self.evaluate("vfirstjan1").is_integer(1)
        assert self.evaluate("vbfirstjan1").is_integer(1)

    def test_vfirstfourdays_constant(self):
        assert self.evaluate("vfirstfourdays").is_integer(2)
        assert self.evaluate("vbfirstfourdays").is_integer(2)

    def test_vfirstfullweek_constant(self):
        assert self.evaluate("vfirstfullweek").is_integer(3)
        assert self.evaluate("vbfirstfullweek").is_integer(3)
