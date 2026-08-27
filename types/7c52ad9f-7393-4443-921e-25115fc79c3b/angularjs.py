class VDOM_angularjs(VDOM_object):
    def render(self, contents=""):
        id_woo = (self.id).replace("-", "_")
        id_out = "o_" + id_woo
        if self.jscode and self.inline == "0":
            resource = application.resources.get_by_label(self.id, "jsdata")
            if resource:
                js_res_id = resource.id
            else:
                js_res_id = application.resources.create_temporary(
                    self.id, "jsdata", self.jscode, "js", "jscode"
                )
            jsdata = (
                '<script type="text/javascript" src="/%s.res"></script>' % js_res_id
            )
        else:
            jsdata = ""
        if self.css:
            resource = application.resources.get_by_label(self.id, "cssdata")
            if resource:
                css_res_id = resource.id
            else:
                css_res_id = application.resources.create_temporary(
                    self.id, "cssdata", self.css, "css", "css"
                )
            # first line of the css must be: @charset "UTF-8";
            cssdata = (
                '<style rel="stylesheet" type="text/css">@import url("/%s.res");</style>'
                % css_res_id
            )
        else:
            cssdata = ""
        request.dyn_libraries[self.name] = "\n" + jsdata + "\n" + cssdata

        id = "o_" + (self.id).replace("-", "_")
        import base64

        udata = """<script type='text/javascript'>
/*        var app = angular.module('%s',  ['ngRoute','ngResource']);
app.service('e2%s', function() {
    this.trigger = function (data) {execEventBinded("%s", "trigger", {"data":data});}
    this.subscribe = function (callback) { document.getElementById("%s").addEventListener("handle", callback );}
});*/
%s
var tmp = document.createElement('div');
tmp.innerHTML = atob('%s');

document.getElementById('%s').appendChild(tmp);


</script>""" % (
            self.name,
            self.name,
            id_woo,
            id_out,
            self.jscode if self.inline == "1" else "",
            base64.b64encode(self.htmlcode),
            id,
        )
        display = "display:none;" if self.visible == "0" else "display:block;"

        if self.nostyle == "2":
            # return u"%s" % udata
            return VDOM_object.render(self, contents="%s" % udata)
        elif self.nostyle == "1":
            # return u"<span id=\"%(id)s\">%(data)s</span>" % { "id": id, "data": udata }
            return VDOM_object.render(
                self,
                contents='<span id="%(id)s">%(data)s</span>'
                % {"id": id, "data": udata},
            )
        else:
            if self.overflow == "1":
                ov = "hidden"
            elif self.overflow == "2":
                ov = "scroll"
            elif self.overflow == "3":
                ov = "visible"
            else:
                ov = "auto"
            style = (
                "overflow:"
                + ov
                + "; position: absolute; z-index: "
                + self.zindex
                + "; top: "
                + self.top
                + "px; left: "
                + self.left
                + "px; width: "
                + self.width
                + "px; height: "
                + self.height
                + "px"
            )
            # return u"<div id=\"%(id)s\" style=\"%(style)s\">%(data)s</div>" % { "id":id, "style":style, "data":udata }
            return VDOM_object.render(
                self,
                contents='<div id="%(id)s" %(display)s style="%(style)s">%(data)s</div>'
                % {"id": id, "display": display, "style": style, "data": udata},
            )

    def wysiwyg(self, contents=""):
        self.width = "50"
        self.height = "50"

        image_width = image_height = 50
        image_x = image_y = 0

        image_id = "0d7cfede-483a-45c1-9cd1-20b91428ece2"

        result = """<container name="{name}" id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" top="{top}" left="{left}"
            width="{width}" height="{height}" backgroundcolor="#f0f0f0" alpha="0.5">
            <svg>
            <image x="{image_x}" y="{image_y}" href="#Res({image_id})" width="{image_width}" height="{image_height}"/>
            </svg>
            <text top="30" left="3" width="{text_width}" textalign="right" color="#ffffff">{text_format}</text>
            </container>
            """.format(
            id=self.id,
            name=self.name,
            zindex=self.zindex,
            hierarchy=self.hierarchy,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            image_x=image_x,
            image_y=image_y,
            image_id=image_id,
            text_format=self.htmlcode,
            image_width=image_width,
            image_height=image_height,
            text_width=image_width - 6,
        )

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    if "jscode" in attributes:
        resource = application.resources.get_by_label(object.id, "jscode")
        if resource:
            application.resources.delete(resource.id)
            js_res_id = application.resources.create_temporary(
                object.id, "jsdata", attributes["jscode"], "js", "jscode"
            )