import json


class VDOM_datatable_v3(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        idn = (self.id).replace("-", "_")
        id = "o_" + idn
        zindex = "z-index: %s;" % self.zindex if int(self.zindex) != 0 else ""
        display = "none" if self.visible == "0" else self.displaying
        position = self.positioning if self.positioning and self.positioning != "static" else ""

        styles = {
            "z-index": zindex,
            "display": display,
            "position": position,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        cssclasses = " ".join([param.strip() for param in [self.cssclass, "vdom_datatablev3"] if param.strip()])
        multiselect = "multiselect" if self.selectionmode == "1" else ""
        tristate = "tristate" if self.tristate == "1" else ""

        classes = [param for param in [cssclasses, multiselect, tristate] if param]

        cssclass = 'class="{}"'.format(" ".join(classes))

        if self.header:
            try:
                header = json.loads(self.header)
                if isinstance(header, int):
                    raise Exception("Incorrect value in header %s" % self.header)
            except Exception:
                raise Exception("Incorrect value in header %s" % self.header)
        else:
            header = []
        if self.data:
            try:
                src_data = json.loads(self.data)
                if isinstance(src_data, int):
                    raise Exception("Incorrect value in data %s" % self.data)
            except Exception:
                raise Exception("Incorrect value in data %s" % self.data)
        else:
            src_data = []

        try:
            key = json.loads(self.key)  # self.key if isinstance(self.key, str) else json.loads(self.key)
        except Exception:
            key = self.key

        if self.hiddenfields:
            try:
                hidden = json.loads(self.hiddenfields)
                if isinstance(hidden, int):
                    hidden = [hidden]
            except Exception:
                if self.hiddenfields in header:
                    hidden = [self.hiddenfields]
                else:
                    raise Exception("Incorrect value in hidden fields  %s" % self.hiddenfields)
        else:
            hidden = []

        data = []
        keys = []
        for value in src_data:
            if len(header) == len(value):
                if isinstance(value, list):
                    row = dict(zip(header, value))
                    data.append(row)
                    if key and key in header:
                        keys.append(row[key])
                else:
                    data.append(value)
                    if key and key in header:
                        keys.append(value[key])

        js_multiselect = ""
        js_singleselect = ""

        if self.selectedrows:
            try:
                selectedRows = json.loads("%s" % self.selectedrows)
                if isinstance(selectedRows, list):
                    js_multiselect = (
                        """
window.selectedRows_"""
                        + id
                        + """ = """
                        + json.dumps(selectedRows)
                        + """;
for (var j in window.selectedRows_"""
                        + id
                        + """){
    if (typeof(window.selectedRows_"""
                        + id
                        + """[j])=="string"){
        for (var i=0; i < window.keys_"""
                        + id
                        + """.length; i++){
            if (window.selectedRows_"""
                        + id
                        + """[j] == window.keys_"""
                        + id
                        + """[i]){
                $j("#"""
                        + id
                        + """ table tr").attr('index', function(index, attr){
                    if (attr == i+1){
                        $j(this).children("td").children("input").attr('checked', 'checked');
                        $j(this).addClass('row_selected');
                    }
                });
            }
        }
    }
    else if (typeof(window.selectedRows_"""
                        + id
                        + """[j])=="number"){
        $j("#"""
                        + id
                        + """ table tr").attr('index', function(index, attr){
            if (attr == window.selectedRows_"""
                        + id
                        + """[j]){
                $j(this).children("td").children("input").attr('checked', 'checked');
                $j(this).addClass('row_selected');
            }
        });
    }
}
"""
                    )

                    js_singleselect = (
                        """
window.selectedRows_"""
                        + id
                        + """ = """
                        + json.dumps(selectedRows)
                        + """;
for (var j in window.selectedRows_"""
                        + id
                        + """){
    if (typeof(window.selectedRows_"""
                        + id
                        + """[j])=="string"){
        for (var i=0; i < window.keys_"""
                        + id
                        + """.length; i++){
            if (window.selectedRows_"""
                        + id
                        + """[j] == window.keys_"""
                        + id
                        + """[i]){
                $j("#"""
                        + id
                        + """ table tr").attr('index', function(index, attr){
                    if (attr == i+1){
                        $j(this).addClass('row_selected');
                    }
                });
            }
        }
    }
    else if (typeof(window.selectedRows_"""
                        + id
                        + """[j])=="number"){
        $j("#"""
                        + id
                        + """ table tr").attr('index', function(index, attr){
            if (attr == window.selectedRows_"""
                        + id
                        + """[j]){
                $j(this).addClass('row_selected');
            }
        });
    }
}
"""
                    )

                # else:
                # raise Exception (u"Attribute must be list or dict (in tristate mode)")
                elif not isinstance(selectedRows, dict):
                    raise Exception("Attribute must be list or dict (in tristate mode)")

            except Exception:
                raise Exception("Incorrect value in selected rows")

        else:
            selectedRows = {} if self.tristate == "1" else []

        js_headerselect = (
            """
$j("#"""
            + id
            + """ table tr th:not([checkbox])").click(function(){
    var hname_"""
            + id
            + """ = $j(this).html();
    execEventBinded('"""
            + idn
            + """', "headerselected", {headername: hname_"""
            + id
            + """});
});
"""
        )
        js_multiselect += (
            """
window.selectionmode_"""
            + id
            + """ = 'multi';
window.tristate_"""
            + id
            + """ = """
            + ("true" if self.tristate == "1" else "false")
            + """;

/* click on checkbox in header */
$j("#"""
            + id
            + """ table tr th input:checkbox").click(function(){
    vdom_dtv3_triBoxClick(this);
    $j("#"""
            + id
            + """ table tr td input.ms").parent().find('em').hide(0);
    if (window.tristate_"""
            + id
            + """) {
        params_"""
            + id
            + """ = {};
        if (this.checked) {
            $j("#"""
            + id
            + """ table tr td input:checkbox").attr('checked', 'checked').parent().parent().addClass('row_selected').each(function(i, e){
                params_"""
            + id
            + """[window.keys_"""
            + id
            + """[i]] = "1";
            });
        } else {
            $j("#"""
            + id
            + """ table tr td input:checkbox").removeAttr('checked').parent().parent().removeClass('row_selected');
        }
        $j("#"""
            + id
            + """ table tr td input:checkbox").siblings('em').hide(0);
    } else {
        params_"""
            + id
            + """ = [];
        if (this.checked) {
            $j("#"""
            + id
            + """ table tr td input:checkbox").attr('checked', 'checked').parent().parent().addClass('row_selected').each(function(i, e){
                params_"""
            + id
            + """.push(window.keys_"""
            + id
            + """[i]);
            });
        } else {
            $j("#"""
            + id
            + """ table tr td input:checkbox").removeAttr('checked').parent().parent().removeClass('row_selected');
        }
    }
    if (window.tristate_"""
            + id
            + """) {
        execEventBinded('"""
            + idn
            + """', "rowsselected", {keyList: JSON.stringify(params_"""
            + id
            + """)});
    } else {
        execEventBinded('"""
            + idn
            + """', "rowsselected", {keyList: params_"""
            + id
            + """});
    }
});

/* click on ckeckbox in row */
$j("#"""
            + id
            + """ table tr td input:checkbox").click(function(){
    vdom_dtv3_triBoxClick(this);
    if (this.checked) {
        $j(this).parent().parent().addClass('row_selected');
    } else {
        $j(this).parent().parent().removeClass('row_selected');
    }
    if (window.tristate_"""
            + id
            + """) {
        params_"""
            + id
            + """ = {};
        $j("#"""
            + id
            + """ table tr td input:checkbox").each(function(i, e){
            if ($j(this).parent().find('em:visible').length > 0) {
                params_"""
            + id
            + """[window.keys_"""
            + id
            + """[i]] = "2";
            } else if (this.checked) {
                params_"""
            + id
            + """[window.keys_"""
            + id
            + """[i]] = "1";
            }
        });
        if ($j("#"""
            + id
            + """ table tr td input:checkbox").length == $j("#"""
            + id
            + """ table tr td input:checked").length) {
            $j("#"""
            + id
            + """ table tr th input:checkbox").attr('checked', 'checked');
        } else {
            $j("#"""
            + id
            + """ table tr th input:checkbox").removeAttr('checked');
        }
        /*$j("#"""
            + id
            + """ table tr th input:checkbox").siblings('em').hide(0);*/
    } else {
        params_"""
            + id
            + """ = [];
        $j("#"""
            + id
            + """ table tr td input:checkbox").each(function(i, e){
            if (this.checked) {
                params_"""
            + id
            + """.push(window.keys_"""
            + id
            + """[i]);
            }
        });
        if ($j("#"""
            + id
            + """ table tr td input:checkbox").length == $j("#"""
            + id
            + """ table tr td input:checked").length) {
            $j("#"""
            + id
            + """ table tr th input:checkbox").attr('checked', 'checked');
        } else {
            $j("#"""
            + id
            + """ table tr th input:checkbox").removeAttr('checked');
        }
    }
    if (window.tristate_"""
            + id
            + """) {
        execEventBinded('"""
            + idn
            + """', "rowsselected", {keyList: JSON.stringify(params_"""
            + id
            + """)});
    } else {
        execEventBinded('"""
            + idn
            + """', "rowsselected", {keyList: params_"""
            + id
            + """});
    }
});

if ($j("#"""
            + id
            + """ table tr td input:checkbox").length == $j("#"""
            + id
            + """ table tr td input:checked").length) {
    $j("#"""
            + id
            + """ table tr th input:checkbox").attr('checked', 'checked');
} else {
    $j("#"""
            + id
            + """ table tr th input:checkbox").removeAttr('checked');
}
"""
        )

        js_cellclick = (
            """

if (window.selectionmode_"""
            + id
            + """ === 'multi') {
    """
            + id
            + """_tds = $j("#"""
            + id
            + """:last table tr.row td:not(:nth-child(1))");
} else {
    """
            + id
            + """_tds = $j("#"""
            + id
            + """:last table tr.row td");
}
"""
            + id
            + """_doo = false;

$j("""
            + id
            + """_tds).bind('click dblclick', function(e){

    var t = $j(this);
    var cell_data = t.html(), cell_index = t.attr("index");
    var header_data = header_"""
            + id
            + """[cell_index - 1];
    var param = window.keys_"""
            + id
            + """[(t.parent().attr("index"))-1];
    params_"""
            + id
            + """[0] = window.keys_"""
            + id
            + """[(t.parent().attr("index"))-1];

    if (e.type == 'dblclick') {
        """
            + id
            + """_doo = false;

        /* double click */
        execEventBinded('"""
            + idn
            + """', "celldblclick", {keyField:param, cellData:cell_data, headerData:header_data});

    } else {
        if (typeof """
            + id
            + """_tout === 'undefined') {
            """
            + id
            + """_tout = setTimeout(function() {
                if ("""
            + id
            + """_doo == true) {

                    /* click */
                    if(window.selectionmode_"""
            + id
            + """ != 'multi'){
                        $j("#"""
            + id
            + """ table tr.row").removeClass('row_selected');
                        t.parent().addClass('row_selected');
                        if ("""
            + ("true" if self.tristate == "1" else "false")
            + """) {
                            execEventBinded('"""
            + idn
            + """', "rowsselected", {keyList: JSON.stringify(params_"""
            + id
            + """)});
                        } else {
                            execEventBinded('"""
            + idn
            + """', "rowsselected", {keyList: params_"""
            + id
            + """});
                        }
                    } else {
                        $j("#"""
            + id
            + """ table tr.row").removeClass('row_clicked');
                        t.parent().addClass('row_clicked');
                    }
                    execEventBinded('"""
            + idn
            + """', "cellclick", {keyField:param, cellData:cell_data, headerData:header_data});
                    $j("#"""
            + id
            + """ table tr.row").removeClass('active');
                    t.parent().addClass('active');
                }
                delete """
            + id
            + """_tout;
            }, 200);
        }
        """
            + id
            + """_doo = true;
    }

    return false;

});
"""
        )

        tdata = ""
        theader = ""
        vheader = [h for h in header if h not in hidden]
        nn = 1
        classfirst = "first"
        classlast = ""

        if vheader:
            theader = (
                '<tr header class="thead"><th checkbox class="th-cell th-cell-0"><div class="tri"><input id="{0}" type="checkbox" /><label for="{0}"></label><em></em></div></th>'.format(
                    str(id) + "tri"
                )
                if self.selectionmode == "1"
                else '<tr header class="thead">'
            )
            for index, colname in zip(range(len(vheader)), vheader):
                theader += '<th index="' + str(index + 1) + '" class="th-cell th-cell-' + str(index + 1) + '">' + str(colname) + "</th>"

            theader += "</tr>"

        lendata = len(data)
        for row_i, row in zip(range(lendata), data):
            if nn > 1:
                classfirst = ""
            if nn >= lendata:
                classlast = "last"
            nn += 1

            # if (row_i + 1) % 2:
            # tdata += u'<tr index="'+str(row_i+1)+'" class="row row-'+str(row_i+1)+' oddrow%(active)s '+classfirst+' '+classlast+'">' % {
            # "active": u" active" if self.rowactive and self.rowactive in keys and keys[row_i] == self.rowactive else u""
            # }
            # else:
            # tdata += u'<tr index="'+str(row_i+1)+'" class="row row-'+str(row_i+1)+' even%(active)s '+classfirst+' '+classlast+'">' % {
            # "active": u" active" if self.rowactive and self.rowactive in keys and keys[row_i] == self.rowactive else u""
            # }
            tdata += '<tr index="%(row)s" class="row row-%(row)s %(even)s %(active)s %(classfirst)s %(classlast)s">' % {
                "classfirst": classfirst,
                "classlast": classlast,
                "row": str(row_i + 1),
                "active": "active" if self.rowactive and self.rowactive in keys and keys[row_i] == self.rowactive else "",
                "even": "oddrow" if (row_i + 1) % 2 else "even",
            }

            if isinstance(selectedRows, dict) and self.tristate == "1" and self.selectionmode == "1":
                checked = ""
                visible = 'style="display:none"'
                for index in selectedRows:
                    if int(index) == int(keys[row_i]):
                        if int(selectedRows[index]) == 1:
                            checked = 'checked="checked"'
                        elif int(selectedRows[index]) == 2:
                            visible = ""

                tristate = '<div class="tri"><input type="checkbox" {checked} /><em {visible}></em></div>'.format(checked=checked, visible=visible)
            else:
                # tristate = u'<input type="checkbox" />'
                tristate = '<input id={0} type="checkbox" /><label for={0}></label>'.format(str(id) + str(row_i))

            # tdata += u'<td checkbox align="center" class="cell cell-0"><input type="checkbox" />%s</td>' % tristate if self.selectionmode == "1" else ""
            tdata += '<td checkbox align="center" class="cell cell-0">%s</td>' % tristate if self.selectionmode == "1" else ""
            if vheader:
                for index, col in zip(range(len(vheader)), vheader):
                    try:
                        tdata += (
                            '<td index="'
                            + str(index + 1)
                            + '" class="cell cell-'
                            + str(row_i + 1)
                            + "_"
                            + str(index + 1)
                            + " cell-"
                            + str(index + 1)
                            + '">'
                            + str(row[col])
                            + "</td>"
                        )
                    except Exception:
                        raise Exception("In row (%s) no column %s" % (json.dumps(row), col))
            else:
                for index, val in zip(range(len(row)), row):
                    tdata += '<td class="cell cell-' + str(index + 1) + '">' + str(val) + "</td>"
            tdata += "</tr>"

        if self.draggable == "1":
            js_drag = """
$j('#%(id)s tr').draggable({
    connectToDynatree: true
    ,appendTo: 'body'
    ,containment: 'document'
    ,zIndex: 99999
    ,opacity: 0.6
    ,helper: 'clone'
    ,option: 'accept'
    ,cursor: 'default'
    ,cursorAt: { left: -2, top: 4 }
    ,start: function(e,u){
        execEventBinded('%(idn)s', "dragstart", {itemid: u.helper.attr('index')});
    }
});
""" % {"id": id, "idn": idn}
        else:
            js_drag = ""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='%s' objname='%s' ver='%s'" % (self.type.name, self.name, self.type.version)
        else:
            debug_info = ""

        select = js_multiselect + js_cellclick if self.selectionmode == "1" else js_cellclick + js_singleselect

        result = """
<div %(debug_info)s id='%(id)s' style='%(style)s' %(cssclass)s>
    <style type="text/css">
        %(selfstyle)s
    </style>
    <table width="100%%" height="100%%" border="2" cellpadding="5" class="table">
        <caption>%(title)s</caption>
        %(theader)s
        <tbody>
            %(tdata)s
        </tbody>
    </table>
    <script type="text/javascript">
        $q(function(){
            var id_%(id)s = '%(id)s';
            window.keys_%(id)s = %(keys)s;
            window.header_%(id)s = %(vheader)s;
            var params_%(id)s = [];
            %(select)s
            %(js_headerselect)s
            %(js_drag)s
            execEventBinded('%(idn)s', 'load', {width:$q('#%(id)s').outerWidth(),height:$q('#%(id)s').outerHeight()});
        });
    </script>
</div>""" % {
            "keys": json.dumps(keys),
            "vheader": json.dumps(vheader),
            "debug_info": debug_info,
            "js_drag": js_drag,
            # "name":            self.name,
            "select": select,
            "js_headerselect": js_headerselect,
            "id": id,
            "idn": idn,
            "style": styles_str,
            "selfstyle": self.style % {"id": id},
            "cssclass": cssclass,
            "title": self.title,
            "theader": "<thead>%s</thead>" % theader if self.showheader == "1" else "",
            "tdata": tdata,
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
}"""

    # o = application.objects.search(object_id)
    o = object

    # set attributes

    # if "skin" in param:
    # 	if param["skin"]["value"] == "1":
    # 		o.set_attributes({"style": css})
    # 	elif param["skin"]["value"] == "2":
    # 		o.set_attributes({"style": eof_style})
    # 	elif param["skin"]["value"] == "3":
    # 		o.set_attributes({"style": pro_suite})
    # if "style" in param and param["style"]["value"] and o.attributes.style != css and o.attributes.style != eof_style and o.attributes.style != pro_suite:
    # 	o.set_attributes({"skin": 0})
    skin_mapping = {"0": users, "1": css, "2": eof_style, "3": pro_suite, "4": empty}
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