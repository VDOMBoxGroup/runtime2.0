import json
from collections import OrderedDict
from collections.abc import Iterable


class VDOM_formlist(VDOM_object):

    def get_data(self):
        # try to parse json
        try:
            value = json.loads(self.value, object_pairs_hook=OrderedDict)

        except Exception:
            if self.value:
                raise Exception(
                    "value: %r. Incorrect format of JSON data" % self.value)

            value = []

        if not isinstance(value, Iterable):
            raise Exception("value: %r. Must be dict or list" % self.value)

        return value

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
            "z-index": zindex
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        style = " ".join([f"{key}: {value};"
                         for key, value in styles.items() if value])

        id = "o_" + (self.id).replace('-', '_')

        disabled = """ disabled="disabled\"""" if self.disabled == "1" else ""
        multi = """ multiple="multiple\"""" if self.multiselect and self.multiselect == "1" else ""
        size = """ size="%s" """ % self.size if self.size else ""

        select = """<select id="{id}" name="{name}" tabindex="{tabind}" autocomplete="off" class="{classname}" style="{style}" {size}{multi}{disabled}>"""\
            .format(
                disabled=disabled,
                id=id,
                name=self.name,
                tabind=self.tabindex,
                style=style,
                size=size,
                multi=multi,
                classname=' '.join([self.classname, 'vdom_formlist']).strip()
            )

        try:
            selected_values = json.loads(self.selectedvalue)
        except Exception:
            selected_values = self.selectedvalue

        if not isinstance(selected_values, list):
            selected_values = [selected_values]

        try:
            disabled_values = json.loads(self.disabledvalue)
        except Exception:
            disabled_values = self.disabledvalue

        if not isinstance(disabled_values, list):
            disabled_values = [disabled_values]

        data = self.get_data()
        try:
            data = iter(data.items())
        except Exception:
            data = zip(range(len(data)), data)

        result = "".join(["""<option value="{value}"{selected}{disabled}>{title}</option>""".format(
            value=value,
            selected=""" selected="selected\"""" if value in selected_values else "",
            disabled=""" disabled="disabled\"""" if value in disabled_values else "",
            title=title
        ) for value, title in data])

        result = f"{select}{result}</select>"
        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(
            self.ide_height), int(self.ide_top), int(self.ide_left)]

        rect_width = width - 1 if width > 1 else width
        rect_height = height - 1 if height > 1 else height

        btn_width = 15 if rect_width > 15 else rect_width
        btn_height = rect_height
        btn_y = 0
        btn_x = rect_width - btn_width - 1 if rect_width > btn_width else 0

        triangle_width = 5
        if btn_width < triangle_width:
            triangle_width = btn_width
            triangle_x = btn_x
        else:
            triangle_x = btn_x + (btn_width - triangle_width) / 2 + 1

        triangle_height = 4
        if btn_height < triangle_height:
            triangle_height = btn_height
            triangle_y = 0
        else:
            triangle_y = (btn_height - triangle_height) / 2

        color = "#aaaaaa" if self.disabled == "1" else "#000000"
        btn = \
            f"""<svg>
                        <rect x="{btn_x}" y="{btn_y}" width="{btn_width}" height="{btn_height}" fill="#EEEEEE" stroke="{color}"/>
                        <polygon fill="{color}" stroke="{color}" points="{triangle_x},{triangle_y} {triangle_x + triangle_width},{triangle_y} {triangle_x + triangle_width / 2},{triangle_y + triangle_height}"/>
                    </svg>
                """

        result = \
            f"""<container name="{self.name}" id="{self.id}" visible="{self.visible}" zindex="{self.zindex}" hierarchy="{self.hierarchy}" order="{self.order}"
                        top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect y="0" x="0" width="{rect_width}" height="{rect_height}" fill="#FFFFFF" stroke="{color}"/>
                    </svg>
                    <svg>
                        <text x="{7}" y="{15 if rect_height < 15 else (rect_height - 15) / 2 + 15}" width="{width}" height="{height}" fill="{color}" font-size="14" font-family="tahoma"></text>
                    </svg>
                    {btn}
                </container>
            """

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):

    users = """
#%(id)s {

}
"""

    skin_mapping = {
        "0": users,
        "1": ""
    }

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
            obj_value = o.attributes.get(attr, '').lower()

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