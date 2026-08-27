import utils
import json
from scripting import e2vdom
from uuid import UUID


def on_compile(application, object, action_name, context, objects):
    result = objects
    for xobject in object.get_objects_list():
        result.append({"object": xobject})
    return result


class VDOM_flexcontainer(VDOM_object):
    def render(self, contents=""):
        if self.securitycode:
            self.visible = "0"
            if session["SecurityCode"] and str(session["SecurityCode"]) in self.securitycode.split(";"):
                self.visible = "1"

        # display = " display: none; " if self.visible == "0" else ""

        e2vdom.process(self)

        if self.overflow == "1":
            overflow = "overflow: hidden;"
        elif self.overflow == "2":
            overflow = "overflow: scroll;"
        elif self.overflow == "3":
            overflow = "overflow: visible;"
        elif self.overflow == "0":
            overflow = "overflow: auto;"
        else:
            overflow = ""

        # Display

        if self.displaying == "1":
            display_style = "block"
            displaying = " display: block; "
        elif self.displaying == "2":
            display_style = "inline"
            displaying = " display: inline; "
        elif self.displaying == "3":
            display_style = "flex"
            displaying = " display: flex; "
        elif self.displaying == "4":
            display_style = "grid"
            displaying = " display: grid; "
        elif self.displaying == "5":
            display_style = "inline-block"
            displaying = " display: inline-block; "
        else:
            display_style = ""
            displaying = ""

        if self.visible == "0":
            displaying = " display: none; "

        # For Display: flex mode

        # Flex-warp
        if self.flexwrap == "1":
            flexwrap = " flex-wrap: wrap; "
        elif self.flexwrap == "0":
            flexwrap = " flex-wrap: nowrap; "
        else:
            flexwrap = ""

        # Justify-content
        if self.justifycontent == "0":
            justifycontent = " justify-content: center; "
        elif self.justifycontent == "1":
            justifycontent = " justify-content: flex-start; "
        elif self.justifycontent == "2":
            justifycontent = " justify-content: flex-end; "
        elif self.justifycontent == "3":
            justifycontent = " justify-content: space-between; "
        elif self.justifycontent == "4":
            justifycontent = " justify-content: space-around; "
        else:
            justifycontent = ""

        # Float
        if self.float == "0":
            float = ""
        elif self.float == "1":
            float = " float: left; "
        elif self.float == "2":
            float = " float: right; "
        elif self.float == "3":
            float = " float: both; "
        else:
            float = ""

        # flexdirection

        if self.flexdirection == "0":
            flexdirection = " flex-direction: row; "
        elif self.flexdirection == "1":
            flexdirection = " flex-direction: row-revers; "
        elif self.flexdirection == "2":
            flexdirection = " flex-direction: column; "
        elif self.flexdirection == "3":
            flexdirection = " flex-direction: column-revers; "
        else:
            flexdirection = ""

        # aligncontent
        if self.aligncontent == "2":
            aligncontent = " align-content: center; "
        elif self.aligncontent == "0":
            aligncontent = " align-content: flex-start; "
        elif self.aligncontent == "1":
            aligncontent = " align-content: flex-end; "
        elif self.aligncontent == "3":
            aligncontent = " align-content: space-between; "
        elif self.aligncontent == "4":
            aligncontent = " align-content: space-around; "
        elif self.aligncontent == "5":
            aligncontent = " align-content: stretch; "
        else:
            aligncontent = ""

        # alignitems
        if self.alignitems == "0":
            alignitems = " align-items: flex-start; "
        elif self.alignitems == "1":
            alignitems = " align-items: flex-end; "
        elif self.alignitems == "2":
            alignitems = " align-items: center; "
        elif self.alignitems == "3":
            alignitems = " align-items: baseline; "
        elif self.alignitems == "4":
            alignitems = " align-items: stretch; "
        else:
            alignitems = ""

        # alignself
        if self.alignself == "0":
            alignself = " align-self: flex-start; "
        elif self.alignself == "1":
            alignself = " align-self: flex-end; "
        elif self.alignself == "2":
            alignself = " align-self: center; "
        elif self.alignself == "3":
            alignself = " align-self: baseline; "
        elif self.alignself == "4":
            alignself = " align-self: stretch; "
        else:
            alignself = ""

        # orderchild
        orderchild = ""
        if self.orderchild != "":
            orderchild = """ order: {order}; """.format(order=self.orderchild)

        # flexgrow
        flexgrow = ""
        if self.flexgrow != "":
            flexgrow = """ flex-grow: {flexgroww}; """.format(flexgroww=self.flexgrow)

        # flexbasis
        flexbasis = ""
        if self.flexbasis != "":
            flexbasis = """ flex-basis: {flexbasiss}; """.format(flexbasiss=self.flexbasis)

        # flexshrink
        flexshrink = ""
        if self.flexshrink != "":
            flexshrink = """ flex-shrink: {flexshrinkk}; """.format(flexshrinkk=self.flexshrink)

        # Background

        if self.backgroundmode == "0":
            backgroundmode = ""
        elif self.backgroundmode == "1":
            backgroundmode = "background-attachment: scroll; background-size:100% auto; background-position: top center; background-repeat: no-repeat; "
        elif self.backgroundmode == "2":
            backgroundmode = "background-attachment: scroll; background-size:auto 100%; background-position: top center; background-repeat: no-repeat; "
        elif self.backgroundmode == "3":
            backgroundmode = "background-attachment: scroll; background-size:cover;  background-repeat: no-repeat; "
        elif self.backgroundmode == "4":
            backgroundmode = "background-attachment: scroll; background-size:contain; background-repeat: no-repeat; "
        elif self.backgroundmode == "5":
            backgroundmode = "background-attachment: scroll; background-position: top left; background-repeat: repeat-x; "
        elif self.backgroundmode == "6":
            backgroundmode = "background-attachment: scroll; background-position: top left; background-repeat: repeat-y; "
        elif self.backgroundmode == "7":
            backgroundmode = "background-attachment: scroll; background-position: top left; background-repeat: repeat; "
        elif self.backgroundmode == "8":
            backgroundmode = "background-attachment: fixed; background-size:cover;  background-repeat: no-repeat; "
        elif self.backgroundmode == "9":
            backgroundmode = "background-position: center; background-repeat: no-repeat; "
        else:
            backgroundmode = ""

        background_color = "background-color: #%s;" % self.backgroundcolor if self.backgroundcolor != "" else ""
        if self.backgroundimage:
            try:
                UUID(self.backgroundimage, version=4)
                background_image = "background-image: url('%s');" % utils.id.id2link1(self.backgroundimage)
            except ValueError:
                background_image = "background-image: url('%s');" % self.backgroundimage
        else:
            background_image = ""

        if self.backgroundposition != "":
            backgroundposition = """ background-position:{backgroundposition};""".format(backgroundposition=self.backgroundposition)
        else:
            backgroundposition = ""

        # if self.backgroundrepeat == '1':
        # background_repeat = 'background-repeat:no-repeat;'
        # elif self.backgroundrepeat == '2':
        # background_repeat = 'background-repeat:repeat-x;'
        # elif self.backgroundrepeat == '3':
        # background_repeat = 'background-repeat:repeat-y;'
        # else:
        # background_repeat = u''

        # Layers and Order

        style_zindex = "z-index:%s;" % self.zindex if int(self.zindex) != 0 else ""

        # Coordinates
        # Left
        if self.superleft == "auto":
            left_coord = " left: auto; "
        elif self.superleft == "":
            left_coord = ""
        else:
            left_coord = """ left: {left}; """.format(left=self.superleft)
        # Top
        if self.supertop == "auto":
            top_coord = " top: auto; "
        elif self.supertop == "":
            top_coord = ""
        else:
            top_coord = """ top: {top}; """.format(top=self.supertop)
        # Right
        if self.right == "auto":
            right_coord = " right: auto; "
        elif self.right == "":
            right_coord = ""
        else:
            right_coord = """ right: {right}; """.format(right=self.right)
        # Bottom
        if self.bottom == "auto":
            bottom_coord = " bottom: auto; "
        elif self.bottom == "":
            bottom_coord = ""
        else:
            bottom_coord = """ bottom: {bottom}; """.format(bottom=self.bottom)

        if self.positioning1 == "2":
            if self.superleft != "":
                left_coord = """ left: {left}; """.format(left=self.superleft)
            else:
                left_coord = ""
            if self.supertop != "":
                top_coord = """ top: {top}; """.format(top=self.supertop)
            else:
                top_coord = ""
        elif self.positioning1 == "0":
            left_coord = ""
            top_coord = ""

        coordinates = """ {top} {left} {right} {bottom} """.format(top=top_coord, left=left_coord, bottom=bottom_coord, right=right_coord)

        # width and height

        if self.superwidth != "":
            superwidth = """ width:{width};""".format(width=self.superwidth)
        else:
            superwidth = ""
        if self.superheight != "":
            superheight = """ height:{height};""".format(height=self.superheight)
        else:
            superheight = ""

        # Positioning mode

        if self.positioning1 == "0":
            positioning = ""
        elif self.positioning1 == "1":
            positioning = " position: absolute; "
        elif self.positioning1 == "2":
            positioning = " position: relative; "
        elif self.positioning1 == "3":
            positioning = " position: fixed; "
        else:
            positioning = ""

        # Margings

        if self.margins == "":
            margins = ""
        else:
            margins = """ margin: {margin}; """.format(margin=self.margins)
        # Paddings

        if self.paddings == "":
            paddings = ""
        else:
            paddings = """ padding: {padding}; """.format(padding=self.paddings)

        # Compound style

        defaultstyle = """{display} {zind} {positioning} {width} {height} {coordinatess} {overflow} {margin} {padding} {background_color} {floatt} {backgroundmodee} {background_image} {backgroundpositions}""".format(
            display=displaying,
            zind=style_zindex,
            background_color=background_color,
            background_image=background_image,
            positioning=positioning,
            margin=margins,
            padding=paddings,
            width=superwidth,
            height=superheight,
            coordinatess=coordinates,
            floatt=float,
            overflow=overflow,
            backgroundmodee=backgroundmode,
            backgroundpositions=backgroundposition,
        )

        flexstyle = """ {justy} {aligncon} {flexwrapp}  {flexbas} {orderchildd} {flexdir} {alignselff} {flexgroww} {alignitemss} {flexshrinkk} """.format(
            justy=justifycontent,
            flexgroww=flexgrow,
            flexshrinkk=flexshrink,
            flexbas=flexbasis,
            orderchildd=orderchild,
            alignselff=alignself,
            flexwrapp=flexwrap,
            flexdir=flexdirection,
            alignitemss=alignitems,
            aligncon=aligncontent,
        )

        style = defaultstyle + flexstyle

        id = "o_" + (self.id).replace("-", "_")
        footer = """rel="footer" """ if self.footer == "1" else ""
        classname = " ".join([self.classname, "vdom_flexcontainer"]).strip()

        custom_attributes = ""
        custom_attr_json = json.loads(self.custom_attributes) if self.custom_attributes else ""
        if custom_attr_json:
            custom_attributes = " ".join(['{}="{}"'.format(key, value) for key, value in custom_attr_json.items()])

        if self.titlewrap == "0":
            title_tag = ""
            cont_tag = "%s" % contents
        else:
            title_tag = """<div class="title"><div><h{twrap}>{title}</h{twrap}></div></div>""".format(twrap=self.titlewrap, title=self.title)
            cont_tag = """<div class="content">%s</div>""" % contents

        css = "<style>\n" + (self.style % {"id": id}) + "</style>" if self.style else ""

        debug_info = ""
        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='container' objname='%s'" % (self.name)

        result = """{css}
                 <{wrap} {debug_info} {footer} data-display='{display_style}' id="{id}" style="{style}" class="{classname}" {custom_attr}>{title_tag}{cont_tag}</{wrap}>""".format(
            debug_info=debug_info,
            footer=footer,
            id=id,
            style=style,
            classname=classname,
            custom_attr=custom_attributes,
            css=css,
            title_tag=title_tag,
            cont_tag=cont_tag,
            display_style=display_style,
            wrap=self.render_mode,
        )

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.legacy.wysiwyg import get_centered_image_metrics

        colorNumber = self.backgroundcolor if self.backgroundcolor != "" else self.designcolor
        colorValue = "#" + colorNumber if colorNumber != "" else "none"

        # title
        title_text = ""
        if self.title != "" and self.titlewrap != "0":
            title_text = """<text x="5" y="14" fill="#000000" font-size="14" width="{width}">{title}</text>
                                """.format(title=self.title, width=self.width)

        # show icon if container is empty
        empty_container_image = ""
        if len(contents) == 0 and self.backgroundimage == "":
            image_id = "88746dc1-2404-e1bd-7ced-c746075863cf"
            image_width = image_height = 50

            image_x, image_y, image_width, image_height = get_centered_image_metrics(image_width, image_height, int(self.width), int(self.height))

            empty_container_image = """<image href="#Res({image_id})" x="{image_x}" y="{image_y}"
                                                        width="{image_width}" height="{image_height}" />
                                        """.format(image_id=image_id, image_width=image_width, image_height=image_height, image_x=image_x, image_y=image_y)

        bg_image = ""
        if self.backgroundmode != "":
            if self.backgroundmode == "7":
                bg_image_repeat = "repeat"
            elif self.backgroundmode == "8":
                bg_image_repeat = "no-repeat"
            elif self.backgroundmode == "5":
                bg_image_repeat = "repeat-x"
            elif self.backgroundmode == "6":
                bg_image_repeat = "repeat-y"
            else:
                bg_image_repeat = ""

            bg_image = """<image href="#Res({backgroundimage})" x="0" y="0" repeat="{repeat}" containerWidth="{containerWidth}"
                        containerHeight="{containerHeight}" />
                """.format(backgroundimage=self.backgroundimage, repeat=bg_image_repeat, containerWidth=self.width, containerHeight=self.height)

        # get overflow value
        overflow_dict = {"0": "auto", "1": "hidden", "2": "scroll", "3": "visible", "4": ""}
        overflow_num = self.overflow if self.overflow else "0"
        overflow = overflow_dict[overflow_num]

        result = """<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}" overflow="{overflow}">
                    <svg>
                        <rect x="0" y="0" width="{width}" height="{height}" fill="{colorValue}" style="stroke-width:1; stroke:rgb(9,120,240)"/>
                        {empty_container_image}
                        {bg_image}
                        {title_text}
                    </svg>{contents}
                </container>""".format(
            id=self.id,
            vis=self.visible,
            zind=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            colorValue=colorValue,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            contents=contents,
            title_text=title_text,
            empty_container_image=empty_container_image,
            bg_image=bg_image,
            overflow=overflow,
        )

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    if (
        object.parent
        and object.parent.type.class_name == "VDOM_tabview"
        and object.attributes["lockposition"] == "1"
        and int(object.attributes["top"]) != 20
        and int(object.attributes["left"]) != 1
    ):
        attributes.update(left="1", top="20")

    modifications = {}

    # Left
    if "left" in attributes:
        if "px" in object.attributes.get("superleft", "").lower():
            newleft = str(attributes["left"]) + "px"
            modifications.update(superleft=newleft)

    if "superleft" in attributes:
        superleft = attributes["superleft"]
        if "px" in superleft.lower():
            modifications.update(left=int(superleft[0 : superleft.find("px")]))

    # top
    if "top" in attributes:
        if "px" in object.attributes.get("supertop", "").lower():
            newtop = str(attributes["top"]) + "px"
            modifications.update(supertop=newtop)

    if "supertop" in attributes:
        supertop = attributes["supertop"]
        if "px" in supertop.lower():
            modifications.update(top=int(supertop[0 : supertop.find("px")]))

    # width
    if "width" in attributes:
        if "px" in object.attributes.get("superwidth", "").lower():
            newwidth = str(attributes["width"]) + "px"
            modifications.update(superwidth=newwidth)

    if "superwidth" in attributes:
        superwidth = attributes["superwidth"]
        if "px" in superwidth.lower():
            modifications.update(width=int(superwidth[0 : superwidth.find("px")]))

    # height
    if "height" in attributes:
        if "px" in object.attributes.get("superheight", "").lower():
            newheight = str(attributes["height"]) + "px"
            modifications.update(superheight=newheight)

    if "superheight" in attributes:
        superheight = attributes["superheight"]
        if "px" in superheight.lower():
            modifications.update(height=int(superheight[0 : superheight.find("px")]))
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