from scripting.legacy.id import id2link1
import re
import json
from io import StringIO


class VDOM_button(VDOM_object):
    def compute(self):
        VDOM_object.compute(self)
        self.finalimage = self.image
        self.finalrollover = self.rollover
        self.finaldisabledimg = self.disabledimg

        deffamily = "tahoma"
        fontsize = self.regex(str(self.fontsize)) or "12"
        fontstyle = self.fontstyle  # or "normal"
        fontfamily = self.fontfamily.split(",")[0]

        if len(fontfamily) > 0:
            fontfamily = fontfamily.strip().lower()
            if len(fontfamily) > len(self.fontfamily.split(" ")[0].strip().lower()):
                fontfamily = self.fontfamily.split(" ")[0].strip().lower().replace('"', "").replace("'", "")
        else:
            fontfamily = deffamily

        fontweight = self.fontweight  # or "normal"
        textdecor = self.textdecoration or "none"
        color = self.color or "000000"

        if self.text and (self.image or self.rollover or self.disabledimg):
            try:
                from scripting.legacy.imaging import VDOM_imaging

                im = VDOM_imaging()

                im.create_font(name=fontfamily, size=int(fontsize), fontstyle=fontstyle, fontweight=fontweight)
                if self.image:
                    resource = application.resources.get_by_label(self.id, "image")
                    if resource:
                        self.finalimage = resource.id
                    else:
                        im.load(application.id, self.image)
                        im.write_text(
                            self.text,
                            color=(int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)),
                            align=self.align or "left",
                            ident=self.fontshift,
                            textdecoration=textdecor,
                        )
                        self.finalimage = im.save_temporary(application.id, self.id, "image")

                    if self.rollover:
                        resource = application.resources.get_by_label(self.id, "rollover")
                        if resource:
                            self.finalrollover = resource.id
                        else:
                            im.load(application.id, self.rollover)
                            im.write_text(
                                self.text,
                                color=(int(color[:2], 16), int(color[2:4], 16), int(color[4:6], 16)),
                                align=self.align or "left",
                                ident=self.fontshift,
                                textdecoration=textdecor,
                            )
                            self.finalrollover = im.save_temporary(application.id, self.id, "rollover")
            except Exception as e:
                debug("Error while text rendering on button image: %s" % str(e))

        if not (self.image or self.rollover or self.disabledimg):
            self.finaltext = self.text
        else:
            self.finaltext = ""

    def get_anchor(self, link):
        if self.ispressed == "0":
            bgimg = "background:url('%s');" % id2link1(self.finalimage) if self.image and self.rollover else ""
        else:
            bgimg = "background:url('%s');" % id2link1(self.finalrollover) if self.image and self.rollover else ""
        height = "height: {height};".format(height=self.check_unit(self.height)) if self.height else ""
        # clname = u"""class="%s" """ % self.classname if self.classname else u""
        if self.disabled == "1":
            clname = """class="%s disabled" """ % self.classname
            donot = """ onclick='return false' """
        else:
            clname = """class="%s" """ % self.classname if self.classname else ""
            donot = ""

        return """<a style="{height} {bgimage}" href="{link}" title="{hint}" {classname} {donot} {tabindex}>
                """.format(
            tabindex="" if int(self.tabindex) <= 0 else 'tabindex="%s"' % self.tabindex,
            bgimage=bgimg,
            height=height,
            link=link,
            hint=(self.hint).replace('"', "&quot;"),
            classname=clname,
            donot=donot,
        )

    def check_unit(self, value):
        return str(value) + "px" if isinstance(value, (int, str)) else value

    def render(self, contents=""):
        id_out = "o_%s" % (self.id).replace("-", "_")
        styleblock = ""
        scriptblock = ""
        text_style = ""
        alt = """alt="{}" """.format(self.alt) if self.alt else ""

        border_style = "border: {border} {bdcolor};".format(border=self.check_unit(self.border), bdcolor=self.bordercolor) if self.border else ""
        text_align = "text-align: {align};".format(align=self.align) if self.align else ""

        width_style = "width: {width};".format(width=self.check_unit(self.width)) if self.width else ""
        height_style = "height: {height};".format(height=self.check_unit(self.height)) if self.height else ""

        margin_in = "margin: {margins};".format(margins=self.margins) if self.margins else ""
        padding_in = "padding: {paddings};".format(paddings=self.paddings) if self.paddings else ""

        if self.positioning == "static":
            position = self.positioning = ""
            self.left = self.top = ""
        else:
            position = "position: {pos};".format(pos=self.positioning)

        top_style = "top: {top};".format(top=self.check_unit(self.top)) if self.top else ""
        left_style = "left: {left};".format(left=self.check_unit(self.left)) if self.left else ""

        flex_styles = {
            "align-self": self.alignself,
            "flex-grow": self.flexgrow,
            "flex-basis": self.flexbasis,
            "order": self.orderchild,
            "flex-shrink": self.flexshrink,
        }
        flex_style = " ".join(["{}: {};".format(key, value) for key, value in flex_styles.items() if value])

        custom_attributes = ""
        custom_attr_json = json.loads(self.custom_attributes) if self.custom_attributes else ""
        if custom_attr_json:
            custom_attributes = " ".join(['{}="{}"'.format(key, value) for key, value in custom_attr_json.items()])

        clname = " ".join(filter(None, [self.classname, "vdom_button"])).strip()
        if self.classname:
            classes = self.classname.split()
            holder_classes = ["{}_holder".format(classname) for classname in classes]
            clname_holder = " ".join(filter(None, holder_classes + ["vdom_button"])).strip()
        else:
            clname_holder = "vdom_button"

        if self.disabled == "0":
            disabled_html = ""
        else:
            zindex_disabled = "z-index: %s;" % str(int(self.zindex) + 1)
            disabled_html = """<div id='{id}_e2vdomhelper' class='disabled-over' style='{zindex_disabled} background: #fff;
                                        opacity: 0.01; filter: alpha(opacity=1); {position} {left} {top} 
                                        {width} {height} {margin} {padding}'></div>
                            """.format(
                id=id_out,
                zindex_disabled=zindex_disabled,
                width=width_style,
                height=height_style,
                left=left_style,
                top=top_style,
                position=position,
                margin=margin_in,
                padding=padding_in,
            )

        overcss = "<style>\n" + (self.style % {"id": id_out}) + "</style>" if self.style else ""
        disablecss = ""
        representation = ""
        render_mode = self.rendermode.lower() if self.rendermode else "default"
        style_zindex = "z-index: %s;" % self.zindex if int(self.zindex) != 0 else ""
        style = """{zindex} {position} {left} {top} {margin} {padding} {wstyle} {hstyle} {align} {border} {flex}""".format(
            zindex=style_zindex,
            left=left_style,
            top=top_style,
            position=position,
            wstyle=width_style,
            hstyle=height_style,
            align=text_align,
            border=border_style,
            margin=margin_in,
            padding=padding_in,
            flex=flex_style,
        )

        display = "display: none; " if self.visible == "0" else "display: {disp}; ".format
        if self.visible == "0":
            display = "display: none; "
        elif self.displaying != "":
            display = "display: {disp}; ".format(disp=self.displaying)
        else:
            display = ""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='button' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        spstyle = StringIO()
        if self.fontweight:
            spstyle.write("font-weight: {}; ".format(self.fontweight))
        if self.fontstyle:
            spstyle.write("font-style: {}; ".format(self.fontstyle))
        if self.fontsize:
            spstyle.write("font-size: %s; " % self.check_unit(self.fontsize))
        if self.fontfamily:
            spstyle.write("font-family: %s;" % self.fontfamily.replace('"', "'"))
        if self.color:
            spstyle.write("color: #%s; " % self.color)
        if self.textdecoration:
            spstyle.write("text-decoration: %s; " % self.textdecoration)
        if self.texttransform:
            spstyle.write("text-transform: %s; " % self.texttransform)
        if self.borderradius:
            spstyle.write("border-radius: %s; " % self.check_unit(self.borderradius))
        if self.backgroundcolor:
            spstyle.write("background-color: #%s; " % self.backgroundcolor)
        text_style = spstyle.getvalue()
        spstyle.close()

        if render_mode == "image":
            if self.image:
                if self.rollover:
                    rover_link = id2link1(self.finalrollover)
                    overcss = """<style>#%(id)s a:hover {background-image: url("%(image)s")!important}</style>
                                    <div style="display: none"><img src="%(image)s"/></div>
                                """ % {"id": id_out, "image": rover_link}
                else:
                    hover_link = id2link1(self.finalimage)
                    width_img = self.check_unit(self.width)
                    height_img = self.check_unit(self.height)

                    if self.ishover == "0":
                        representation = """<img src="{image}" width={width} height={height} title="{hint}" {alt}/>
                            """.format(image=hover_link, width=width_img, height=height_img, hint=self.hint, alt=alt)
                    else:
                        if not self.classname:
                            self.classname = "imagebtn"
                        classtut = self.classname
                        if self.ispressed == "1":
                            self.classname = "{classname} {classname}_sel".format(classname=self.classname)

                        matches = re.match(r"(\d+)(px|em|rem|vh|%)", height_img)
                        # shift background position for show another state of button
                        if matches:
                            value = int(matches.group(1)) * 2
                            unit = matches.group(2)
                            bgpos_left = str(value) + unit
                        else:
                            bgpos_left = "100px"
                            height_img = width_img = "50px"

                        styleblock = """<style>#%(id)s .%(classname)s, #%(id)s .%(classname)s_sel {
                                    display: block; width: %(width)s; height: %(height)s; 
                                    background: url("%(image)s") left top no-repeat;
                                }
                                #%(id)s .%(classname)s:hover {
                                    background-position: left -%(height)s
                                }
                                #%(id)s .%(classname)s_sel, #%(id)s .%(classname)s_sel:hover {
                                    background-position: left -%(bgleft)s!important
                                }
                                </style>
                            """ % {"classname": classtut, "width": width_img, "height": height_img, "image": hover_link, "bgleft": bgpos_left, "id": id_out}

                        scriptblock += """$q("#%(id)s a").click(function(){$q(this).toggleClass("%(classname)s_sel");});
                            """ % {"id": id_out, "classname": self.classname}
                        # ------------------------
                if self.disabledimg:
                    disablecss = """<style>#%(id)s .disabled {background-image:url("%(image)s")!important}</style>
                                        <div style="display:none"><img src="%(image)s"/></div>
                                """ % {"id": id_out, "image": id2link1(self.finaldisabledimg)}
            else:
                def_image_id = "e6017485-3493-484c-6a86-0867a82288fe"

                representation = """<img src="/{image}.res" width={width} height={height} title="{hint}" {alt}/>
                    """.format(image=def_image_id, width=self.width, alt=alt, height=self.height, hint=self.hint)

            if self.link:
                anchor = self.get_anchor(self.link)
            elif self.containerlink:
                ref_obj = application.objects.search(self.containerlink)
                ref_page = ref_obj.name + ".vdom" if ref_obj else ""
                anchor = self.get_anchor(ref_page)
            else:
                anchor = self.get_anchor("javascript://")

            if scriptblock != "":
                scriptblock = '<script type="text/javascript">%s</script>' % scriptblock

            return """{ocss}
                        <div {debug_info} id="{id}" style="{style}{disp}" class="{classname} image" {custom_attr}>
                            {anchor}{repr}</a>
                        </div>{disabled}{styleblk}{scriptblk}{disablecss}
                    """.format(
                repr=representation,
                custom_attr=custom_attributes,
                debug_info=debug_info,
                ocss=overcss,
                id=id_out,
                style=style,
                disp=display,
                disabled=disabled_html,
                classname=clname_holder,
                anchor=anchor,
                styleblk=styleblock,
                scriptblk=scriptblock,
                disablecss=disablecss,
            ).strip()

        elif render_mode == "link":
            link_html = 'href="{}"'.format(self.link) if self.link else ""

            return """{ocss}
<a {debug_info} id="{id}" style="{style}{disp}{text_style}" {link_html} title="{hint}" class="{clname} link" {custom_attr}>{text}</a>
                """.strip().format(
                text=self.text,
                debug_info=debug_info,
                id=id_out,
                style=style,
                ocss=overcss,
                custom_attr=custom_attributes,
                disp=display,
                link_html=link_html,
                clname=clname,
                text_style=text_style,
                hint=self.hint,
            )

        elif render_mode == "div":
            inner_html = """<a style="{}" {}>{}</a>""".format(text_style, 'href="{}"'.format(self.link) if self.link else "", self.text)

            return """{ocss}
<div {debug_info} id="{id}" style="{style}{disp}" title="{hint}" class="{clname} button" {custom_attr}>{inner_html}</div>
                """.format(
                debug_info=debug_info,
                id=id_out,
                style=style,
                ocss=overcss,
                custom_attr=custom_attributes,
                disp=display,
                clname=clname,
                inner_html=inner_html,
                hint=self.hint,
            )

    def regex(self, obj):
        match = re.search(r"\d+", obj)
        return int(match.group()) if match else ""

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        self.border = self.regex(self.border)
        deffamily = "Tahoma, 'Geneva CY', geneva, sans-serif".replace('"', "").replace("'", "")

        if self.border and self.border != "0":
            bw = int(self.border)
            minsize = min(width, height)
            if bw > minsize / 2:
                bw = minsize / 2
            border_string = """ stroke="#000000" stroke-width="%s" """ % bw
        else:
            bw = 1
            border_string = """ stroke="#000000" stroke-width="%s" """ % bw

        self.fontweight = self.fontweight or "normal"
        self.fontstyle = self.fontstyle or "normal"
        self.fontsize = self.regex(self.fontsize) or "12"
        self.fontfamily = self.fontfamily.replace('"', "").replace("'", "") or deffamily
        self.align = self.align or "left"
        self.color = str(self.color) or "000000"
        self.textdecoration = self.textdecoration or "none"

        if self.rendermode == "image":
            if not self.image:
                image_id = "e6017485-3493-484c-6a86-0867a82288fe"

                result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                            top="{top}" left="{left}" width="{out_wid}" height="{out_hei}">
                            <svg>
                                <image href="#Res({img_id})" x="0" y="0" width="{out_wid}" height="{out_hei}"/>
                            </svg>
                            {contents}
                        </container>
                    """.format(
                    id=self.id,
                    vis=self.visible,
                    zind=self.zindex,
                    hierarchy=self.hierarchy,
                    order=self.order,
                    top=top,
                    left=left,
                    out_wid=width,
                    out_hei=height,
                    img_id=image_id,
                    name=self.name,
                    contents=contents,
                )

                return VDOM_object.wysiwyg(self, contents=result)

            width = int(width) if width else 50
            height = int(height) if height else 50

            if self.image:
                result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                                top="{top}" left="{left}" width="{width}" height="{height}">
                            <svg>
                                <image href="#Res({image})" x="0" y="0" width="{width}" height="{height}"/>
                            </svg>{contents}
                            <svg>
                                <rect x="{rleft}" y="{rtop}" width="{rwid}" height="{rhei}" fill="#FFFFFF" fill-opacity=".0" {bord}/>
                            </svg>
                        </container>
                    """.format(
                    id=self.id,
                    vis=self.visible,
                    zind=self.zindex,
                    hierarchy=self.hierarchy,
                    order=self.order,
                    top=top,
                    left=left,
                    width=width,
                    height=height,
                    image=self.finalimage,
                    contents=contents,
                    rleft=bw / 2,
                    rtop=bw / 2,
                    rwid=width - bw,
                    rhei=height - bw,
                    bord=border_string,
                    name=self.name,
                )

                return VDOM_object.wysiwyg(self, contents=result)

        else:
            label = "<![CDATA[%s%s]>" % (self.text, "]")
            result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                            top="{top}" left="{left}" width="{width}" height="{height}">
                        <svg>
                            <rect x="{rec_left}" y="{rec_top}" width="{rec_wid}" height="{rec_hei}" fill="#FFFFFF" {bord}/>
                        </svg>
                        <text top="{txt_top}" left="{txt_left}" width="{txt_wid}" textalign="{align}" 
                            color="#{color}" fontstyle="{fstyle}" 
                            textdecoration="{txt_decor}" fontweight="{fweight}" fontfamily="{ffamily}" fontsize="{fsize}">
                            {label}
                        </text>{contents}
                    </container>
                """.format(
                id=self.id,
                vis=self.visible,
                zind=self.zindex,
                hierarchy=self.hierarchy,
                order=self.order,
                top=top,
                left=left,
                width=width,
                height=height,
                rec_left=bw / 2,
                rec_top=bw / 2,
                rec_wid=width - bw,
                rec_hei=height - bw,
                bord=border_string,
                txt_top=bw,
                txt_left=bw,
                txt_wid=width - 2 - 2 * bw,
                align=self.align,
                color=self.color,
                fstyle=self.fontstyle,
                txt_decor=self.textdecoration,
                fweight=self.fontweight,
                ffamily=self.fontfamily.replace('"', "").replace("'", ""),
                fsize=self.fontsize,
                label=label,
                contents=contents,
                name=self.name,
            )

            return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    o = object
    modifications = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, "").lower()

            if obj_value.isdigit() and attr_value.isdigit():
                modifications[attr] = attr_value + "px"
                modifications["ide_" + attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                modifications[attr] = attr_value.rstrip("px") + "px"
                modifications["ide_" + attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                modifications[attr] = attr_value if "px" in attr_value else obj_value
                modifications["ide_" + attr] = attr_value.rstrip("px")
            else:
                modifications[attr] = attr_value

    attributes.update(modifications)

    # if "image" in param and not "width" in param and not "height" in param:
    if "image" in attributes and "ide_width" not in attributes and "ide_height" not in attributes:
        # res_id = param["image"]["value"]
        res_id = attributes["image"]
        ro = application.resources.get(res_id)
        if not ro:
            return "Resource not found"

        # get image resource, obtain width and height and set width and height of the object
        from PIL import Image

        s = StringIO()
        s.write(ro.get_data())
        s.seek(0, 0)
        im = Image.open(s)
        width, height = im.size
        # set attributes
        # if o.attributes.width != width or o.attributes.height != height:
        #     o.set_attributes({"width": width, "height": height})
        if o.attributes["ide_width"] != width or o.attributes["ide_height"] != height:
            attributes.update(ide_width=str(width), ide_height=str(height))

    users = """\
#%(id)s {

}
#%(id)s .link {

}
#%(id)s .button {

}
#%(id)s .image {

}
"""

    pro_suite = """#%(id)s {height: 33px !important}
#%(id)s a {
 text-align:center !important;
 background:#fff url("/c016ef5e-c636-586d-9841-f3ff499831aa.png") !important;
 background-repeat:repeat-x;
 background-position:bottom center;
 text-decoration:none;
 line-height:25px;
 border:1px solid #c5c5c5;
 border-radius: 6px;
 -moz-border-radius:6px;
 -webkit-border-radius: 6px;
 -o-border-radius:6px;
 -ms-border-radius: 6px;
 cursor:pointer;
 outline:none !important;
 height:26px !important;
 box-shadow:inset 0px 0px 3px #fff;
    -moz-box-shadow:inset 0px 0px 3px #fff;
    -webkit-box-shadow:inset 0px 0px 3px #fff;
 -o-box-shadow:inset 0px 0px 3px #fff;
 -ms-box-shadow:inset 0px 0px 3px #fff;
 -webkit-transition: all 0.7s ease;
    -moz-transition: all 0.7s ease;
 -o-transition: all 0.7s ease;
}
#%(id)s a:hover {
 box-shadow:inset 0px 0px 6px #fff;
    -moz-box-shadow:inset 0px 0px 6px #fff;
    -webkit-box-shadow:inset 0px 0px 6px #fff;
 -o-box-shadow:inset 0px 0px 6px #fff;
 -ms-box-shadow:inset 0px 0px 6px #fff;
 border:1px solid #a8a8a8;
}
#%(id)s a span {
 line-height:22px !important;
 font-size:14px;
}
#%(id)s a span {
 line-height:22px !important;
 font-size:14px;
color:#000;
font-family:Arial,sans-serif;
}
#%(id)s a.disabled span {
color: #999 !important;
}"""

    empty = ""

    # if "skin" in param:
    #     if param["skin"]["value"] == "1":
    #         o.set_attributes({"style": pro_suite})
    skin_mapping = {"0": users, "1": pro_suite, "2": empty}

    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    # if "style" in param and param["style"]["value"] and o.attributes.style != pro_suite:
    #     o.set_attributes({"skin": 0})

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")