import collections
import json

CLICK_N_SELECT = (
  "click",
  "ctrlclick",
  "dblclick",
  "ctrldblclick",
  "manual",
)


class VDOM_listv2(VDOM_object):

    def parse_property(self, pname, ptype, *args, **kwargs):
        prop = getattr(self, pname)
        if not prop:
            return ptype()

        try:
            value = json.loads(prop, *args, **kwargs)

        except Exception:
            if prop:
                raise Exception(u"Can't parse '%s'. It must be '%s'" % (pname, ptype.__name__))

            value = ptype()

        return value

    def check_unit(self, value):
        return value + "px" if value.isdigit() else value
    
    def render(self, contents=""):

        obj_id = self.id.replace('-', '_')
        zindex = u"%s" % self.zindex if int(self.zindex) != 0 else u""

        items = self.parse_property("data", dict, object_pairs_hook=collections.OrderedDict)
        selected_rows = self.parse_property("selectedrows", list)
        selectable_rows = self.parse_property("selectablerows", list)
        droppable_rows = self.parse_property("droppablerows", list)
        active_row = self.activeitem
        multi_selection = True if self.selectionmode == "1" else False
        already_selected = False

        # compatibility with old version
        can_be_droppable = False
        if self.droppable == "1":
            if not droppable_rows:
                can_be_droppable = True

        can_be_selectable = False
        if not selectable_rows:
            can_be_selectable = True

        result = []
        index = 1
        is_first = True
        
        display = u"none" if self.visible == "0" else self.displaying
        position = u"{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else u""
        
        styles = {
            "z-index": zindex,
            "display": display,
            "position": position,
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

        for key, value in items.items():
            
            css_class = u"list-item-{index}{is_first}{is_last}{is_odd}{is_active}{is_selected}{is_selectable}{is_droppable}".format(
                index=index,
                is_first=" list-item-first" if is_first else "",
                is_last=" list-item-last" if index == len(items) else "",
                is_odd=" list-item-odd" if index % 2 == 0 else "",
                is_active=u" active" if active_row == key else u"",
                is_selected=u" selected" if key in selected_rows and not already_selected else u"",
                is_selectable=u" selectable" if key in selectable_rows or can_be_selectable else u"",
                is_droppable=u" droppable" if key in droppable_rows or can_be_droppable else u""
            )

            result.append(u"""<li itemid="{key}" class="{css_class}">{content}</li>""".format(
                key=key,
                css_class=css_class,
                content=value
            ))

            if not multi_selection and key in selected_rows:
              already_selected = True

            index += 1
            is_first = False

        options = {
          "droppable": self.droppable == "1",
          "clickClasses": self.clickclass.strip().split(),
        }
        usercss = "<style type='text/css'>"
        if self.layout == "1":
            usercss += "#o_%(id)s ul li {\n display: inline; \n} \n" % {"id": obj_id}
        if self.style:
            usercss += self.style % {"id": "o_" + obj_id}
        usercss += "</style>"
        if not self.style and self.layout != "1":
            usercss = ""

        output = u"""
<div
    id="o_{id}"
    name="{name}"
    objtype="listv2"
    ver="{version}"
    style="{styles}"
    class="{css_class}"
    selectionmode="{selectionmode}"
    select-on-click="{selectonclick}"
>
    <ul>{content}</ul>
</div>
{usercss}
<script type="text/javascript">$(document).ready(function(){{$("#o_{id}").vdomList_v2({options});}});</script>""" 

        contents += output.format(
            version=self.type.version,
            name=self.name,
            css_class=' '.join([self.classname, 'vdom_listv2']).strip(),
            content="".join(result),
            id=obj_id,
            usercss = usercss,
            styles=styles_str,
            options=json.dumps(options),
            selectionmode="multiselection" if multi_selection else "singleselection",
            selectonclick=CLICK_N_SELECT[int(self.selectonclick)],
        )

        return VDOM_object.render(self, contents=contents)        
        
            
    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value
        self.width, self.height, self.top, self.left = [
            int(self.ide_width), int(self.ide_height), 
            int(self.ide_top), int(self.ide_left)
        ]
        
        image_id = "e1246b00-381e-4b32-bad7-4a647a08d557"
        result = get_empty_wysiwyg_value(self, image_id)
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
    
    empty = ""
    
    default = u"""\
#%(id)s li.selected {
    background: #fdeeb5; 
}
#%(id)s li.active {
    background: #fbdf75 !important; 
}
"""

    users = u"""\
#%(id)s {

}
"""
    
    skin_mapping = {
        "0": users,
        "1": default,
        "2": empty
    }
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")
            
    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")
        
    data_example = u"""\
{"item1": "value 1", "item2": "Value 2", "item3": "Value3"}
"""

    data_map = {
        "data_ex": data_example,
        "empty": u""
    }
    
    if "skindata" in attributes:
        skindata = attributes["skindata"]
        if skindata == "1":
            attributes.update(data=data_example)
        else:
            attributes.update(data=u"")
    
    if "data" in attributes:
        if attributes.get("data") not in data_map.values():
            attributes.update(skindata="0")
    
    return ""
            
def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]
        
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_"+ attr] = obj_value.rstrip("px")