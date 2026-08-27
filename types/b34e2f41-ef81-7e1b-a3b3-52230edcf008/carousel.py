class VDOM_carousel(VDOM_object):
    def render(self, contents=""):
        display = "display:none;" if self.visible == "0" else "display:block;"

        style_zindex = "z-index:%s;" % self.zindex if int(self.zindex) != 0 else ""

        style = """{display} {zind} position: {pos}; top: {top}px; left: {left}px;
                    width: {width}px; height: {height}px; """.format(
            display=display, zind=style_zindex, pos=self.position, top=self.top, left=self.left, width=self.width, height=self.height
        )

        id = "o_" + (self.id).replace("-", "_")
        idin = id + "-inner"

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='carousel' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        data = self.data % {"id": idin}

        if self.direction == "1":
            dir = "right"
        elif self.direction == "2":
            dir = "up"
        elif self.direction == "3":
            dir = "down"
        else:
            dir = "left"

        classname = """class="%s" """ % self.classname if self.classname else ""

        if self.custominit != "":
            custom_init = self.custominit
        else:
            custom_init = """
        items: %(items)s,
        direction: "%(dir)s",
        scroll: {
            items: %(items)s,
            duration: %(duration)s,
            pauseOnHover: true
        }
            """ % {"dir": dir, "items": int(self.itemscount), "duration": int(self.duration)}

        result = """
<div %(debug_info)s id="%(id)s" style="%(style)s" %(classname)s>%(data)s</div>
<script type="text/javascript">
$j(function(){
    $j("#%(idin)s").carouFredSel({
        %(custom_init)s
    });
});
</script>""" % {"debug_info": debug_info, "id": id, "idin": idin, "style": style, "classname": classname, "data": data, "custom_init": custom_init}

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        image_id = "065ea1aa-cc4d-a3dd-8383-13ebc037be9e"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)