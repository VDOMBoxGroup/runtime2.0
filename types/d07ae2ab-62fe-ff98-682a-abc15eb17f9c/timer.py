class VDOM_time(VDOM_object):
    def render(self, contents=""):
        result = ""
        id = (self.id).replace("-", "_")
        oid = "o_" + id
        if self.active == "1":
            if self.once == "1":
                jstartscript = """vdom_ui_timerStartOnce("%s", %s);""" % (oid, self.interval)
            else:
                jstartscript = """vdom_ui_timerStart2("%s", %s);""" % (oid, self.interval)
            jstart = """<script type='text/javascript'> $j(function(){ $j(function(){ %s }); }); </script>""" % (jstartscript)
        else:
            jstart = ""
        result += """<div id="%s" style="display:none">%s</div>""" % (oid, jstart)
        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.zindex = "0"
        self.width = "50"
        self.height = "50"

        image_id = "5aec5fea-8e46-3378-4783-16ef3fa46b04"
        result = get_empty_wysiwyg_value(self, image_id, 0.4)

        return VDOM_object.wysiwyg(self, contents=result)