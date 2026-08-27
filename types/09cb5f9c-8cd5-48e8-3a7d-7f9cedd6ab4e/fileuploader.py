class VDOM_fileuploader(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        zindex = "%s" % self.zindex if int(self.zindex) != 0 else ""
        display = "none" if self.visible == "0" else self.displaying
        position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""

        styles = {
            "z-index": zindex,
            "display": display,
            "position": position,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "border": self.border,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        woid = (self.id).replace("-", "_")
        id = "o_" + woid
        input_html = ""

        classname = """class="%s" """ % " ".join([self.classname, "uploader_holder"]).strip()

        js = """\
<script type='text/javascript'>
$(document).ready(() => {
    if (typeof file_upl_%(id)s !== 'undefined') {
        delete(file_upl_%(id)s);
    }
    file_upl_%(id)s = new FileUploader('%(id)s', '%(endpoint)s', %(disabled)s, '%(title)s', '%(description)s');
});
</script>""" % {
            "id": id,
            "endpoint": self.endpoint,
            "disabled": self.dropzone_disabled,
            "title": self.title,
            "description": self.description,
        }

        if self.input_file == "1":
            input_html = """
                <input type="file" accept="{accept}" {required} name="{name}" tabindex="{tabind}" {multiple}/>
            """.format(
                accept=self.accept,
                required="required" if self.required == "1" else "",
                name=self.name,
                tabind=self.tabindex,
                multiple="multiple='multiple'" if self.multiple == "1" else "",
            )

        debug_info = ""
        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='container' objname='%s'" % (self.name)

        result = """
            <style>{skin}</style>
            <div {debug_info} style="{style}" id="{id}" {classname}>
                    <div class="intro">
                        <div class="intro_title">{title}</div>
                        <div class="intro_description">{description}</div>
                    </div>
                    <div class="upload_btn">
                        <span>Upload</span>
                        <div class="upload_icon">
                            {svg}
                        </div>
                    </div>
                    <div class="upload_hint">{hint}</div>
                    {input_html}
                </div>
            {js}
            """.format(
            id=id,
            style=styles_str,
            classname=classname,
            js=js,
            debug_info=debug_info,
            title=self.title,
            description=self.description,
            hint=self.hint,
            skin=self.style % {"id": id},
            svg=self.svg_image,
            input_html=input_html,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [
            int(self.ide_width),
            int(self.ide_height),
            int(self.ide_top),
            int(self.ide_left),
        ]

        image_id = "655979b3-c438-c17d-be3f-7faea488f06f"
        result = get_empty_wysiwyg_value(self, image_id)
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

    empty = ""

    default = """\
#%(id)s {
  display: flex;
  align-items: center;
  justify-content: center;
}
"""

    users = """\
#%(id)s {

}
"""

    skin_mapping = {"0": empty, "1": default, "2": users}
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="2")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="2")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")