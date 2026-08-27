class VDOM_formcheckbox(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        disable = "disabled='disabled'" if self.disable == "1" else ""

        state = ["", """checked="checked" """][int(self.attributes["state"])]

        styles = {
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "display": "none" if self.visible == "0" else self.displaying,
            "position": "%s" % self.positioning if self.positioning != "static" else "",
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "font-size": self.check_unit(self.fontsize),
            "font-weight": self.fontweight,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        clean_id = (self.id).replace("-", "_")
        id = "o_" + clean_id
        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""

        result = """%(css)s
          <div id="%(id)s" class="%(css_class)s vdom_formcheckbox" style="%(style)s">
            <input name="%(name)s" type="checkbox" %(state)s tabindex="%(tabind)s" value="%(value)s" 
              id="inp_%(id)s" style="vertical-align:top;#vertical-align:middle" %(disable)s/> 
            <label for="inp_%(id)s" style="vertical-align:middle">%(label)s</label>
            %(contents)s
          </div>
          <script type="text/javascript">jQuery(document).ready(function($){
$('#inp_%(id)s').on('click',function(e){
  var v = ($(this).is(':checked')) ? "1" : "0";
  execEventBinded('%(clean_id)s', 'change', { "Value": v });
  execEventBinded('%(clean_id)s', v == "1" ? 'checked' : 'unchecked', { "value": v })
  e.stopPropagation();
});
          });</script>
        """ % {
            "id": id,
            "style": style,
            "name": self.customname or self.name,
            "state": state,
            "tabind": self.tabindex,
            "value": self.value,
            "disable": disable,
            "label": self.label,
            "contents": contents,
            "clean_id": clean_id,
            "css_class": self.classname,
            "css": css,
        }

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        fontsize = self.fontsize
        if "px" not in fontsize and not fontsize.isdigit():
            fontsize = " 12px"
        else:
            fontsize = " {}px ".format(fontsize.rstrip("px")) if fontsize else " "
        state = ["", """ checked="checked" """][int(self.state)]
        disable = """ disabled="disabled" """ if self.disable == "1" else ""

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
            top="{top}" left="{left}" width="{width}" height="{height}" >
          <htmltext top="0" left="0" width="{width}" height="{height}" locked="true" overflow="hidden">
            <input type="checkbox" {state} {disable}
                  style="vertical-align:top; font: {fontweight} {fontsize} tahoma;" /> 
            <label style="vertical-align:middle; font: {fontweight} {fontsize} tahoma;">{label}</label>
            
          </htmltext>
        </container>
      """.format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            name=self.name,
            hierarchy=self.hierarchy,
            order=self.order,
            top=top,
            left=left,
            width=width,
            height=height,
            label=self.label,
            fontsize=fontsize,
            fontweight=self.fontweight or "normal",
            state=state,
            disable=disable,
        )

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

    users = """\
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