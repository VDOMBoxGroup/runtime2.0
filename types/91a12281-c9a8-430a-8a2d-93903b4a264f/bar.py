class VDOM_bar(VDOM_object):
    
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = u"none" if self.visible == "0" else self.displaying

        style_zindex = u"z-index: %s;" % self.zindex if int(self.zindex) != 0 else u"" # 123
        backgrnd = u"background: #{color}".format(color=self.color) if self.color else u""
        position = u"position: {pos};".format(pos=self.positioning) if self.positioning and self.positioning != "static" else u""
        
        styles = {
            "display": display,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left)
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
        
        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        style = (u"""{zind} {pos} {styles} {color}""")\
                .format(
                    zind = style_zindex, pos = position,
                    styles = styles_str, color = backgrnd)

        id = u"o_" + (self.id).replace('-', '_')
        css = u"<style>\n" + self.style % {"id": id} + u"</style>" if self.style else u""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='bar' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = u""

        result = u"""{css}\
                    <div {debug_info} id="{id}" style="{style}" class="{classname}">{contents}</div>""".format(
            debug_info = debug_info,
            id = id, css = css,
            style = style,
            classname = ' '.join([self.classname, 'vdom_bar']).strip(),
            contents = contents )

        return VDOM_object.render(self, contents=result)
        

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        result = \
            u"""<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect x="0" y="0" width="{width}" height="{height}" fill="#{color}"/>
                    </svg>
                    {contents}
                </container>
            """.format(
                    id = self.id, vis = self.visible, zind = self.zindex,
                    hierarchy = self.hierarchy, order = self.order,
                    top = top, left = left, width = width, height = height,
                    color = self.color or "000000", contents = contents, name = self.name)

        return VDOM_object.wysiwyg(self, contents=result)

def on_update(object, attributes):
    o = object
    modifications = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, '').lower()
            
            if obj_value.isdigit() and attr_value.isdigit():
                modifications[attr] = attr_value + "px"
                modifications["ide_"+ attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                modifications[attr] = attr_value.rstrip("px") + "px"
                modifications["ide_"+ attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                modifications[attr] = attr_value if "px" in attr_value else obj_value
                modifications["ide_"+ attr] = attr_value.rstrip("px")
            else:
                modifications[attr] = attr_value
                
    attributes.update(modifications)
    
    users = u"""\
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
    
    return ""
    
            
def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]
        
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_"+ attr] = obj_value.rstrip("px")