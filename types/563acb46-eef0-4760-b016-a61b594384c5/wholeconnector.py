class VDOM_wholeconnector(VDOM_object):

    def render(self, contents=""):
        id = 'o_' + (self.id).replace('-', '_')
        style = ""
        return VDOM_object.render(self, contents=u"<div id=\"%(id)s\" style=\"%(style)s\"></div>" % { "id":id, "style":style})
        
    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value
        
        image_id = "e1dda532-5f2b-4631-808a-3eed69abde13"
        result = get_empty_wysiwyg_value(self, image_id)
        
        return VDOM_object.wysiwyg(self, contents=result)