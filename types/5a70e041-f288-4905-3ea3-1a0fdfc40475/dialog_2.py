from scripting import e2vdom, VDOM_object


CSS_SQUARE = """.boxy-wrapper { position: absolute;  }
.boxy-wrapper.fixed { position: fixed; }
.boxy-modal-blackout { position: fixed; background-color: black; left: 0; top: 0; }

.boxy-wrapper .title-bar {
position: relative;
background-color: #e9e9e9;
padding:1px;
font-size:10px;
text-align:center;
}
.boxy-wrapper .title-bar a.close{
outline: none;
position: absolute;
background: url("/3938bd92-e009-2767-09e2-1da56035c24a.png") -95px -128px;
height: 18px;
width: 19px;
top: 6px;
right: 6px;
}
.boxy-wrapper .title-bar a.close:hover{
border: 1px inset #999999;
}
.boxy-inner {
background-color:#fff !important;
border:3px solid #ccc;
}"""
CSS_ROUNDED = """.boxy-wrapper { position: absolute; 
-moz-box-shadow: 0 0 20px #777;
-webkit-box-shadow: 0 0 20px #777;
box-shadow: 0 0 20px rgba(0,0,0,0.5);
-moz-border-radius:6px;
-webkit-border-radius:6px;
border-radius:6px;
}
.boxy-wrapper.fixed { position: fixed; }
.boxy-modal-blackout { position: fixed; background-color: black; left: 0; top: 0; }

.boxy-wrapper .title-bar {
position: relative;
background-color: #e9e9e9;
padding:1px;
font-size:10px;
text-align:center;
}

.boxy-wrapper .title-bar a.close{
outline: none;
position: absolute;
background: url("/3938bd92-e009-2767-09e2-1da56035c24a.png") -95px -128px;
height: 18px;
width: 19px;
top: 6px;
right: 6px;
}
.boxy-wrapper .title-bar a.close:hover{
border: 1px inset #999999;
}

.boxy-inner {
background-color:#fff !important;
border:3px solid #ccc;
overflow: hidden;
}
"""
PRO_SUITE = """.boxy-wrapper { position: absolute; }
.boxy-wrapper.fixed { position: fixed; }
.boxy-modal-blackout { position: fixed; background-color: black; left: 0; top: 0; }

.boxy-wrapper .title-bar {
position: relative;
background-color: #fff !important;
margin-left:12px !important;
margin-right:12px !important;
margin-top:8px !important;
padding-bottom:8px !important;
text-align:left;
font-weight:normal;
border-bottom:1px solid #e5e5e5;

}
.boxy-wrapper .title-bar h2{
font-size:24px;
text-align:left;
font-weight:normal;
margin:0;
padding:0;
}

.boxy-wrapper .title-bar a.close{
outline: none;
position: absolute;
background: url("/3938bd92-e009-2767-09e2-1da56035c24a.png") -95px -128px;
height: 18px;
width: 19px;
top: 6px;
right: 6px;
display:none !important;
}
.boxy-wrapper .title-bar a.close:hover{
border: 1px inset #999999;
}

.boxy-inner {
border:0 !important;
background-color:#fff !important;
box-shadow: 0 0 40px #000;
-moz-box-shadow: 0 0 40px #000;
-webkit-box-shadow: 0 0 40px #000;
background: url("/ac84402d-b5d7-dcc7-fb33-357b0426918f.png") left bottom repeat-x;
}"""


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    # o = application.objects.search(object_id)

    skin = attributes.get("skin")
    style = attributes.get("style")
    # set attributes
    # if "skin" in param:
    # 	if param["skin"]["value"] == "1":
    # 		o.set_attributes({"style": CSS_SQUARE})
    # 	elif param["skin"]["value"] == "2":
    # 		o.set_attributes({"style": CSS_ROUNDED})
    # 	elif param["skin"]["value"] == "3":
    # 		o.set_attributes({"style": PRO_SUITE})
    if skin == "1":
        attributes.update(style=CSS_SQUARE)
    elif skin == "2":
        attributes.update(style=CSS_ROUNDED)
    elif skin == "3":
        attributes.update(style=PRO_SUITE)
    # 	if "style" in param and param["style"]["value"] != CSS_SQUARE and param["style"]["value"] != CSS_ROUNDED and param["style"]["value"] != PRO_SUITE:
    # 		o.set_attributes({"skin": "0"})
    if style not in (CSS_SQUARE, CSS_ROUNDED, PRO_SUITE):
        attributes.update(skin="0")

    return ""


class VDOM_dialog_2(VDOM_object):
    def render(self, contents=""):
        idn = (self.id).replace("-", "_")
        id = "o_" + idn

        e2vdom.process(self)

        result = """<style type="text/css">
/*defaults*/
.boxy-wrapper .title-bar h2{font-size:12px;font-weight:normal;margin:7px 0;padding:0;}
/*style*/
%(css)s</style>""" % {"css": self.style}
        result += """<!--[if lt IE 9]><style type="text/css">.boxy-modal-blackout{background:transparent;
filter:progid:DXImageTransform.Microsoft.Gradient(GradientType=1, StartColorStr='#88000000', EndColorStr='#88000000');}</style><![endif]-->"""

        # if self.draggable == "0":
        #     draggable = "true"
        # else:
        #     draggable = "false"

        if self.show == "1":
            show = "true"
        else:
            show = "false"

        if self.modal == "0":
            modal = "true"
        else:
            modal = "false"

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='%s' objname='%s' ver='%s'" % (
                self.type.name,
                self.name,
                self.type.version,
            )
        else:
            debug_info = ""

        result += """<table style='display:none' cellspacing='0' cellpadding='0' border='0' class='boxy-wrapper'>
            <tr><td class='top-left'></td><td class='top'></td><td class='top-right'></td></tr>
            <tr><td class='left'></td><td class='boxy-inner'>
                <div %(debug_info)s id='%(id)s' style='position: relative; width: %(width)spx; height: %(height)spx; z-index: %(zindex)s'>%(contents)s</div>
            </td><td class='right'></td></tr>
            <tr><td class='bottom-left'></td><td class='bottom'></td><td class='bottom-right'></td></tr></table>""" % {
            "debug_info": debug_info,
            "id": id,
            "width": self.width,
            "height": self.height,
            "zindex": self.zindex,
            "contents": contents,
            "classname": self.classname,
        }

        # result += """<div style='display:none'><div id='%(id)s' style='width: %(width)spx; height: %(height)spx; z-index: %(zindex)s'>%(contents)s</div></div>""" % {
        # "id": id, "width": self.width, "height": self.height, "zindex": self.zindex, "contents": contents
        # }

        result += """<script type='text/javascript'>
$(document).ready(function(){
    if (typeof dialog_win_%(id)s !== 'undefined') {
        dialog_win_%(id)s.hide();
        delete(dialog_win_%(id)s);
    }
    dialog_win_%(id)s=new Boxy($('#%(id)s'),{
        width: %(width)s
        ,height: %(height)s
        ,title: "%(title)s"
        ,closeText: ''
        ,show: %(show)s
        ,modal: %(modal)s
        ,fixed: false
        ,userclass: "%(classname)s"
        ,afterHide: function(){ 
            execEventBinded("%(idn)s", "hide", {});
            $('#ui-datepicker-div,#ColorDropdown_selector').fadeOut(); 
        }
        ,afterShow: function(){ 
            execEventBinded("%(idn)s", "show", {}); 
        }
    });
    $('.boxy-modal-blackout').scroll(function(){
        $('#ui-datepicker-div').fadeOut(); 
        $('input.formcolorpicker').click(); 
        $('input[name^=formdate_]').focusout(); 
    });
});
</script>""" % {
            "id": id,
            "idn": idn,
            "width": self.width,
            "height": self.height,
            "title": (self.title).replace('"', "&quot;"),
            "show": show,
            "modal": modal,
            "classname": (self.classname).replace('"', "&quot;"),
        }

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        result = """<container name="{name}" id="{id}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" top="{top}" left="{left}" width="{container_width}" height="{container_height}">
                <svg>
                    <rect x="0" y="0" width="{width}" height="{height}" stroke="#cccccc" stroke-width="3" fill="#ffffff">
                        <rect x="0" y="0" width="{width}" height="40" fill="#e9e9e9"/>
                        <line x1="{line_x1}"  y1="16" x2="{line_x2}"   y2="24" style="stroke:#222222"/>
                        <line x1="{line_x1}"  y1="24" x2="{line_x2}"   y2="16" style="stroke:#222222"/>
                    </rect>
                </svg>
                <text top="10" width="{width}" fontsize="14" color="black" textalign="center">{title}</text>
                {contents}
            </container>""".format(
            id=self.id,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            container_width=int(self.width) + 3,
            container_height=int(self.height) + 3,
            width=self.width,
            height=self.height,
            title=self.title,
            contents=contents,
            line_x1=int(self.width) - 20,
            line_x2=int(self.width) - 12,
            name=self.name,
        )

        return VDOM_object.wysiwyg(self, contents=result)