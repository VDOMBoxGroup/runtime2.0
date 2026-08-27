import utils
import re


class VDOM_formimage(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        alt = """alt="{}" """.format(self.alt) if self.alt else ""
        link = utils.id.id2link1(self.value)
        id_out = "o_" + (self.id).replace("-", "_")
        styleblock = ""
        scriptblock = ""
        display = "none" if self.visible == "0" else self.displaying
        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": self.zindex if self.zindex != 0 else "",
            "position": self.positioning,
            "display": display,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            styles["position"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])
        css = "<style>\n" + self.style % {"id": id_out} + "</style>" if self.style else ""

        if self.ishover == "1":
            src_classname = self.classname if self.classname else "imagebutton"
            src_id = id_out[2:]
            classtut = "{src_cname}_{src_id}".format(src_cname=src_classname, src_id=src_id)
            if self.ispressed == "1":
                self.classname = "{classtut} {classtut}_sel".format(classtut=classtut)
            else:
                self.classname = classtut

            styleblock = """<style>.%(class)s,.%(class)s_sel{background:url("%(link)s") left top no-repeat;}
                                .%(class)s_sel{background-position:left -%(height)s!important}</style>
                        """ % {"class": classtut, "link": link, "height": self.height}

            scriptblock = """<script type="text/javascript">
                                    jQuery("#%(id)s").hover(function(){jQuery(this).addClass("%(class)s_sel");},
                                        function(){jQuery(this).removeClass("%(class)s_sel");});
                                    jQuery("#%(id)s").click(function(){jQuery(this).toggleClass("%(class)s_sel");});
                            </script>
                        """ % {"id": id_out, "class": self.classname}
            link = "/2ca0f428-ffc2-ca5b-3337-610d2384821f.gif"

        result = """<input value=" " id="{id}" name="{name}" style="{style}" tabindex="{tabind}" {alt}
                    src="{link}" border="0" type="image" class="{lclass} vdom_formimage" />{css} {styleblk} {scriptblk}
            """.format(
            id=id_out,
            name=self.name,
            style=styles_str,
            tabind=self.tabindex,
            css=css,
            alt=alt,
            link=link,
            lclass=self.classname,
            styleblk=styleblock,
            scriptblk=scriptblock,
        )

        return VDOM_object.render(self, contents=result)

    def regex(self, obj):
        match = re.search(r"\d+", obj)
        return int(match.group()) if match else ""

    def wysiwyg(self, contents=""):
        image_id = self.value
        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        if not image_id:
            from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

            image_id = "ba54cd2d-ade1-c3c0-35b2-170f9a00b033"
            result = get_empty_wysiwyg_value(self, image_id)

            return VDOM_object.wysiwyg(self, contents=result)

        image_width = """ width="{width}" """.format(width=self.width)
        image_height = """ height="{height}" """.format(height=self.height)

        if self.ishover == "1":
            image_width = image_height = ""
            if self.ispressed == "1":
                image_id = "2ca0f428-ffc2-ca5b-3337-610d2384821f"

        result = """<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                            top="{top}" left="{left}" width="{width}" height="{height}">
                        <svg>
                            <image x="0" y="0" {image_width} {image_height} href="#Res({img_id})" editable="value"/>
                        </svg>
                        {contents}
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
            image_width=image_width,
            image_height=image_height,
            img_id=image_id,
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

    if "value" in attributes and "ide_width" not in attributes and "ide_height" not in attributes:
        attr = attributes["value"]
        res_id = attributes["value"]

        ro = application.resources.get(res_id)
        if not ro:
            return "Resource not found"

        # get image resource, obtain width and height and set width and height of the object
        from PIL import Image
        from io import StringIO

        s = StringIO()
        s.write(ro.get_data())
        s.seek(0, 0)
        im = Image.open(s)
        width, height = im.size
        # set attributes
        if o.attributes["ide_width"] != width or o.attributes["ide_height"] != height:
            attributes.update(ide_width=str(width), ide_height=str(height))
    else:
        unit = "px"
        if "ide_width" in attributes and attributes["ide_width"] != "" and int(attributes["ide_width"].rstrip(unit)) > 2500:
            attributes["ide_width"] = "2500" + unit
        if "ide_height" in attributes and attributes["ide_height"] != "" and int(attributes["ide_height"].rstrip(unit)) > 2500:
            attributes["ide_height"] = "2500" + unit

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