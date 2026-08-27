class VDOM_printtowebaction(VDOM_object):
    def render(self, contents=""):
        result = ""
        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        result = ""
        return VDOM_object.wysiwyg(self, contents=result)