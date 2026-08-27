def on_compile(application, object, action_name, context, objects):
    result = objects
    for xobject in object.get_objects_list():
        result.append({"object": xobject})
    return result


class VDOM_printtowebcontainer(VDOM_object):
    def render(self, contents=""):
        return ""

    def wysiwyg(self, contents=""):
        result = '<container id="%s" visible="%s" zindex="%s" hierarchy="%s"></container>' % (self.id, self.visible, self.zindex, self.hierarchy)
        return VDOM_object.wysiwyg(self, contents=result)