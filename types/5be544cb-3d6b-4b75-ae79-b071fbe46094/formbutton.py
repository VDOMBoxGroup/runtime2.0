class VDOM_formbutton(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = "none" if self.visible == "0" else self.displaying
        type = ["submit", "reset", "button"][int(self.attributes["type"])]
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

        id = "o_" + (self.id).replace("-", "_")
        alt = """alt="{}" """.format(self.alt) if self.alt else ""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='formbutton' objname='%s'" % ((self.name).replace("'", ""))
        else:
            debug_info = ""

        result = """<style type="text/css">{css}</style>
                        <input {debug_info} id="{id}" name="{name}" style="{style}" type="{type}" {alt}
                                tabindex="{tabind}" value="{label}" class="{clname}" />
            """.format(
            debug_info=debug_info,
            css=self.style % {"id": id},
            id=id,
            name=self.name,
            style=styles_str,
            type=type,
            tabind=self.tabindex,
            label=self.label,
            clname=" ".join([self.classname, "vdom_formbutton"]).strip(),
            alt=alt,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        width, height, top, left = [
            int(self.ide_width),
            int(self.ide_height),
            int(self.ide_top),
            int(self.ide_left),
        ]

        label = "<![CDATA[%s%s]>" % (self.label, "]")
        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect x="0" y="0" width="{rec_wid}" height="{rec_hei}" fill="#CCCCCC" stroke="#000000"/>
                    </svg>
                    <text top="{txt_top}" width="{txt_wid}" color="#000000" textalign="center">{label}</text>{contents}
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            name=self.name,
            hierarchy=self.hierarchy,
            order=self.order,
            top=top,
            left=left,
            width=width,
            height=height,
            rec_wid=width - 1,
            rec_hei=height - 1,
            txt_top=height / 2 - 9,
            txt_wid=width - 4,
            label=label,
            contents=contents,
        )

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    pro_suite = """#%(id)s {
text-align:center !important;
background:#fff url("/f704b515-d69d-24d9-5e81-8dc0984592fa.png") !important;
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
line-height:22px !important;
font-size:14px !important;
color:#000;
font-family:Arial,sans-serif;
}
#%(id)s:hover {
box-shadow:inset 0px 0px 6px #fff;
-moz-box-shadow:inset 0px 0px 6px #fff;
-webkit-box-shadow:inset 0px 0px 6px #fff;
-o-box-shadow:inset 0px 0px 6px #fff;
-ms-box-shadow:inset 0px 0px 6px #fff;
border:1px solid #a8a8a8;
}"""

    empty = ""

    users = """
#%(id)s {

}
"""

    skin_mapping = {"0": users, "1": pro_suite, "2": empty}

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

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")