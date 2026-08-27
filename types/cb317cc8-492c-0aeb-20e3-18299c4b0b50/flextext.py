class VDOM_flextext(VDOM_object):
    def render(self, contents=""):
        # ------------------------------------------------------------------------------------------------------------------------------

        # Visible

        # if self.visible == "1":
        #     invisible = ""
        # else:
        #     invisible = "display:none;"

        # class

        if self.classname == "":
            classname = "class=' vdom_flextext ' "
        else:
            classname = " class='%s vdom_flextext ' " % (self.classname)
        the_value = self.value

        # ID

        id = "o_" + (self.id).replace("-", "_")

        # debug

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = "objtype='flextext' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = ""

        # oveerflow

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
            displaying = " display: block; "
        elif self.displaying == "2":
            displaying = " display: inline; "
        elif self.displaying == "3":
            displaying = " display: inline-block; "
        else:
            displaying = ""

        if self.visible == "0":
            displaying = " display: none; "

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

        style = """{display} {zind} {positioning} {width} {height} {coordinatess} {overflow} {margin} {padding} {floatt}""".format(
            display=displaying,
            zind=style_zindex,
            positioning=positioning,
            margin=margins,
            padding=paddings,
            width=superwidth,
            height=superheight,
            coordinatess=coordinates,
            floatt=float,
            overflow=overflow,
        )

        # ------------------------------------------------------------------------------------------------------------------------------
        result = '<div %s id="%s" style="%s" %s>%s</div>' % (debug_info, id, style, classname, the_value)

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        the_value = self.value

        empty_value = (
            """<svg>
                <text fill="#cccccc" x="7" y="13" >Text</text>
            </svg>
            """
            if the_value == ""
            else ""
        )

        color = """color="%s" """ % self.color if self.color != "" else ""

        cdata = "<![CDATA" + "[" + the_value + "]" + "]>"

        result = """<container id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}" order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                    <rect x="0" y="0" width="{width1}" height="{height1}" fill="" style="stroke-width:1; stroke:rgb(9,120,240)"/>
                    </svg>
                    {empty_value}
                    <htmltext top="{textTop}" left="{textLeft}" width="{width}" height="{height}" {color} editable="{value}">{cdata}</htmltext>
                    {contents}
                </container>""".format(
            id=self.id,
            visible=self.visible,
            zindex=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            width1=self.width,
            height1=self.height,
            empty_value=empty_value,
            textTop=0,
            textLeft=0,
            color=color,
            value="value",
            cdata=cdata,
            contents=contents,
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
            modifications.update(width=int(superheight[0 : superheight.find("px")]))

    attributes.update(modifications)
    return ""