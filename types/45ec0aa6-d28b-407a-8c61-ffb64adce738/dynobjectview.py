import json
import re
import sys
from scripting import e2vdom
from collections import OrderedDict
from uuid import uuid4

import managers
# from memory import vdomxml


# auxiliary

def xml_escape(value):
    global xml_escape

    illegal_unichrs = [
        (0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
        (0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
        (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
        (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
        (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
        (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
        (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
        (0x10FFFE, 0x10FFFF)
    ]
    illegal_ranges = ["%s-%s" % (chr(low), chr(high))
        for (low, high) in illegal_unichrs if low < sys.maxunicode]
    regex = re.compile("[%s]" % "".join(illegal_ranges))

    def real_xml_escape(text):
        return regex.sub("", text)

    xml_escape = real_xml_escape
    return real_xml_escape(value)


class CachedDict(dict):

    def __init__(self, items, compute):
        super(CachedDict, self).__init__()
        self.initial_items = items
        self.computed_items = {}
        self.compute = compute

    def __getitem__(self, key):
        if key not in self.computed_items:
            self.computed_items[key] = self.compute(self.initial_items[key])
        return self.computed_items[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


# template

class Template:

    __slots__ = ("_attributes", "_vdomxml", "_object")

    def __init__(self, root, vdomxml, vdomjson, attributes=None):
        self._attributes = attributes or {}
        self._vdomxml = vdomxml
        # self._object = vdomxml.loads(vdomxml, managers.engine.application)
        self._object = root.loads(vdomxml, vdomjson, handler=root.handler)
        managers.memory.track(self._object, sync=root)

    def __getitem__(self, key):
        return self._attributes.get(key.lower(), "")

    def __setitem__(self, key, value):
        self._attributes[key.lower()] = value

    def __delitem__(self, key):
        del self._attributes[key.lower()]

    def render(self, parent):
        if self._attributes:
            cache = {0: (self._object, {})}

            for name, value in self._attributes.items():
                pair = name.rsplit(".", 1)

                if len(pair) == 1:
                    target, attributes = cache[0]
                elif pair[0] in cache:
                    target, attributes = cache[pair[0]]
                else:
                    target, attributes = self._object, {}
                    for object_name in pair[0].split("."):
                        target = target.objects.get(object_name)
                        if not target:
                            break
                    else:
                        cache[pair[0]] = target, attributes

                if target and pair[-1] in target.attributes:
                    attributes[pair[-1]] = value

            for target, attributes in cache.values():
                target.attributes.update(attributes)
                
        with managers.engine.start_render(self._object, parent=parent) as context:
            contents = context.contents
            declarations, libraries = e2vdom.generate(context.instance, registrations=True)
            return contents, declarations, libraries
#        return managers.engine.render(self._object, parent, "vdom")


# layouts

DEFAULT_MARGIN = 17


class Layout:

    __slots__ = ("_elements", "_left", "_top", "_width", "_height", "_margin")

    def __init__(self, margin=DEFAULT_MARGIN):
        self._elements = []
        self._left = 0
        self._top = 0
        self._width = 0
        self._height = 0
        self._margin = margin

    def arrange(self, element):
        pass

    def append(self, element):
        self._elements.append(element)
        if not isinstance(element, str):
            self.arrange(element)

    def render(self, parent):
        with e2vdom.select(dynamic=True):
            elements = []
            declarations = []
            libraries = []
            for element in self._elements:
                if isinstance(element, str):
                    elements.append(element)
                else:
                    element["top"] = str(self._top + int(element["top"] or 0))
                    element["left"] = str(self._left + int(element["left"] or 0))
                    contents, declaration, library = element.render(parent)
                    elements.append(contents)
                    declarations.append(declaration)
                    libraries.append(library)
            #declarations.extend(e2vdom.registrations())
            return ("""{}
<script type='text/javascript'>{}</script>""".format("".join(libraries), "".join(declarations)),"".join(elements))


class VerticalLayout(Layout):

    def __init__(self, margin=DEFAULT_MARGIN):
        super(VerticalLayout, self).__init__(margin=margin)

    def arrange(self, element):
        element["left"] = "0"
        element["top"] = str(self._height + 0 if self._elements else self._margin)

        width = int(element["width"] or 0)
        height = int(element["height"] or 0)

        self._width = max(self._width, width)
        self._height += self._margin + height


class HorizontalLayout(Layout):

    def __init__(self, margin=DEFAULT_MARGIN, container=None):
        super(HorizontalLayout, self).__init__(margin=margin)
        self._width = container._height if container else 0

    def arrange(self, element):
        element["left"] = str(self._left + self._width + self._margin)
        element["top"] = str(self._top)

        width = int(element["width"] or 0)
        height = int(element["height"] or 0)

        self._width += self._margin + width
        self._height = max(self._height, height)


# main class

LAYOUTS = (VerticalLayout, HorizontalLayout, VerticalLayout)

CSS_FIRST = "dov-item-first"
CSS_LAST = "dov-item-last"
CSS_ODD = "dov-item-odd"
CSS_ACTIVE = "dov-item-active"

CLICK_N_SELECT = (
    "click",
    "ctrlclick",
    "dblclick",
    "ctrldblclick",
    "manual",
)

OVERFLOW = {
    "1": "hidden",
    "2": "scroll",
    "3": "visible",
}

LAYOUT = {
    "0": "clear: both",
    "1": "float: left;",
    "2": "width: 100% !important; clear: both;",
}


class DynamicObjectView(VDOM_object):

    def generate_layout(self):

        # parse data
        try:
            data = json.loads(self.data, object_pairs_hook=OrderedDict)
        except Exception:
            if self.data:
                raise Exception("Unable to parse data")
            data = None

        # parse templates
        try:
            templates = json.loads(self.template)
        except Exception:
            if self.template:
                raise Exception("Unable to parse template")
            templates = None

        # parse actions
        try:
            actions = json.loads(self.actions)
        except Exception:
            if self.actions:
                raise Exception("Unable to parse actions")
            actions = None

        # parse bindings
        try:
            bindings = json.loads(self.bindings)
        except Exception:
            if self.bindings:
                raise Exception("Unable to parse bindings")
            bindings = None

        # instantiate layout
        if self.layout:
            layout_index = int(self.layout)
        else:
            layout_index = 0
        layout = LAYOUTS[layout_index]()
        if not (data and templates and bindings):
            return layout

        # obtain xml template root element attributes
        # TODO: optimize this later...
        def get_root_attributes(xml):
            toplvl = xml.split(">", 1)[0]
            if toplvl[-1] == "/":
                toplvl = toplvl[:-1]
            attrs = [attr.split("=", 1) for attr in toplvl.split(" ") if "=" in attr]
            return {key.lower(): value[1: len(value) - 1] for key, value in attrs}

        # initialize templates
        templates = CachedDict(templates, lambda xml: xml) #.encode("utf8")
        templates_attributes = CachedDict(templates, get_root_attributes)

        # initialize actions
        if actions is not None:
            actions = CachedDict(actions, lambda data: json.dumps(data))
        
        for index, (uuid, item) in enumerate(data.items(), 1):
            template_name = item.get("vdomclass", "default")
            template_attributes = templates_attributes[template_name]

            template = Template(self, templates[template_name],
                (None if actions is None else actions.get(template_name)))

            binding = bindings.get(template_name, {})
            for key, value in item.items():
                if key not in binding:
                    continue

                attributes = binding[key]
                if not isinstance(attributes, list):
                    attributes = [attributes]

                for name in attributes:
                    template[name] = xml_escape(value)

            classes = (
                template["classname"],
                template_attributes["classname"],
                CSS_FIRST if index == 1 else None,
                CSS_LAST if index == len(data) else None,
                CSS_ODD if index % 2 == 0 else None,
                CSS_ACTIVE if self.activeitem == uuid else None,
                "dov-item dov-item-%d" % index
            )

            template["name"] = "dovtemplate_%d" % index
            template["classname"] = " ".join([_f for _f in classes if _f])

            template["dataid"] = uuid

            layout.append(template)

        return layout

    def check_unit(self, value):
        return value + "px" if value.isdigit() else value
    
    def compile_style(self):
        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "position": self.positioning,
            "display": "none" if self.visible == "0" else self.displaying,
            "overflow": OVERFLOW.get(self.overflow, "")
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            styles["position"] = ""
        
        object_style = " ".join([f"{key}: {value};" for key, value in styles.items() if value])

        id4js = "o_" + self.id.replace('-', '_')
        element_style = "<style type=\"text/css\">\n" \
            "{user_css}\n" \
            "#{id4js} .dov-item {{{layout}}}\n" \
            "</style>\n".format(
                id4js=id4js,
                user_css=self.css % {"id": id4js},
                layout=LAYOUT.get(self.layout, ""))

        return object_style, element_style

    def render(self, contents=""):
        with e2vdom.select(dynamic=True):
            e2vdom.process(self)
            layout = self.generate_layout()
            id4js = "o_" + self.id.replace('-', '_')
            insertmethod = ["insertHTMLAtBegining", "insertHTMLAtEnd"][int(self.insertmethod)]
            static_declarations, static_libraries = e2vdom.generate(self)
            declarations, layoutcontent = layout.render(self)
            declarations= static_libraries+ "<script type='text/javascript'>"+ static_declarations +"</script>" + declarations
        #request.dyn_libraries[self.name] = declarations
        if request.render_type == "e2vdom" and self.dynamicrender == "1":
            result = """<noreplace/>
<div id="{tmp_id}" style="display:none">{contents}</div>
<script type='text/javascript'>
$(document).ready(function(){{
  var x = $('#{id4js}>div.dov-content');
  var dovtmp = $('#{tmp_id}:last');
  if ($.trim(dovtmp.html()) != '') {{
      $("#{id4js}").dynamicObjectView("{insertmethod}", dovtmp);
  }}
}});
</script>""".format(
                id4js=id4js,
                tmp_id=str(uuid4()),
                contents=layoutcontent,
                insertmethod=insertmethod,
            )

            return VDOM_object.render(self, contents=contents + result)
        else:
            options = {
                "dragndrop": self.draggable == "1",
                "dragnsort": self.sortable == "1",
                "dragndropHelper": self.draghelper if self.draghelper else "clone",
                "dynamicLoading": self.dynamicloading == "1",
                "clickClasses": self.clickclass.strip().split(),
                "clickAndSelect": CLICK_N_SELECT[int(self.selectonclick)],
                "multiSelection": self.selectionmode == "1",
            }

            object_style, element_style = self.compile_style()
            result = """
{element_style}
<div objname="{name}" id="{id4js}" style="{object_style}" class="{classes}">
<div class='dov-content'>
{contents}
<span class='dov-eoi' style='display: block; clear: both'></span>
</div>
</div>
{declarations}
<script>jQuery(document).ready(function(){{jQuery("#{id4js}").dynamicObjectView({options});}});</script>"""
            contents += result.format(
                declarations = declarations,
                name=self.name,
                element_style=element_style,
                id4js=id4js,
                object_style=object_style,
                classes=' '.join([self.classname, 'vdom_dynobjectview']).strip(),
                contents=layoutcontent,
                options=json.dumps(options)
            )

            return super(DynamicObjectView, self).render(contents=contents)
    
    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value
        self.width, self.height, self.top, self.left = [
            int(self.ide_width), int(self.ide_height), 
            int(self.ide_top), int(self.ide_left)
        ]
   
        image_id = "76bfc7be-dbe3-46e3-8d11-cc78a576b63a"
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
    
    
    users = """\
#%(id)s {

}

"""

    default = """\
#%(id)s .loading-helper {
    background: #fff url('/1869b90e-c056-1337-dfac-72b9873df6fa.res') center center no-repeat;
}
#%(id)s .not-loaded {
    background: url('/feb69c13-3f9b-f49f-6527-72f5a7193a34.res') center center no-repeat;
}
"""

    skin_mapping = {
        "0": users,
        "1": "",
        "2": default
    }
    
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(css=skin_mapping[skin])
        else:
            attributes.update(skin="0")
            
    if "css" in attributes and attributes.get("css") not in skin_mapping.values():
        attributes.update(skin="0")
        
    template_ex = """\
{ "default": "<VDOMCLASS visible=\\"1\\" name=\\"meeting\\" top=\\"464\\" left=\\"129\\" width=\\"542\\" height=\\"118\\" classname=\\"meeting\\"> <FLEXCONTAINER name=\\"cal_date_holder\\" classname=\\"cal_date_holder medium\\" flexshrink=\\"0\\" margins=\\"0px 30px 0px 15px\\" superleft=\\"0px\\" supertop=\\"0px\\" width=\\"60\\" superwidth=\\"60px\\" height=\\"60\\" superheight=\\"60px\\"> <TEXT name=\\"cal_date_day\\" left=\\"7\\" width=\\"39\\" value=\\"1\\" classname=\\"cal_date_day\\"/> <TEXT name=\\"cal_date_month\\" top=\\"14\\" left=\\"9\\" width=\\"35\\" value=\\"Dec\\" classname=\\"cal_date_month\\"/> </FLEXCONTAINER></VDOMCLASS>"}
"""
    
    data_ex = """\
{
  "1": {
    "month": "Novembre",
    "day": "29", 
    "title": "Ordinare CSE1", 
    "time": "9:00 - 18:00"
  },
  "2": {
    "month": "Novembre",
    "day": "29", 
    "title": "CSE1-1", 
    "time": "9:00 - 13:00"
  }
}"""

    actions_ex = """\
{"default": {
  "def_item.text1:click": [["def_item.text1:toggleClass",  "'status'"]]
}
}"""
        
    bindings_ex = """\
{"default":{
  
    "day": "left_col.cal_date_holder.cal_date_day.value",
    "month": "left_col.cal_date_holder.cal_date_month.value", 
    "title": "right_col.title.value", 
    "time": "right_col.time.value"
}
}"""
    data_map = {
        "data_ex": data_ex,
        "template_ex": template_ex,
        "actions_ex": actions_ex,
        "bindings_ex": bindings_ex,
        "empty": ""
    }
    
    if "skindata" in attributes:
        skindata = attributes["skindata"]
        if skindata == "1":
            attributes.update(data=data_ex, template=template_ex, actions=actions_ex, bindings=bindings_ex)
        else:
            attributes.update(data="", template="", actions="", bindings="")

    if any(key in attributes for key in ["data", "template", "actions", "bindings"]):
        if any(attributes.get(key) not in data_map.values() for key in ["data", "template", "actions", "bindings"]):
            attributes.update(skindata="2")

    return ""
    
def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]
        
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_"+ attr] = obj_value.rstrip("px")