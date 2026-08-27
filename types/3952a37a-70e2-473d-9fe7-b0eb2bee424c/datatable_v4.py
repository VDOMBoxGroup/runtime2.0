import json


class VDOM_datatable_v4(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        idn = (self.id).replace("-", "_")
        id = "o_" + idn
        id_table = "t_" + id

        styles = {
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "position": self.positioning,
            "display": "none" if self.visible == "0" else self.displaying,
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""
            styles["position"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        cssclasses = " ".join([param.strip() for param in [self.cssclass, "vdom_datatablev4"] if param.strip()])
        multiselect = "multiselect" if self.selectionmode == "1" else ""
        tristate = "tristate" if self.tristate == "1" else ""

        classes = [param for param in [cssclasses, multiselect, tristate] if param]
        cssclass = 'class="{}"'.format(" ".join(classes))

        if self.header:
            try:
                header = json.loads(self.header)
                if isinstance(header, int):
                    raise Exception("Incorrect value in header %s" % self.header)
                else:
                    col_title = []
                    for i in header:
                        col_title.append({"title": i})
            except Exception:
                raise Exception("Incorrect value in header %s" % self.header)
        else:
            col_title = []
        if self.data:
            try:
                src_data = json.loads(self.data)
                if isinstance(src_data, int):
                    raise Exception("Incorrect value in data %s" % self.data)
            except Exception:
                raise Exception("Incorrect value in data %s" % self.data)
        else:
            src_data = [[]]

        key_index = -1
        if self.key:
            try:
                key_index = [_["title"] for _ in col_title].index(self.key)
            except ValueError:
                print("Datatable {table_name} has incorrect key value".format(table_name=self.name))
                key_index = 0
        else:
            pass

        VALID_KEY = key_index != -1 or key_index == 0
        if VALID_KEY and not self.customcolumns:
            self.customcolumns = """{targets: %(index)s, visible: false}""" % {"index": key_index}
        elif VALID_KEY and self.customcolumns:
            self.customcolumns += """,{targets: %(index)s, visible: false}""" % {"index": key_index}

        if self.fixedheight == "1":
            fixed_height = """height = "%(height)s" """ % {"height": styles["height"]}
        else:
            fixed_height = ""

        if self.showheader == "1":
            show_header = ""
        else:
            show_header = """
        const header = $("#%(id)s thead th");
        header.css('line-height', 0, "!important");
        header.css('font-size', 0, "!important");
        header.css('overflow','hidden', "!important");
        header.css('padding-top', '0', "!important");
        header.css('max-height', 0, "!important");
        header.css('padding-bottom', '0', "!important");
        header.css('height', 0, "!important");
      """ % {"id": id}

        scrollY_styles = ""
        if self.fixedheader != "0":
            scrollY = '"scrollY": "%(scrollY)s",' % {"scrollY": styles["height"]}
            scrollY_styles = """
      #%(id)s .dataTables_scrollHead, 
      #%(id)s .dataTables_scrollHeadInner, 
      #%(id)s table.display.dataTable.no-footer 
      {width: 100%% !important;}
      #%(id)s .dataTables_scroll, #%(id)s .dataTables_wrapper
      {height: 100%%;}
      """ % {"id": id}
        else:
            scrollY = ""

        if self.pagelength:
            page_length = """
      "pageLength": %(pagelength)s,
""" % {"pagelength": self.pagelength}
        else:
            page_length = ""

        if self.splittable == "0":
            paging = '"paging": false,'
        else:
            paging = ""

        if self.searching == "0":
            searching = '"searching": false,'
        else:
            searching = ""

        if self.title:
            title = """$('#%(id_table)s').append('<caption style="caption-side: top-right">%(title)s</caption>');
      """ % {"title": self.title, "id_table": id_table}
        else:
            title = ""

        # if multiselect
        slelection_mode = ""
        if self.selectionmode == "1":
            slelection_mode = """
      $('#%(id_table)s tbody').on( 'click', 'td', function () {
            const tr = $(this).parent();
            tr.toggleClass('selected');
            const {keyField} = get_column_data(this);
        execEventBinded('%(idn)s', 'rowsselected', {keyList: keyField});
      } );""" % {"id_table": id_table, "idn": idn}

        if self.selectedrows:
            try:
                json.loads(self.selectedrows)
                selectedrows = """
          const mas  = %(selectedrows)s;
          const _table = this.api();
          mas.forEach(function(id) {
            $(_table.row( id ).node()).addClass('selected');
          });
""" % {"selectedrows": self.selectedrows}
            except Exception:
                raise Exception("Incorrect value in selectedrows %s" % self.selectedrows)
        else:
            selectedrows = ""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='%s' objname='%s' ver='%s'" % (self.type.name, self.name, self.type.version)
        else:
            debug_info = ""

        result = """
    <div %(debug_info)s id='%(id)s' style='%(style)s' %(cssclass)s>
  <style type="text/css">
    %(scrollY_styles)s

    #%(id)s .dt-buttons {
        display:none;
    }
    %(selfstyle)s
  </style>
    <table id="%(id_table)s" class="display" width="100%%" %(fixed_height)s>
    </table>
  <script type="text/javascript">
    $(document).ready(function(){
      var id_%(id)s = '%(id)s';
      const table = $('#%(id_table)s').DataTable({
        data: %(data)s,
        dom: 'Bfri<"table_wrapper"t>p',
        buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
        columns: %(columns)s,
        order: [],
        %(paging)s
        %(searching)s
        %(scrollY)s
        %(page_length)s
        autoWidth: %(autoWidth)s,
        columnDefs: [%(customcolumns)s],
        initComplete : function() { 
          execEventBinded('%(idn)s', 'load', {width:$q('#%(id)s').outerWidth(),height:$q('#%(id)s').outerHeight()});
          %(selectedrows)s 
        },
        %(customparams)s
        // NOTE: Hides pagination panel if there's only one page
        "drawCallback": function(oSettings) {
            %(show_header)s
            if (oSettings._iDisplayLength == -1 || oSettings._iDisplayLength > oSettings.fnRecordsDisplay()) {
                jQuery(oSettings.nTableWrapper).find('.dataTables_paginate').addClass('datatable-pagination-disable');
            } else {
                jQuery(oSettings.nTableWrapper).find('.dataTables_paginate').removeClass('datatable-pagination-disable');
            }
            
         }
      });

      %(title)s

      $.fn.dataTable.Api.register( 'column().title()', function () {
        var colheader = this.header();
        return $(colheader).text().trim();
      } );

      function get_column_data(clicked_element) {
        const column = table.cell( clicked_element ).index().column;
        const row = table.cell( clicked_element ).index().row;

        const first_column_data = table.cell({row: row, column: %(key_index)s}).data();
        const cellData = table.row(row).data();
        const title = table.column(column).title();

        return {keyField:first_column_data, cellData:cellData, headerData:title}
      }

      table.click_timer = 0;
      table.click_delay = 200;
      table.click_prevent = false;

      $("#%(id_table)s tbody").on("click", 'td', function() {
          const sinleSelectionMode = %(single_selection_mode)s;
          const tr = $(this).parent();
          table.click_timer = setTimeout(() => {
            if (!table.click_prevent) {
             if (sinleSelectionMode) {
               if (tr.hasClass('selected')) {
                 tr.removeClass('selected');
                 execEventBinded('%(idn)s', 'rowsunselected', {});
               } else {
                 table.$('tr.selected').removeClass('selected');
                 const {keyField} = get_column_data(this);
                 execEventBinded('%(idn)s', 'rowsselected', {keyList: keyField});
                 tr.addClass('selected');
               }
             }
              execEventBinded('%(idn)s', 'cellclick', get_column_data(this));
            }
            table.click_prevent = false;
          }, table.click_delay);
        })
        .on("dblclick", 'td', function() {
          clearTimeout(table.click_timer);
          table.click_prevent = true;
          execEventBinded('%(idn)s', 'celldblclick', get_column_data(this));
        });

      %(customfunc)s
      %(selection_mode)s
    });
  </script>
</div>
""" % {
            "debug_info": debug_info,
            "id": id,
            "idn": idn,
            "id_table": id_table,
            "customcolumns": self.customcolumns,
            "show_header": show_header,
            "page_length": page_length,
            "paging": paging,
            "searching": searching,
            "selection_mode": slelection_mode,
            "single_selection_mode": "true" if self.selectionmode == "0" else "false",
            "autoWidth": self.autowidth,
            "selectedrows": selectedrows,
            "scrollY": scrollY,
            "style": styles_str,
            "selfstyle": self.style % {"id": id},
            "scrollY_styles": scrollY_styles,
            "cssclass": cssclass,
            "title": title,
            "fixed_height": fixed_height,
            "customparams": self.customparams,
            "customfunc": self.customfunc,
            "data": json.dumps(src_data),
            "columns": json.dumps(col_title),
            "key_index": key_index,
        }

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        # parse data
        try:
            header = json.loads(self.header)
        except Exception:
            header = []

        try:
            src_data = json.loads(self.data)
        except Exception:
            src_data = []

        data = []
        theader = ""
        tdata = ""

        if len(src_data) == 0 and len(header) == 0:
            image_id = "f7e008b4-3eef-3269-b004-089c613a538b"

            result = get_empty_wysiwyg_value(self, image_id)

            return VDOM_object.wysiwyg(self, contents=result)

        # collect data
        for value in src_data:
            if isinstance(value, list) and len(header) == len(value):
                row = dict(zip(header, value))
                data.append(row)
            else:
                data.append(value)

        # generate table header
        for colname in header:
            theader += """<cell backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="1">
            <text fontsize="14" color="#000000" textalign="center">
              {colname}
            </text>
          </cell>""".format(colname=str(colname))

        # generate table data
        for row in data:
            tdata += """<row backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="1">"""
            if header and len(header) == len(row):
                for col in header:
                    tdata += """<cell backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="1">
                <text fontsize="12" color="#000000" textalign="center">
                  {cell_data}
                </text>
              </cell>""".format(cell_data=str(row[col]))
            else:
                for val in row:
                    tdata += """<cell backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="1">
                <text fontsize="12" color="#000000" textalign="center">
                  {cell_data}
                </text>
              </cell>""".format(cell_data=str(val))

            tdata += "</row>"

        # collect result
        result = """<container name="{name}" id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" top="{top}" left="{left}" width="{width}" height="{height}">
          <table zindex="{zindex}" top="0" left="0" width="{width}" height="{height}" backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="1" >
            <row backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="1">
              {theader}
            </row>
            {tdata}
          </table>
          {contents}
        </container>
      """.format(
            id=self.id,
            zindex=self.zindex,
            hierarchy=self.hierarchy,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            theader=theader,
            tdata=tdata,
            contents=contents,
            name=self.name,
        )

        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    eof_style = """
#%(id)s caption
{
}

#%(id)s table.table
{
  border-collapse:collapse;
  border: none;
  height: 0;
}

#%(id)s .thead
{
  font-size: 12px;
  text-align: left;
  color: #7d7d4f;
  padding: 0 6px;
}

#%(id)s .th-cell
{
  background: #efefec;
  border: none;
  padding-left: 6px;
  font-size: 12px;
}


#%(id)s .th-cell-0
{
  width: 10px;
  -webkit-border-radius: 6px 0px 0px 6px;
  -moz-border-radius: 6px 0px 0px 6px;
  border-radius: 6px 0px 0px 6px;
}

/* Set this to the last header cell. Here we had 4 header cell, so I put it to 3.*/
#%(id)s .th-cell-3
{
  width: 10px;
  padding: 0 16px;
  -webkit-border-radius: 0px 6px 6px 0px;
  -moz-border-radius: 0px 6px 6px 0px;
  border-radius: 0px 6px 6px 0px;
}

#%(id)s table.table td.cell
{
  border: none;
}

#%(id)s table.table td.cell:hover
{
  color: #006699;
}

#%(id)s tr.even
{
}

#%(id)s .row
{
}

#%(id)s .row:hover
{
  background: #fafafa !important;
}

#%(id)s .row_selected
{
  background: #effdff !important;
}"""

    css = """
#%(id)s caption {
  font: 18px Arial;
  text-align: left;
  margin-bottom: 15px;
}

#%(id)s table.table {
  border-collapse: collapse;
  border: 1px solid #d4d4d4;
  height: 0;
}

#%(id)s .th-cell {
  height: 32px !important;
  background: #f5f5f5;
  text-align: left;
  padding-left: 10px;
  border-bottom: 2px solid #d4d4d4;
}

#%(id)s .thead {
  height: 32px !important;
  background: #f5f5f5;
}

#%(id)s table.table td.cell {
  height: 32px !important;
  text-align: left;
  padding-left: 10px;
}
#%(id)s tr.even {
  background: #f0f0f0;
}
#%(id)s .row {
  cursor: pointer;
}
#%(id)s .row_selected {
  background: #effdff !important;
}
"""
    pro_suite = """
#%(id)s table{
  height: 0 !important;
  border-collapse: collapse;
  border: none;
  margin-top: 10px;
}
#%(id)s caption{
  text-align: left;
  font-size: 18px;
  margin-bottom: 15px;
}
#%(id)s table .thead {
  background: #fff url("/168eab1b-d9e1-9d79-01ce-0211fc938fbf.png") bottom right repeat-x;
  border: none;
  border-top: 1px solid #ececec;
  border-bottom: 1px solid #ececec;
  -webkit-border-radius: 4px;
  -moz-border-radius: 4px;
  border-radius: 4px;
}
#%(id)s table .thead .th-cell {
  border: none;
  text-align:left;
}
#%(id)s table .thead .th-cell-0 {
  border: none;
  border-left:1px solid #ececec;
  -webkit-border-radius: 4px;
  -moz-border-radius: 4px;
  border-radius: 4px;
  width:32px;
}
#%(id)s table .thead .th-cell-2 {
  border: none;
  border-right:1px solid #ececec;
  border-radius: 4px;
  -moz-border-radius:4px;
  -webkit-border-radius: 4px;
}
#%(id)s table tr td{
  border: none;
  text-align: left;
  border-bottom: 1px dotted #bfbfbf;
  line-height: 27px;
}
"""

    users = """
#%(id)s .vdom_datatablev4 {

}
#%(id)s .vdom_datatablev4.multiselect.tristate div.tri {

}
#%(id)s input {

}
#%(id)s .vdom_datatablev4.multiselect.tristate div.tri em {

}
#%(id)s table{

}
#%(id)s caption{

}
#%(id)s table tr td {

}
"""

    empty = ""

    o = object

    skin_mapping = {"0": users, "1": css, "2": eof_style, "3": pro_suite, "4": empty}

    if "skin" in attributes:
        skin = attributes["skin"]

        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    modif = {}

    for attr in ["left", "width", "height", "top"]:
        if attr in attributes:
            attr_value = attributes[attr]
            obj_value = o.attributes.get(attr, "").lower()

            if obj_value.isdigit() and attr_value.isdigit():
                modif[attr] = attr_value + "px"
                modif["ide_" + attr] = attr_value
            elif obj_value.endswith("px") and (attr_value.isdigit() or "px" in attr_value):
                modif[attr] = attr_value.rstrip("px") + "px"
                modif["ide_" + attr] = attr_value.rstrip("px")
            elif attr_value.isdigit() or "px" in attr_value:
                modif[attr] = attr_value if "px" in attr_value else obj_value
                modif["ide_" + attr] = attr_value.rstrip("px")
            else:
                modif[attr] = attr_value
    attributes.update(modif)

    header1 = """[ "ID", "Name", "Price", "Author" ]"""

    arraydata = """\
[
    [1, "CF-Card", "123.12", "user1"], 
    [2, "VdomBox", "23.4", "user2"] 
]"""

    data_map = {"0": arraydata, "1": "", "2": header1}

    if "skindata" in attributes:
        skindata = attributes["skindata"]
        if skindata in ["0", "1"]:
            attributes.update(data=data_map[skindata], header=header1)
        else:
            attributes.update(data="", header="")

    if any(key in attributes for key in ["data", "header"]):
        if any(attributes.get(key) not in data_map.values() for key in ["data", "header"]):
            attributes.update(skindata="3")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")