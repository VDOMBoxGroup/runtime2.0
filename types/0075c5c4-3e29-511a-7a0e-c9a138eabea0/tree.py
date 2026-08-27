from xml.dom.minidom import parseString


class VDOM_tree(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        zindex = "%s" % self.zindex if int(self.zindex) != 0 else ""
        woid = (self.id).replace("-", "_")
        id = "o_" + woid

        if self.visible == "1":
            visible = ""
        else:
            visible = "none"

        result = ""
        css = "<style>\n" + self.style % {"id": id} + "</style>" if self.style else ""
        position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""

        styles = {
            "z-index": zindex,
            "display": self.displaying,
            "visible": visible,
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

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='tree' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        result += """{css}\
      <div {debug_info} class='{classname} vdom_tree dynatreetype' style='{style}' id='{id}'> {contents} {data}""".format(
                style=styles_str, id=id, css=css, contents=contents, debug_info=debug_info, data=self.data, classname=self.classname
            )

        result_s = """</div>
<script type='text/javascript' charset="UTF-8">
function in_array(needle, haystack, strict) {
  var found = false, key, strict = !!strict;
  for (key in haystack) {
    if ((strict && haystack[key] === needle) || (!strict && haystack[key] == needle)) {
      found = true;
      break;
    }
  }
  return found;
}

jQuery(document).ready(function($){

  $q('#%(id)s').dynatree({
    title: %(title)s,
    checkbox: %(checkbox)s,
    keyboard: %(keyboard)s,
    autoCollapse: %(autoCollapse)s,
    children: %(children)s,
    selectMode: %(selectMode)s,
    fx: %(fx)s,
    generateIds: true,
    idPrefix: "dynatree-id-",
    //clickFolderMode: 2,
    debugLevel: 0,
    activeVisible: false,
    
    onActivate: function(node) {
      execEventBinded("%(woid)s", "activate", {
        title: node.data.title,
        key: node.data.key,
        isFolder: node.data.isFolder
      });
      execEventBinded("%(woid)s", "itemclick", {
        title: node.data.title,
        key: node.data.key,
        isFolder: node.data.isFolder
      });
    },
    onDeactivate: (node) => {
      execEventBinded("%(woid)s", "deactivate", {
        title: node.data.title,
        key: node.data.key,
        isFolder: node.data.isFolder
      });
    },
    onSelect: (flag, node) => {
      const keyList = [];
      $('#%(id)s').dynatree("getRoot").visit(function(node){
        if (node.isSelected()) keyList.push(node.data.key);
      });
      if (keyList.length === 0) {
        execEventBinded("%(woid)s", "unselectedall");
      } else {
        execEventBinded("%(woid)s", "select", {keyList});
      }
    },
    onExpand: (flag, node) => {
      if (typeof fixfooter !== 'undefined') fixfooter();
      execEventBinded("%(woid)s", "expand", {});
    },
    onLazyRead: (node) => {
      execEventBinded("%(woid)s", "lazyLoad", {nodeKey: node.data.key});
    }
    /*,dnd: {
      onDragStart: (node) => {
        // This function MUST be defined to enable dragging for the tree.
        // Return false to cancel dragging of node.
        //logMsg("tree.onDragStart(%(o)s)", node);
        if(node.data.isFolder)
          return false;
        return true;
      },
    }
    */
    ,dnd: {
      preventVoidMoves: false,
      onDragEnter: function(node, sourceNode) {
//console.info('onDragEnter');
        //return true;
        return "over";
      },
      onDragOver: function(node, sourceNode, hitMode) {
//console.info('onDragOver');
        return true;
      },
      onDragLeave: function(node, sourceNode) {
//console.info('onDragLeave');
      },
      onDrop: function(node, sourceNode, hitMode, ui, draggable) {
//console.info(ui);
        var ditem = '', dobj = '';
        if (ui.helper.context.attributes !== 'undefined') {
          if (in_array('objtype', ui.helper.context.attributes)) {
            if (ui.helper.context.attributes.objtype.value == 'vdomclass') {
              dobj = ui.helper.context.parentNode.id;
              ditem = ui.helper.context.attributes.dataid.value || '';
            }
          } else
          if (in_array('index', ui.helper.context.attributes)) {
            dobj = ui.helper.context.parentNode.parentNode.parentNode.id;
            ditem = ui.helper.context.attributes.index.value || '';
          }
        }
        execEventBinded('%(woid)s', "drop", {itemid: node.data.key});
/*
        var copynode;
        if(sourceNode) {
          copynode = sourceNode.toDict(true, function(dict){
            dict.title = "Copy of " + dict.title;
            delete dict.key; // Remove key, so a new one will be created
          });
        }else{
          copynode = {title: "This node was dropped here (" + ui.helper + ")."};
        }
        if(hitMode == "over"){
          // Append as child node
          node.addChild(copynode);
          // expand the drop target
          node.expand(true);
        }else if(hitMode == "before"){
          // Add before this, i.e. as child of current parent
          node.parent.addChild(copynode, node);
        }else if(hitMode == "after"){
          // Add after this, i.e. as child of current parent
          node.parent.addChild(copynode, node.getNextSibling());
        }
*/
      },
    }
  });

});
</script>""" % {
            "woid": woid,
            "id": id,
            "title": "false" if self.showtitle == "0" else '"%s"' % (self.title).replace('"', "&quot;"),
            "o": "%o",
            "checkbox": self.checkbox,
            "keyboard": self.keyboard,
            "autoCollapse": self.autoCollapse,
            "children": "null" if not self.initAjax else "%(initAjax)s" % {"initAjax": self.initAjax},
            "selectMode": self.selectMode,
            "fx": "null" if not self.fx else "%(fx)s" % {"fx": self.fx},
        }
        result += result_s
        return VDOM_object.render(self, contents=result)

    def __errorString(self, error):
        return """<p style="color:#ff0000;"><b>Error:</b> {err}</p>""".format(err=error)

    def __get_checkbox_node(self, doc, label="", checked=False):
        if not doc:
            return None

        node = doc.createElement("input")
        node.setAttribute("type", "checkbox")
        node.appendChild(doc.createTextNode(label))
        if checked:
            node.setAttribute("checked", "checked")

        return node

    def __parse_tree_data(self):
        if not self.data:
            return ""

        tree_data = ""
        try:
            tree_data = (self.data)#.encode("utf8")
            tree_data = "<htm style='font-size:12;'>{tree_data}</htm>".format(tree_data=tree_data)
            dom = parseString(tree_data)
        except Exception as err:
            return self.__errorString(str(err))

        # remove not expanded tags
        for element in dom.getElementsByTagName("li"):
            if not element:
                continue

            classes = element.getAttribute("class").split(" ")
            if "expanded" not in classes:
                for chld in element.childNodes:
                    if chld.nodeType == chld.ELEMENT_NODE:
                        chld.parentNode.removeChild(chld)

        # mark selected tags
        if self.checkbox == "1":
            for element in dom.getElementsByTagName("li"):
                text_node = element.childNodes[0] if len(element.childNodes) > 0 else None

                classes = element.getAttribute("class").split(" ")
                checked = "selected" in classes
                label = text_node.nodeValue if text_node else ""
                checkbox_node = self.__get_checkbox_node(dom, label, checked)

                if not checkbox_node:
                    continue

                if text_node:
                    element.replaceChild(checkbox_node, text_node)
                else:
                    element.appendChild(checkbox_node)

        return dom.toxml()

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value, get_centered_image_metrics

        image_id = "cbd47a55-cfad-bba6-e2a5-16f2a90371de"
        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        if len(self.initAjax) > 0:
            image_width = image_height = 50
            image_x = image_y = 0
            image_x, image_y, image_width, image_height = get_centered_image_metrics(image_width, image_height, int(self.width), int(self.height))

            text_tag = ""
            if int(self.height) > 20:
                text_tag = """<text top="{top}" left="0" width="{width}" textalign="right" color="#777777">initAjax</text>""".format(
                    top=int(self.height) - 20, width=self.width
                )

            result = """<container name="{name}" id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" top="{top}" left="{left}"
            width="{width}" height="{height}" backgroundcolor="#f0f0f0">
            <svg>
              <image x="{image_x}" y="{image_y}" href="#Res({image_id})" width="{image_width}" height="{image_height}"/>
            </svg>
            {text_tag}
          </container>
        """.format(
                id=self.id,
                zindex=self.zindex,
                hierarchy=self.hierarchy,
                name=self.name,
                top=self.top,
                left=self.left,
                width=self.width,
                height=self.height,
                image_x=image_x,
                image_y=image_y,
                image_id=image_id,
                image_width=image_width,
                image_height=image_height,
                text_tag=text_tag,
            )

            return VDOM_object.wysiwyg(self, contents=result)

        if not self.data:
            result = get_empty_wysiwyg_value(self, image_id)
            return VDOM_object.wysiwyg(self, contents=result)

        html_data = self.__parse_tree_data()

        result = """<container name="{name}" id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" 
            order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
          <htmltext left="2" top="2" width="{html_width}" height="{html_height}">
            {html_data}
          </htmltext>
        </container>
      """.format(
            id=self.id,
            zindex=self.zindex,
            name=self.name,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            html_width=int(self.width) - 4,
            html_height=int(self.height) - 4,
            html_data=html_data,
        )

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

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")