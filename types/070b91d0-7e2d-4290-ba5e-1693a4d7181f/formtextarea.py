class VDOM_formtextarea(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = "none" if self.visible == "0" else self.displaying
        clean_id = (self.id).replace("-", "_")
        id = "o_" + (self.id).replace("-", "_")
        required = "required" if self.required == "1" else ""
        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

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
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            styles["position"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        result = """
            <textarea {required} id="{id}" name="{name}" tabindex="{tabind}"
                style="{style}" class="{classname} vdom_formtextarea"
            >{value}</textarea> {css}
        """.format(
            id=id,
            name=self.customname or self.name,
            tabind=self.tabindex,
            style=styles_str,
            value=self.value,
            required=required,
            classname=self.classname,
            css=css,
        )

        focused = "$q('#%s').focus();" % id if self.focused == "1" else ""

        result += """<script type='text/javascript'>
$(document).ready(function(){
    $('#%(id)s').blur(function(){
        var x = $.trim($(this).val());
        execEventBinded("%(clean_id)s", "blur", { itemValue: x, charCount: x.length });
    });
    $('#%(id)s').focusin(function(){
        execEventBinded("%(clean_id)s", "focus", {});
    });
    %(focused)s
});</script>""" % {"id": id, "clean_id": clean_id, "focused": focused}

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                        top="{top}" left="{left}" width="{width}" height="{height}" >
                    <htmltext top="0" left="0" width="{width}" height="{height}" overflow="hidden" blendMode="normal">
                        <textarea style="width: {width}px; height: {height}px; background-color:#ffffff; font: 14px tahoma; padding: 2px 5px;">
                            {value}
                        </textarea>
                    </htmltext>
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            name=self.name,
            width=self.width,
            height=self.height,
            value=self.value,
        )

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