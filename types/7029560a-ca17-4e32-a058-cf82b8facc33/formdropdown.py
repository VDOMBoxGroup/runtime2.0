from io import StringIO


class VDOM_formdropdown(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = "none" if self.visible == "0" else self.displaying
        zindex = self.zindex if int(self.zindex) != 0 else ""
        position = self.positioning if self.positioning and self.positioning != "static" else ""

        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "position": position,
            "display": display,
            "font-size": "%s" % self.check_unit(self.fontsize) or None,
            "font-family": "%s" % self.fontfamily.replace('"', "'") or None,
            "z-index": zindex,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        id = "o_" + (self.id).replace("-", "_")
        size_attr = """size="%s" """ % self.size if self.size else ""

        classname = """class='%s'""" % " ".join([self.classname, "vdom_formdropdown"]).strip()

        if self.multiselect and self.multiselect == "1":
            multiselect_attr = """multiselect="1" """
        else:
            multiselect_attr = ""

        select = """<select id="{id}" name="{name}" tabindex="{tabind}" {size} {multisel} style="{style}" {classname}>
                """.format(id=id, name=self.name, tabind=self.tabindex, size=size_attr, multisel=multiselect_attr, style=style, classname=classname)

        if not self.value:
            self.value = self.value1

        list = self.value.split("|")
        list1 = self.value1.split("|")
        if len(list) != len(list1):
            return ""

        res_buffer = StringIO("")
        res_buffer.write(select)

        for idx in range(len(list1)):
            if str(list1[idx]) == str(self.selectedvalue):
                selected = """selected="selected" """
            else:
                selected = ""
            option = """<option value="{cur_value}" {selected}>{cur_item}</option>""".format(cur_value=list1[idx], selected=selected, cur_item=list[idx])
            res_buffer.write(option)

        res_buffer.write("</select>")
        result = res_buffer.getvalue()
        res_buffer.close()
        return result

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                        top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect y="{out_top}" x="{out_left}" width="{out_wid}" height="{out_hei}" fill="#FFFFFF" stroke="#000000"/>
                    </svg>{contents}
                    <svg>
                        <rect x="{inn_left}" y="{inn_top}" width="{inn_wid}" height="{inn_hei}" fill="#EEEEEE" stroke="#000000"/>
                        <polygon fill="black" stroke="#000000" points="{xa},{ya} {xb},{yb} {xc},{yc}"/>
                    </svg>
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
            out_top=0,
            out_left=0,
            out_wid=width - 1,
            out_hei=height - 1,
            contents=contents,
            inn_left=width - 14,
            inn_top=0,
            inn_wid=14,
            inn_hei=height - 1,
            xa=width - 9,
            ya=height / 2 - 3,
            xb=width - 5,
            yb=height / 2 - 3,
            xc=width - 7,
            yc=height / 2 + 3,
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
    #    if "skin" in attributes:
    #    	skin = attributes["skin"]
    #    	if skin in skin_mapping:
    #    		attributes.update(style=skin_mapping[skin])
    #    	else:
    #    		attributes.update(skin="0")
    #    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
    #    	attributes.update(skin="0")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")