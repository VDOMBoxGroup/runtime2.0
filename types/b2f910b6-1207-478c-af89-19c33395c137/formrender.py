class VDOM_formrender(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = "none" if self.visible == "0" else self.displaying
        woid = (self.id).replace("-", "_")
        language = {
            "en-US": "a9f8d2bc-1a80-bc8e-11cd-1e4a7b049588",
            "fr-FR": "a34e5e27-27a4-2210-b689-1e4a8b79c487",
            "ru-RU": "a86bbdc0-012d-4942-f010-1e4a9759bba4",
        }
        current_language = language.get(self.language, "a9f8d2bc-1a80-bc8e-11cd-1e4a7b049588")

        id = "o_" + woid
        position = self.positioning if self.positioning and self.positioning != "static" else ""

        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": self.zindex if int(self.zindex) != 0 else "",
            "position": position,
            "display": display,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        classname = """class='%s'""" % " ".join([self.classname, "vdom_formrender"]).strip()
        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='formRender' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        result = """{css}
                    <div {debug_info} id="{id}" style="{style}" name="{name}" {classname}></div>
       <script>
              if (typeof {id} === 'undefined') {{
              	const {id} = {{}};
              }}
              {id}.formData = {contents};
              jQuery(function($) {{
                $('#{id}').formRender({{fields: $.formRenderModules.fields, disableInjectedStyle:"bootstrap", templates: $.formRenderModules.templates ,dataType: '{datatype}',formData: {id}.formData, i18n: {{
                  locale: '{language}',
                  location: '/',
                  extension: '.lang',
                }}}});
                
                $('.formBuilder-injected-style').remove();

                //fix rerender(for example onchange VDOM attrs)
                $('body').off("change", "#{id} input, #{id} select");
                
                $('body').on("change", "#{id} input, #{id} select", e => {{
                    const $input = $(e.currentTarget);
                    const itemName = $input.attr('name');
                    const itemValue = $input.val();
                    execEventBinded('{id}'.slice(2), 'inputonchange', {{itemName, itemValue}});
                  }}
                );
              }});
       </script>""".format(
            debug_info=debug_info,
            css=css,
            id=id,
            # woid=woid,
            # display=display,
            style=style,
            name=self.name,
            contents=self.data or "[]" if self.datatype == "json" else "'<form-template></form-template>'",
            classname=classname,
            datatype=self.datatype,
            language=current_language,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        image_id = "54e7f8ab-64f1-b113-029e-1703a76c6fa4"
        result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    o = object
    mods = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, "").lower()

            if obj_value.isdigit() and attr_value.isdigit():
                mods[attr] = attr_value + "px"
                mods["ide_" + attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                mods[attr] = attr_value.rstrip("px") + "px"
                mods["ide_" + attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                mods[attr] = attr_value if "px" in attr_value else obj_value
                mods["ide_" + attr] = attr_value.rstrip("px")
            else:
                mods[attr] = attr_value
    attributes.update(mods)

    users = """
#%(id)s {

}
"""
    skin_mapping = {"0": users, "1": ""}
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")
    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")