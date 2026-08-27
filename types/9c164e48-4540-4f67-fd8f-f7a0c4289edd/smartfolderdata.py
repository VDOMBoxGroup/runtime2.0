from scripting import e2vdom

class VDOM_smartfolderdata(VDOM_object):

    def render(self, contents=""):

        woid = u"" + (self.id).replace('-', '_')
        id = u"o_" + woid

        display = u"display:none;" if self.visible == "0" else u"display:block;"

        e2vdom.process(self)

        classname = u"""class="%s" """ % self.classname if self.classname else u""
        classname_item = 'sf-item'

        style_zindex = u"z-index:%s;" % self.zindex if int(self.zindex) != 0 else u""

        #style = u"""{display} {zind} position: {pos}; top: {top}px; left: {left}px;  height: {height}px; """\
        style = u"""{display} {zind} position: {pos}; top: {top}px; left: {left}px; width: {width}px;"""\
            .format( display = display, zind = style_zindex, pos = self.position, 
                top = self.top, left = self.left, width = self.width)


        js_items_data = u""

        ### javascript

        js_base = u"""
$j('#%(id)s')
    %(js_items_data)s
;
$j("#%(id)s .items .%(class)s").bind('click dblclick', function(e){
    if (e.preventDefault) e.preventDefault(); else e.returnValue = false;
    var t = $j(this);
    if (e.type == 'dblclick') {
        %(id)s_doo = false;
        execEventBinded('%(woid)s', "itemdblclick", {"id":t.attr("index")});
    } else {
        setTimeout(function() {
            if (%(id)s_doo == true) {

var x = $j('#%(id)s').data("sf"), i = $j(this).attr('index');
%(id)s_current_item = x[i];
$j('#%(id)s>.%(class)s').removeClass('selected');
$j(this).addClass('selected');

                execEventBinded('%(woid)s', "itemclick", {"id":t.attr("index")});
            }
        }, 300);
        %(id)s_doo = true;
    }
    return false;
});
$j("#%(id)s .items .%(class)s").hover(function(e){
    execEventBinded('%(woid)s', "itemmouseover", {"id":$j(this).attr("index")});
    return false;
},function(e){
    execEventBinded('%(woid)s', "itemmouseout", {"id":$j(this).attr("index")});
    return false;
});
""" % { "id": id, "woid": woid, "class": classname_item, "js_items_data": js_items_data }

        if self.testhtml != '':
            js_add = ""
            testhtml = self.testhtml % { "id": id, "woid": woid, "class": classname_item }
        else:
            testhtml = ""
            js_add = u"""

$q(function(){
    vdom_sfd_init('%(woid)s', %(page_current)s, %(page_itemsper)s);
});
""" % {"woid": woid, "page_current": int(self.currentpage), "page_itemsper": int(self.itemsperpage) }

        ### pages

        currentpage = int(self.currentpage)
        if currentpage <= 0:
            currentpage = 1

        itemsperpage = int(self.itemsperpage)
        if itemsperpage <= 0:
            itemsperpage = 1

        ### consolidate javascript

        js = u"""<script type="text/javascript">
%(id)s_doo = false;
%(id)s_current_item = null;
$j(function(){
    %(js_base)s
    %(js_add)s
    execEventBinded('%(woid)s', "requestmeta", {}, true);
});
</script>""" % { "id": id, "woid": woid, "class": classname_item, "js_base": js_base, "js_add": js_add,
            "offset": str(itemsperpage*(currentpage-1)), "limit": str(itemsperpage) }

        ### styles

        css = u"""<style type='text/css'>
#%(id)s {
}
#%(id)s .items {
width: %(width)spx;
height: %(height)spx;
overflow: hidden;
}

#%(id)s {
background: #999;
border: 1px solid #888;
border-left: 1px solid #ddd;
border-top: 1px solid #ddd;
padding: 1px;
}
#%(id)s .sf-disabled {
background: #fff;
position: absolute;
left: 0;
top: 0;
width: 100%%;
height: 100%%;
opacity: 0.7;
}
#%(id)s .ui-state-disabled {
opacity: 1;
}
#%(id)s .info {
position: relative;
}
#%(id)s .title {
color: #fff;
font-size: 16px;
margin-left: 4px;
}
#%(id)s .metafields {
background: #ececec;
padding: 4px 1px;
position: relative;
border-bottom: 1px solid gray;
}
    #%(id)s .metafields .clear {
    clear: both;
    display: block;
    }
    #%(id)s .metafields .meta {
    width: 45%%;
    float: left;
    padding-left: 5px;
    border-right: 1px solid gray;
    position: relative;
    }
        #%(id)s .metafields .meta span,
        #%(id)s .metafields .meta input {
        display: block;
        float: right;
        width: 39%%;
        }
        #%(id)s .metafields .meta span {
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        }
        #%(id)s .metafields .meta a.del {
        display: block;
        width: 12px;
        height: 12px;
        border: 1px solid red;
        background: #f99;
        float: left;
        margin: 0 2px 0 0;

        }
    #%(id)s .info .btn-save,
    #%(id)s .info .btn-cancel,
    #%(id)s .info .btn-edit,
    #%(id)s .info .btn-add {
    display: block;
    width: 20px;
    height: 20px;
    color: #fff;
    background: blue;
    border: 1px solid #444;
    border-left: 1px solid #fff;
    border-top: 1px solid #fff;
    position: absolute;
    right: 2px;
    top: 2px;
    text-decoration: none;
    text-align: center;
    font-weight: bold;
    line-height: 18px;
    font-size: 20px;
    }
    #%(id)s .info .btn-save,
    #%(id)s .info .btn-add {
    top: 26px;
    background: green;
    }
    #%(id)s .info .btn-cancel {
    background: red;
    }
#%(id)s .items {
background: #fcfcfa;
position: relative;
}
#%(id)s .pages {
}
    #%(id)s .pages a {
    color: #eee;
    }
    #%(id)s .pages a:hover {
    color: #fff;
    text-decoration: none;
    }
    #%(id)s .pages a,
    #%(id)s .pages span {
    padding: 2px 4px;
    margin: 1px;
    display: block;
    float: left;
    }
    #%(id)s .pages span {
    background: #eee;
    }

</style>""" % {
            "id": id, "class": classname_item,
            "itemwidth": self.itemwidth, "itemheight": self.itemheight,
            "width": self.width, "height": self.height
        }

        # shide = u"style='display:none'"

        # toolbar = u"""<div class='' ><div style='clear:both'></div></div>"""

        ### debug info

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='smartfolder' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = u""

        ### out

        result = u"""
            {css}
            <div {debug_info} {classname} id="{id}" style="{style}">
                <div class="title"></div>
                <div class="info">
                    <form class="metafields"></form>
                    <a class="btn-edit" href="#"></a><a class="btn-add" href="#"></a>
                    <a class="btn-save" style='display:none' href="#"></a><a class="btn-cancel" style='display:none' href="#"></a>
                </div>
                <div class='items'>{contents}</div>
                <div class='pages'></div>
                <div class='sf-disabled' style='display:none'></div>
            </div>
            {js}
            {testhtml}
            """.format(
                    debug_info = debug_info, id = id, style = style, js = js, css = css, classname = classname,
                    testhtml = testhtml, contents = contents
                )

        return VDOM_object.render(self, contents=result)


    def wysiwyg(self, contents = ""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value
        
        image_id = "3da66ba6-5c23-4e4a-7b77-16e671733af3"
        result = get_empty_wysiwyg_value(self, image_id)
        
        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    css = """
#%(id)s {
}
#%(id)s .items {
}
#%(id)s .items .%(class)s {
}
#%(id)s .items .%(class)s-hover {
}
#%(id)s .controls {
}
    #%(id)s .controls .control {
    }
    #%(id)s .controls .control {
    }
    #%(id)s .controls .control:hover {
    }
    #%(id)s .controls .control:active {
    }
"""

    # o = application.objects.search(object_id)
    o = object

    # if "skin" in param:
    if "skin" in attributes:
        # if param["skin"]["value"] == "1":
        if attributes["skin"] == "1":
            # o.set_attributes({"style": css})
            attributes.update(style=css)
        # # elif param["skin"]["value"] == "2":
        # elif attributes["skin"] == "2":
        # #	o.set_attributes({"style": eof_style})
        # o.attributes.update(style=eof_style)
    # if "style" in param and param["style"]["value"] and o.attributes.style != css:
    if "style" in attributes and attributes["style"] and o.attributes["style"] != css:
        # o.set_attributes({"skin": 0})
        attributes.update(skin="0")

    return ""