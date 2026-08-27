from scripting import e2vdom


class VDOM_tabview(VDOM_object):
    def check_unit(self, value):
        if value.isdigit():
            return value + "px"
        else:
            return value

    def render(self, contents=""):
        from collections import OrderedDict

        display = "display: none; " if self.visible == "0" else "display: {};".format(self.displaying) if self.displaying else ""
        zindex = "z-index: {}; ".format(self.zindex) if self.zindex != "0" and self.zindex else ""

        e2vdom.process(self)

        width_in = "width: {width};".format(width=self.check_unit(self.width)) if self.width else ""
        height_in = "height: {height};".format(height=self.check_unit(self.height)) if self.height else ""

        margin_in = "margin: {margins};".format(margins=self.margins) if self.margins else ""
        padding_in = "padding: {paddings};".format(paddings=self.paddings) if self.paddings else ""

        if self.positioning == "static":
            position = self.positioning = ""
            self.left = self.top = ""
        else:
            position = "position: {pos};".format(pos=self.positioning)

        top_inline = "top: {top};".format(top=self.check_unit(self.top)) if self.top else ""
        left_inline = "left: {left};".format(left=self.check_unit(self.left)) if self.left else ""

        style = """{display} {zind} {pos} {top} {left} {width} {height} {margin} {padding}""".format(
            display=display, zind=zindex, pos=position, top=top_inline, left=left_inline, width=width_in, height=height_in, margin=margin_in, padding=padding_in
        )

        id = "o_" + (self.id).replace("-", "_")
        cont_tag = """<div class="tabContent">%s</div>""" % contents
        tab_tag = ""
        tag_array = {}
        js = ""
        children_array = []
        children = self.objects
        for key in children:
            child = children[key]
            children_array.append([str(child.id), str(child.name), str(child.hierarchy), "o_" + str(child.id).replace("-", "_")])
            tab_class = "tab-item"
            tab_class += " tab-item{num}".format(num=str(int(child.hierarchy) + 1))
            if int(child.hierarchy) == 0:
                tab_class += " tab-item-first"
            if int(child.hierarchy) == len(children) - 1:
                tab_class += " tab-item-last"
            if self.currenttab == child.hierarchy:
                tab_class += " active"

            tag_array[child.hierarchy] = """<li class="{tab_class}"><a href='#{id}' class="{active}">{tabname}</a></li>\n""".format(
                tab_class=tab_class, id="o_" + (child.id).replace("-", "_"), tabname=child.title, active="active" if self.currenttab == child.hierarchy else ""
            )

            if self.currenttab == child.hierarchy:
                show_guid = "o_" + (child.id).replace("-", "_")
                js = """<script type="text/javascript">
    $('#%(id)s div.tabContent').children('div').hide();
    $('#%(id)s #%(show_guid)s').show();
    $('#%(id)s ul.tabNavigation a[href="#%(show_guid)s"]');
    </script>""" % {"id": id, "show_guid": show_guid}

        sortTagArray = OrderedDict(sorted(tag_array.items(), key=lambda t: t[0]))
        for key in sortTagArray:
            tab_tag += tag_array[key]

        if self.showtabs == "1":
            tabclass = "with_tabs"
            tabs = '<ul id="ul_%(id)s" class="tabNavigation" style="list-style: none"> %(tab)s </ul>' % {"id": id, "tab": tab_tag}
            js += """<script type="text/javascript">
var tabview_children_%(id)s = %(arr)s;
$(document).ready(function($){
    $("#ul_%(id)s a").click(function(){
        $("#%(id)s>div.tabContent>div").hide();
        $("#%(id)s>div.tabContent>div").filter(this.hash).show();
        $("#ul_%(id)s li").removeClass('active');
        $(this).parent('li').addClass('active');
        $("#ul_%(id)s a").removeClass('active');
        $(this).addClass('active');
        var cont_id = this.hash.substring(3, this.hash.length).replace(/_/g, "-");
        for (var i = 0; i<tabview_children_%(id)s.length; i++){
            if (cont_id == tabview_children_%(id)s[i][0]){
                execEventBinded("%(id)s".substring(2, "%(id)s".length), "tabchanged", {ID:tabview_children_%(id)s[i][0], Name:tabview_children_%(id)s[i][1], Hierarchy:tabview_children_%(id)s[i][2]});
            }
        }
        return false;
    });
});
</script>""" % {"id": id, "arr": str(children_array)}
        else:
            tabclass = ""
            tabs = ""
            js += """<script type="text/javascript">
var tabview_children_%(id)s = %(arr)s;
</script>""" % {"id": id, "arr": str(children_array)}

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='%s' objname='%s' ver='%s'" % (self.type.name, self.name, self.type.version)
        else:
            debug_info = ""

        outcss = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        result = """\
{css}
<div {debug_info} id="{id}" class="{classname}" style="{style}">
    {tabs}
    {cont_tag}
</div>
{js}
            """.format(
            debug_info=debug_info,
            classname=" ".join(list(filter(None, [self.classname, "vdom_tabview", tabclass]))),
            css=outcss,
            id=id,
            style=style,
            tabs=tabs,
            cont_tag=cont_tag,
            js=js,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        top, left = [int(self.ide_top), int(self.ide_left)]
        object_width = 200
        object_height = 200
        if self.ide_width and int(self.ide_width) > 0:
            object_width = int(self.ide_width)
        if self.ide_height and int(self.ide_height) > 0:
            object_height = int(self.ide_height)

        image_id = "a48a6898-5596-4b88-5864-f82e57f64545"
        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" 
                    top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect x="{panel_width}" y="0" width="140" height="20" style="stroke:#DDDDDD;stroke-width:1;" fill="#EEEEEE">
                            <image x="5" y="0" width="131" height="17" href="#Res({img_id})" />
                        </rect>
                    </svg>
                    <svg>
                        <rect x="0" y="20" width="{container_width}" height="{container_height}" style="stroke:#DDDDDD;stroke-width:1;" fill="#EEEEEE"/>
                    </svg>{contents}
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            name=self.name,
            hierarchy=self.hierarchy,
            top=top,
            left=left,
            width=object_width + 2,
            height=object_height + 2,
            panel_width=object_width - 140,
            container_height=object_height - 20,
            container_width=object_width,
            img_id=image_id,
            contents=contents,
        )

        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    # obj = application.objects.search(object_id)
    # if "width" in param:
    # 	if param["width"]["value"] and param["width"]["value"] > 0:
    # 		width = int(param["width"]["value"])
    # 	else:
    # 		width = 200
    # 	if obj.attributes.width != width:
    # 		obj.set_attribute_ex("width", width)objects
    # if "height" in param:
    # 	if param["height"]["value"] and param["height"]["value"] > 0:
    # 		height = int(param["height"]["value"])
    # 	else:
    # 		height = 200
    # 	if obj.attributes.height != height:
    # 		obj.set_attribute_ex("height", height)
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

    width = attributes.get("ide_width")
    if width is not None:
        width = int(width)
        if width > 0:
            width = str(width - 2)
        else:
            attributes["ide_width"] = width = "200"

    height = attributes.get("ide_height")
    if height is not None:
        height = int(height)
        if height > 0:
            height = str(height - 20)
        else:
            attributes["ide_height"] = height = "200"

    # childs = obj.objects
    # for key in childs:
    for child in o.objects.values():
        # child = childs[key]
        # if obj.attributes.currenttab == child.attributes.hierarchy and str(child.attributes.zindex) != "1":
        # 	child.set_attribute_ex("zindex", "1")
        # elif obj.attributes.currenttab != child.attributes.hierarchy and str(child.attributes.zindex) != "0":
        # 	child.set_attribute_ex("zindex", "0")
        if o.attributes["currenttab"] == child.attributes["hierarchy"] and child.attributes["zindex"] != "1":
            child.attributes.update(zindex="1")
        elif o.attributes["currenttab"] != child.attributes["hierarchy"] and child.attributes["zindex"] != "0":
            child.attributes.update(zindex="0")

        # if "width" in param:
        # 	if param["width"]["value"] and param["width"]["value"] > 0:
        # 		width = int(param["width"]["value"]) - 2
        # 	else:
        # 		width = 200
        # 	child.set_attribute_ex("width", width)
        # if "height" in param:
        # 	if param["height"]["value"] and param["height"]["value"] > 0:
        # 		height = int(param["height"]["value"]) - 20
        # 	else:
        # 		height = 200
        # 	child.set_attribute_ex("height", height)
        if width is not None:
            child.attributes.update(ide_width=width)
        if height is not None:
            child.attributes.update(ide_height=height)

    users = """\
#%(id)s {

}
"""

    empty = ""

    # o = application.objects.search(object_id)

    # if "skin" in param:
    # 	if param["skin"]["value"] == "1":
    # 		obj.set_attributes({"style": css})
    # if "style" in param and param["style"]["value"] and obj.attributes.style != css:
    # 	obj.set_attributes({"skin": 0})
    # if attributes.get("skin") == "1":
    # 	attributes["style"] = css

    # style = attributes.get("style")
    # if style is not None and object.attributes["style"] != css:
    # 	attributes["skin"] = "0"

    # return ""

    skin_mapping = {"0": users, "1": empty}

    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    return ""


# def add_child(app_id, object_id, param):
def on_insert(parent, object):
    # object = application.objects.search(param["child_id"])

    # width_container = int(object.parent.attributes.width) - 2
    # height_container = int(object.parent.attributes.height) - 20
    width_container = int(parent.attributes["ide_width"]) - 2
    height_container = int(parent.attributes["ide_height"]) - 20
    # pdb.set_trace()

    # object.set_attributes({"width": width_container, "height": height_container, "lockposition": "1"})
    object.attributes.update(ide_width=width_container, ide_height=height_container, top=20, left=1, lockposition="1")

    # childs = object.parent.objects
    container_hierarchy = []
    # for key in childs:
    for child in parent.objects.values():
        # child = application.objects.search(key)
        # container_hierarchy.append(child.attributes.hierarchy)
        container_hierarchy.append(child.attributes["hierarchy"])

        # if object.parent.attributes.currenttab == child.attributes.hierarchy and str(child.attributes.zindex) != "1":
        # 	child.set_attributes({"zindex": "1"})
        # elif object.parent.attributes.currenttab != child.attributes.hierarchy and str(child.attributes.zindex) != "0":
        # 	child.set_attributes({"zindex": "0"})
        if parent.attributes["currenttab"] == child.attributes["hierarchy"] and child.attributes["zindex"] != "1":
            child.attributes.update(zindex="1")
        elif parent.attributes["currenttab"] != child.attributes["hierarchy"] and child.attributes["zindex"] != "0":
            child.attributes.update(zindex="0")

    # if len(container_hierarchy) > 1 and int(object.attributes.hierarchy) == 0:
    # 	object.set_attributes({"hierarchy": int(max(container_hierarchy)) + 1})
    # 	if object.parent.attributes.currenttab == child.attributes.hierarchy and str(object.attributes.zindex) != "1":
    # 		object.set_attributes({"zindex": "1"})
    # 	elif object.parent.attributes.currenttab != child.attributes.hierarchy and str(object.attributes.zindex) != "0":
    # 		object.set_attributes({"zindex": "0"})
    if len(container_hierarchy) > 1 and int(object.attributes["hierarchy"]) == 0:
        object.attributes.update(hierarchy=str(int(max(container_hierarchy)) + 1))
        if parent.attributes["currenttab"] == child.attributes["hierarchy"] and object.attributes["zindex"] != "1":
            object.attributes.update(zindex="1")
        elif parent.attributes["currenttab"] != child.attributes["hierarchy"] and object.attributes["zindex"] != "0":
            object.attributes.update(zindex="0")

    # return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")