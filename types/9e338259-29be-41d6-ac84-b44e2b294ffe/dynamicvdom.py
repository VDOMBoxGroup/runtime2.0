from xml.sax.saxutils import escape as xml_escape
import managers
from scripting import e2vdom


def exception_trace():
    import sys
    import traceback

    type_, val, tb = sys.exc_info()
    s = "\n".join(traceback.format_exception(type_, val, tb))
    return s


WYSIWYG_IMAGE_UUID = "76bfc87a-dbe3-46e3-8d11-cc78a576b63a"
TEMPLATE = """{libraries}
<div objname="{name}" id="{id}" style="{style}" class="{classes}">{contents}
</div>
<script type='text/javascript'>
{observer}
{declarations}
</script>
{dynlibraries}"""
observer = """
const observer_{id} = new MutationObserver((mutationsList) => {{
  for (const mutation of mutationsList) {{
    const target = mutation.target;
    if (target.getAttribute('objname') === 'dynamicvdom' || target.id == 'e2vdomloading') {{
      window.dynamicObjectLoading = true;
    }}
  }}
}});

observer_{id}.observe(document.body, {{ childList: true, subtree: true }});"""


class VDOM_DynamicObject(VDOM_object):
    def inner_render(self):
        e2vdom.process(self)
        try:
            with e2vdom.select(dynamic=True):
                vdomobject = self.loads(self.vdomxml.encode("utf8"), self.vdomactions, handler=self.handler)
                if vdomobject:
                    if self.lifetime == "1":
                        managers.memory.track(vdomobject, sync=managers.request_manager.current)
                    elif self.lifetime == "2":
                        managers.memory.track(vdomobject, sync=managers.session_manager.current)
                    with managers.engine.start_render(vdomobject, parent=self) as context:
                        contents = context.contents
                        declarations, libraries = e2vdom.generate(context.instance)
                        return contents, declarations, libraries
                else:
                    return "", "", ""
        except Exception as error:
            ex_trace = exception_trace().replace("\n", "<br>")

            if self.debugmode == "1":
                raise
            else:
                if self.rendererrormsg:
                    message = self.rendererrormsg
                else:
                    lines = xml_escape(self.vdomxml).split("\n")
                    for i, txt in enumerate(lines):
                        lines[i] = "{}: {}".format(i + 1, txt)
                    message = "Render error: {}<br>{}<br>{}".format(error, ex_trace, "<br>".join(lines))
                return '<span class="render-error">%s</span>' % message, "", ""

    # use inner_render for raw_content
    def render(self, contents=""):
        inner, declarations, libraries = self.inner_render()
        style = "{display}z-index: {zindex}; position: {pos}; top: {top}px; left: {left}px; height: {height}px; width: {width}px; overflow: {overflow};".format(
            display="display:none; " if self.visible == "0" else "",
            zindex=self.zindex,
            pos=self.position,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            overflow={"1": "hidden", "2": "scroll", "3": "visible"}.get(self.overflow, "auto"),
        )

        dynlibraries = "".join(managers.request_manager.current.dyn_libraries.values()) if request.render_type == "e2vdom" else ""

        contents += TEMPLATE.format(
            name=self.name,
            id="o_" + self.id.replace("-", "_"),
            style=style,
            classes=self.classname,
            contents=inner,
            libraries=libraries,
            declarations=declarations,
            dynlibraries=dynlibraries,
            observer=observer.format(id="o_" + self.id.replace("-", "_")) if request.render_type != "e2vdom" else "",
        )

        return super(VDOM_DynamicObject, self).render(contents=contents)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        contents += get_empty_wysiwyg_value(self, WYSIWYG_IMAGE_UUID)
        return super(VDOM_DynamicObject, self).wysiwyg(contents=contents)