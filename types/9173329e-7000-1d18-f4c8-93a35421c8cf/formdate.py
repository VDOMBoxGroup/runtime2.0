class VDOM_formdate(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = "none" if self.visible == "0" else self.displaying

        if self.mode == "1":
            mode = """readonly="readonly" """
        elif self.mode == "2":
            mode = """disabled="disabled" """
        else:
            mode = ""

        auto = "off" if self.autocomplete == "0" else "on"

        clean_id = (self.id).replace("-", "_")
        id = "o_%s" % clean_id

        if self.inputmode == "1":
            js = """<script type='text/javascript'>$j(function(){
$j.datepicker.setDefaults($j.datepicker.regional['%(regional)s']);
/*$j.datepicker.setDefaults({ dateFormat: 'yy-mm-dd', showButtonPanel: %(showb)s });*/
$j('#%(id)s').datepicker('destroy').datepicker({
    dateFormat: 'yy-mm-dd', showButtonPanel: %(showb)s,
    onSelect: function(d,i) { execEventBinded('%(clean_id)s', "valuechange", {"itemValue": d}); }
});
});</script>""" % {"id": id, "clean_id": clean_id, "regional": self.regional, "showb": "true" if self.showbuttonpanel == "1" else "false"}
            modestyle = "url('/0f94d563-04ee-0283-2138-62c68af01145.res') right 50% no-repeat"
        else:
            js = ""
            modestyle = ""

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
            "background": modestyle,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            styles["position"] = ""

        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        result = """<input id="{id}" ver="2011-12-26" name="{name}" style="{style}" type="text" tabindex="{tabind}"
                    value="{value}" class="{classn} vdom_formdate" autocomplete="{auto}" {mode} /> {css} {js}
            """.format(id=id, name=self.name, style=style, tabind=self.tabindex, css=css, value=self.value, classn=self.classname, auto=auto, mode=mode, js=js)

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]
        image_width = image_height = 16
        image_x = image_y = 0

        if width > image_width - 2:
            image_x = width - image_width - 2
        else:
            image_x = 1
            image_width = width - 2

        if height > image_height:
            image_y = (height - image_height - 2) / 2
        else:
            image_y = 1
            image_height = height - 2

        modestyle = ""
        if self.inputmode == "1":  # input mode "date"
            modestyle = """<image x="{image_x}" y="{image_y}" width="{image_width}" height="{image_height}" href="#Res(0f94d563-04ee-0283-2138-62c68af01145)" />
                """.format(image_x=image_x, image_y=image_y, image_width=image_width, image_height=image_height)

        text = ""
        if self.value:
            text = """<text left="{text_x}" top="{text_y}" width="{text_width}" color="#000000">{value}</text>""".format(
                text_x=2, text_y=image_y, text_width=width if self.value else 0, value=self.value
            )

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect x="0" y="0" width="{rect_width}" height="{rect_height}" fill="#FFFFFF" stroke="#000000"/>
                        {modestyle}
                    </svg>
                    {text}
                </container>
             """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            modestyle=modestyle,
            text=text,
            name=self.name,
            top=top,
            left=left,
            width=width,
            height=height,
            rect_width=width - 1,
            rect_height=height - 1,
        )

        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
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

    if "ide_width" in attributes:
        if int(attributes["ide_width"]) < 10:
            attributes.update(ide_width="10")

    if "ide_height" in attributes:
        if int(attributes["ide_height"]) < 4:
            attributes.update(ide_height="4")

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