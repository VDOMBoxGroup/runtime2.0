import re


class VDOM_hypertext(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        id = "o_" + (self.id).replace("-", "_")
        zindex = "%s" % self.zindex if int(self.zindex) != 0 else ""
        display = "none" if self.visible == "0" else self.displaying
        display_style = "display: {}".format(display) if display else ""

        if self.nostyle == "2":
            if self.visible == "0":
                return '<div style="%s">%s</div>' % (display_style, self.htmlcode)
            else:
                return "%s" % (self.htmlcode)
        elif self.nostyle == "1":
            return '<span id="%s" style="%s">%s</span>' % (id, display_style, self.htmlcode)
        else:
            overflow_values = {"1": "hidden", "2": "scroll", "3": "visible", "0": "auto"}
            overflow = overflow_values.get(self.overflow, "")

            position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""
            styles = {
                "z-index": zindex,
                "display": display,
                "overflow": overflow,
                "position": position,
                "width": self.check_unit(self.width),
                "height": self.check_unit(self.height),
                "margin": self.margins,
                "padding": self.paddings,
                "top": self.check_unit(self.top),
                "left": self.check_unit(self.left),
            }
            if self.positioning == "static":
                styles["top"] = styles["left"] = ""

            styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

            classname = 'class="%s"' % " ".join([self.classname, "vdom_hypertext"]).strip()
            css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

            if VDOM_CONFIG_1["DEBUG"] == "1":
                debug_info = "objtype='hypertext' objname='%s' ver='%s'" % (self.name, self.type.version)
            else:
                debug_info = ""

            return '%s<div %s id="%s" %s style="%s">%s</div>' % (css, debug_info, id, classname, styles_str, self.htmlcode)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        if not self.htmlcode:
            image_id = "f74a4262-469b-f3cf-8e10-08a127dfbdbf"
            result = get_empty_wysiwyg_value(self, image_id)

            return VDOM_object.wysiwyg(self, contents=result)

        # get overflow value
        overflow_dict = {"0": "auto", "1": "hidden", "2": "scroll", "3": "visible"}
        overflow_num = self.overflow if self.overflow else "0"
        overflow = overflow_dict[overflow_num]

        # disable javascript
        html_with_server = re.sub("=/", "=http://" + request.server.host + "/", self.htmlcode)
        html_wys = re.sub(r"(href\s*=\s*['\"]{1}(.*?)['\"]{1})", r"""style="text-decoration: underline; color:#394fa2;" """, html_with_server)
        html_wys = re.sub(r"<script\s*\>", "<pre>Script:<br/>", self.htmlcode)
        html_wys = re.sub(r"</script>", "</pre>", self.htmlcode)

        result = """<container name="{name}" id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}"
                        order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
                    <htmltext top="0" left="0" width="{width}" height="{height}" locked="true" overflow="{overflow}">
                        {html_data}
                    </htmltext>
                </container>
            """.format(
            id=self.id,
            visible=self.visible,
            zindex=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            html_data="<![CDATA" + "[" + html_wys + "]" + "]>",
            overflow=overflow,
            name=self.name,
        )

        return VDOM_object.wysiwyg(self, contents=result)


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

    users = """\
#%(id)s {

}
"""

    skin_mapping = {"0": users, "1": ""}
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")