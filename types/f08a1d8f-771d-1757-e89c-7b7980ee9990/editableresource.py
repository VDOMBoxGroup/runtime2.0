from scss.compiler import compile_string

def patch_lib():
    import scss.grammar.expression
    for i in range(len(scss.grammar.expression.SassExpressionScanner._patterns)):
        if scss.grammar.expression.SassExpressionScanner._patterns[i][0] == 'OPACITY':
            scss.grammar.expression.SassExpressionScanner._patterns[i] = ('OPACITY', '(?i)(opacity)')
            break
patch_lib()

class VDOM_editableresource(VDOM_object):
    def render(self, contents=""):
        id = "o_" + (self.id).replace("-", "_")
        if self.datatype == "4":
            return VDOM_object.render(self, contents="")
        import_way_is_inline = self.import_way == "1" or self.import_way == "2"
        if self.visible == "1":
            resource = application.resources.get_by_label(self.id, "userdata")
            if resource:
                res_id = resource.id
            else:
                res_type = "js" if self.datatype == "1" else "css" if (self.datatype == "2" or self.datatype == "3") else "txt"
                self.data = compile_string(self.data) if self.datatype == "3" else self.data
                if not import_way_is_inline:
                    res_id = application.resources.create_temporary(self.id, "userdata", self.data, res_type, "data")

            udata = ""
            if self.datatype == "1":
                if import_way_is_inline:
                    udata = f'<script id="{id}">{self.data}</script>'
                    if self.import_way == "1":
                        request.dyn_libraries[self.name] = udata
                        return VDOM_object.render(self, contents="")
                    if self.import_way == "2":
                        return VDOM_object.render(self, contents=udata)
                if res_id:
                    udata = '<script type="text/javascript" src="/%s.res"></script>' % res_id
                    request.dyn_libraries[self.name] = udata
                    return VDOM_object.render(self, contents="")
                else:
                    udata = "<!-- no res for script -->"
            elif self.datatype == "2" or self.datatype == "3":
                if import_way_is_inline:
                    udata = f'<style id="{id}">{self.data}</style>'
                    if self.import_way == "1":
                        request.dyn_libraries[self.name] = udata
                        return VDOM_object.render(self, contents="")
                    if self.import_way == "2":
                        return VDOM_object.render(self, contents=udata)
                if res_id:
                    udata = '<style rel="stylesheet" type="text/css">@import url("/%s.css");</style>' % res_id
                    request.dyn_libraries[self.name] = udata
                    return VDOM_object.render(self, contents="")
                else:
                    udata = "<!-- no res for style -->"
            else:
                udata = self.data

        else:
            return VDOM_object.render(self, contents="")

    def get_data_format(self):
        format_dict = {"1": "JS", "2": "CSS", "3": "SCSS", "4": "OFF"}

        text_format = ""
        try:
            text_format = format_dict[self.datatype] if self.datatype in format_dict else ""
        except Exception:
            pass

        return text_format

    def wysiwyg(self, contents=""):
        self.width = "80"
        self.height = "80"

        image_width = image_height = 50
        image_x = (int(self.width) - image_width) / 2
        image_y = 0

        txt_format_left = 3 + image_x

        image_id = "a61a9853-638a-8f83-0a70-16a8c65eb8a1"

        text_format = self.get_data_format()

        result = f"""<container name="{self.name}" id="{self.id}" zindex="{self.zindex}" hierarchy="{self.hierarchy}" top="{self.top}" left="{self.left}"
                    width="{self.width}" height="{self.height}" backgroundcolor="#f0f0f0" alpha="0.5">
                    <svg>
                        <image x="{image_x}" y="{image_y}" href="#Res({image_id})" width="{image_width}" height="{image_height}"/>
                    </svg>
                    <text top="30" left="{txt_format_left}" width="{image_width - 6}" textalign="right" color="#ffffff">{text_format}</text>
                    <text top="50" width="80" textalign="center" color="#000000">{self.name}</text>
                </container>
            """

        return VDOM_object.wysiwyg(self, contents=result)