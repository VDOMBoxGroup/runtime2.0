class VDOM_formeobuilder(VDOM_object):
    def get_css_style(self, style_name, style_value):
        if style_name == "z-index" and style_value == "0":
            return ""

        if style_value.isdigit():
            return "{}: {}px;".format(style_name, style_value)

        if style_value == "":
            return ""
        else:
            return "{}: {};".format(style_name, style_value)

    def render(self, contents=""):
        woid = (self.id).replace("-", "_")
        id = "o_" + woid

        if self.positioning1 == "static":
            self.left = self.top = ""
            self.positioning1 = ""

        result = """
            <div objname="%(name)s" data-id="%(id)s" class="%(classname)s vdom_formeobuilder">
                <div id="%(id)s"></div>
                <button data-ident="%(id)s">GET JSON IN CONSOLE</button>
            </div>
            """ % {"id": id, "name": self.name, "classname": self.classname}

        javascript = """
    <script type='module'>
      var %(id)s = null
      async function init() {
        if (!window.FormeoEditor) await import('/72aef15c-ab6b-bb04-8163-1d8828ab5651.js');
        %(id)s = new FormeoEditor({
          editorContainer: '#%(id)s',
          svgSprite: 'https://draggable.github.io/formeo/assets/img/formeo-sprite.svg',
          events: {
            onSave: evt => {
              execEventBinded('%(woid)s', "onSave", {"formJSON": JSON.stringify(%(id)s.formData)});
            }
          }
        }, %(data)s);
        return %(id)s
      }
      init().then(function(data) {
        %(id)s = data
        $("[data-ident='%(id)s']").click(function() {
          console.log(JSON.stringify(%(id)s.formData))
        })
      });
        </script>
        """ % {"id": id, "woid": woid, "data": self.data}

        styles = """<style>
        #%(id)s { width: 100%%; height: 100%%; }
        .formeo-editor { width:100%%; height: 100%%; }
        .formeo-controls { overflow-x: hidden; overflow-y: auto; }
        %(css)s
        [data-id="%(id)s"] { %(width)s %(height)s %(position)s %(top)s %(left)s %(zindex)s %(display)s %(margin)s %(padding)s }
        </style>""" % {
            "id": id,
            "zindex": self.get_css_style("z-index", self.zindex),
            "width": self.get_css_style("width", self.width),
            "height": self.get_css_style("height", self.height),
            "top": self.get_css_style("top", self.top),
            "left": self.get_css_style("left", self.left),
            "position": self.get_css_style("position", self.positioning1),
            "display": self.get_css_style("display", self.displaying),
            "margin": self.get_css_style("margin", self.margins),
            "padding": self.get_css_style("padding", self.paddings),
            "css": self.style % {"id": id},
        }
        styles = styles.replace(" ", "").replace("\t", "")

        result += javascript
        result += styles
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


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]
        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")