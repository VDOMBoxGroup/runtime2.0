WYSIWYG_IMAGE_UUID = "dd93dcb4-4372-9740-d39a-16ae1feaedd4"


class VDOM_flot(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        id = "o_" + (self.id).replace("-", "_")

        result = """"""

        if self.options == "":
            options = ""
        else:
            options = ", %s" % self.options

        zindex = "%s" % self.zindex if int(self.zindex) != 0 else ""
        display = "none" if self.visible == "0" else self.displaying
        position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""

        styles = {
            "z-index": zindex,
            "display": display,
            "position": position,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "overflow": self.overflow,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        result += "<div id='{id}' style='{styles}'>{contents}</div>".format(id=id, styles=styles_str, contents=contents)

        if self.bars == "1":
            bars = "true"
        else:
            bars = "false"

        if self.lines == "1":
            lines = "true"
        else:
            lines = "false"

        if self.points == "1":
            points = "true"
        else:
            points = "false"

        if (self.jsondata).strip() == "":
            jsondata = "[]"
        else:
            jsondata = self.jsondata

        result += (
            """<script type='text/javascript'>
$j(function(){
    $j('#"""
            + id
            + """').data('opt', {
        lines: { show: """
            + lines
            + """ },
        points: { show: """
            + points
            + """ },
        bars: { show: """
            + bars
            + """ }
        """
            + options
            + """
    });
    if (/MSIE|Trident/.test(navigator.userAgent)) {
        setTimeout(function() {
            $j.plot($j('#"""
            + id
            + """'), """
            + jsondata
            + """, $j('#"""
            + id
            + """').data('opt'));
        }, 500);
    } else {
        $j.plot($j('#"""
            + id
            + """'), """
            + jsondata
            + """, $j('#"""
            + id
            + """').data('opt'));
    }
});
</script>"""
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]
        result = get_empty_wysiwyg_value(self, WYSIWYG_IMAGE_UUID)
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

    skin_mapping = {"0": "", "1": users}
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