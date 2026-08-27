class VDOM_codeeditor(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        id = "o_" + (self.id).replace("-", "_")

        display = "display:none;" if self.visible == "0" else "display:block;"
        width = "width: {};".format(self.check_unit(self.width)) if self.width else ""
        height = "height: {};".format(self.check_unit(self.height)) if self.height else ""
        top = "top: {};".format(self.check_unit(self.top)) if self.top else ""
        left = "left: {};".format(self.check_unit(self.left)) if self.left else ""

        style = """z-index: {zind}; {top} {left} overflow: visible; position: absolute;
            {width} {height} padding: 2px 5px 2px 5px; {display} font: 14px tahoma
            """.format(
            zind=self.zindex,
            top=top,
            left=left,
            width=width,
            height=height,
            display=display,
        )

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='codeeditor' objname='%s' ver='%s'" % (
                self.name,
                self.type.version,
            )
        else:
            debug_info = ""

        is_readonly = "true" if self.is_readonly == "1" else "false"

        result = """
<style type="text/css">
#%(id)s .CodeMirror-scroll { %(height)s }
</style>
<div id="%(id)s" style="%(style)s" %(debug_info)s class="%(classname)s">
    <textarea name="%(name)s" style='%(height)s %(width)s'>%(value)s</textarea>
</div>
<script type="text/javascript">
$(document).ready(() => {
    if (typeof window.%(id)s_codeeditor !== 'undefined') {
        window.%(id)s_codeeditor.toTextArea();
        delete(window.%(id)s_codeeditor);
    }


    window.%(id)s_codeeditor = CodeMirror.fromTextArea($('#%(id)s>textarea').get(0), {
        mode: '%(mode)s',
        lineNumbers: true,
        styleActiveLine: true,
        highlightSelectionMatches: {minChars: 2},
        readOnly: %(is_readonly)s,
    });
    //bug fix

    $('#%(id)s').parents('form:first').submit(function(){
        window.%(id)s_codeeditor.save();
    });

    window.%(id)s_codeeditor.refresh();

    const el = $('#%(id)s');

    var intervalId = setInterval(function() {
        if (el.is(':visible')) {
            window.%(id)s_codeeditor.refresh();
            clearInterval(intervalId);
        }
    }, 200);
});
</script>""" % {
            "mode": self.syntax,
            "id": id,
            "name": self.customname or self.name,
            "style": style,
            "value": str(self.value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"),
            "width": width,
            "height": height,
            "debug_info": debug_info,
            "is_readonly": is_readonly,
            "classname": " ".join([self.classname, "vdom_codeeditor"]).strip(),
        }

        return VDOM_object.render(self, contents=result)

    def get_lines_amount(self, value):
        count = value.count("\n")

        return int(count) + 1

    def get_lines_text(self, value, text_height):
        amount = self.get_lines_amount(value)

        lines = """ <text x="0" y="2" width="28" height="{text_height}" 
                    font-family="tahoma" font-size="14" fill="#aaaaaa" align="right"> 
            """.format(text_height=text_height)

        i = 1
        while i <= amount:
            text_y = (i - 1) * 17

            if text_y >= text_height:
                i = i + 1
                break

            text_h = 20 if text_y + 20 <= text_height else text_height - text_y
            lines += """ <tspan y="{y}" height="{height}">{line_number}</tspan> """.format(y=text_y, line_number=i, height=text_h)
            i = i + 1

        lines += " </text> "

        return lines

    def wysiwyg(self, contents=""):
        self.width, self.height, self.top, self.left = [
            int(self.ide_width),
            int(self.ide_height),
            int(self.ide_top),
            int(self.ide_left),
        ]

        text_width = self.width - 38
        text_height = self.height - 2

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}" 
                    backgroundcolor="#ffffff" bordercolor="#cccccc">
                    <svg>
                        <rect x="1" y="1" width="28" height="{text_height}" fill="#F7F7F7"/>
                        <line x1="30" y1="1" x2="30" y2="{line_y_end}" style="stroke:#eeeeee"/>
                        <text x="40" y="17" width="{text_width}" height="{text_height}" font-family="Courier New" font-size="14">{value}</text>
                        {lines}
                    </svg>
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            text_width=text_width,
            text_height=text_height,
            line_y_end=1 + self.height - 2,
            value=self.value,
            name=self.name,
            lines=self.get_lines_text(self.value, text_height),
        )

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    o = object
    mods = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, "").lower()

            if obj_value.isdigit() and attr_value.isdigit():
                mods[attr] = attr_value + "px"
                mods["ide_" + attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                mods[attr] = attr_value.rstrip("px") + "px"
                mods["ide_" + attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                mods[attr] = attr_value if "px" in attr_value else obj_value
                mods["ide_" + attr] = attr_value.rstrip("px")
            else:
                mods[attr] = attr_value
    attributes.update(mods)

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"