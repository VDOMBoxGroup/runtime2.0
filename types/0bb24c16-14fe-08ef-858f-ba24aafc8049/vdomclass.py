from scripting import e2vdom
class VDOM_vdomclass(VDOM_object):

    def render(self, contents=""):
        e2vdom.process(self)
        if self.classname == "":
            #classname = ""
            classname = u" class='%s' " % (self.classauto)
        else:
            classname = u" class='%s %s' " % (self.classauto, self.classname)

        if self.positioning == "0":
            style_pattern = u"position:relative;width:{width}px;height:{height}px;"
        else:
            style_pattern = u"position:absolute;width:{width}px;height:{height}px;left:{left}px;top:{top}px;"

        # style = "position:relative;width:{width}px;height:{height}px;left:{left}px;top:{top}px;".format(
        # style = "position:relative;width:{width}px;height:{height}px;".format(
        style = style_pattern.format(
            width=self.width,
            height=self.height,
            left=self.left,
            top=self.top
        )

        if self.visible == '1':
            style += "display:block;"
        else:
            style += "display:none;"

        dataid = ""
        if self.dataid != '':
            dataid = u"dataid=\"%s\"" % (self.dataid).replace("\"", "")

        if style != "":
            style = u" style='%s' " % style
        # result = u"<div {classname} {style}>{contents} DATA: {data}</div>".format(
        result = u"<div objtype='vdomclass' objname='{name}' {classname} {style} {dataid}>{contents}</div>".format(
            #data      = self.data,
            name=self.name,
            dataid=dataid,
            classname=classname,
            style=style,
            contents=contents
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        if len(contents) == 0:
            from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

            image_id = "51267b9d-7246-639e-ab19-16f8321bb2dd"
            result = get_empty_wysiwyg_value(self, image_id)

            return VDOM_object.wysiwyg(self, contents=result)

        result = u"""<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
<svg>
    <rect x="0" y="0" width="{width}" height="{height}" fill="#EEEEEE" />
</svg>
{contents}
</container>""".format(
                id=self.id, vis=self.visible, name = self.name,
                zind=self.zindex, hierarchy=self.hierarchy, order=self.order,
                top=self.top, left=self.left,
                width=self.width, height=self.height,
                contents=contents)

        return VDOM_object.wysiwyg(self, contents=result)