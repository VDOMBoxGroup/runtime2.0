import collections
import json
from io import StringIO


class VDOM_list(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        zindex = "%s" % self.zindex if int(self.zindex) != 0 else ""
        woid = (self.id).replace("-", "_")
        id = "o_" + woid

        display = "none" if self.visible == "0" else self.displaying
        position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""

        styles = {
            "z-index": zindex,
            "display": display,
            "position": position,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        multclass = "multiselect" if self.selectionmode == "1" else ""
        cssclass = list(filter(None, [self.cssclass, "vdom_list", multclass]))

        if self.data:
            try:
                data = json.loads(self.data, object_pairs_hook=collections.OrderedDict)
                if isinstance(data, int):
                    raise Exception("Incorrect value in data %s" % self.data)
            except Exception:
                raise Exception("Incorrect value in data %s" % self.data)
        else:
            data = {}

        selectedRows = []
        if self.selectedrows:
            try:
                selectedRows = json.loads(self.selectedrows)
                if isinstance(selectedRows, list):
                    js_multiselect = ""
                else:
                    raise Exception("Attribute must be list")
            except Exception:
                raise Exception("Incorrect value in selected rows")
        else:
            js_multiselect = ""

        # 		hlayout = u"#%(id)s ul li{display: inline;}" % {"id": id} if self.layout == "1" else u""

        # 		if self.skin == "2":
        # 			css = u"#%(id)s ul{list-style: none outside none;margin: 0;padding: 0;}%(hlayout)s" % {"id": id, "hlayout": hlayout}
        # 		else:
        # 			css = u"%(hlayout)s" % {"id": id, "hlayout": hlayout}
        res_buffer = StringIO("")
        res_buffer.write("<style type='text/css'>")
        # 		res_buffer.write(css)
        css = self.style % {"id": id} if self.style else ""
        res_buffer.write(css)
        res_buffer.write("</style>")

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='list' objname='%s' ver='%s'" % (
                self.name,
                self.type.version,
            )
        else:
            debug_info = ""

        rslt = """<div {debug_info} id="{id}" style="{style}" class="{cssclass}"><ul>""".format(
            debug_info=debug_info,
            id=id,
            style=styles_str,
            cssclass=" ".join(cssclass),
        )

        res_buffer.write(rslt)

        for key, value in data.items():
            active = 'class="list-item-%s %s %s"' % (
                key,
                "active" if key == self.selecteditem else "",
                "selected" if key in selectedRows else "",
            )
            if isinstance(value, list):
                if len(value) == 3:
                    image = '<img src="%s" />' % value[1]
                    li = '<li itemid="%(elem_id)s" %(active)s>%(left_image)s%(content)s%(right_image)s</li>' % {
                        "elem_id": str(key),
                        "content": str(value[0]),
                        "active": active,
                        "left_image": image if value[2] == "left" else "",
                        "right_image": image if value[2] == "right" else "",
                    }
                    res_buffer.write(li)
                else:
                    raise Exception("Must be 3 parameters in string %s" % str(value))
            elif isinstance(value, str):
                li = '<li itemid="%(elem_id)s" %(active)s>%(content)s</li>' % {
                    "elem_id": str(key),
                    "active": active,
                    "content": str(value),
                }
                res_buffer.write(li)

            else:
                raise Exception("Incorrect value in string %s" % str(value))

        if self.dragdrop == "1":
            dragdrop = """
$j('#%(id)s li').droppable({
    //greedy: true,
    //activeClass: "ui-state-hover",
    hoverClass: "ui-state-active",
    drop: function(e, ui) {
        execEventBinded('%(woid)s', "drop", {itemid: $j(this).attr('itemid')});
    }
});
            """ % {"id": id, "woid": woid}
        else:
            dragdrop = ""

        if (self.clickclass).strip() == "":
            clickclass = ""
        else:
            clickclass = self.clickclass
            clickclass = ".%s" % clickclass.replace(" ", " .")

        handleclick = """
    var %(id)s_doo = false, m = $j('#%(id)s').hasClass('multiselect');
    $j('#%(id)s ul li %(clickclass)s').bind('click dblclick', function(e){
        var tt = $j(this);
        if (tt.is('li')) {
            t = tt;
        } else {
            t = tt.closest('li');
        }
        t.parent().children().removeClass("active");
        if (m) {
            if (t.hasClass("selected")) t.removeClass("selected");
            else t.addClass("selected");
        }
        t.addClass("active");
        if (e.type == 'dblclick') {
            %(id)s_doo = false;
            if (m) {
                var a = [];
                t.parent().find('li.selected[itemid]').each(function(i,e){ a.push($q(e).attr('itemid')); });
                execEventBinded('%(woid)s', "rowsselected", {keyList: a });
            } else {
                execEventBinded('%(woid)s', "itemdblclick", {itemid: t.attr('itemid')});
            }
        } else {
            setTimeout(function() {
                if (%(id)s_doo == true) {
                    %(id)s_doo = false;
                    if (m) {
                        var a = [];
                        t.parent().find('li.selected[itemid]').each(function(i,e){ a.push($q(e).attr('itemid')); });
                        execEventBinded('%(woid)s', "rowsselected", {keyList: a });
                    } else {
                        execEventBinded('%(woid)s', "itemclick", {itemid: t.attr('itemid')});
                    }
                }
            }, 300);
            %(id)s_doo = true;
        }
        return false;
    });
        """ % {"id": id, "woid": woid, "clickclass": clickclass}

        res_buffer.write("</ul></div>")
        js_script = """<script type="text/javascript">
$j(function(){
    %(handleclick)s
    %(dragdrop)s
});
</script>""" % {
            "dragdrop": dragdrop,
            "handleclick": handleclick,
        }

        res_buffer.write(js_script)
        result = res_buffer.getvalue()
        res_buffer.close()

        return VDOM_object.render(self, contents=result)

    def __get_error_wysiwyg_obj(self, error_text):
        result = """<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" 
                            top="{top}" left="{left}" width="{width}" height="{height}">
                    <text top="0" left="5" color="#ff0000" textalign="left">{value}</text>
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            value=error_text,
        )

        return VDOM_object.wysiwyg(self, contents=result)

    def wysiwyg(self, contents=""):
        incorrect_data_text = "Incorrect value in data:\n{data}".format(data=self.data)
        self.width, self.height, self.top, self.left = [
            int(self.ide_width),
            int(self.ide_height),
            int(self.ide_top),
            int(self.ide_left),
        ]

        if self.data:
            try:
                data = json.loads(self.data, object_pairs_hook=collections.OrderedDict)
                if isinstance(data, int):
                    return self.__get_error_wysiwyg_obj(incorrect_data_text)
            except Exception:
                return self.__get_error_wysiwyg_obj(incorrect_data_text)
        else:
            data = {}

        if not data:
            from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

            image_id = "4a582b3d-09ee-8ac1-1451-08a964bbb510"
            result = get_empty_wysiwyg_value(self, image_id)
            return VDOM_object.wysiwyg(self, contents=result)

        try:
            items = data.items()

        except Exception:
            return self.__get_error_wysiwyg_obj(incorrect_data_text)

        res_buffer = StringIO("")
        if self.layout == "1":
            res_buffer.write("""<row backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0">""")
            for key, value in items:
                if isinstance(value, list):
                    li = (
                        '<cell backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0"><text fontsize="14" color="#000000" textalign="left">%s</text></cell>'
                        % str(value[0])
                    )
                    res_buffer.write(li)
                elif isinstance(value, str):
                    li = (
                        '<cell backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0"><text fontsize="14" color="#000000" textalign="left">%s</text></cell>'
                        % str(value)
                    )
                    res_buffer.write(li)
            res_buffer.write("</row>")
        else:
            for key, value in items:
                if isinstance(value, list):
                    li = (
                        '<row backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0"><cell backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0"><text fontsize="14" color="#000000" textalign="left">%s</text></cell></row>'
                        % str(value[0])
                    )
                    res_buffer.write(li)
                elif isinstance(value, str):
                    li = (
                        '<row backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0"><cell backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0"><text fontsize="14" color="#000000" textalign="left">%s</text></cell></row>'
                        % str(value)
                    )
                    res_buffer.write(li)

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}"
                    top="{top}" left="{left}" width="{width}" height="{height}">
                    <table zindex="{zind}" top="0" left="0" width="{width}" height="{height}" backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0" >
                        {res_buffer}
                    </table>
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            name=self.name,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            res_buffer=res_buffer.getvalue(),
        )

        res_buffer.close()
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

    default = """\
#%(id)s li.selected {
    background: #fdeeb5;
}
#%(id)s li.active {
    background: #fbdf75 !important;
}
"""

    users = """\
#%(id)s {

}
"""

    skin_mapping = {"0": users, "1": default, "2": empty}
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    data_example = """\
{"item1": "value 1", "item2": "Value 2", "item3": "Value3"}
"""

    data_map = {"data_ex": data_example, "empty": ""}

    if "skindata" in attributes:
        skindata = attributes["skindata"]
        if skindata == "1":
            attributes.update(data=data_example)
        else:
            attributes.update(data="")

    if "data" in attributes:
        if attributes.get("data") not in data_map.values():
            attributes.update(skindata="0")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")