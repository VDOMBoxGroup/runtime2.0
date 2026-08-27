class VDOM_printtowebscript(VDOM_object):
    def render(self, contents=""):
        result = ""
        return VDOM_object.render(self, parent, contents=result)

    def wysiwyg(self, contents=""):
        result = ""
        return VDOM_object.wysiwyg(self, contents=result)