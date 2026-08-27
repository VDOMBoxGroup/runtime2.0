class VDOM_uploader(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": self.zindex if int(self.zindex) != 0 else "",
            "position": self.positioning if self.positioning != "static" else "",
            "display": "none" if self.visible == "0" else self.displaying,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        woid = (self.id).replace("-", "_")
        id = "o_" + woid
        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        js = """<script type='text/javascript'>
            $j(function($){
                $('#%(id)s input').change(function() {
                    $('#%(id)s input').each(function() {
                        var name = this.value;
                        //var fileTitle = name.replace(/.*\\(.*)/g, "$1");
                        //fileTitle = fileTitle.replace(/.*\/(.*)/g, "$1");
                        execEventBinded('%(woid)s', "change", {title:name});
                    });
                });
            });
            </script>
            """ % {"id": id, "woid": woid}

        result = """
            {skin}
            <div style="{style}" id="{id}" class="{classname} vdom_uploader">
                <div class="label" style="display: none">{text}</div>
                <input type="file" accept="{accept}" {required} name="{name}" tabindex="{tabind}" />
            </div>
            {js}
            """.format(
            id=id,
            name=self.name,
            style=style,
            tabind=self.tabindex,
            classname=self.classname,
            text=self.text,
            js=js,
            skin=css,
            required="required" if self.required == "1" else "",
            accept=self.accept,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                        top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect x="{r1_left}" y="{r1_top}" width="{r1_wid}" height="{r1_hei}" fill="#FFFFFF" stroke="#000000"/>
                        <rect x="{r2_left}" y="{r2_top}" width="{r2_wid}" height="{r2_hei}" fill="#CCCCCC" stroke="#000000"/>
                    </svg>
                    <text top="{txt_top}" left="{txt_left}" width="{txt_wid}" color="#000000" textalign="center">{value}</text>
                    {contents}
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            name=self.name,
            top=top,
            left=left,
            width=width,
            height=height,
            r1_left=0,
            r1_top=0,
            r1_wid=width - 87,
            r1_hei=height - 1,
            r2_left=width - 80,
            r2_top=0,
            r2_wid=79,
            r2_hei=height - 1,
            txt_top=height / 2 - 9,
            txt_left=width - 80,
            txt_wid=79,
            value="Browse...",
            contents=contents,
        )

        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    # o = application.objects.search(object_id)
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

    pro_suite = """
#%(id)s {
    height: 33px;
    overflow: hidden;
}
#%(id)s .label {
    display: block !important;
    text-align: center;
    background: #fff url("/c016ef5e-c636-586d-9841-f3ff499831aa.png") bottom center repeat-x !important;
    text-decoration: none;
    line-height: 25px;
    border: 1px solid #c5c5c5;
    -webkit-border-radius: 6px;
    -moz-border-radius:6px;
    -ms-border-radius: 6px;
    -o-border-radius:6px;
    border-radius: 6px;
    cursor: pointer;
    outline: none !important;
    height: 26px !important;
    -webkit-box-shadow:inset 0 0 3px #fff;
    -moz-box-shadow:inset 0 0 3px #fff;
    -ms-box-shadow:inset 0 0 3px #fff;
    -o-box-shadow:inset 0 0 3px #fff;
    box-shadow:inset 0 0 3px #fff;
    -webkit-transition: all 0.7s ease;
    -moz-transition: all 0.7s ease;
    -ms-transition: all 0.7s ease;
    -o-transition: all 0.7s ease;
    transition: all 0.7s ease;
    line-height: 24px !important;
    font-size: 14px;
    color: #000;
    font-family: Arial,sans-serif;
}
#%(id)s .label:hover {
    -webkit-box-shadow:inset 0 0 6px #fff;
    -moz-box-shadow:inset 0 0 6px #fff;
    -ms-box-shadow:inset 0 0 6px #fff;
    -o-box-shadow:inset 0 0 6px #fff;
    box-shadow:inset 0 0 6px #fff;
    border: 1px solid #a8a8a8;
}
#%(id)s input {
    margin-top: -50px;
    margin-left:-410px;
    -moz-opacity: 0;
    filter: alpha(opacity=0);
    opacity: 0;
    font-size: 150px;
    height: 100px;
}
"""
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