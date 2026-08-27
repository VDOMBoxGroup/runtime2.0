from scripting import e2vdom, VDOM_object


class VDOM_dialog_3(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        idn = (self.id).replace("-", "_")
        id = "o_" + idn

        e2vdom.process(self)

        position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""

        styles = {
            "z-index": "%s" % self.zindex if int(self.zindex) != 0 else "",
            "display": self.displaying,
            "position": position,
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
            "margin": self.margins,
            "padding": self.paddings,
        }

        dialog_style = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        result = """<style type="text/css">%(css)s</style>""" % {"css": self.style} if self.style else ""

        # if self.draggable == "0":
        #     draggable = "true"
        # else:
        #     draggable = "false"

        if self.show == "1":
            show = "true"
        else:
            show = "false"

        if self.modal == "0":
            modal = "true"
        else:
            modal = "false"

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='%s' objname='%s' ver='%s'" % (self.type.name, self.name, self.type.version)
        else:
            debug_info = ""

        result += """			
        <div %(debug_info)s style='%(dialog_style)s' id='%(id)s' class='hide'>%(contents)s</div>
""" % {"debug_info": debug_info, "dialog_style": dialog_style, "id": id, "contents": contents}

        result += """<script type='text/javascript'>
(function(){
    if (typeof dialog_win_%(id)s !== 'undefined') {
        dialog_win_%(id)s.hide();
        delete(dialog_win_%(id)s);
    }
    dialog_win_%(id)s=new Popup($('#%(id)s'),{
        width: '%(width)s'
        ,height: '%(height)s'
        ,title: "%(title)s"
        ,closeText: ''
        ,show: %(show)s
        ,modal: %(modal)s
        ,fixed: false
        ,userclass: "%(classname)s"
        ,locationclass: "%(locationclass)s"
        ,background: "%(background)s"
        ,afterHide: function(){ 
            execEventBinded("%(idn)s", "hide", {});
            $('#ui-datepicker-div,#ColorDropdown_selector').fadeOut(); 
        }
        ,afterShow: function(){ 
            execEventBinded("%(idn)s", "show", {}); 
        }
    });
    $('.popup-modal-blackout').scroll(function(){
        $('#ui-datepicker-div').fadeOut(); 
        $('input.formcolorpicker').click(); 
        $('input[name^=formdate_]').focusout(); 
    });
    $('%(id)s .close-button').click(function() {
        dialog_win_%(id)s.hide();
    });
})();
</script>""" % {
            "id": id,
            "idn": idn,
            "width": self.width,
            "height": self.height,
            # "drag": draggable,
            "background": self.backgroundcolor,
            "locationclass": self.locationclass,
            "title": (self.title).replace('"', "&quot;"),
            "show": show,
            "modal": modal,
            "classname": (self.classname).replace('"', "&quot;"),
        }

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        width, height, top, left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]

        result = """<container name="{name}" id="{id}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" top="{top}" left="{left}" width="{container_width}" height="{container_height}">
                <svg>
                    <rect x="0" y="0" width="{width}" height="{height}" stroke="#cccccc" stroke-width="3" fill="#ffffff">
                        <rect x="0" y="0" width="{width}" height="40" fill="#e9e9e9"/>
                        <line x1="{line_x1}"  y1="16" x2="{line_x2}"   y2="24" style="stroke:#222222"/>
                        <line x1="{line_x1}"  y1="24" x2="{line_x2}"   y2="16" style="stroke:#222222"/>
                    </rect>
                </svg>
                <text top="10" width="{width}" fontsize="14" color="black" textalign="center">{title}</text>
                {contents}
            </container>""".format(
            id=self.id,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=top,
            left=left,
            container_width=width + 3,
            container_height=height + 3,
            width=width,
            height=height,
            title=self.title,
            contents=contents,
            line_x1=width - 20,
            line_x2=width - 12,
            name=self.name,
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

    users = """\
#%(id)s {

}
"""

    default = """\
.popup-modal-blackout {
    background: rgba(47, 47, 47, 0.6);
    top: 0px !important;
    width: 100%;
    height: 100%;
    position: fixed;
    overflow: hidden;
    z-index: 10000 !important;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper {
    background-color: white;
    max-height: 100%;
    max-width: 100%;
    overflow: auto; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    max-height: 100%; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .popup-content {
    overflow: auto; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .title-bar {
    position: relative;
    padding: 30px 25px 15px 50px;
    display: flex;
    align-items: center;
    flex-shrink: 0; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .title-bar h2 {
    color: inherit;
    font-size: 16px;
    font-weight: 600;
    margin: 0px auto 0px 0px; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .title-bar a.close {
    outline: none;
    background: url("") !important;
    font: 0 / 0 a;
    color: transparent;
    text-shadow: none;
    background-color: transparent;
    border: 0;
    display: block;
    position: relative;
    width: 20px !important;
    height: 20px !important;
    margin-left: 10px; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .title-bar a.close:before {
    display: block;
    content: "";
    width: 1px;
    height: 100%;
    background-color: #3e3e3e;
    position: absolute;
    right: 50%;
    -webkit-transition: all 0.15s ease;
    transition: all 0.15s ease;
    -webkit-transform: rotate(-45deg);
    transform: rotate(-45deg); }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .title-bar a.close:after {
    display: block;
    content: "";
    width: 1px;
    height: 100%;
    background-color: #3e3e3e;
    position: absolute;
    right: 50%;
    -webkit-transition: all 0.15s ease;
    transition: all 0.15s ease;
    -webkit-transform: rotate(45deg);
    transform: rotate(45deg); }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .title-bar a.close:hover {
    border: 0px inset #999999 !important; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .title-bar a.close:hover:before {
    -webkit-transform: rotate(-90deg);
    transform: rotate(-90deg);
    width: 2px !important; }
.popup-modal-blackout .vdom_dialog3.popup-wrapper .popup-inner .title-bar a.close:hover:after {
    -webkit-transform: rotate(90deg);
    transform: rotate(90deg);
    width: 2px !important; }
"""

    skin_mapping = {"0": users, "1": "", "2": default}
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