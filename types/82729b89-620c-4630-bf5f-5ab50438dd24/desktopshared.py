class VDOM_desktopshared(VDOM_object):
    def render(self, contents=""):
        return ""

    def wysiwyg(self, contents=""):
        result = '<container name="%s" id="%s" visible="%s" zindex="%s" hierarchy="%s"></container>' % (
            self.name,
            self.id,
            self.visible,
            self.zindex,
            self.hierarchy,
        )
        return VDOM_object.wysiwyg(self, contents=result)