from scripting.legacy.id import id2link1


class VDOM_cropper(VDOM_object):
    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        zindex = "%s" % self.zindex if int(self.zindex) != 0 else ""
        woid = (self.id).replace("-", "_")
        id = "o_" + woid
        css_scale = ""

        display = "none" if self.visible == "0" else self.displaying
        position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""

        styles = {
            "z-index": zindex,
            "display": display,
            "position": position,
            "top": self.check_unit(self.top),
            "left": self.check_unit(self.left),
            "width": self.check_unit(self.width),
            "height": self.check_unit(self.height),
        }
        if self.positioning == "static":
            styles["top"] = styles["left"] = ""

        styles_str = " ".join(["{}: {};".format(key, value) for key, value in styles.items() if value])

        hide_render = "hide" if self.hide_render == "1" else ""
        classname = " ".join([self.classname, "cropper_holder", hide_render]).strip()

        image_start = id2link1(self.value) if self.value else self.database64

        fill_container = "true" if self.fill_container == "1" else "false"

        if self.scale != "1":
            css_scale = """\
#%(id)s .cropper-container.cropper-bg { transform: scale(%(scale)s); }
        """ % {"id": id, "scale": self.scale}

        js = """
        <script type="text/javascript">
        $(document).ready(() => {
            let scale = %(scale)s;
            const cropperWidth = %(width)s * scale;
            const cropperHeight = %(height)s * scale;
            const imageStartData = "%(src)s";
            
            $('#%(id)s .cropper-wrapper').css({width: cropperWidth, height: cropperHeight});
            $('#%(id)s .preview-cropper').css({width: %(width)s, height: %(height)s});
             
            const container = $("#%(id)s .cropper-wrapper");
            $(container).MyImageCropper({
                uploadClass: "%(uploadclass)s",
                cropperWidth: %(width)s,
                cropperHeight: %(height)s,
                imgGuidName: '%(name_guid)s',
                imgUrlName: '%(name_url)s',
                imgData: imageStartData,
                fillContainerSize: %(fillContainer)s,
                hideOnRender: %(hide_render)s,
            });
        });	
</script>
""" % {
            "uploadclass": self.form_uploader_class,
            "id": id,
            "width": self.crop_width,
            "height": self.crop_height,
            "scale": self.scale,
            "name_guid": self.guid_image_field_name,
            "name_url": self.data_image_field_name,
            "src": image_start,
            "fillContainer": fill_container,
            "hide_render": "true" if self.hide_render == "1" else "false",
        }

        if self.preview_mode == "1":
            result = """
            <style>{css}{css_scale}</style>
            <div style="{styles}" id="{id}" class="{classname}" objname="{name}">
                <dialog class="cropper-modal-dialog dialog_cropper">
                    <div class="cropper-modal-wrapper">
                        <div class="title-bar">
                            <h2>Image editor</h2>
                            <a href='#' class='close_btn'></a>
                        </div>
                        <div class="cropper-content">
                            <div class="cropper-wrapper">
                                <img class="hide" tabindex="0" style="">
                            </div>
                            <div class="btn_wrapper">
                                <div class="control_btns">
                                    <button class="yes_btn">Save</button>
                                    <button class="no_btn">Cancel</button>
                                </div>
                                <div class="zoom_btns">
                                    <button class="plus_btn"></button>
                                    <button class="minus_btn"></button>
                                </div>
                            </div>
                        </div>
                    </div>
                </dialog>
                <div class="preview-cropper">
                    <img class="" tabindex="0">
                </div>
            </div>
            {js}
<script type="text/javascript">
    $('#{id} .preview-cropper').on('click', (event) => {{
                event.preventDefault();
                $("#{id} dialog")[0].showModal();
    }});
    
    $('#{id}').on('click', '.title-bar .close_btn, .btn_wrapper .yes_btn, .btn_wrapper .no_btn', (event) => {{
                event.preventDefault();
                $("#{id} dialog")[0].close();
    }});
</script>
            """.format(id=id, classname=classname, css=self.style % {"id": id}, styles=styles_str, js=js, css_scale=css_scale, name=self.name)
        else:
            result = """
            <style>{css}{css_scale}</style>
            <div style="{styles}" id="{id}" class="{classname}" objname="{name}">
                <div class="cropper-content">
                    <div class="cropper-wrapper">
                        <img class="hide" tabindex="0" style="">
                    </div>
                    <div class="btn_wrapper">
                        <div class="control_btns">
                            <button class="yes_btn">Save</button>
                            <button class="no_btn">Cancel</button>
                        </div>
                        <div class="zoom_btns">
                            <button class="plus_btn"></button>
                            <button class="minus_btn"></button>
                        </div>
                    </div>
                </div>
            </div>
            {js}
            """.format(id=id, classname=classname, css=self.style % {"id": id}, styles=styles_str, js=js, css_scale=css_scale, name=self.name)

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]
        image_id = "905dbdb8-e199-6069-34f6-c297723ed941"
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

    ff = """\
#%(id)s .preview-cropper {
  margin-bottom: 15px;
  border: 1px solid #b5c3cf !important;
  position: static !important;
  overflow: hidden !important;
  background-color: #f2f2f2;
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
  display: flex;
  justify-content: center;
  align-items: center;
}

#%(id)s .cropper_holder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

#%(id)s .cropper-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

#%(id)s .cropper-modal-dialog[open] {
  opacity: 1;
  pointer-events: inherit;
}

#%(id)s .cropper-modal-dialog {
  z-index: 10000 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: none;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s;
  padding: 0px;
}

#%(id)s .dialog_cropper::backdrop {
  background: rgba(47, 47, 47, 0.6);
}

#%(id)s .cropper-content {
  padding: 0px 50px 30px;
  display: flex;
  align-items: center;
  flex-direction: column;
}

#%(id)s .cropper-modal-dialog .cropper-wrapper {
  background-color: white;
  max-height: 100%%;
  overflow: hidden;
}

#%(id)s .cropper-content .btn_wrapper {
  margin: 20px 0px;
  display: flex;
  justify-content: space-between;
  width: 100%%;
}

#%(id)s .dialog_cropper .title-bar {
  position: relative;
  background-color: #fff !important;
  padding: 1px;
  font-size: 10px;
  text-align: center;
}

#%(id)s .dialog_cropper .title-bar h2 {
  color: #262626;
  font-size: 16px !important;
  padding: 30px 50px !important;
  padding-bottom: 15px !important;
  font-weight: 600;
  margin: 0px !important;
  text-align: left !important;
}

#%(id)s .dialog_cropper .title-bar a.close_btn {
  outline: none;
  background: url("") !important;
  font: 0 / 0 a;
  color: transparent;
  text-shadow: none;
  background-color: transparent !important;
  border: 0;
  display: block;
  position: absolute;
  right: 20px !important;
  top: 20px !important;
  width: 20px !important;
  height: 20px !important;
  margin: 0;
  padding: 0;
  z-index: 10000;
}

#%(id)s .dialog_cropper .title-bar a.close_btn:before {
  display: block;
  content: "";
  width: 1px;
  height: 100%%;
  background-color: #3e3e3e;
  position: absolute;
  right: 50%%;
  -webkit-transition: all 0.15s ease;
  transition: all 0.15s ease;
  -webkit-transform: rotate(-45deg);
  transform: rotate(-45deg);
}

#%(id)s .dialog_cropper .title-bar a.close_btn:after {
  display: block;
  content: "";
  width: 1px;
  height: 100%%;
  background-color: #3e3e3e;
  position: absolute;
  right: 50%%;
  -webkit-transition: all 0.15s ease;
  transition: all 0.15s ease;
  -webkit-transform: rotate(45deg);
  transform: rotate(45deg);
}

#%(id)s .dialog_cropper .title-bar a.close_btn:hover {
  border: 0px inset #999999 !important;
}

#%(id)s .dialog_cropper .title-bar a.close_btn:hover:before {
  -webkit-transform: rotate(-90deg);
  transform: rotate(-90eg);
  width: 2px !important;
}

#%(id)s .dialog_cropper .title-bar a.close_btn:hover:after {
  -webkit-transform: rotate(90deg);
  transform: rotate(90deg);
  width: 2px !important;
}

#%(id)s .btn_wrapper .yes_btn {
  position: static !important;
  display: inline !important;
  width: initial !important;
  text-align: center !important;
  margin-top: 0px;
  padding: 12px 20px;
  background: #262626;
  height: auto !important;
  border-radius: 5px;
  color: #fff !important;
  font-weight: 600;
  font-size: 13px !important;
  border: 0px;
  cursor: pointer;
  margin-right: 5px;
  opacity: 0.9;
}

#%(id)s .btn_wrapper .yes_btn:hover {
  opacity: 1;
}

#%(id)s .btn_wrapper .no_btn {
  position: static !important;
  display: inline !important;
  width: initial !important;
  text-align: center !important;
  margin-top: 0px;
  padding: 12px 20px;
  background: transparent;
  height: auto !important;
  border-radius: 5px;
  color: #262626 !important;
  font-weight: 600;
  font-size: 13px !important;
  border: 0px;
  cursor: pointer;
  margin-right: 5px;
}

#%(id)s .btn_wrapper .no_btn:hover {
  background-color: #f3f5f7 !important;
}

#%(id)s .btn_wrapper .plus_btn,
#%(id)s .btn_wrapper .minus_btn {
  position: static !important;
  display: inline !important;
  width: initial !important;
  text-align: center !important;
  margin-top: 0px;
  padding: 12px 20px;
  background: transparent;
  height: 39px !important;
  border-radius: 5px;
  color: #262626 !important;
  font-weight: 600;
  font-size: 13px !important;
  border: 0px;
  cursor: pointer;
  margin-right: 5px;
  background-repeat: no-repeat;
  background-position: 10px center;
}

#%(id)s .btn_wrapper .plus_btn {
  background-image: url(/fdbc57b2-2e93-1161-53cd-e198a01f3a26.svg);
}

#%(id)s .btn_wrapper .minus_btn {
  background-image: url(/e5b8c78f-c753-d954-4eeb-e198aa7e9e8a.svg);
}

#%(id)s .btn_wrapper .plus_btn:hover,
#%(id)s .minus_btn:hover {
  background-color: #F2F3F3;
}
"""

    users = """\
#%(id)s {

}
"""

    skin_mapping = {"0": empty, "1": ff, "2": users}
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="2")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="2")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")