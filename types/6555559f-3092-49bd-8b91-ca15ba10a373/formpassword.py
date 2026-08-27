class VDOM_formpassword(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        bord = "border-width: 0px;" if self.border == "0" else ""

        styles = {
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "display": "none" if self.visible == "0" else self.displaying,
            "position": "%s" % self.positioning if self.positioning != "static" else "",
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "font-size": self.check_unit(self.fontsize),
            "border-width": "0px" if self.border == "0" else "",
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        id = "o_" + (self.id).replace("-", "_")
        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""
        auto = "off" if self.autocomplete == "0" else "on"

        result = """<input id="{id}" name="{name}" style="{style}" type="password" 
                        tabindex="{tabind}" value="{value}" class="{cname} vdom_formpassword" autocomplete="{auto}" placeholder="{placeholder}" />
                """.format(
            id=id, name=self.name, style=style, tabind=self.tabindex, value=self.value, cname=self.classname, auto=auto, placeholder=self.placeholder
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        rect_width = self.width - 1
        rect_height = self.height - 1

        value = "*" * len(self.value) if self.value else ""
        stroke = """ stroke="#888888" """ if self.border == "1" else ""

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                            top="{top}" left="{left}" width="{width}" height="{height}">
                        <svg>
                            <rect x="0" y="0" width="{rect_width}" height="{rect_height}" fill="#FFFFFF" {stroke}/>
                        </svg>
                        <svg>
                            <text x="{text_x}" y="{text_y}" width="{text_width}" height="{height}">{value}</text>
                        </svg>
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
            rect_width=rect_width,
            rect_height=rect_height,
            text_width=rect_width - 7,
            text_x=7,
            text_y=15 if rect_height < 15 else (rect_height - 15) / 2 + 15,
            value=value,
            stroke=stroke,
        )

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
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

    if "ide_width" in attributes:
        if int(attributes["ide_width"]) < 10:
            attributes.update(ide_width="10")

    if "height" in attributes:
        if int(attributes["ide_height"]) < 4:
            attributes.update(ide_height="4")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")