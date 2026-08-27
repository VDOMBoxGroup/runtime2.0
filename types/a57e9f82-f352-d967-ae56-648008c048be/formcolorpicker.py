class VDOM_formcolorpicker(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        self.set_color_value()

        display = "none" if self.visible == "0" else self.displaying

        if self.mode == "1":
            mode = """readonly="readonly" """
        elif self.mode == "2":
            mode = """disabled="disabled" """
        else:
            mode = ""

        clean_id = (self.id).replace("-", "_")
        id = "o_%s" % clean_id

        # for doctype xhtml 1.0 - width|height depends on padding
        # fixw = int(self.width) - 10
        # fixh = int(self.height) - 4

        border = "border-width: 0px;" if self.border == "0" else ""
        hide = "true" if self.mode == "1" else "false"
        title_OK = (self.titleok).replace('"', "'")
        title_Canc = (self.titlecancel).replace('"', "'")

        div_styles = {
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": self.zindex if int(self.zindex) != 0 else "",
            "position": self.positioning if self.positioning != "static" else "",
            "display": display,
        }
        if self.positioning == "static":
            div_styles["top"] = div_styles["left"] = ""
        div_style = " ".join(["{}: {};".format(key, value) for key, value in div_styles.items() if value])

        inp_styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "border-width": "0px" if self.border == "0" else "",
        }
        inp_style = " ".join(["{}: {};".format(key, value) for key, value in inp_styles.items() if value])

        result = """<div id="%(id)s" style="%(div_style)s"><input id="inp_%(id)s" class='%(userclass)s vdom_formcolorpicker' name="%(name)s" style="%(inp_style)s" type="text" tabindex="%(tabind)s" value="%(value)s" /></div>
<script type="text/javascript">$(document).ready(function(){
    $("#inp_%(id)s").colorInput({
        hideInput:%(hide)s,textAccept:"%(title_OK)s",textCancel:"%(title_Canc)s",
        change:function(){
            execEventBinded("%(clean_id)s","changecolor",{color:this.value});
        }
    });
});</script>""" % {
            "div_style": div_style,
            "id": id,
            "name": self.name,
            "userclass": self.classname,
            "inp_style": inp_style,
            "tabind": self.tabindex,
            "value": self.value,
            "hide": hide,
            "title_OK": title_OK,
            "title_Canc": title_Canc,
            "clean_id": clean_id,
        }

        return VDOM_object.render(self, contents=result)

    def get_btn_properties(self):
        form_width = int(self.width)
        try:
            object = application.objects.search(self.id)
            if object and object.parent:
                form_obj = application.objects.search(object.parent.id)
                if form_obj:
                    form_width = int(form_obj.attributes.width)
        except Exception:
            form_width = int(self.width)

        distance = 2

        btn_width = btn_height = 20

        if self.mode == "1":  # "hide"
            btn_x = btn_y = 0
        else:
            btn_x = int(self.width) + distance
            btn_y = (int(self.height) - btn_height) / 2

            obj_max_right = int(self.left) + int(self.width) + distance + btn_width
            if form_width < obj_max_right:
                btn_x = 0
                btn_y = int(self.height)

        return btn_x, btn_y, btn_width, btn_height

    def set_color_value(self):
        if self.value:
            if not self.value.startswith("#"):
                self.value = "#" + self.value
        else:
            self.value = "#cccccc"

    def wysiwyg(self, contents=""):
        self.set_color_value()
        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        text_size = self.width if self.value else 0

        btn_x, btn_y, btn_width, btn_height = self.get_btn_properties()

        text_y = 0 if self.height <= 22 else (int(self.height) - 20) / 2
        text = (
            ""
            if self.mode == "1"
            else """<text x="3" y="{text_y}" width="{txt_wid}" height="20" align="left" color="#000000" font-family="tahoma" font-size="14">{value}</text>""".format(
                txt_wid=text_size, value=self.value, text_y=text_y
            )
        )

        input_stroke = "" if self.border == "0" else """ stroke="#aaaaaa" """
        rect_input = (
            ""
            if self.mode == "1"
            else """<rect x="0" y="0" width="{rec_wid}" height="{rec_hei}" fill="#FFFFFF" {stroke}/>""".format(
                rec_wid=self.width - 1, rec_hei=self.height - 1, stroke=input_stroke
            )
        )

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                        top="{top}" left="{left}" width="{width}" height="{height}" >
                    <svg>
                        {rect_input}
                        <rect x="{btn_x}" y="{btn_y}" width="{btn_width}" height="{btn_height}" fill="{color}"/>
                        {text}
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
            width=self.width,
            height=self.height,
            color=self.value,
            name=self.name,
            btn_x=btn_x,
            btn_y=btn_y,
            btn_width=btn_width,
            btn_height=btn_height,
            rect_input=rect_input,
            text=text,
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


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")