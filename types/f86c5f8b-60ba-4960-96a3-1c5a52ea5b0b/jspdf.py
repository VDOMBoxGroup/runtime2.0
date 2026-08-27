class VDOM_jspdf(VDOM_object):
    def render(self, contents=""):
        id = "o_" + (self.id).replace("-", "_")

        display = "display:none;" if self.visible == "0" else "display:block;"

        if self.overflow == "1":
            ov = "hidden"
        elif self.overflow == "2":
            ov = "scroll"
        elif self.overflow == "3":
            ov = "visible"
        else:
            ov = "auto"

        height = "height: " + self.height + "px;" if int("0%s" % self.height) > 0 else ""

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
            + "px; "
            + height
        )

        classname = 'class="%s"' % self.classname if self.classname else ""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='jspdf' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        js_code = """
<script>

    function pdfFromContainer_%(id)s() {

        var orientation = '%(orientation)s',
            units = '%(units)s',
            hide_container = %(hide_container)s,
            pdf_type = '%(object_id)s',
            page_format = '%(page_format)s',
            html_data = %(html_data)s,
            has_class = %(has_class)s;
                    
        var pdf = new jsPDF(orientation, units, page_format);

        var fake_body = document.createElement('body');

        if (!has_class) {
        
            fake_body.innerHTML = html_data;
            document.body.appendChild(fake_body);
            
            html2canvas(fake_body, {
                canvas:pdf.canvas,
                onrendered: function(canvas) {
                    if (hide_container) { fake_body.remove() };
                    
                    var iframe = document.getElementById(pdf_type);
                    iframe.src = pdf.output('datauristring');
                    
                }
            });
            
        } else {
        
            var coord_left = html_data.style.left,
                coord_top = html_data.style.top,
                zind = html_data.style.zIndex;
            html_data.style.left = "0px";
            html_data.style.top = "0px";
            html_data.style.zIndex = "1000";
        
            fake_body.appendChild(html_data);
            document.body.appendChild(fake_body);

            html2canvas(fake_body, {
                canvas:pdf.canvas,
                onrendered: function(canvas) {
                    if (hide_container) { fake_body.remove() };
                    
                    var iframe = document.getElementById(pdf_type);
                    iframe.src = pdf.output('datauristring');
                    
                    html_data.style.left = coord_left;
                    html_data.style.top = coord_top;
                    html_data.style.zIndex = zind;
                }
            });
        }
        
        
    }
</script>

<iframe id="%(object_id)s" type="application/pdf" width="100%%" height="100%%" frameborder="0" src=""></iframe>
            
        """ % {
            "orientation": self.orientation,
            "units": self.units,
            "page_format": self.format,
            "object_name": self.name,
            "object_id": "i" + id,
            "has_class": "true" if self.container_class else "false",
            "hide_container": "true" if self.hide_parent == "1" else "false",
            "id": id,
            "html_data": "document.getElementByClassName('%s')" % self.container_class if self.container_class != "" else "`%s`" % self.htmlcode,
        }

        return '<div %s id="%s" %s style="%s%s">%s</div>' % (debug_info, id, classname, style, display, js_code)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        # emtpy container right now, will update later
        image_id = "3026ac49-9910-f0a9-5fc5-8ebcd9698b8d"
        result = get_empty_wysiwyg_value(self, image_id)
        return VDOM_object.wysiwyg(self, contents=result)