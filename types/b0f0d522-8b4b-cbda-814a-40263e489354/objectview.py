import sys
import re
import json
from collections import OrderedDict
from uuid import uuid4

import managers
from scripting import e2vdom


JS_DRAG = """
$j(document).on('mouseover', "#%(id)s div[dataid]", function () {
    if (!$j(this).data('initDraggable')) {
        $j(this).data('initDraggable', true);
        $j(this).draggable({
            connectToDynatree: true,
            appendTo: 'body',
            containment: 'document',
            zIndex: 99999,
            /*option: 'accept',*/
            cursor: 'default',
            /*cursorAt: { left: -2, top: 4 },*/
            start: function (e, u) {
                execEventBinded('%(woid)s', "dragstart", { id: $j(this).attr('dataid') }, true);
            },
            connectToSortable: '#%(id)s',
            revert: "invalid",
            revertDuration: 200,
            /*helper: 'clone'*/
            opacity: 1/*,
            helper: function (e) {
                return $j("<div class='ov-drag-helper' style='width:50px;height:20px;background:#555'></div>");
            }*/
        });
    }
});
/*
$('#%(id)s').droppable({
    disabled: true,
    accept: ".nobody",
    drop: function(event, ui){
        type = ui.draggable.find('.link_type').val();
        ui.draggable.empty();
        //return ui.draggable.html(create(type,0))
        return ui.draggable;
    }
});
*/
"""

JS_SORTABLE = """
$j(document).on('mouseover', "#%(id)s", function () {
    if (!$j(this).data('initSortable')) {
        $j(this).data('initSortable', true);
        $j(this).sortable({
            items: 'div[dataid]',
            receive: function (event, ui) {
                ui.item.remove();
                // ui.sender.remove();
            },
            stop: function (e, u) {
                execEventBinded('%(woid)s', "itemsort", { position: u.item.index(), id: u.item.attr('dataid') });
            }
        });
    }
});
/*}).disableSelection().bind("sortstop",function(e,u){
    execEventBinded('%(woid)s', "itemsort", {position: u.item.index(), id: u.item.attr('dataid')});
    //ui.draggable.empty();
    //return ui.draggable;
});*/
"""

JS_LOADING = """
function %(id)s_ld(t) {
    var z = $j('>.loading', t);
    if (z.length > 0) {
        if (z.is(':visible')) return;
        z.fadeIn(100);
    } else {
        var x = $j('<div class="loading" style="width:100%%;height:100%%"></div>').css({position:'absolute',opacity:0.9}).hide().fadeIn(100);
        t.append(x);
    }
    e2vdomAfterResponse('$j("#%(id)s>div.ov-content>div[dataid='+t.attr('dataid')+']>.loading").fadeOut(100);');
}
"""

JS_DYNAMIC = """
    $j("#%(id)s").on('scroll resize', function () {
        clearTimeout(jQuery.data(this, 'scrollTimer'));
        jQuery.data(this, 'scrollTimer', setTimeout(function () {
            var obj = $j("#%(id)s");
            var $content = obj.find('>div.ov-content');
            var canLoadContent = $content.outerHeight() - obj.innerHeight() - obj.scrollTop() <= 30;
            
            if (canLoadContent) {
                execEventBinded("%(woid)s", 'endscroll', {});
            }
            vdom_ov_markShow("%(woid)s");
        }, 200));
    });
    vdom_ov_markShow("%(woid)s");
    
    window.setTimeout(function () {
        vdom_ov_markShow("%(woid)s");
    }, 2000);
"""

JS = """
<script type="text/javascript">
%(js_loading)s

$j(function(){
    // The item class is read back off this element by vdom_ov_makeDiv when it
    // builds a lazy placeholder. `$j(document).on("#id")` is jQuery's on() with
    // no handler, which returns document untouched - so the data landed on the
    // document and every placeholder was built with class "undefined".
    $j("#%(id)s").data("ovitemclass","%(class)s-item");

    $j(document).on('click dblclick', "#%(id)s div[dataid]", function(e){
        if (e.preventDefault) e.preventDefault(); else e.returnValue = false;
        var t = $j(this);
        if (e.type == 'dblclick') {
            t.data('doo', false);
            %(js_loading_call)s
            execEventBinded('%(woid)s', "itemdblclick", {"id":t.attr("dataid")});
            return false;
        } else {
            setTimeout(function() {
                if (t.data('doo') == true) {
                    %(js_loading_call)s
                    execEventBinded('%(woid)s', "itemclick", {"id":t.attr("dataid")});
                    return false;
                }
            }, 220);
            t.data('doo', true);
        }
        return false;
    });

    $j(document).on('mouseover', "#%(id)s div[dataid]", function(e){
        execEventBinded('%(woid)s', "itemmouseover", {"id":$j(this).attr("dataid"), 'X':e.pageX, 'Y':e.pageY});
        return false;
    }).on('mouseout', "#%(id)s div[dataid]", function(e){
        execEventBinded('%(woid)s', "itemmouseout", {"id":$j(this).attr("dataid")});
        return false;
    });

    %(js_sortable)s
    %(js_drag)s
    %(js_dynamic)s

});
</script>"""

JS_INFINITE_SCROLL = """/*
$j(document).on('infiniteScroll', '#%(id)s', {
    'ovid': '%(woid)s',
    'cssc': '%(cssc)s'
});*/
/*
var obj = $j("#%(id)s");
var $content = obj.find('>div.ov-content');
var canLoadContent = $content.outerHeight() - obj.innerHeight() - obj.scrollTop() <= 30;
if (canLoadContent) {
    execEventBinded("%(woid)s", 'itemsrequestforinfinite', { loaded: $('>div.ov-content>div[dataid]', obj).length });
}
*/
"""


E2VDOM_DYNAMIC_JAVASCRIPT = """
var x = $j('#%(id)s>div.ov-content');
$j('>div[dataid]', x).remove();
var ovtmp = $j('#%(tmp_id)s:last');
if ($j.trim(ovtmp.html()) != '') {
    $j(">span.ov-eoi", x).before( $j('>div[dataid]', ovtmp) );
}
"""

E2VDOM_DIV_ONLY_JAVASCRIPT = """
var x = $j('#%(id)s>div.ov-content');
$j('>div[dataid]', x).remove();
var ovtmp = $j('#%(tmp_id)s:last');
if ($j.trim(ovtmp.html()) != '') {
    $j(">span.ov-eoi", x).before( $j('>div[dataid]', ovtmp) );
    /*$j('>div[dataid]',ovtmp).each(function(){
        $j(">span.ov-eoi", x).before($j(this));
    });*/
    // vdom_ov_markShow("%(woid)s");
    // NOTE: Workaround for not working vdom_ov_markShow after load
    window.setTimeout(function { vdom_ov_markShow("%(woid)s"); }, 1);
}
"""

E2VDOM_RENDER_JAVASCRIPT = """
var ovtmp = $j('#%(tmp_id)s:last');
if ($j.trim(ovtmp.html()) != '') {
    var x = $j('#%(id)s>div.ov-content');
    $j('>div[dataid]',ovtmp).each(function(){
        var t = $j(this);
        var i = $j(">div[dataid="+t.attr('dataid')+"]", x);
        if (i.length > 0) {
            if (i.hasClass('selected')) t.addClass('selected');
            i.before(t);
            i.remove();
            //} else {
            //  $j(">span.ov-eoi", x).before($j(this));
        }
    });
    vdom_ov_markShow("%(woid)s");
}
"""
OVERFLOW = {
    "0": "auto",
    "1": "hidden",
    "2": "scroll",
    "3": "visible"
}

LAYOUT = {
    "0": "clear: both",
    "1": "float: left;",
    "2": "width: 100% !important; clear: both;",
}

def xml_escape(value):
    global xml_escape

    illegal_chrs = [
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
        for (low, high) in illegal_chrs if low < sys.maxunicode]
    regex = re.compile("[%s]" % "".join(illegal_ranges))

    def real_xml_escape(text):
        return regex.sub("", text)

    xml_escape = real_xml_escape
    return real_xml_escape(value)


class VDOM_objectview(VDOM_object):
    
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render_items(self, items, div_only, bindings):
        if not self.vdomclassid:
            return ""

        classname = self.classname or "ov"
        source_object = self.lookup(self.vdomclassid)
        parent_object = None if div_only else self.lookup(self.id)

        if not source_object:
            return "Invalid VDOM class"
        used_types = set()
        used_types.add(source_object.type)
        for obj in source_object.objects.values():
            used_types.add(obj.type)        
        
        source_classname = source_object.attributes["classname"]
        source_width = source_object.attributes["width"]
        source_height = source_object.attributes["height"]

        last_index = len(items) - 1
        contents = []
        for index, (key, data) in enumerate(items.items()):
            copy = managers.engine.application.objects.new(source_object.type,
                name="vdomclass%d" % index, virtual=True, attributes=source_object.attributes)
            copy.objects.replicate(source_object.objects)
            copy.actions.replicate(source_object.actions)

            if self.lifetime == "1":
                managers.memory.track(copy, sync=managers.request_manager.current)
            elif self.lifetime == "2":
                managers.memory.track(copy, sync=managers.session_manager.current)

            classes = " ".join(filter(None, (
                "%s-item" % classname,
                "%s-item-%s" % (classname, index + 1),
                "%s-item-first" % classname if index == 0 else None,
                "%s-item-last" % classname if index == last_index else None,
                "%s-item-odd" % classname if index % 2 else None,
                "not-loaded" if div_only else None)))

            values = {
                "dataid": key,
                "visible": "1",
                "width": source_width,
                "height": source_height,
                "classauto": classes,
                "classname": source_classname
            }

            if not isinstance(data, dict):
                values["data"] = data
                try:
                    data = json.loads(data)
                except Exception:
                    pass
            if bindings is not None and isinstance(data, dict):
                template_name = data.get("vdomclass", "default")
                binding = bindings.get(template_name)

                cache = {0: (copy, {})}

                for key, value in data.items():
                    if binding is None or key not in binding:
                        continue

                    attributes = binding[key]
                    if not isinstance(attributes, list):
                        attributes = [attributes]

                    for name in attributes:
                        pair = name.rsplit(".", 1)

                        if len(pair) == 1:
                            target, attributes = cache[0]
                        elif pair[0] in cache:
                            target, attributes = cache[pair[0]]
                        else:
                            target, attributes = copy, {}
                            for object_name in pair[0].split("."):
                                target = target.objects.get(object_name)
                                if not target:
                                    print ("!!!", object_name)
                                    break
                            else:
                                cache[pair[0]] = target, attributes

                        if target and pair[-1] in target.attributes:
                            attributes[pair[-1]] = xml_escape(value)

                for target, attributes in cache.values():
                    target.attributes.update(attributes)

            copy.attributes.update(values)

            if div_only:
                contents.append("""<div class="{classes}" dataid="{id}" style="{style}"></div>""".format(
                    id=key,
                    classes=classes,
                    style="position:relative;width:%spx;height:%spx;display:block;" % (
                        source_width, source_height)))
            else:
                contents.append(managers.engine.render(copy, parent_object, "vdom"))
        
        e2vdom.update_types(self,used_types)
        return "".join(contents)

    def render(self, contents=""):
        woid = (self.id).replace('-', '_')
        id4js = "o_" + woid

        try:
            items = json.loads(self.data, object_pairs_hook=OrderedDict)
            if isinstance(items, dict):
                div_only = False
            elif isinstance(items, list):
                items, div_only = OrderedDict((str(key), "") for key in items), True
            else:
                raise Exception("Unable to parse data")
        except Exception:
            if self.data:
                raise Exception("Unable to parse data")
            items, div_only = {}, False

        # parse bindings
        try:
            bindings = json.loads(self.bindings)
        except Exception:
            if self.bindings:
                raise Exception("Unable to parse bindings")
            bindings = None

        items_contents = self.render_items(items, div_only, bindings)

        if request.render_type == "e2vdom":
            # action render
            tmp_id = "ov%s" % uuid4()
            if self.dynamicrender == "0":
                js = E2VDOM_DYNAMIC_JAVASCRIPT % {"id": id4js, "tmp_id": tmp_id, "woid": woid}
            else:
                if div_only:   # [] - empty frames: rerender
                    js = E2VDOM_DIV_ONLY_JAVASCRIPT % {"id": id4js, "tmp_id": tmp_id, "woid": woid}
                else:         # {} - items with content: render items in empty frames
                    js = E2VDOM_RENDER_JAVASCRIPT % {"id": id4js, "tmp_id": tmp_id, "woid": woid}

            return VDOM_object.render(self, contents="""<noreplace/>
<div id="%(tmp_id)s" style="display: none">%(contents)s</div>
<script type='text/javascript'>
    %(js)s
</script>""" % {"js": js, "contents": items_contents, "tmp_id": tmp_id})
        else:
            # initial render
            e2vdom.process(self, self.parent.id if self.parent else None)
            
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
                
            style = " ".join([f"{key}: {value};" for key, value in styles.items() if value])

            classname_item = 'ov' if self.classname == '' else (self.classname).replace(' ', '')
            css = "<style>\n" + self.style % {"id": id4js} + "</style>" if self.style else ""

            style_items = """<style type="text/css">
#%(id)s .%(class)s-item {
%(layout)s
}
</style>""" % {"id": id4js, "class": classname_item, "layout": LAYOUT.get(self.layout, "")}

            if self.loading == "0":
                js_loading_call = ""
                js_loading = ""
            else:
                js_loading_call = "%s_ld(t);" % id4js
                js_loading = JS_LOADING % {"id": id4js}

            js_dynamic = JS_DYNAMIC % {"id": id4js, "woid": woid, "cssc": classname_item}

            js_drag = JS_DRAG % {"id": id4js, "woid": woid, "class": classname_item} if self.draggable == "1" else ""

            js_sortable = JS_SORTABLE % {"id": id4js, "woid": woid} if self.sortable == "1" else ""

            js = JS % {
                "js_drag": js_drag,
                "id": id4js,
                "woid": woid,
                "class": classname_item,
                "js_loading": js_loading,
                "js_loading_call": js_loading_call,
                "js_dynamic": js_dynamic,
                "js_sortable": js_sortable
            }

            if VDOM_CONFIG_1["DEBUG"] == "1":
                debug_info = "objtype='objectview' objname='%s' ver='%s'" % (self.name, self.type.version)
            else:
                debug_info = ""

            result = """{css}
                <div {debug_info} id="{id}" style="{style}" class="{classname}">
                    {style_items}
                    <div class='ov-content'>
                        {contents}
                        <span class='ov-eoi' style='display: block; clear: both'></span>
                    </div>
                </div>
                {js}
                """.format(
                js=js,
                css=css,
                id=id4js,
                debug_info=debug_info,
                style=style,
                style_items=style_items,
                classname=' '.join([self.classname, 'vdom_objectview']).strip(),
                contents=items_contents
            )

            return VDOM_object.render(self, contents=result)

    def regex(self, obj):
        match = re.search(r'\d+', obj)
        return int(match.group()) if match else ""
    
    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value
        self.width, self.height, self.top, self.left = [
            int(self.ide_width), int(self.ide_height), 
            int(self.ide_top), int(self.ide_left)
        ]
        result = get_empty_wysiwyg_value(self, "cc72f740-5527-4dab-3c59-16b7fccb0032")
        return VDOM_object.wysiwyg(self, contents=result)
        
def on_update(object, attributes):
    
    o = object
    modif = {}
    
    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, '').lower()
            
            if obj_value.isdigit() and attr_value.isdigit():
                modif[attr] = attr_value + "px"
                modif["ide_"+ attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                modif[attr] = attr_value.rstrip("px") + "px"
                modif["ide_"+ attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                modif[attr] = attr_value if "px" in attr_value else obj_value
                modif["ide_"+ attr] = attr_value.rstrip("px")
            else:
                modif[attr] = attr_value
    attributes.update(modif)
    
    default = """\
#%(id)s .loading { 
    background: #fff url('/1869b90e-c056-1337-dfac-72b9873df6fa.res') center center no-repeat; 
}
#%(id)s .not-loaded { 
    background: url('/feb69c13-3f9b-f49f-6527-72f5a7193a34.res') center center no-repeat; 
}
"""
    
    users = """\
#%(id)s {

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
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")
            
    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")
        
    list = """\
[ "item1", "item2", "item3" ]
"""
    
    dict = """\
{
    "A": {"label": "AAA"},
    "B": {"label": "BBB"},
    "C": {"label": "CCC"},
    "D": "DDD" 
}
"""

    bindings_ex = """\
{
    "default": {
        "label": "text.value" 
    }
}"""

    data_map = {
        "0": "",
        "1": list,
        "2": dict,
        "3": bindings_ex
    }
    
    if "skindata" in attributes:
        skindata = attributes["skindata"]
        if skindata in ["1", "2"]:
            attributes.update(data=data_map[skindata], bindings=bindings_ex)
        else:
            attributes.update(data="", bindings="")

    if any(key in attributes for key in ["data", "bindings"]):
        if any(attributes.get(key) not in data_map.values() for key in ["data", "bindings"]):
            attributes.update(skindata="0")


    return ""
    
def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]
        
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_"+ attr] = obj_value.rstrip("px")