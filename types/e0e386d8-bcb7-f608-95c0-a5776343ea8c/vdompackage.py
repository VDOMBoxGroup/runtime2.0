from scripting import e2vdom


def on_compile(application_object, object, action_name, context, objects):
    result = objects
    for xobject in object.get_objects_list():
        result.append({"object": xobject})
    return result


class VDOM_vdompackage(VDOM_object):
    def render(self, contents=""):
        # result = u""
        # return VDOM_object.render(self, parent, contents = result)

        e2vdom.process(self)
        # libraries, declarations, registrations = e2vdom.generate(self)
        # javascript = "%s\n%s\n" % (declarations, registrations)
        javascript, libraries = e2vdom.generate(self)

        #clean_id = (application.id).replace("-", "_")

        doctype = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">"""

        result = (
            "%(doctype)s\n"
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            "<head>\n"
            "<title>%(title)s</title>\n"
            '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />\n'
            "%(libraries)s"
            "</head>\n"
            "<body>\n"
            "%(contents)s\n"
            '<script type="text/javascript" src="/113513d0-ebae-42c4-9bdf-44ebf7828910.res?v=152"></script>\n'
            """<script>jQuery(document).ready(function($){
            $("[objtype='vdomclass']").show();
            });</script>"""
            "</body>\n"
            "</html>"
            % {
                "doctype": doctype,
                #"clean_id": clean_id,
                #"application": application.id,
                #"session": session.id,
                "title": self.title,
                #"javascript": javascript,
                "libraries": libraries,
                "contents": contents,
            }
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        result = """<container name="{name}" id="{id}" zindex="{zind}" hierarchy="{hierarchy}" top="0" left="0" width="100%" height="100%">
    {contents}
</container>""".format(
            id=self.id,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            name=self.name,
            # order = self.order,  # ???
            contents=contents,
        )

        return VDOM_object.wysiwyg(self, contents=result)