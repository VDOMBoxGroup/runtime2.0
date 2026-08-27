class VDOM_formtext(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        display = "none" if self.visible == "0" else self.displaying

        if self.mode == "1":
            mode = """readonly="readonly" """
        elif self.mode == "2":
            mode = """disabled="disabled" """
        else:
            mode = ""

        auto = "off" if self.autocomplete == "0" else "on"

        clean_id = (self.id).replace("-", "_")
        id = "o_%s" % clean_id

        # for doctype xhtml 1.0 - width|height depends on padding
        # fixw = int(self.width) - 10
        # fixh = int(self.height) - 4

        border = "0px" if self.multiline == "0" and self.border == "0" else ""

        required = "required" if self.required == "1" else ""

        pattern = 'pattern="{}"'.format(self.pattern) if self.pattern else ""
        # titlepattern = 'title="{}"'.format(self.titlepattern) if self.titlepattern else ""

        maxlength = 'maxlength="{}"'.format(self.maxlength) if self.maxlength else ""
        minlength = 'minlength="{}"'.format(self.minlength) if self.minlength else ""
        inputtype = self.inputtype
        maxvalue = 'max="{}"'.format(self.maxvalue) if self.minlength else ""
        minvalue = 'min="{}"'.format(self.minvalue) if self.minlength else ""

        usercss = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": self.zindex if int(self.zindex) != 0 else "",
            "position": self.positioning,
            "display": display,
            "border-width": border,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            styles["position"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        if self.title == "":
            title = ""
        else:
            title = 'title="%s"' % (self.title).replace('"', "&quot;")

        if self.placeholder == "":
            placeholder = ""
        else:
            placeholder = 'placeholder="%s"' % (self.placeholder).replace('"', "&quot;")

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='formtext' objname='%s' ver='2012-02-6'" % self.name
        else:
            debug_info = ""

        if self.multiline == "0":
            result = """
                <input {debug_info} {required} id="{id}" name="{name}" 
                    style="{style}" tabindex="{tabind}" 
                    value="{value}" class="{classn} vdom_formtext" autocomplete="{auto}" 
                    type="{inputtype}" {maxvalue} {minvalue} {pattern} {maxlength} {minlength} 
                    {mode} {title} {placeholder} 
                />
            """.format(
                id=id,
                name=self.customname or self.name,
                style=styles_str,
                tabind=self.tabindex,
                debug_info=debug_info,
                value=str(self.value).replace('"', "&quot;"),
                classn=self.classname,
                auto=auto,
                mode=mode,
                placeholder=placeholder,
                title=title,
                required=required,
                pattern=pattern,
                maxlength=maxlength,
                minlength=minlength,
                inputtype=inputtype,
                maxvalue=maxvalue,
                minvalue=minvalue,
            )
        else:
            result = """
                <textarea {debug_info} {required} id="{id}" name="{name}" 
                    tabindex="{tabind}" style="{style}" class="{classn} vdom_formtext" 
                    type="{inputtype}" {pattern} {maxlength} 
                    {minlength} {mode} {title} {placeholder} 
          {maxvalue} {minvalue} 
                >{value}</textarea>
            """.format(
                id=id,
                name=self.customname or self.name,
                tabind=self.tabindex,
                debug_info=debug_info,
                style=styles_str,
                classn=self.classname,
                mode=mode,
                value=self.value,
                placeholder=placeholder,
                title=title,
                required=required,
                pattern=pattern,
                maxlength=maxlength,
                minlength=minlength,
                inputtype=inputtype,
                maxvalue=maxvalue,
                minvalue=minvalue,
            )

        focused = "$q('#%s').focus();" % id if self.focused == "1" else ""

        result += "{css}".format(css=usercss)

        result += """<script type='text/javascript'>
$(document).ready(function(){
    $('#%(id)s').blur(function(){
        var x = $.trim($(this).val());
        execEventBinded("%(clean_id)s", "blur", { itemValue: x, charCount: x.length });
    });
    $('#%(id)s').focusin(function(){
        execEventBinded("%(clean_id)s", "focus", {});
    });
    %(focused)s
});</script>""" % {"id": id, "clean_id": clean_id, "focused": focused}

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        disabled = """ disabled="disabled" """ if self.mode == "2" else ""
        border = "border-width:0;" if self.multiline == "0" and self.border == "0" else ""
        placeholder = 'placeholder="%s"' % (self.placeholder).replace('"', "&quot;") if self.placeholder != "" else ""

        style = """ style="width: {width}px; height: {height}px; background-color:#ffffff; font: 14px tahoma; padding: 2px 5px; {border}" """.format(
            border=border, width=self.width, height=self.height
        )

        if self.multiline == "1":  # multiline
            text = """<textarea objtype="formtext" {style} {disabled} {placeholder}>
                        {value}
                    </textarea>
                """.format(width=self.width, height=self.height, value=self.value, placeholder=placeholder, disabled=disabled, style=style)
        else:  # singleline
            text = """<input objtype="formtext" value="{value}" {style} {disabled} {placeholder}/>""".format(
                width=self.width, height=self.height, value=self.value, placeholder=placeholder, disabled=disabled, style=style
            )

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                        top="{top}" left="{left}" width="{width}" height="{height}" >
                    <htmltext top="0" left="0" width="{width}" height="{height}" overflow="hidden" blendMode="normal">
                        {text}
                    </htmltext>
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            name=self.name,
            width=self.width,
            height=self.height,
            text=text,
        )

        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
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