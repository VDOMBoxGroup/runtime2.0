from scripting.legacy.id import id2link1
import re
import json


class VDOM_image(VDOM_object):
    def get_css_style(self, style_name, style_value):
        if style_name == 'clear' and style_value == 'none':
            return ""

        if style_name == 'background-color' and style_value == '#':
            return ""

        if style_name == 'z-index' and style_value == '0':
            return ""
        elif style_name == 'z-index' and style_value.isdigit():
            return "{}: {};".format(style_name, style_value)

        if style_value.isdigit() and style_name not in ['flex-grow', 'order', 'flex-shrink']:
            return "{}: {}px;".format(style_name, style_value)

        if style_value == "":
            return ""
        else:
            return "{}: {};".format(style_name, style_value)

    def render(self, contents=""):
        alt = u"""alt="{}" """.format(self.alt) if self.alt else ""
        link = ""
        svg = ""

        if self.value:
            link = id2link1(self.value)
        elif self.svgvalue:
            svg = self.svgvalue
        elif self.externalurl:
            link = self.externalurl
        elif self.base64stream:
            import base64
            data = base64.b64decode(self.base64stream)
            res_id = application.resources.create_temporary(
                self.id, "data", data, "png", "data")
            link = "/%s.png" % res_id

        visible = u"none" if self.visible == "0" else self.displaying
        positioning_map = {
            "0": "",
            "1": "absolute",
            "2": "relative",
            "3": "fixed"
        }
        position = positioning_map.get(self.positioning1, "")
        if position == "":
            self.left = self.top = ""
            self.right = self.bottom = ""

        id = 'o_' + (self.id).replace('-', '_')

        custom_attributes = ""
        custom_attr_json = json.loads(
            self.custom_attributes) if self.custom_attributes else ""
        if custom_attr_json:
            custom_attributes = " ".join(
                ['{}="{}"'.format(key, value) for key, value in custom_attr_json.items()])

        style_mixin = u""
        clear = "none"
        if self.float == 'both':
            clear = "both"
            self.float = "none"

        title = ""
        if self.hint:
            title = u"""title="{hint}" """.format(hint=self.hint)

        iw = self.width if self.width else "0px"
        ih = self.height if self.height else "0px"

        style_properties = [
            ('width', self.width),
            ('height', self.height),
            ('z-index', self.zindex),
            ('top', self.top),
            ('left', self.left),
            ('right', self.right),
            ('bottom', self.bottom),
            ('background-position', self.backgroundposition),
            ('background-repeat', self.backgroundrepeat),
            ('display', visible),
            ('position', position),
            ('float', self.float),
            ('clear', clear),
            ('margin', self.margins),
            ('padding', self.paddings),
            ('align-self', self.alignself),
            ('flex-grow', self.flexgrow),
            ('flex-basis', self.flexbasis),
            ('order', self.orderchild),
            ('flex-shrink', self.flexshrink),
            ('background-color', "#" + self.backgroundcolor)
        ]
        styles = [self.get_css_style(name, value)
                  for name, value in style_properties if value]
        styles = " ".join(styles)

        css = u"<style>\n" + \
            self.style % {"id": id} + u"</style>" if self.style else u""
        classname = ' '.join([self.classname, 'vdom_image']).strip()

        result = ""
        if self.render_mode == "0":
            if svg:
                svg = svg.replace("<svg ", '<svg id="{id}" objname="{name}" class="{classname} image" tabindex="{tabindex}" style="{styles}" '.format(
                    id=id,
                    name=self.name,
                    classname=classname,
                    styles=styles,
                    tabindex=self.tabindex
                ))
                if self.hint:
                    pattern = r"</svg>"
                    replacement = "<title>{}</title>\n</svg>".format(self.hint)
                    result = re.sub(pattern, replacement, svg)
                else:
                    result = svg

            else:
                result = \
                    u"""<img id="{id}" objname={name} class="{classname} image" src="{link}" tabindex="{tabindex}" style="{styles}" {title} {custom_attr} {alt}/>""".format(
                        id=id,
                        name=self.name,
                        link=link,
                        tabindex=self.tabindex,
                        classname=classname,
                        title=title,
                        custom_attr=custom_attributes,
                        styles=styles,
                        alt=alt)
        if self.render_mode == "1":
            style_mixin = "{backgroundimage} ".format(
                backgroundimage=self.get_css_style('background-image', "url(" + link + ")"))

            result = u"""<div objname={name} class="{classname} background_image" {width} {height} id="{id}" style="{styles} {bgimage}" {custom_attr}></div>""".format(
                id=id,
                name=self.name,
                width=self.get_css_style('width', iw),
                height=self.get_css_style('height', ih),
                classname=classname,
                styles=styles,
                custom_attr=custom_attributes,
                bgimage=style_mixin)

        if self.render_mode == "2":
            if svg:
                result = \
                    u"""<div objname={name} class="{classname} div_image" id="{id}" style="{styles}" {custom_attr}>
    {svg_code}
</div>""".format(
                        id=id,
                        name=self.name,
                        classname=classname,
                        styles=styles,
                        svg_code=svg,
                        custom_attr=custom_attributes)
            else:
                result = u"""<div objname={name} class="{classname} div_image" id="{id}" style="{styles}" {custom_attr}>
    <img src="{link}" tabindex="{tabindex}" {title} {alt}/>
</div>""".format(
                    id=id,
                    name=self.name,
                    link=link,
                    tabindex=self.tabindex,
                    classname=classname,
                    title=title,
                    styles=styles,
                    custom_attr=custom_attributes,
                    alt=alt)

        result += css

        return VDOM_object.render(self, contents=result)

    def is_correct_exturnal_url(self, url):
        if url.lower().startswith("http://") or url.lower().startswith("https://"):
            return True
        return False

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(
            self.ide_height), int(self.ide_top), int(self.ide_left)]

        if self.value:      # show image from resources
            editable = u' editable="value" '

            result = \
                u"""<container name="{name}" id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" top="{top}" left="{left}"
                        width="{width}" height="{height}" backgroundcolor="#f0f0f0" bordercolor="#000000">
                        <svg>
                            <image x="{image_x}" y="{image_y}" href="#Res({image_id})"
                                width="{width}" height="{height}" {editable}/>
                        </svg>
                    </container>
                """.format(
                    id=self.id,
                    zindex=self.zindex,
                    hierarchy=self.hierarchy,
                    top=top,
                    left=left,
                    width=width,
                    height=height,
                    image_x=0,
                    image_y=0,
                    image_id=self.value,
                    editable=editable,
                    name=self.name)

        elif self.externalurl:
            url = self.externalurl
            if not self.is_correct_exturnal_url(self.externalurl):
                url = u"http://empty.png"

            result = \
                u"""<container name="{name}" id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}"
                        order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
                        <htmltext top="0" left="0" width="{width}" height="{height}" locked="true">
                            <img width="{width}" height="{height}" src="{image_url}"/>
                        </htmltext>
                    </container>
                """.format(
                    id=self.id,
                    visible=self.visible,
                    zindex=self.zindex,
                    hierarchy=self.hierarchy,
                    order=self.order,
                    top=top,
                    left=left,
                    width=width,
                    height=height,
                    image_url=url,
                    name=self.name)

        else:
            image_id = "e8115c4a-903a-a4c6-c0bc-08a336586d51"
            result = \
                u"""<container name="{name}" id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" top="{top}" left="{left}"
                        width="{width}" height="{height}" backgroundcolor="#f0f0f0" bordercolor="#000000">
                        <svg>
                            <image x="{image_x}" y="{image_y}" href="#Res({image_id})"/>
                        </svg>
                    </container>
                """.format(
                    id=self.id,
                    zindex=self.zindex,
                    hierarchy=self.hierarchy,
                    top=top, left=left,
                    width=width, height=height,
                    image_x=(width - 50) / 2,
                    image_y=(height - 50) / 2,
                    image_id=image_id,
                    name=self.name)

        return VDOM_object.wysiwyg(self, contents=result)

# def set_attr(app_id, object_id, param):


def on_update(object, attributes):
    o = object
    modifications = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, '').lower()

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

    users = """\
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
    # o = application.objects.search(object_id)

    # if "value" in param and not "width" in param and not "height" in param:
    if "value" in attributes and "width" not in attributes and "height" not in attributes:
        # attr = param["value"]
        attr = attributes["value"]
        # res_id = attr["value"]
        res_id = attributes["value"]

        ro = application.resources.get(res_id)
        if not ro:
            return "Resource not found"

        # get image resource, obtain width and height and set width and height of the object
        from PIL import Image
        import io
        s = io.StringIO()
        s.write(ro.get_data())
        s.seek(0, 0)
        try:
            im = Image.open(s)
            width, height = im.size
        except Exception:
            width = 65

        if o.attributes["width"] != width or o.attributes["height"] != height:
            attributes.update(width=str(width) + "px", height="")
    else:
        # if "width" in param and param["width"]["value"] != '' and int(param["width"]["value"]) > 2500:
        #     o.set_attributes({"width": 2500})
        if "ide_width" in attributes and attributes["ide_width"] != '' and int(attributes["ide_width"]) > 2500:
            attributes["ide_width"] = "2500"
        # if "height" in param and param["height"]["value"] != '' and int(param["height"]["value"]) > 2500:
        #     o.set_attributes({"height": 2500})
        if "ideheight" in attributes and attributes["ide_height"] != '' and int(attributes["ide_height"]) > 2500:
            attributes["ide_height"] = "2500"
    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")