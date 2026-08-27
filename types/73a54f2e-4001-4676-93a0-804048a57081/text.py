import json
import re

class VDOM_text(VDOM_object):
    
    def get_px(self, value):
        if value.isdigit():
            return value + "px"
        else:
            return value

    def render(self, contents=""):
                    
        if self.positioning == "static":
            self.positioning = ""
            self.left = self.top = ""

        custom_attributes = ""
        style_zindex = u"z-index: %s;" % self.zindex if int(self.zindex) != 0 else u""
        style = {
            "display": "none" if self.visible=="0" else self.displaying or None,
            "position": self.positioning if self.positioning else None,
            # "overflow": "auto",
            "top": "%s" % self.get_px(self.top) if self.top else None,
            "left": "%s" % self.get_px(self.left) if self.left else None,
            "width": "%s" % self.get_px(self.width) if self.width else None,
            "text-align": "%s" % self.align or None,
            "font-size": "%s" % self.get_px(self.fontsize)or None,
            "font-family": "%s" % self.fontfamily.replace('"', "'") or None,
            "font-style": "%s" % self.fontstyle or None,
            "font-weight": "%s" % self.fontweight or None,
            "text-transform": "%s" % self.texttransform or None,
            "color": "#%s" % self.color if self.color else None,
            "text-decoration": "%s" % self.textdecoration or "",
            "margin": "%s" % self.margins if self.margins else None,
            "padding": "%s" % self.paddings if self.paddings else None
        }

        hint = u" title=\"%s\" " % (self.hint).replace('"', '&quot;') if (self.hint).strip() != "" else u""
        css = u"<style>\n" + self.style % {"id": self.id_special} + u"\n</style>" if self.style else u""
        
        custom_attr_json = json.loads(self.custom_attributes) if self.custom_attributes else ""
        if custom_attr_json:
            custom_attributes = " ".join(['{}="{}"'.format(key, value) for key, value in custom_attr_json.items()])

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='text' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = u""

        result = u"""<{html_tag} {debug_info} id="{id}" style="{zind} {style}" class="{classname}" {hint} {custom_attr}>{value}</{html_tag}>
                  {css}
                  """.format(
            hint = hint,
            css = css,
            zind = style_zindex,
            debug_info = debug_info,
            id = self.id_special,
            style = "; ".join(["%s: %s" % (key, value) for key, value in style.items() if value]),
            classname = ' '.join([self.classname, 'vdom_text']).strip(),
            value = self.value,
            html_tag = self.htmltag,
            custom_attr = custom_attributes
        )

        return VDOM_object.render(self, contents=result)
            
    def regex(self, obj):
        match = re.search(r'\d+', obj)
        return int(match.group()) if match else ""
    
    def wysiwyg(self, contents=""):
        the_value = self.value

        value = "<![CDATA[%s]""]>" % the_value

        empty_value = \
            u"""<svg>
                <text fill="#cccccc" x="5" y="10">Text</text>
            </svg>""" if the_value == "" else ""

        fontsize="fontsize=\"%s\"" % self.regex(self.fontsize) if self.fontsize else ""
        self.fontfamily = self.fontfamily.replace('"', '').replace("'", '') or 'Tahoma, "Geneva CY", geneva, sans-serif'
        editable="value,color,fontfamily,fontsize,fontstyle,fontweight,align,textdecoration"
            
        width, top, left = [int(self.ide_width), int(self.ide_top), int(self.ide_left)]
        
        result=\
            u"""<container name="{name}" id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}" order="{order}" top="{top}" left="{left}" width="{width}">
                {empty_value}
                <text top="{textTop}" left="{textLeft}" width="{width}" color="#{color}" fontstyle="{fontstyle}" fontweight="{fontweight}" fontfamily="{fontfamily}"
                {fontsize} textalign="{align}" textdecoration="{textdecoration}" editable="{editable}">{value}</text>
                {contents}
            </container>""".format(
                id = self.id,
                visible = self.visible,
                zindex = self.zindex,
                hierarchy = self.hierarchy,
                order = self.order,
                top = top,
                left = left,
                width = width,
                textTop = 0,
                textLeft = 0,
                color = self.color or "000000",
                fontstyle = self.fontstyle or "normal",
                fontweight = self.fontweight or "normal",
                fontfamily = self.fontfamily.replace('"', '').replace("'", ''),
                fontsize = fontsize,
                align = self.align or "left",
                textdecoration = self.textdecoration or "none",
                editable = editable,
                value = value,
                contents = contents,
                empty_value = empty_value,
                name = self.name
            )

        #print result
        return VDOM_object.wysiwyg(self, contents=result)

def on_update(object, attributes):
    o = object
    modifications = {}
    
    for attr in ["left", "width", "top"]:
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
    empty = ""
    
    skin_mapping = {
        "0": users,
        "1": empty
    }
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")
            
    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")
            
    # if "style" in attributes and attributes["style"] and o.attributes.style != custom:
    # 	o.attributes.update(skin=0)

    return ""
            
def on_compile(object, attributes):
    for attr in ["left", "width", "top"]:
        obj_value = object.attributes[attr]
        
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_"+ attr] = obj_value.rstrip("px")