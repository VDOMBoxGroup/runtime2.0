import re


class VDOM_tabulator(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        idn = (self.id).replace("-", "_")
        id = "o_" + idn
        id_tabulator = "t_" + idn

        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "position": self.positioning,
            "display": "none !important" if self.visible == "0" else self.displaying,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            styles["position"] = ""

        object_style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        params = []

        # custom_style = []

        hidden_columns = [item for item in self.hiddenfields.split()]

        # hidden_fields_styles = ""

        if self.fit_to_container == "1":
            params.append("fitToContainer:true,")

        if self.rows_height:
            params.append("rowHeight: %s," % (self.rows_height))

        params.append("selectable:true," if self.selection == "multi" else "selectable:1,")

        if self.columns_auto_width == "1":
            params.append('layout: "fitDataStretch",')

        if self.pagelength != "-1" or self.pagging == "remote":
            params.append('pagination: "{}",'.format(self.pagging))
            params.append("paginationSize: {},".format(self.pagelength))

        if self.toggle_tree_by_click_row == "1":
            toggle_tree_by_click_row = "row.treeToggle();"
        else:
            toggle_tree_by_click_row = ""

        if self.custom:
            params.append(self.custom)

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='%s' objname='%s' ver='%s'" % (self.type.name, self.name, self.type.version)
        else:
            debug_info = ""

        search_field = ""
        if self.search_field == "true":
            search_field = """
          <div class="tabulator-search-wrapper">
            <input class="tabulator-search" type="search" oninput="clearTimeout(window.t{id}.filter_timeoutID); window.t{id}.filter_timeoutID = setTimeout(() => {{Obj{id}.filter(this.value)}}, 500)">
          </div>
          """.format(id=id[1:])

        result = """
        <div %(debug_info)s id='%(id)s' style='%(style)s' class='%(cssclass)s'>
            %(search_field)s
            <div id="%(id_tabulator)s" style="width: 100%%; height: 100%%"></div>
        </div>
        <style type="text/css">
            %(selfstyle)s
        </style>

        <script type="text/javascript">
$(document).ready(() => {
    const clickInfo = {
        click_timer: 0,
        click_delay: 200,
        click_prevent: false
    };

    function rowClick(e, row) {
        %(toggle_tree_by_click_row)s
        execEventBinded('%(idn)s', 'rowclick', {
                rowKeyValue: row.getData().%(keyField)s,
                rowData: JSON.stringify(row.getData())
        });
    }

    function selectionChange(data, rows) {
        const keys = data.map(({ %(keyField)s }) => %(keyField)s);
        
        execEventBinded('%(idn)s', 'rowsselectionchanged', {
                rowsKeysList: keys,
                rowsDataList: data
        });
    }
    
    function rowSelect(row) {
        execEventBinded('%(idn)s', 'rowselect', {
            rowKeyValue: row.getData().%(keyField)s,
            rowData: JSON.stringify(row.getData())
        });
    }


    function rowDoubleClick(e, row) {
        execEventBinded('%(idn)s', 'rowdoubleclick', {
            rowKeyValue: row.getData().%(keyField)s,
            rowData: JSON.stringify(row.getData())
        });
    }

    window.%(id_tabulator)s = new Tabulator("#%(id_tabulator)s", {
      height:"100%%",
      groupToggleElement:"header",
      data: %(data)s,
      dataTree:true,
      dataTreeStartExpanded: %(data_tree_start_expanded)s,
      columns: %(columns)s,
      responsiveLayout: "hide",
      placeholder:"No Data Available",
      rowClick: rowClick,
      rowDblClick: rowDoubleClick,
      rowSelectionChanged: selectionChange,
      rowSelected: rowSelect,
      %(params)s
    });

    var cols_to_hide = %(hidden_columns)s;

    cols_to_hide.forEach(function(item,i,cols_to_hide) { %(id_tabulator)s.hideColumn(item) }); 
});
        </script>
""" % {
            "debug_info": debug_info,
            "id": id,
            "idn": idn,
            "id_tabulator": id_tabulator,
            "style": object_style,
            "selfstyle": self.style % {"id": id},
            "cssclass": " ".join([self.cssclass, "vdom_tabulator"]).strip(),
            "params": "\n".join(params),
            "data": self.data,
            "columns": self.columns,
            "keyField": self.key,
            # "hidden_fields_styles": hidden_fields_styles,
            "hidden_columns": hidden_columns,
            "data_tree_start_expanded": "true" if self.datatreestartexpanded == "1" else "false",
            "search_field": search_field,
            "toggle_tree_by_click_row": toggle_tree_by_click_row,
        }

        return VDOM_object.render(self, contents=result)

    def regex(self, obj):
        match = re.search(r"\d+", obj)
        return int(match.group()) if match else ""

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

    empty = ""

    users = """\
#%(id)s {

}
"""

    skin_mapping = {"0": users, "1": empty}

    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    columns_ex = """\
[
    {title:"Name", field:"name"},
    {title:"Age", field:"age"},
    {title:"Gender", field:"gender"},
    {title:"Height", field:"height"},
    {title:"Date of Birth", field:"dob"}
]
"""

    data_ex = """\
[
    {id:1, name:"Billy Bob", age:"12", gender:"ClientsNot payed", height:1, col:"red", dob:"", cheese:1},
    {id:2, name:"Mary May", age:"1", gender:"ClientsNot notpayed", height:2, col:"blue", dob:"14/05/1982", cheese:true},
    {id:3, name:"Christine Lobowski", age:"42", height:0, col:"green", dob:"22/05/1982", cheese:"true"},
    {id:4, name:"Brendon Philips", age:"125", gender:"ClientsNot payed", height:1, col:"orange", dob:"01/08/1980"}
]
"""

    data_map = {"key_ex": "id", "data_ex": data_ex, "columns_ex": columns_ex, "hidden_ex": "gender height", "empty": ""}

    if "skindata" in attributes:
        skindata = attributes["skindata"]
        if skindata == "1":
            attributes.update(key="id", data=data_ex, columns=columns_ex, hiddenfields="gender height")
        else:
            attributes.update(data="", columns="")

    if any(key in attributes for key in ["data", "columns", "key", "hiddenfields"]):
        if any(attributes.get(key) not in data_map.values() for key in ["key", "data", "columns", "hiddenfields"]):
            attributes.update(skindata="2")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")