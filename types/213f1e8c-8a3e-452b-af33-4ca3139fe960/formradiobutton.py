class VDOM_formradiobutton(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        zind = "%s" % self.zindex if int(self.zindex) != 0 else ""
        display = "none" if self.visible == "0" else self.displaying
        disable = "disabled='disabled'" if self.disable == "1" else ""
        position = "{pos}".format(pos=self.positioning) if self.positioning != "static" else ""

        if self.parent and self.parent.type.class_name == "VDOM_formradiogroup":
            name = self.parent.name
            state = ["", """checked="checked" """][int(self.attributes["state"])]
            styles = {
                "z-index": zind,
                "display": display,
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
            style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

            clean_id = (self.id).replace("-", "_")
            id = "o_%s" % clean_id
            fixw = self.check_unit(self.width)
            css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

            if int(self.align) == 0:
                label_pos = "position: absolute; left: 20px"
                button_pos = "position: absolute; left: 0px"
            else:
                label_pos = "position: absolute; left: 20px"
                if fixw and fixw != "auto":
                    button_pos = "position: absolute; right: calc({width} - 20px)".format(width=fixw)
                else:
                    button_pos = "position: absolute; left: 0px"

            result = """<div id="%(id)s" style="%(style)s" class="%(classn)s vdom_formradiobutton">
                        <input name="%(name)s" type="radio" %(state)s tabindex="%(tabind)s" 
                            value="%(value)s" id="inp_%(id)s" style="%(inp_style)s" %(disable)s/>
                        <label for="inp_%(id)s" style="%(lbl_style)s" title="%(label)s">%(label)s</label>
                        %(contents)s
                    </div>
                    %(css)s
                    <script type="text/javascript">
                        jQuery(document).ready(function(){
                            jQuery("#inp_%(id)s").change(function(){
                                execEventBinded("%(clean_id)s", "change", { Value: jQuery("#inp_%(id)s").val() });});
                        });
                    </script>
                """ % {
                "id": id,
                "style": style,
                "classn": self.classname,
                "name": name,
                "state": state,
                "tabind": self.tabindex,
                "value": self.value,
                "inp_style": button_pos,
                "disable": disable,
                "lbl_style": label_pos,
                "label": self.label,
                "contents": contents,
                "clean_id": clean_id,
                "css": css,
            }
        else:
            result = ""

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        label_left = 16 if self.align == "0" else 1
        label_width = width - label_left

        label = """<text top="-1" left="{left}" width="{label_width}" height="{label_height}">{label}</text>
            """.format(left=label_left, label_width=label_width, label_height=height, label=self.label)

        circle_x = 10 if self.align == "0" else width - 10
        circle_color = "#888888" if self.disable == "1" else "#000000"

        state_circle = ""
        if int(self.state):  # checked
            state_circle = """<circle cx="{circle_x}" cy="8.5" r="2" fill="{circle_color}" stroke="{circle_color}"/>
                """.format(circle_x=circle_x, circle_color=circle_color)

        circle = """<svg>
                    <circle cx="{circle_x}" cy="8.5" r="4.5" fill="#EEEEEE" stroke="{circle_color}"/>
                    {state_circle}
                </svg>
            """.format(circle_x=circle_x, circle_color=circle_color, state_circle=state_circle)

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                            top="{top}" left="{left}" width="{width}" height="{height}">
                    {circle}
                    {label}
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
            name=self.name,
            width=width,
            height=height,
            label=label,
            circle=circle,
            contents=contents,
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


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")