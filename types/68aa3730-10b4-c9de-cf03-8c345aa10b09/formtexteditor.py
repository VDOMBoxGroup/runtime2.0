class VDOM_formtexteditor(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        id = "o_" + (self.id).replace("-", "_")

        display = "none" if self.visible == "0" else self.displaying
        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": self.zindex if int(self.zindex) != 0 else "",
            "position": self.positioning,
            "display": display,
            "font-size": self.check_unit(self.fontsize),
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            styles["position"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        # style_area = u"""padding: 2px 5px; font: 14px tahoma; width: {width}px; height:{height}px""".format(width = self.width, height = self.height)

        result = """
<script type="text/javascript">$q(function(){
    if (typeof %(id)s_editor !== 'undefined') { delete(%(id)s_editor); }
    var wd = '%(width)s';
    var hg = '%(height)s';
    var %(id)s_a=$q('#%(id)s>textarea');
    %(id)s_editor = %(id)s_a.cleditor({
        width: wd,
        height: hg,
        bodyStyle: "%(style_area)s"
    })[0];
    $q('#%(id)s').parents('form:first').bind("reset",function(){
        %(id)s_a.val('');
        %(id)s_editor.updateFrame();
    });
});</script>
<div class="%(classname)s vdom_formtexteditor" objname="%(name)s" objtype="formtexteditor" id="%(id)s" style="%(style)s">
    <textarea name="%(name)s" tabindex="%(tabind)s" style="%(style_area)s">%(value)s</textarea>
</div>
            """ % {
            "id": id,
            "name": self.name,
            "tabind": self.tabindex,
            "style": styles_str,
            "style_area": "font-size: {}".format(styles["font-size"] if styles["font-size"] else ""),
            "value": self.value,
            "width": styles["width"],
            "height": styles["height"],
            "classname": self.classname,
        }

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        image_id = "4541bf6b-4416-e677-ad2a-172266047733"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    o = object
    mods = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, "").lower()

            if obj_value.isdigit() and attr_value.isdigit():
                mods[attr] = attr_value + "px"
                mods["ide_" + attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                mods[attr] = attr_value.rstrip("px") + "px"
                mods["ide_" + attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                mods[attr] = attr_value if "px" in attr_value else obj_value
                mods["ide_" + attr] = attr_value.rstrip("px")
            else:
                mods[attr] = attr_value
    attributes.update(mods)

    users = """
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