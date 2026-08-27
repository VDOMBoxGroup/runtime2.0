class VDOM_xmlcontainer(VDOM_object):
    def render(self, contents=""):
        return self.declaration or ""

    def wysiwyg(self, contents=""):
        result = (
            '<container name="%s" id="%s" visible="%s" zindex="%s" hierarchy="%s" order="%s"><svg>%s</svg></container>'
            % (
                self.name,
                self.id,
                self.visible,
                self.zindex,
                self.hierarchy,
                self.order,
                contents,
            )
        )
        return VDOM_object.wysiwyg(self, contents=result)