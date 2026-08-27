from scripting import e2vdom
from utils.csrf import create_csrf_token, csrf_token_arg_name


class VDOM_form(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = "none" if self.visible == "0" else self.displaying
        zind = "%s" % self.zindex if int(self.zindex) != 0 else ""
        e2vdom.process(self)

        overflow_values = {"0": "auto", "1": "hidden", "2": "scroll", "3": "visible"}
        overflow = overflow_values.get(self.overflow, "")

        if not self.target or self.meth == "event":
            target = ""
        else:
            ref_obj = application.objects.search(self.target)
            target = "/%s.vdom" % ref_obj.name if ref_obj else ""

        submitonce = ""

        woid = (self.id).replace("-", "_")
        id = "o_" + woid
        reportvalidity = self.reportvalidity
        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        if self.meth == "post":
            csrftoken = '<input type="hidden" name="%s" value="%s">' % (csrf_token_arg_name, create_csrf_token())
        else:
            csrftoken = ""

        if self.meth == "event":
            submitjs = """
      <script type="text/javascript">$(function () {new $.SubmitVDOMFormJs("%(id)s", %(reportvalidity)s);});
      </script>""" % {"id": id, "reportvalidity": "true" if reportvalidity == "1" else "false"}
        else:
            submitjs = ""

        if not self.enctype or self.meth == "event":
            enctype = ""
        else:
            enctype = """enctype="%s" """ % self.enctype

        position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""

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
            "overflow": overflow,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='form' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        result = """\
                {css}
                <form {debug_info} id="{id}" style="{style}" 
                    name="{name}" method="{method}" action="{target}" 
                    {enctype} {submitonce} class="{classname}">
                    {contents}
                    {csrftoken}
                </form> {submitjs} 
            """.format(
            debug_info=debug_info,
            id=id,
            style=styles_str,
            name=self.name,
            method=self.meth,
            target=target,
            enctype=enctype,
            submitonce=submitonce,
            css=css,
            contents=contents,
            csrftoken=csrftoken,
            submitjs=submitjs,
            classname=" ".join([self.classname, "vdom_form"]).strip(),
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        if len(contents) == 0:
            from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

            image_id = "54e7f8ab-64f1-b113-029e-1703a76c6fa4"
            self.width = width
            self.height = height
            self.top = top
            self.left = left
            result = get_empty_wysiwyg_value(self, image_id)

            return VDOM_object.wysiwyg(self, contents=result)

        # get overflow value
        overflow_dict = {"0": "auto", "1": "hidden", "2": "scroll", "3": "visible"}
        overflow_num = self.overflow if self.overflow else "0"
        overflow = overflow_dict[overflow_num]

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                            top="{top}" left="{left}" width="{width}" height="{height}" overflow="{overflow}">
                        <svg>
                            <rect x="0" y="0" width="{width}" height="{height}" fill="#EEEEEE" fill-opacity=".4" />
                        </svg>{contents}
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
            contents=contents,
            overflow=overflow,
        )

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

    users = """\
#%(id)s {

}
"""

    skin_mapping = {"0": users, "1": empty}
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