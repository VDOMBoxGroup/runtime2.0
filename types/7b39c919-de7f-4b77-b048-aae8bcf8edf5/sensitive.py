from scripting import e2vdom


class VDOM_Sensitive(VDOM_object):
    def render(self, contents=""):
        e2vdom.process(self)
        display = "display:none" if self.visible != "1" else ""
        alt = """alt="{}" """.format(self.alt) if self.alt else ""
        target = ""
        if self.target:
            target = """ target="{target}" """.format(target=self.target)

        if self.link:
            link_render_1 = """<a href="{link}" {target}>""".format(link=self.link, target=target)
            link_render_2 = "</a>"
        elif self.containerlink:
            ref_obj = application.objects.search(self.containerlink)
            ref_page = "/{page_name}.vdom".format(page_name=ref_obj.name) if ref_obj else ""
            link_render_1 = """<a href="{page}" {target}>""".format(page=ref_page, target=target)
            link_render_2 = "</a>"
        else:
            link_render_1 = ""
            link_render_2 = ""

        link_image = (
            """<img style="width:{width}px; height:{height}px; border:none;" {alt} """
            """src="/7d0e6d03-2fc2-4e3d-9c6b-acab5c2e97d5.res" >""".format(width=self.width, height=self.height, alt=alt)
        )

        bw = 0
        if self.border != "0":
            bw = int(self.border)
            minsize = min(int(self.width), int(self.height))
            if bw > minsize / 2:
                bw = minsize / 2

        style = (
            """position: absolute; z-index: {zindex}; left: {left}px; top: {top}px; width: {width}px; """
            """height: {height}px; border:{bw}px solid black; overflow: hidden; {display} """.format(
                zindex=self.zindex,
                left=self.left,
                top=self.top,
                width=self.width,
                height=self.height,
                display=display,
                bw=str(bw),
            )
        )

        id = "o_" + (self.id).replace("-", "_")

        result = """<div id="{id}" style="{style}">{link}</div>""".format(id=id, style=style, link=link_render_1 + link_image + link_render_2)
        if contents:
            parse_style_int = lambda x: x + "px" if x.isdigit() else x
            styles = {
                "margin": self.margins,
                "display": "inline-block" if self.visible == "1" else "none",
                "z-index": self.zindex,
                "top": parse_style_int(self.top),
                "left": parse_style_int(self.left),
                "width": parse_style_int(self.superwidth),
                "height": parse_style_int(self.superheight),
                "position": {
                    "1": "absolute",
                    "2": "relative",
                    "3": "fixed",
                    "0": "static",
                }.get(self.positioning1, "static"),
            }
            result = """
                <div data-progress='0' class="%(css_class)s" id="%(id)s">%(contents)s</div>
                <script>
                    $(document).ready(() => {
                        window.sensetive_%(id)s = new SensetiveDragAndDropUploader("%(id)s", "%(drop_target)s", {
                            maxFileSizeKb: %(max_file_size_kb)s,
                            bannedExt: %(banned_ext)s,
                            disabled: %(disabled)s,
                        });
                    });
                </script>
                <style>
                    #%(id)s { %(styles)s }

                    #%(id)s.hover %(drop_target)s {
                        background: #ddd;
                        background-image: url(/91ba66a1-391a-4d95-8421-8aaa3a57e103.svg);
                        background-position: center center;
                        background-repeat: no-repeat;
                        background-size: clamp(30px, 1rem, 100px);
                        border-color: #aaa;
                    }
                </style>
            """ % {
                "contents": contents,
                "id": id,
                "drop_target": self.droptarget or "",
                "max_file_size_kb": self.maxfilesizekb or 0,
                "banned_ext": self.bannedext or "[]",
                "disabled": "true" if self.disabled == "1" else "false",
                "css_class": self.cssclass,
                "styles": ";".join(k + ":" + v for k, v in styles.items()),
            }

        return result

    def wysiwyg(self, contents=""):
        bw = 0
        s = ""
        if (self.border != "0") & (self.border != ""):
            bw = int(self.border)
            minsize = min(int(self.width), int(self.height))
            if bw > minsize / 2:
                bw = minsize / 2
            s = """ stroke="#000000" stroke-width="{bw}" """.format(bw=bw)

        result = """<container name="{name}" id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}" order="{order}"
                        top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect x="{x}" y="{y}" width="{rect_width}" height="{rect_height}" fill="#EEEEEE" fill-opacity=".4" {stroke}/>
                    </svg>
                    {contents}
                </container>
            """.format(
            id=self.id,
            visible=self.visible,
            zindex=self.zindex,
            hierarchy=self.hierarchy,
            order=self.order,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            x=bw / 2,
            y=bw / 2,
            rect_width=int(self.width) - bw,
            rect_height=int(self.height) - bw,
            stroke=s,
            contents=contents,
            name=self.name,
        )

        return VDOM_object.wysiwyg(self, contents=result)


def on_update(object, attributes):
    modifications = {}

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