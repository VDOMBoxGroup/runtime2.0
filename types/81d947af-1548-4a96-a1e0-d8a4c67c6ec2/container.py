from scripting import e2vdom
from scripting.legacy.id import id2link1

class VDOM_container(VDOM_object):
    
    def check_unit(self, value):
        if value.startswith("-") and value[1:].isdigit():
            return value + "px"
        elif value.isdigit():
            return value + "px"
        else:
            return value

    def render(self, contents=""):

        if self.securitycode:
            self.visible = "0"
            if session["SecurityCode"] and str(session["SecurityCode"]) in self.securitycode.split(";"):
                self.visible = "1"

        display = u"none" if self.visible == "0" else self.displaying

        e2vdom.process(self)
        
        overflow_values = {
            "0": "auto",
            "1": "hidden",
            "2": "scroll",
            "3": "visible"
        }
        overflow = overflow_values.get(self.overflow, "")

        background_color = u"#%s" % self.backgroundcolor if self.backgroundcolor != "" else u""

        bgimage = id2link1(self.backgroundimage) if self.backgroundimage else u""
        
        if bgimage.endswith("."):
            bgimage += 'png'
            
        background_image = u"url('%s')" % bgimage if bgimage != "" else u""

        bgrepeat_values = {
            "0": "repeat",
            "1": "no-repeat",
            "2": "repeat-x",
            "3": "repeat-y"
        }
        background_repeat = bgrepeat_values.get(self.backgroundrepeat, "")

        style_zindex = u"%s" % self.zindex if int(self.zindex) != 0 else u""
        
        position = u"{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else u""
        
        styles = {
            "z-index": style_zindex,
            "display": display,
            "position": position,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "background-image": background_image,
            "background-color": background_color,
            "background-repeat": background_repeat,
            "overflow": overflow
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            
        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        id = u"o_" + (self.id).replace('-', '_')
        footer = u"""rel="footer" """ if self.footer == "1" else u""

        if self.titlewrap == "0":
            title_tag = u""
            cont_tag = u"%s" % contents
        else:
            title_tag = u"""<div class="title"><div><h{twrap}>{title}</h{twrap}></div></div>"""\
                        .format(twrap = self.titlewrap, title = self.title)
            cont_tag = u"""<div class="content">%s</div>""" % contents


        classname = ' '.join([self.classname, 'vdom_container']).strip()
        css = u"<style>\n" + self.style % {"id": id} + u"</style>" if self.style else u""
        debug_info = u""
        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='container' objname='%s'" % ( self.name )


        result = u"""{css}\
                    <{wrap} {debug_info} {footer} id="{id}" style="{style}" class="{classname}">
                        {title_tag}{cont_tag}
                    </{wrap}>"""\
                .format(debug_info = debug_info, footer =  footer, id = id, style = styles_str, classname = classname,
                            title_tag = title_tag, cont_tag = cont_tag, css = css, wrap = self.wrapper)

        return VDOM_object.render(self, contents=result)


    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_centered_image_metrics

        colorNumber = self.backgroundcolor if self.backgroundcolor != "" else self.designcolor
        colorValue = "#" + colorNumber if colorNumber != "" else "none"
        
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]
        # title
        title_text = ""
        if self.title!="" and self.titlewrap!="0":
            title_text = u"""<text x="5" y="14" fill="#000000" font-size="14" width="{width}">{title}</text>
                                """.format(title = self.title, width=self.width)

        # show icon if container is empty
        empty_container_image = ""
        if len(contents)==0 and self.backgroundimage == "":
            image_id = "8c8c753c-f1e4-07bb-e5bf-08771d63f502"
            image_width = image_height = 50

            image_x, image_y, image_width, image_height = get_centered_image_metrics( image_width, image_height, width, height )

            empty_container_image = u"""<image href="#Res({image_id})" x="{image_x}" y="{image_y}"
                                                        width="{image_width}" height="{image_height}" />
                                        """.format(image_id = image_id, image_width = image_width,
                                         image_height = image_height, image_x = image_x, image_y = image_y)

        bg_image = ""
        if self.backgroundimage != "":
            if self.backgroundrepeat == '0':
                bg_image_repeat = 'repeat'
            elif self.backgroundrepeat == '1':
                bg_image_repeat = 'no-repeat'
            elif self.backgroundrepeat == '2':
                bg_image_repeat = 'repeat-x'
            elif self.backgroundrepeat == '3':
                bg_image_repeat = 'repeat-y'
            else:
                bg_image_repeat = u''

            bg_image = \
                u"""<image href="#Res({backgroundimage})" x="0" y="0" repeat="{repeat}" containerWidth="{containerWidth}"
                        containerHeight="{containerHeight}" />
                """.format(
                    backgroundimage = self.backgroundimage, repeat = bg_image_repeat,
                    containerWidth = width,  containerHeight = height
                )

        # get overflow value
        overflow_dict = {"0":"auto", "1":"hidden", "2":"scroll", "3":"visible"}
        overflow_num = self.overflow if self.overflow else "0"
        overflow = overflow_dict[overflow_num]
        
        result = \
            u"""<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}" overflow="{overflow}">
                    <svg>
                        <rect x="0" y="0" width="{width}" height="{height}" fill="{colorValue}"/>
                        {empty_container_image}
                        {bg_image}
                        {title_text}
                    </svg>{contents}
                </container>""".format(
                    id = self.id, vis = self.visible, zind = self.zindex, name = self.name,
                    hierarchy = self.hierarchy, order = self.order, colorValue = colorValue,
                    top = top, left = left, width = width, height = height,
                    contents = contents,
                    title_text = title_text,
                    empty_container_image = empty_container_image,
                    bg_image = bg_image,
                    overflow = overflow
                )

        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    # object = application.objects.search(object_id)
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
    
    empty = ""
    
    users = """\
#%(id)s {

}
"""

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

    if object.parent and object.parent.type.class_name == "VDOM_tabview_v2" and object.attributes["lockposition"] == "1" and int(object.attributes["top"]) != 20 and int(object.attributes["left"]) != 1:
        # top_container = 20
        # left_container = 1
        # object.set_attributes({"left": left_container, "top": top_container})
        attributes.update(left="1", top="20")

    return ""
            
def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]
        
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_"+ attr] = obj_value.rstrip("px")