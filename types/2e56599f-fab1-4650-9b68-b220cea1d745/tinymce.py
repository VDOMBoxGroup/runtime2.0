class VDOM_tinymce(VDOM_object):
    def render(self, contents=""):
        """
            Args:
                contents (str): Content into this type.
        """
        WOID = (self.id).replace('-', '_')
        ID = 'o_' + WOID

        DEBUG_INFO = {
            "objname": self.name,
            "objtype": self.type.name,
            "id": ID,
            "version": self.type.version
        }
        debug_info_string = " ".join(
            ["{}='{}'".format(key, value) for key, value in DEBUG_INFO.items()]
        )

        def DISPLAY_CONVERT(v):
            return "none" if v == "0" else None

        def SIZE_CONVERT(v):
            return str(v) + "px" if v.isdigit() else v
        STYLES = {
            "display": DISPLAY_CONVERT(self.visible),
            "position": self.positioning1,
            "z-index": self.zindex,
            "top": SIZE_CONVERT(self.top),
            "left": SIZE_CONVERT(self.left),
            "width": SIZE_CONVERT(self.width),
            "height": SIZE_CONVERT(self.height),
            "margin": self.margins,
            "padding": self.paddings,
        }
        STYLES_STRING_FORMAT = ";".join(
            ["{}:{}".format(key, value)
             for key, value in STYLES.items() if value]
        )
        STYLES_STRING = """
        <style>
            .%(id)s {
                %(styles)s
            }

            .%(id)s * {
                box-sizing: border-box !important;
            }

            .%(id)s > div {
                height: 100%%;
            }

            .%(id)s > div > div {
                height: 100%% !important;
                display: flex;
                flex-direction: column;
            }

            .%(id)s .mce-edit-area {
                flex: 1;
            }

            /* fix icons */
            .mce-ico {
                font-family: 'tinymce' !important;
            }

        </style>
        """ % {"id": ID, "styles": STYLES_STRING_FORMAT}

        script = """
        <script defer>
            $(document).ready(() => {
                /*
                * @function          generateEvent  This function generate E2VDOM event.
                * @param    {String} name           name of event.
                * @param    {Object} payload        payload of event.
                * @return   {null}                  return nothing
                */
                function generateEvent(name, payload) {
                  execEventBinded("%(woid)s", name, payload);
                }


                window.%(id)s_tinymce = $('#%(id)s textarea').tinymce({
                  skin: false,
                  inline_boundaries: false,
                  resize: false,
                  plugins: [
                    'pagebreak', 'paste', 'image', 'hr',
                    'insertdatetime', 'link', 'lists',
                    'preview', 'table', 'textcolor',
                    'visualblocks', 'searchreplace', 'wordcount',
                    'save', 'importcss', 'imagetools', 'fullscreen',
                    'fullpage', 'codesample', 'code', 'charmap', 'advlist'
                  ],
                  height: "100%%",
                  content_css: ['/83a15133-3af1-10d8-be80-f76d0461cf6b.css'],
                  menu: {
                    file: { title: 'File', items: 'restoredraft | preview | print ' },
                    edit: { title: 'Edit', items: 'undo redo | cut copy paste | selectall | searchreplace' },
                    view: { title: 'View', items: 'code | visualaid visualchars visualblocks | preview fullscreen' },
                    insert: { title: 'Insert', items: 'image link media template codesample inserttable | charmap emoticons hr | pagebreak nonbreaking anchor toc | insertdatetime' },
                    format: { title: 'Format', items: 'bold italic underline strikethrough superscript subscript codeformat | blockformats fontformats fontsizes align lineheight | removeformat' },
                    /*tools: { title: 'Tools', items: 'spellchecker spellcheckerlanguage | code wordcount' },*/
                    table: { title: 'Table', items: 'inserttable | cell row column | tableprops deletetable' },
                    help: { title: 'Help', items: 'help' }
                  },
                  toolbar: 'undo redo | styleselect | code | formatselect fontselect fontsizeselect | ' +
                    'bold italic | forecolor backcolor | alignleft aligncenter ' +
                    'alignright alignjustify | bullist numlist outdent indent | ' +
                    ' removeformat | ' +
                    'link image wordcount',
                  /* The document font, stated so that nothing depends on a
                     default. The content stylesheet above carries only the
                     visualblocks decoration and declares no font at all, so
                     without this the author was looking at the browser default
                     for an unstyled iframe - Times New Roman 16px - while the
                     PDF came out in something else. Must stay equal to
                     DOC_FONT in the LimeOS library `model_template.py`. */
                  content_style:
                    "html, body, div, span, p, li, ul, ol, table, thead, tbody,"
                    + " tr, th, td, h1, h2, h3, h4, h5, h6"
                    + " { font-family: Helvetica, Arial, sans-serif; }"
                    + " html, body, div, span, p, li, ul, ol, table, thead,"
                    + " tbody, tr, th, td { font-size: 12pt; }"
                    + " h1 { font-size: 20pt; } h2 { font-size: 15pt; }"
                    + " h3 { font-size: 13pt; }",
                  font_formats:
                    "Helvetica=Helvetica,Arial,sans-serif;"
                    + "Arial=arial,helvetica,sans-serif;"
                    + "Courier=courier new,courier,monospace;"
                    + "Times New Roman=times new roman,times,serif",
                  paste_data_images: true,
                  extended_valid_elements: "div[data-mce-placeholder|class]",
                  fontsize_formats: '8pt 10pt 12pt 14pt 16pt 18pt 24pt 36pt 48pt',
                  setup: (editor) => {
                    editor.on('change', function () {
                      editor.save();
                      generateEvent("change", {value: editor.getBody().innerHTML});
                    });
                  }
                });
            })
        </script>
        """ % {
            "id": ID,
            "woid": WOID
        }

        html = """<textarea id="{id}_{name}" name="{name}">{value}</textarea>""".format(
            id=ID,
            name=self.name,
            value=self.value
        )

        RESULT = """
        <div {debug_string} class='{classname} vdom_tinymce {id}'>
            {styles}
            {html}
            {script}
        </div>
        """.format(
            debug_string=debug_info_string,
            classname=self.cssclass,
            id=ID,
            styles=STYLES_STRING,
            html=html,
            script=script
        )

        return VDOM_object.render(self, contents=RESULT)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value
        self.width, self.height, self.top, self.left = [int(self.ide_width), int(
            self.ide_height), int(self.ide_top), int(self.ide_left)]

        image_id = "188c34ad-1869-4bf2-91ef-95f1e53e3f94"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    o = object
    modifications = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, '').lower()

            if obj_value.isdigit() and attr_value.isdigit():
                modifications[attr] = attr_value + "px"
                modifications["ide_" + attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                modifications[attr] = attr_value.rstrip("px") + "px"
                modifications["ide_" + attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                modifications[attr] = attr_value if "px" in attr_value else obj_value
                modifications["ide_" + attr] = attr_value.rstrip("px")
            else:
                modifications[attr] = attr_value

    attributes.update(modifications)

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")