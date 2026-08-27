import json


class VDOM_treegrid(VDOM_object):
    def render(self, contents=""):
        idn = (self.id).replace("-", "_")
        id = "o_" + idn
        id_treegrid = "t_" + idn
        check_unit = lambda v: str(v) + "px" if v.isdigit() else v

        styles = {
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "display": "none" if self.visible == "0" else self.displaying,
            "position": self.positioning if self.positioning != "static" else "",
            "width": check_unit(self.width),
            "height": check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": check_unit(self.top),
            "left": check_unit(self.left),
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
        style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        params = []
        # custom_style = []

        def create_styles_for_hidden_field(col_number):
            return """
            .dhx_grid-header-cell:nth-child({0})
            {{display: none;}}
            .dhx_grid-cell:nth-child({0})
            {{display: none;}}""".format(col_number + 1)

        hidden_fields_styles = ""
        if self.hiddenfields:
            fields_for_hidde = json.loads(self.hiddenfields)
            hidden_fields_styles = " ".join([create_styles_for_hidden_field(col_number) for col_number in fields_for_hidde])

        if self.fit_to_container == "1":
            params.append("fitToContainer:true,")

        if self.rows_height:
            params.append("rowHeight: %s," % (self.rows_height))

        if self.selection == "1":
            params.append("selection:true,")

        if self.columns_auto_width == "1":
            params.append("columnsAutoWidth: true,")

        if self.custom:
            params.append(self.custom)

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='%s' objname='%s' ver='%s'" % (self.type.name, self.name, self.type.version)
        else:
            debug_info = ""

        result = """
        <div %(debug_info)s id='%(id)s' style='%(style)s' class="%(cssclass)s">
            <div id="%(id_treegrid)s" style="width:100%%; height:100%%;"></div>
        </div>
    <style type="text/css">
        %(hidden_fields_styles)s
        %(selfstyle)s
    </style>

    <script type="text/javascript">
                    var %(id_treegrid)s = new dhx.TreeGrid("%(id_treegrid)s", {
                    columns: %(columns)s,
                    columnsAutoWidth: false,
                    data: %(data)s,
                    %(params)s
                });


                %(id_treegrid)s.events.on("cellClick", function (row, column) {
          //window.console.log(row);
          //window.console.log('********');
          //window.console.log(column);

          const key = row.%(keyField)s

                    execEventBinded('%(idn)s', 'cellclick', {
            keyField: key,
            cellData:JSON.stringify(row),
            columnData:JSON.stringify(column)});
                });

        %(id_treegrid)s.events.on("cellDblClick", function (row, column) {
          //window.console.log(row);
          //window.console.log('********');
          //window.console.log(column);

          const key = row.%(keyField)s

          execEventBinded('%(idn)s', 'celldblclick', {
            keyField: key,
            cellData:JSON.stringify(row),
            columnData:JSON.stringify(column)});
        });
    </script>
""" % {
            "debug_info": debug_info,
            "id": id,
            "idn": idn,
            "id_treegrid": id_treegrid,
            "style": style,
            "selfstyle": self.style % {"id": id},
            "cssclass": " ".join([self.cssclass, "vdom_treegrid"]).strip(),
            "params": "\n".join(params),
            "data": self.data,
            "columns": self.columns,
            "keyField": self.key,
            "hidden_fields_styles": hidden_fields_styles,
        }

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        image_id = "40264b4b-9d99-4453-941c-fe836f1c86ec"
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