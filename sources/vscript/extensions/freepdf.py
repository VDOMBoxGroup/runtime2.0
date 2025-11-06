
from builtins import str
from builtins import object
import re

from types import MethodType
from fpdf import FPDF

import managers
import file_access

from .. import errors
from ..subtypes import generic, integer, double, string, binary, boolean
from ..decorators import ignore, vsub, vfunction, vproperty


FONT_SIGNATURES = "(?P<TTF>\x00\x01\x00\x00\x00)"
IMAGE_SIGNATURES = "(?P<PNG>\x89PNG)|(?P<JPG>\xFF\xD8\xFF\xE0..JFIF)|(?P<GIF>GIF8[79]a)"


class FPDFWrapper(FPDF):

    def __init__(self, *arguments, **keywords):
        self._owner = keywords.pop("owner", None)
        super(FPDFWrapper, self).__init__(*arguments, **keywords)

    def error(self, message):
        raise errors.internal_error(message)

    def header(self):
        if self._owner._header:
            self._owner._header(self._owner)

    def footer(self):
        if self._owner._footer:
            self._owner._footer(self._owner)


class PDFProperty(object):

    def __get__(self, instance, owner=None):
        if instance is not None:
            instance._pdf = value = FPDFWrapper(instance._orientation, instance._unit, instance._format, owner=instance)
            return value


class v_fpdf(generic):

    _fonts_regex = re.compile(FONT_SIGNATURES)
    _images_regex = re.compile(IMAGE_SIGNATURES)

    def __init__(self):
        generic.__init__(self)
        self._orientation = "P"
        self._unit = "mm"
        self._format = "A4"
        self._header = None
        self._footer = None

    @vproperty(double)
    class v_x(object):

        def get(self):
            return self._pdf.get_x()

        def let(self, value):
            self._pdf.set_x(value)

    @vproperty(double)
    class v_y(object):

        def get(self):
            return self._pdf.get_y()

        def let(self, value):
            self._pdf.set_y(value)

    _pdf = PDFProperty()

    @vsub(string, string, string, ignore)
    def v_setup(self, orientation=None, unit=None, format=None, klass=None):
        self._orientation = orientation or self._orientation
        self._unit = unit or self._unit
        self._format = format or self._format

        if klass is not None:
            instance = klass()

            header = getattr(instance, "v_header", None)
            if header is not None:
                if not isinstance(header, MethodType):
                    raise errors.expected_function
                self._header = header

            footer = getattr(instance, "v_footer", None)
            if footer is not None:
                if not isinstance(footer, MethodType):
                    raise errors.expected_function
                self._footer = footer

    @vsub(string, string, (string, binary))
    def v_addfont(self, family, style, filename):
        match = self._fonts_regex.match(filename)
        if match:
            file = managers.file_manager.open_temporary(None, None, delete=False)
            location = file.name
            try:
                try:
                    file.write(filename)
                finally:
                    file.close()
                self._pdf.add_font(family, style, location, True)
            finally:
                managers.file_manager.delete(file_access.TEMPORARY, None, location)
        else:
            application = managers.engine.application
            location = managers.file_manager.locate(file_access.storage, application.id, filename)
            self._pdf.add_font(family, style, location, True)

    @vfunction(result=string)
    def v_addlink(self):
        return self._pdf.add_link()

    @vsub(string)
    def v_addpage(self, orientation=""):
        self._pdf.add_page(orientation)

    @vsub
    def v_aliasnbpages(self):
        self._pdf.alias_nb_pages()

    @vsub(double, double, string)
    def v_text(self, x, y, txt=""):
        self._pdf.text(x, y, txt)

    @vsub(double, double, string, (integer, string), integer, string, boolean, string)
    def v_cell(self, w, h=0, txt="", border=0, ln=0, align="", fill=False, link=""):
        self._pdf.cell(w, h, txt, border, ln, align, fill, link)

    @vsub(double, double, string, (integer, string), string, boolean, boolean)
    def v_multicell(self, w, h, txt="", border=0, align="J", fill=0, split_only=False):
        self._pdf.multi_cell(w, h, txt, border, align, fill, split_only)

    @vsub((string, binary), double, double, double, double, string, string)
    def v_image(self, filename, x=None, y=None, w=0, h=0, type="", link=""):
        match = self._images_regex.match(filename)
        if match:
            type = match.lastgroup
            file = managers.file_manager.open_temporary(None, None, delete=False)
            location = file.name
            try:
                file.write(filename)
                file.close()
                self._pdf.image(location, x, y, w, h, type, link)
            finally:
                managers.file_manager.delete(file_access.TEMPORARY, None, location)
        else:
            application = managers.engine.application
            location = managers.file_manager.locate(file_access.storage, application.id, filename)
            self._pdf.image(location, x, y, w, h, type, link)

    @vsub(double, double, double, double)
    def v_line(self, x1, y1, x2, y2):
        self._pdf.line(x1, y1, x2, y2)

    @vsub(double, double, double, double, string)
    def v_rect(self, x, y, w, h, style=''):
        self._pdf.rect(x, y, w, h, style)

    @vsub(double, double, double, double, string)
    def v_link(self, x, y, w, h, link):
        self._pdf.link(x, y, w, h, link)

    @vsub(double, string, string)
    def v_write(self, h, txt="", link=""):
        self._pdf.write(h, txt, link)

    @vsub(double)
    def v_ln(self, h=""):
        self._pdf.ln(h)

    @vsub
    def v_accept_page_break(self):
        self._pdf.accept_page_break()

    @vsub
    def v_close(self):
        self._pdf.close()

    @vfunction(string, result=string)
    def v_output(self, filename=""):
        if filename:
            application = managers.engine.application
            location = managers.file_manager.locate(file_access.storage, application.id, filename)
            return str(self._pdf.output(location, dest="F"))
        else:
            return str(self._pdf.output(dest="S").decode("latin1"))

    @vfunction(string, result=double)
    def v_getstringwidth(self, s):
        return self._pdf.get_string_width(s)

    @vfunction(result=double)
    def v_getx(self):
        return self._pdf.get_x()

    @vfunction(result=double)
    def v_gety(self):
        return self._pdf.get_y()

    @vsub(string)
    def v_setauthor(self, author):
        self._pdf.set_author(author)

    @vsub(boolean, double)
    def v_setautopagebreak(self, auto, margin=0):
        self._pdf.set_auto_page_break(auto, margin)

    @vsub(boolean)
    def v_setcompression(self, compress):
        self._pdf.set_compression(compress)

    @vsub(string)
    def v_setcreator(self, creator):
        self._pdf.set_creator(creator)

    @vsub(string, string)
    def v_setdisplaymode(self, zoom, layout="continuous"):
        self._pdf.set_display_mode(zoom, layout)

    @vsub(integer, integer, integer)
    def v_setdrawcolor(self, r, g=-1, b=-1):
        self._pdf.set_draw_color(r, g, b)

    @vsub(integer, integer, integer)
    def v_setfillcolor(self, r, g=-1, b=-1):
        self._pdf.set_fill_color(r, g, b)

    @vsub(string, string, integer)
    def v_setfont(self, family, style="", size=0):
        self._pdf.set_font(family, style, size)

    @vsub(integer)
    def v_setfontsize(self, size):
        self._pdf.set_font_size(size)

    @vsub(string)
    def v_setkeywords(self, keywords):
        self._pdf.set_keywords(keywords)

    @vsub(double)
    def v_setleftmargin(self, margin):
        self._pdf.set_left_margin(margin)

    @vsub(double)
    def v_setlinewidth(self, width):
        self._pdf.set_line_width(width)

    @vsub(string, double, integer)
    def v_setlink(self, link, y=0, page=-1):
        self._pdf.set_link(link, y, page)

    @vsub(double, double, double)
    def v_setmargins(self, left, top, right=-1):
        self._pdf.set_margins(left, top, right)

    @vsub(double)
    def v_setrightmargin(self, margin):
        self._pdf.set_right_margin(margin)

    @vsub(string)
    def v_setsubject(self, subject):
        self._pdf.set_subject(subject)

    @vsub(integer, integer, integer)
    def v_settextcolor(self, r, g=-1, b=-1):
        self._pdf.set_text_color(r, g, b)

    @vsub(string)
    def v_settitle(self, title):
        self._pdf.set_title(title)

    @vsub(double)
    def v_settopmargin(self, margin):
        self._pdf.set_top_margin(margin)

    @vsub(double)
    def v_setx(self, x):
        self._pdf.set_x(x)

    @vsub(double)
    def v_sety(self, y):
        self._pdf.set_y(y)

    @vsub(double, double)
    def v_setxy(self, x, y):
        self._pdf.set_xy(x, y)
