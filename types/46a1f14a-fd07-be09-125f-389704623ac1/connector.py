import collections
import json
from scripting import e2vdom
import managers


class VDOM_connector(VDOM_object):
    def render_items(self, items):
        if not self.vdomclassid:
            return ""

        classname = self.classname or "conn"
        source_object = self.lookup(self.vdomclassid)
        parent_object = self.lookup(self.id)

        if not source_object:
            return "Invalid VDOM class"

        source_classname = source_object.attributes["classname"]
        source_width = source_object.attributes["width"]
        source_height = source_object.attributes["height"]

        last_index = len(items) - 1
        contents = []
        for index, (key, data) in enumerate(items.items()):
            copy = managers.engine.application.objects.new(source_object.type, name="vdomclass%d" % index, virtual=True, attributes=source_object.attributes)
            copy.objects.replicate(source_object.objects)
            copy.actions.replicate(source_object.actions)

            if self.lifetime == "1":
                managers.memory.track(copy, sync=managers.request_manager.current)
            elif self.lifetime == "2":
                managers.memory.track(copy, sync=managers.session_manager.current)

            classes = " ".join(
                filter(
                    None,
                    (
                        "%s-item" % classname,
                        "%s-item-%s" % (classname, index + 1),
                        "%s-item-first" % classname if index == 0 else None,
                        "%s-item-last" % classname if index == last_index else None,
                        "%s-item-odd" % classname if index % 2 else None,
                    ),
                )
            )
            copy.attributes.update(
                {
                    "data": json.dumps(data.get("data", "{}")),
                    "dataid": key,
                    "visible": "1",
                    "positioning": "1",
                    "top": str(data.get("y", "0")),
                    "left": str(data.get("x", "0")),
                    "width": source_width,
                    "height": source_height,
                    "classauto": classes,
                    "classname": source_classname,
                }
            )
            contents.append(managers.engine.render(copy, parent_object, "vdom"))

        return "".join(contents)

    def render(self, contents=""):
        woid = (self.id).replace("-", "_")
        id = "o_" + woid

        try:
            obj_data = json.loads(self.data, object_pairs_hook=collections.OrderedDict)
        except Exception:
            obj_data = {}

        if isinstance(obj_data, list):
            nod = {}
            for x in obj_data:
                nod[x] = {}
            obj_data = nod

        inner_render = self.render_items(obj_data)

        display = " display:none; " if self.visible == "0" else ""

        e2vdom.process(self, self.parent.id if self.parent else None)

        if self.overflow == "1":
            overflow = "hidden"
        elif self.overflow == "2":
            overflow = "scroll"
        elif self.overflow == "3":
            overflow = "visible"
        else:
            overflow = "auto"

        height = "height: %spx;" % self.height

        lines_color = "#%s" % self.linescolor
        lines_color_hover = "#%s" % self.linescolorhover
        lines_width = "%s" % int("0%s" % (self.lineswidth).strip())

        style = """{display} z-index: {zind}; position: absolute; top: {top}px; left: {left}px;
                width: {width}px; overflow: {overflow}; {height}""".format(
            display=display, zind=self.zindex, top=self.top, left=self.left, overflow=overflow, width=self.width, height=height
        )

        classname = """class="%s" """ % self.classname if self.classname else ""

        classname_item = "conn" if self.classname == "" else (self.classname).replace(" ", "").replace('"', "")

        endpoint_css_class = self.endpointcssclass.replace(" ", "").replace('"', "")
        endpoint_hover_css_class = self.endpointhovercssclass.replace(" ", "").replace('"', "")
        endpoint_type = self.endpointtype
        endpoint_size = self.endpointsize

        style_items = """
        <style type="text/css">
            #%(id)s .%(class)s-item {
                position: absolute !important;
            }
            #%(id)s ._jsPlumb_overlay {
                background: #fff;
                background: rgba(255, 255, 255, 0.8);
                padding: 1px 4px 3px;
            }
        </style>
            """ % {"id": id, "class": classname_item}

        # set sorced for connects drag

        connectorclass = "%s" % (self.connectorclass).replace('"', "").strip()

        if connectorclass == "":
            connectorclass_js = ""
        else:
            connectorclass_js = """
$("#%(id)s .%(connectorclass)s").each(function(i,e) {
    var p = $(e).parent();
    x.makeSource($(e), {
        parent: p,
        anchor: "Continuous",
        connector: [ "StateMachine", { curviness: 1 } ],//"Straight"
        connectorStyle: { strokeStyle: "%(lines_color)s", lineWidth: %(lines_width)s }
    });
});
            """ % {
                "id": id,
                "connectorclass": connectorclass,
                "lines_color": lines_color,
                "lines_width": lines_width,
            }
        """
        //anchor: "BottomCenter",
        maxConnections: 5,
        onMaxConnections: function(info, e) {
            //alert("Maximum connections (" + info.maxConnections + ") reached");
        }*/
        """

        # defined connects

        connects = ""

        try:
            connects_array = json.loads(self.defaultconnects)
        except Exception:
            connects_array = False
            print("[connector] ERROR parse defaultconnects JSON: %s" % self.defaultconnects)

        if isinstance(connects_array, list):
            for x in connects_array:
                lbl_tmp = "%s" % x.get("label", "").replace('"', "&quot;").strip()
                lbl = ""
                if lbl_tmp != "":
                    # lbl = u""",overlays:[["Label",{label:"%s"}]]""" % lbl_tmp
                    lbl = ',label:"%s"' % lbl_tmp

                clr_tmp = "%s" % x.get("color", "").replace('"', "").strip()
                clr = ""
                if clr_tmp != "":
                    clr = ',paintStyle:{strokeStyle:"%s"}' % clr_tmp

                # connects += u""" x.connect({source:"conn-%(source)s",target:"conn-%(target)s" %(label)s },ourConnector /*,%(skin)s*/); """ % {
                connects += """ x.connect({source:"conn-%(source)s",target:"conn-%(target)s" %(clr)s %(label)s},ourConnector); """ % {
                    "source": x.get("source", "").replace('"', "&quot;"),
                    "target": x.get("target", "").replace('"', "&quot;"),
                    "label": lbl,
                    "clr": clr,
                }

        if self.link_type == "0":
            link_type = "Straight"
        elif self.link_type == "1":
            link_type = "Flowchart"
        elif self.link_type == "2":
            link_type = "StateMachine"

        if self.draggable == "1":
            draggable = """
x.draggable(x.getSelector('#%(id)s div[dataid]'), {
    start: function(event) {
        //console.log("start  " + $(this).attr("dataid") + "  " + $(this).position().left + "  " + $(this).position().top);
        execEventBinded('%(woid)s', "itemDragStart", {"item_id": $(this).attr("dataid"), "x": $(this).position().left, "y": $(this).position().top}, true);
    },
    stop: function(event) {
        x.repaintEverything();
        execEventBinded('%(woid)s', "itemDragStop", {"item_id": $(this).attr("dataid"), "x": $(this).position().left, "y": $(this).position().top}, true);
    }
});
""" % {"id": id, "woid": woid}
        else:
            draggable = ""

        # main js

        js = """
<script type="text/javascript">
(function(){

    var ourConnector = {
        margin:          0,
        connector:       [ "%(link_type)s", { curviness: 1 } ],//"Straight",//"Flowchart",//"StateMachine"
        paintStyle:      { lineWidth: %(lines_width)s, strokeStyle: "%(lines_color)s" },
        hoverPaintStyle: { strokeStyle: "%(lines_color_hover)s" },
        endpoint:        "Blank",
        anchor:          "Continuous",
        overlays:        [ ["Arrow", { location: 1, width: 10, length: 15 } ] ]
    };

    $('#%(id)s div[dataid]').each(function(){
        $(this).attr('id', 'conn-' + $(this).attr('dataid'));
    });

    window.plumb_%(id)s = jsPlumb.getInstance();

    window.plumb_%(id)s.bind("ready", function() {

        var x = window.plumb_%(id)s;

        x.importDefaults({
            DragOptions: { cursor: "pointer", zIndex: 2000 },
            HoverClass: "connector-hover",
            LogEnabled: false,
            Endpoint: "Blank",
            PaintStyle:      { lineWidth: %(lines_width)s, strokeStyle: "%(lines_color)s" },
            HoverPaintStyle: { strokeStyle: "%(lines_color_hover)s" },
            ConnectionOverlays: [
                ["Arrow", { location: 1, width: 10, length: 15 } ]
            ]
        });

        x.endpointClass = "%(endpoint_css_clss)s";

        %(draggable)s

        document.onselectstart = function () { return false; }; // chrome fix

        %(defaultconnects)s

        x.bind("click", function(connection) {
            //x.detach(connection);
            execEventBinded('%(woid)s', "connectionClick", {"source": connection.sourceId, "target": connection.targetId}, true);
        });

        x.bind("dblclick", function(connection, originalEvent) {
            execEventBinded('%(woid)s', "connectionDblClick", {"source": connection.sourceId, "target": connection.targetId}, true);
        });

        %(connectorclass_js)s

        x.bind("connection", function(info) {
/*
            conn.connection.setPaintStyle({
                lineWidth: %(lines_width)s, strokeStyle: "%(lines_color)s"
            });
            conn.connection.getOverlay("label").setLabel(conn.connection.id);
            conn.connection.setConnector({
                paintStyle:      { lineWidth: %(lines_width)s, strokeStyle: "%(lines_color)s" },
                hoverPaintStyle: { strokeStyle: "%(lines_color_hover)s" },
                endpoint:        "Blank",
                anchor:          "Continuous",
                overlays:        [ ["PlainArrow", { location: 1, width: 10, length: 15 } ]]
            });
*/
            var conn = info.connection;
            var existing_connects_to_target = x.select({source:conn.sourceId,target:conn.targetId});
            var existing_connects_from_target = x.select({source:conn.targetId,target:conn.sourceId});
            if(existing_connects_to_target.length > 1 || existing_connects_from_target.length > 0 || conn.sourceId === conn.targetId) {
                conn.setDetachable();
                x.detach(conn, {
                    "forceDetach": true,
                });
                x.repaintEverything();
            }
            else {
                execEventBinded('%(woid)s', "connection", {"source": conn.sourceId, "target": conn.targetId}, true);
            }
        });

        x.bind("jsPlumbConnectionDetached", function(conn) {
            console.info('jsPlumbConnectionDetached');
            execEventBinded('%(woid)s', "connectionDetached", {"source": conn.sourceId, "target": conn.targetId}, true);
        });

        x.bind("connectionDrag", function(conn) {
            console.info('connectionDrag');
            execEventBinded('%(woid)s', "connectionDrag", {"source": conn.sourceId, "target": conn.targetId}, true);
        });

        x.bind("connectionDragStop", function(conn) {
            console.info('connectionDragStop');
            execEventBinded('%(woid)s', "connectionDragStop", {"source": conn.sourceId, "target": conn.targetId}, true);
        });

        x.bind("beforeDetach", function(conn) {
            execEventBinded('%(woid)s', "beforeDetach", {"source": conn.sourceId, "target": conn.targetId}, true);
        });

        x.makeTarget(x.getSelector(".%(class)s-item"), {
            anchor: "Continuous"
        });

        /*x.makeSource(x.getSelector(".%(class)s-item"), {
            connector: [ "%(link_type)s", { curviness: 1 } ],
            anchor: "Continuous"
        });*/

        x.addEndpoints(x.getSelector(".%(class)s-item"), [{
            isSource: true,
            isTarget: false,
            hoverClass: "%(endpoint_hover_css_clss)s",
            anchor: "TopCenter",
            maxConnections: 2,
            endpoint: ["%(endpoint_type)s", {radius: %(endpoint_size)s}],
            connector: [ "%(link_type)s", { curviness: 1 } ],
        }, {
            isSource: true,
            isTarget: false,
            hoverClass: "%(endpoint_hover_css_clss)s",
            anchor: "BottomCenter",
            maxConnections: 2,
            endpoint: ["%(endpoint_type)s", {radius: %(endpoint_size)s}],
            connector: [ "%(link_type)s", { curviness: 1 } ],
        }]);
        x.repaintEverything();

        $("#%(id)s div[dataid]").bind('click dblclick', function(e){
            if (e.preventDefault) e.preventDefault(); else e.returnValue = false;
            var t = $(this);
            if (e.type == 'dblclick') {
                t.data('doo', false);
                execEventBinded('%(woid)s', "itemdblclick", {"id":t.attr("dataid")});
                return false;
            } else {
                setTimeout(function() {
                    if (t.data('doo') == true) {
                        execEventBinded('%(woid)s', "itemclick", {"id":t.attr("dataid")});
                        return false;
                    }
                }, 220);
                t.data('doo', true);
            }
            return false;
        });

    });

})();
</script>""" % {
            "id": id,
            "woid": woid,
            "class": classname_item,
            "connectorclass_js": connectorclass_js,
            "defaultconnects": connects,
            "link_type": link_type,
            "lines_color": lines_color,
            "lines_color_hover": lines_color_hover,
            "lines_width": lines_width,
            "draggable": draggable,
            "endpoint_css_clss": endpoint_css_class,
            "endpoint_hover_css_clss": endpoint_hover_css_class,
            "endpoint_type": endpoint_type,
            "endpoint_size": endpoint_size,
        }

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='connector' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        result = """<div {debug_info} id="{id}" style="{style}" {classname}>
                    {style_items}
                    <div class='conn-content'>
                        {contents}
                        <span class='conn-eoi' style='display:block;clear:both'></span>
                    </div>
                </div>
                {js}""".format(
            js=js, id=id, debug_info=debug_info, style=style.strip(), style_items=style_items.strip(), classname=classname.strip(), contents=inner_render
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        html_items = ""
        if self.data != "":
            try:
                obj_data = json.loads(tuple(self.data), object_pairs_hook=collections.OrderedDict)
            except Exception:
                obj_data = {}
            nn = 0
            for key in obj_data:
                nn += 1
                item_data_id = key
                item_data = obj_data[key]
                b, tail = item_data[:0], item_data
                while len(tail) > 2:
                    b += tail[:2] + "&shy;"
                    tail = tail[2:]
                data = b + tail
                html_items += "<div><b>{nn}</b> <i>{id}</i><br />{data}</div>".format(nn=nn, id=item_data_id, data=data)

        html = """
        <style type="text/css">
        .conn_container {
            postition: relative;
            margin: 4px 4px 0 4px;
        }
            .conn_container div {
                background: #ddd;
                border: 1px solid #ccc;
                color: #777;
                float: left;
                font-size: 10px;
                height: 55px;
                overflow: hidden;
                margin: 0 1px 1px 0;
                padding: 1px;
                white-space: wrap;
            }
            .conn_container div b {
                font-color: #333;
            }
            .conn_container div i {
                color: #222;
                font-style: normal;
                font-size: 12px;
            }
        </style>
        <div class="conn_container">%(items)s</div>
        """ % {"items": html_items}

        html = "<![CDATA[" + html + "]]" + ">"

        result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                        top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect x="0" y="0" width="{width}" height="{height}" fill="#EEEEEE"/>
                    </svg>{contents}
                    <text textalign="right" fontweight="bold" top="{ttop}" left="{tleft}" color="#aaaaaa">Connector</text>
                    <htmltext top="2" left="2" width="{hwidth}" height="{hheight}">{html}</htmltext>
                </container>
            """.format(
            id=self.id,
            vis=self.visible,
            name=self.name,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            contents="",  # contents
            tleft=int(self.width) - 130,
            ttop=int(self.height) - 24,
            hwidth=int(self.width) - 8,
            hheight=int(self.height) - 24,
            html=html,
        )

        return VDOM_object.wysiwyg(self, contents=result)