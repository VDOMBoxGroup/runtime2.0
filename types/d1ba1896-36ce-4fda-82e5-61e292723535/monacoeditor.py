class VDOM_monacoeditor(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        """
        Args:
            contents (str): Content into this type.
        """
        WOID = (self.id).replace("-", "_")
        ID = "o_" + WOID

        DEBUG_INFO = {"objname": self.name, "objtype": self.type.name, "id": ID, "version": self.type.version}
        debug_info_string = " ".join(["{}='{}'".format(key, value) for key, value in DEBUG_INFO.items()])

        display = "none" if self.visible == "0" else self.displaying
        position = "{pos}".format(pos=self.positioning1) if self.positioning1 and self.positioning1 != "static" else ""

        styles = {
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "display": display,
            "position": position,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
        }
        if self.positioning1 == "static":
            styles["top"] = styles["left"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        STYLES_STRING = """
        <style>
            .%(id)s {
                %(styles)s
            }
        </style>
        """ % {"id": ID, "styles": styles_str}

        script = """
        <script type="text/javascript">
            const loadMonacoEditor = (url, callback) => {
                const script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = url;
                script.onload = callback;
                
                document.head.appendChild(script);
            };
            
            const doNothing = () => {};
            
            loadMonacoEditor('https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.48.0/min/vs/loader.min.js', () => {
                /*
                 * @function generateEvent  This function generate E2VDOM event.
                 * @param    {String} name           name of event.
                 * @param    {Object} payload        payload of event.
                 * @return   {null}                  return nothing
                 */
                function generateEvent(name, payload) {
                    execEventBinded("%(woid)s", name, payload);
                }
                
                require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.48.0/min/vs' }});
                window.MonacoEnvironment = { getWorkerUrl: () => proxy };
                
                let proxy = URL.createObjectURL(new Blob(
                    [`
                        self.MonacoEnvironment = { baseUrl: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.48.0/min/' };
                        importScripts('https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.48.0/min/vs/base/worker/workerMain.js');
                    `],
                    { type: 'text/javascript' }
                )
            );
            
            require(["vs/editor/editor.main"], () => {
                const config = {
                    values: JSON.parse(`%(values)s` || '{}'),
                    theme: "vb", // ["vs", "vs-dark", "hc-black"]
                    textAreaName: "%(name)s",
                    "bracketPairColorization.enabled": false,
                    hover: {delay: 3000, enabled: true}
                }
                window.monacoEditor = new MonacoEditor(document.getElementById("%(id)s"), config);
            });
            
            generateEvent("load", {param: "I am loaded"});
        });
        </script>

        """ % {"id": ID, "woid": WOID, "values": self.value, "name": self.name}

        RESULT = """
        <div {debug_string} class='{id} {classname}'>
            {styles}
            {script}
        </div>
        """.format(debug_string=debug_info_string, classname=" ".join([self.cssclass, "vdom_monacoeditor"]).strip(), id=ID, styles=STYLES_STRING, script=script)

        return VDOM_object.render(self, contents=RESULT)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        image_id = "30b2054e-61bc-46dc-8f7b-263540d8eaaa"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    o = object
    modifications = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, "").lower()

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