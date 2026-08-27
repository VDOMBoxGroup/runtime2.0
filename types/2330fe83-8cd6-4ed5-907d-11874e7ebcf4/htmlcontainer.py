import codecs
import json
import time
import email
import email.utils
import managers
from scripting import e2vdom


# DOCTYPE = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">"""
DOCTYPE = """<!DOCTYPE html>"""


JAVASCRIPT = "<script type='text/javascript' src='/{uuid}.res'></script><script type='text/javascript'>\n{declarations}\n</script>\n"


JQUERY_UI = """
    <link rel="preload" href="/a0fb93f7-826e-9be6-02fd-1348887cb685.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="/a0fb93f7-826e-9be6-02fd-1348887cb685.css"></noscript>

    <script type='text/javascript' src='/ab87f9cd-7202-1b37-94ed-63001c47a8d9.res?v=1.13.2.1m'></script>
"""

DEFAULT_TEST_FUNCTIONS = "<script type='text/javascript' src='/ad0f545d-18c6-37ce-fb87-fe54dcb8a0a6.res?v20240112'></script>"
DEFAULT_TEST_CLASSES = "<script type='text/javascript' src='/e4d11b10-b197-f1d1-49b1-0e0b0e59df57.res?v20240920'></script>"

CENTERING_CSS = ".center {width: 1100px; margin: 0 auto !important; position: relative;}\n.ui-widget-overlay {position: fixed;}"

TEMPLATE = """{doctype}
<!--[if gt IE 9]><!-->
<html>
<!--<![endif]-->
<head>
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
<meta charset="utf-8"/>
<title>{title}</title>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
{metas}
<script type="text/javascript">
    var APPLICATION_ID="{application}", SESSION_ID="{session}"
    var SERVER_URL="/e2vdom.py"
    var E2VDEBUG={e2vdebug}, E2VSTATE="{e2vstate}", E2VSV={e2vsv};
</script>
<script type="text/javascript" src="/910d5aa6-aeef-2e2d-6127-5434d62562fc.res?v20231217"></script>
<script type="text/javascript" src="/70d4e0af-7126-b74b-81af-1938f5a2673c.res?v20240425"></script>
<script defer type="text/javascript" src="/ccfb4678-798f-230e-0cc8-22bad806c706.res?v20180123"></script>
{jquery_ui}
{test_functions}
<script type="text/javascript" src="/3e932470-0e08-446c-a866-30c00e6d812a.res"></script>
{static_libraries}
{dynamic_libraries}
{test_classes}
<style type="text/css">
{css}
</style>
<!--[if lt IE 9]><script src="/62bfaaa0-c2fd-02d5-2a32-49056e416a65.res"></script><![endif]-->
</head>
<body id="{element_name}" style="{style} {font_style}"{inline_style}{inline_class}>
{cookiewarning}
{noscript}
{content}
<div id='e2vdomindicator' style='z-index:99999;width:1px;height:1px;position:absolute;position:fixed;left:0;top:0;display:none'></div>
<script type="text/javascript" src="/6cdc7eef-c7d2-bc99-b202-98b2d9052836.res"></script>
<script type="text/javascript">
    hchInit({center},'#{bgcolor}','{id4code}');
    hchSetEvents('{id4code}');
</script>
</body>
<!-- type {type_version}, runtime {server_version} -->
</html>"""


class VDOM_htmlcontainer(VDOM_object):
    def render(self, contents=""):
        if self.visible != "1":
            return VDOM_object.render(self, contents="<html></html>")

        if self.securitycode != "":
            code = str(session["SecurityCode"])
            redirection = not code or code not in self.securitycode.split(";")
            if redirection:
                if self.deniedlink == "":
                    return VDOM_object.render(self, contents="<html></html>")
                else:
                    target = managers.engine.application.objects.catalog.get(self.deniedlink)
                    reference = "/%s.vdom" % target.name if target else ""
                    response.redirect(reference)

        e2vdom.process(self)

        # NOTE: cleanup later
        # static, dynamic = e2vdom.generate(self)

        # static_declarations, static_libraries = static
        # dynamic_declarations, dynamic_libraries = dynamic

        static_declarations, static_libraries = e2vdom.generate(self)
        dynamic_declarations, dynamic_libraries = "", "".join(managers.request_manager.current.dyn_libraries.values())

        javascript_label = "jsdata-%s" % len(static_declarations)
        javascript_resource = application.resources.get_by_label(self.id, javascript_label)
        if javascript_resource:
            javascript_resource_uuid = javascript_resource.id
        else:
            javascript_resource_uuid = application.resources.create_temporary(
                self.id, "jsdata-htmlcontainer", static_declarations.encode("utf-8"), "js", javascript_label
            )

        javascript = JAVASCRIPT.format(declarations=dynamic_declarations, uuid=javascript_resource_uuid)

        id4code = self.id.replace("-", "_")
        element_name = "o_%s" % id4code

        if self.position == "jscenter":
            classname = self.cssclass
            center = "1"
            centering_css = ""
        elif self.position == "center":
            classname = "%s center" % self.cssclass if self.cssclass else "center"
            center = "0"
            centering_css = CENTERING_CSS
        else:
            classname = self.cssclass
            center = "0"
            centering_css = ""

        style = self.style
        style += " margin: 0 auto;"
        if self.bgcolor:
            style += " background-color: #%s;" % self.bgcolor
        if self.image:
            style += " background-image: url('/%s.res'); background-repeat: %s;" % (self.image, self.bgrepeat)

        inline_style = ""
        if self.linkcolor:
            inline_style += ' link="#' + self.linkcolor + '"'
        if self.activelinkcolor:
            inline_style += ' alink="#' + self.activelinkcolor + '"'
        if self.visitedlinkcolor:
            inline_style += ' vlink="#' + self.visitedlinkcolor + '"'

        fstyles = {
            "color": "#" + self.textcolor if self.textcolor else "",
            "font-family": self.fontfamily.replace('"', "'"),
            "font-size": self.fontsize,
            "font-weight": self.fontweight,
            "letter-spacing": self.letterspacing,
            "line-height": self.lineheight,
            "font-style": self.fontstyle,
        }
        font_style = " ".join(["{}: {};".format(key, value) for key, value in fstyles.items() if value])

        metas = ""
        if self.metadescription:
            metas += '<meta name="description" content="%s" />\n' % (self.metadescription).replace('"', "&quot;")
        if self.metakeywords:
            metas += '<meta name="keywords" content="%s" />\n' % (self.metakeywords).replace('"', "&quot;")
        if self.customheaders:
            metas += "%s" % self.customheaders

        if self.noscript:
            noscript = "<noscript>%s</noscript>" % self.noscript
        else:
            noscript = ""

        content = """{contents}{javascript}"""
        if self.page_wrapper_mode == "1":
            content = """<div id='container'>{contents}{javascript}</div>"""

        cookie_name = "cookiewarning"
        cookiewarning = ""
        if self.cookiewarning == "1":
            if cookie_name not in request.cookies:
                cookiewarning = """<div id="cookieWarningDiv" style="display: block; text-align: center; background: #333; color: #fff; font-size: 15px !important; width: 90%%; box-sizing: content-box; font-family: sans-serif !important; padding-top: 5px; padding-right: 5%%; padding-bottom: 5px; padding-left: 5%%; vertical-align: initial;">
                                  <span id="cookieWarningAlert" style="font: 15px verdana;"> %(text)s </span>
                                  <span id="cookieWarningOK" style="cursor: pointer; display: inline-block; font-size: 16px; background: #4596ec !important; border-radius: 10px; font-family: sans-serif !important; box-sizing: initial; vertical-align: initial; padding-top: 5px; padding-right: 10px; padding-bottom: 5px; padding-left: 10px; margin-left: 7px;" onclick="$(function(){ document.cookie = '%(cookie)s=1; expires=%(cookie_exp)s'; $('#cookieWarningDiv').hide(); });">&#x2713; OK</span>
                                  </div>""" % {
                    "text": self.cookiewarningtext,
                    "cookie": cookie_name,
                    "cookie_exp": email.utils.formatdate(time.time() + 31536000, usegmt=True),  # set one year expiration
                }

        result = TEMPLATE.format(
            doctype=DOCTYPE,
            type_version=self.type.version,
            server_version=server.version,
            title=codecs.encode(self.title, "html"),
            metas=metas,
            application=application.id,
            session=session.id,
            e2vdebug="true" if VDOM_CONFIG_1["ENABLE-PAGE-DEBUG"] == "1" else "false",
            e2vstate="0",
            e2vsv=json.dumps(response.shared_variables.copy()),
            jquery_ui=JQUERY_UI,
            test_functions=self.testfunctions or DEFAULT_TEST_FUNCTIONS,
            test_classes=self.testclasses or DEFAULT_TEST_CLASSES,
            css="\n".join((self.css, centering_css)),
            static_libraries=static_libraries,
            dynamic_libraries=dynamic_libraries,
            element_name=element_name,
            style=style,
            inline_style=inline_style,
            font_style=font_style,
            inline_class=" class='%s'" % classname if classname else "",
            cookiewarning=cookiewarning,
            content=content.format(contents=contents, javascript=javascript),
            noscript=noscript,
            center=center,
            bgcolor=self.bgcolor,
            id4code=id4code,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        result = (
            '<container name="%s" id="%s" visible="%s" zindex="%s" hierarchy="%s" order="%s" backgroundcolor="#%s" backgroundimage="%s" backgroundrepeat="%s" >%s</container>'
            % (self.name, self.id, self.visible, self.zindex, self.hierarchy, self.order, self.bgcolor, self.image, self.bgrepeat, contents)
        )
        return VDOM_object.wysiwyg(self, contents=result)