import collections
import json
from scripting.legacy.id import id2link1


class VDOM_dropdown_menu(VDOM_object):
    def parse_property(self, pname, ptype, *args, **kwargs):
        prop = getattr(self, pname)
        if not prop:
            return ptype()

        try:
            value = json.loads(prop, *args, **kwargs)
        except Exception:
            if prop:
                raise Exception("Can't parse '%s'. It must be '%s'" % (pname, ptype.__name__))
            value = ptype()

        return value

    def check_unit(self, value):
        return value + "px" if value.isdigit() else value

    def render(self, contents=""):
        obj_id = self.id.replace("-", "_")

        zindex = "%s" % self.zindex if int(self.zindex) != 0 else ""
        display = "none" if self.visible == "0" else self.displaying
        position = "{pos}".format(pos=self.positioning) if self.positioning and self.positioning != "static" else ""

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

        result = []
        onclick = ""
        html_image = ""
        items = self.parse_property("data", dict, object_pairs_hook=collections.OrderedDict)

        if self.btn_image:
            alt = "alt='{}'".format(self.alt) if self.alt else ""
            html_image = "<img class='buttonIcon' src='{link}' {alt}>".format(link=id2link1(self.btn_image), alt=alt)
        elif self.button_svg:
            html_image = self.button_svg

        if self.show_clicked == "1":
            onclick = """
    $("#o_{id}").on("click", "ul li", function() {{
        var selectedItemHtml = $(this).html();
        $("#o_{id} .menuButton").html(selectedItemHtml);
        $(".menuList", "#o_{id}").addClass("hide");
        
        var dropdownMenu = $("#o_{id}");
        dropdownMenu.toggleClass('is-open');
    }});""".format(id=obj_id)

        usercss = "<style type='text/css'>"
        if self.style:
            usercss += self.style % {"id": "o_" + obj_id}
        usercss += "</style>"

        for key, value in items.items():
            result.append("""<li itemid="{key}" class="">{content}</li>""".format(key=key, content=value))

        output = """
{css}
<div id="o_{id}" name="{name}" objtype="dropdown_menu" style="{styles}" class="{css_class}">
    <div class="menuButton">
        {html_image}
        <span class="buttonLabel">{label}</span>
    </div>
    <ul class="menuList hide">{content}</ul>
</div>
<script>
$(document).ready(function() {{

    var selectedItem = $("#o_{id} ul li[itemid='{selected_id}']");
    let menuListTimer;
    const toggleMode = '{toggle_mode}';
    
    if (selectedItem.length > 0) {{
        selectedItem.addClass('active');
        $("#o_{id} .menuButton").html(selectedItem.html());
    }}
    
    $("#o_{id} .menuButton").on('click', function() {{
        var dropdownMenu = $(this).closest('.vdom_dropdown_menu');
        if (toggleMode === 'click') {{
            $(".menuList", dropdownMenu).toggleClass("hide");
            dropdownMenu.toggleClass('is-open');
        }}
    }});
    
    if (toggleMode === 'hover') {{
        $("#o_{id}").on('mouseenter', function() {{
            $(".menuList", this).removeClass("hide");
            $(this).addClass('is-open');
            clearTimeout(menuListTimer);
        }}).on('mouseleave', function(event) {{
            let self = this;
            menuListTimer = setTimeout(function() {{
                if (!$(self).is(':hover') && !$(".menuList", self).is(':hover')) {{
                    $(".menuList", self).addClass("hide");
                    $(self).removeClass('is-open');
                }}
            }}, 200);
        }});
        
        $(".menuList").on('mouseenter', function() {{
            clearTimeout(menuListTimer);
        }}).on('mouseleave', function(event) {{
            let self = this;
            let menuList = $(self);
            
            menuListTimer = setTimeout(function() {{
                if (!menuList.is(':hover') && !$("#o_{id}").is(':hover')) {{
                    $(self).addClass("hide").closest('#o_{id}').removeClass('is-open');
                }}
            }}, 200);
        }});
    }}
    
    {show_clicked}
    
    $(document).click(function(event) {{
        var dropdownMenu = $("#o_{id}");
        var target = $(event.target);
        if(!target.closest(dropdownMenu).length && !target.is(dropdownMenu)) {{
            $(".menuList", dropdownMenu).addClass("hide");
            dropdownMenu.removeClass('is-open');
        }}
    }});
    
    $("#o_{id}").dropdown_menu();
}});
</script>
""".format(
            content="".join(result),
            id=obj_id,
            name=self.name,
            label=self.btn_label,
            styles=styles_str,
            css_class=" ".join([self.classname, "vdom_dropdown_menu"]).strip(),
            css=usercss,
            html_image=html_image,
            show_clicked=onclick,
            toggle_mode=self.toggle_mode,
            selected_id=self.activeitem if self.activeitem else "",
        )

        contents += output

        return VDOM_object.render(self, contents=contents)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_empty_wysiwyg_value

        self.width, self.height, self.top, self.left = [int(self.ide_width), int(self.ide_height), int(self.ide_top), int(self.ide_left)]
        image_id = "8da56bee-32be-1c85-8d90-a81ab646275e"
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

    skin_mapping = {"0": "", "1": users}
    if "skin" in attributes:
        skin = attributes["skin"]
        if skin in skin_mapping:
            attributes.update(style=skin_mapping[skin])
        else:
            attributes.update(skin="0")

    if "style" in attributes and attributes.get("style") not in skin_mapping.values():
        attributes.update(skin="0")

    data_example = """\
{"item1": "value 1", "item2": "<p>Value 2</p>", "item3": "<div>Value3</div><img style='background-color: green; width: 40px; height: 40px;' src=''/>"}
"""

    data_map = {"data_ex": data_example, "empty": ""}

    if "skindata" in attributes:
        skindata = attributes["skindata"]
        if skindata == "1":
            attributes.update(data=data_example)
        else:
            attributes.update(data="")

    if "data" in attributes:
        if attributes.get("data") not in data_map.values():
            attributes.update(skindata="2")

    return ""


def on_compile(object, attributes):
    for attr in ["left", "width", "height", "top"]:
        obj_value = object.attributes[attr]

        if obj_value.isdigit() or "px" in obj_value:
            object.attributes[attr] = obj_value.rstrip("px") + "px"
            object.attributes["ide_" + attr] = obj_value.rstrip("px")