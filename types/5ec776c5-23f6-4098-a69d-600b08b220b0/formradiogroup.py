from scripting import e2vdom


class VDOM_formradiogroup(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        e2vdom.process(self)

        styles = {
            "z-index": self.zindex if int(self.zindex) != 0 else "",
            "display": "none" if self.visible == "0" else self.displaying,
            "position": self.positioning if self.positioning != "static" else "",
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

        id = "o_" + (self.id).replace("-", "_")

        result = """<div id="{id}" class="{css_class} vdom_formradiogroup" objname="{objname}" objtype="formradiogroup" style="{style}">
                        {contents}
                    </div>""".format(
            id=id,
            style=style,
            contents=contents,
            css_class=self.classname,
            objname=self.name,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        self.width, self.height, self.top, self.left = [
            int(self.ide_width),
            int(self.ide_height),
            int(self.ide_top),
            int(self.ide_left),
        ]
        if len(contents) == 0:
            from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

            image_id = "1ac76095-3282-e956-f43a-171ce744e574"
            result = get_empty_wysiwyg_value(self, image_id)

            return VDOM_object.wysiwyg(self, contents=result)

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                            top="{top}" left="{left}" width="{width}" height="{height}">
                        <svg>
                            <rect top="0" left="0" width="{rec_wid}" height="{rec_hei}" fill="#EEEEEE" stroke="#000000"/>
                        </svg>
                        {contents}
                    </container>""".format(
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
            rec_wid=self.width - 1,
            rec_hei=self.height - 1,
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