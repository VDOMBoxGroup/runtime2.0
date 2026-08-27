import json


class VDOM_langsel(VDOM_object):
    def render(self, contents=""):
        if self.visible == "1":
            lang_display = self.lang_display.split(",")
            id = "o_" + (self.id).replace("-", "_")
            alt = """alt="{}" """.format(self.alt) if self.alt else ""
            style = "position: absolute; white-space:nowrap; z-index: " + self.zindex + "; top: " + self.top + "px; left: " + self.left + "px;"
            if len(lang_display) == 0 or len(self.lang_res) == 0:
                return ""

            try:
                lang_res = json.loads(self.lang_res)
            except Exception:
                return ""

            if self.layout == "1":
                htmlcode = '<select id="%s"><option disabled>Select your language</option>' % (id)

                for lang in lang_display:
                    key = lang.strip()
                    lang = lang_res[key][0] if key in lang_res.keys() else key
                    htmlcode += '<option value="%s">%s</option>' % (key, lang)

                htmlcode += "</select>"
                script = """<script type='text/javascript' charset="UTF-8">
                                jQuery(document).ready(function(){
                                    $('select#%s').change(function(){
                                        execEventBinded("%s", "select", {
                                            lang: $(this).val()
                                        });
                                    });
                                });
                            </script>""" % (id, id[2:])

            elif self.layout == "0":
                htmlcode = ""
                for lang in lang_display:
                    key = lang.strip()
                    img = lang_res[key][1] if key in lang_res.keys() else None

                    if img:
                        htmlcode += '<img style="margin-left:5px;" name="%s" src="/%s.png" %s/>' % (key, img, alt)

                    else:
                        htmlcode += '<span style="margin-left:5px;" name="%s">%s</span>' % (key, key)

                script = """<script type='text/javascript' charset="UTF-8">
                                jQuery(document).ready(function(){
                                    $('div#%s img').click(function(){
                                        execEventBinded("%s", "select", {
                                            lang: $(this).attr("name")
                                        });
                                    });
                                    $('div#%s span').click(function(){
                                        execEventBinded("%s", "select", {
                                            lang: $(this).attr("name")
                                        });
                                    });
                                });
                            </script>""" % (id, id[2:], id, id[2:])

            result = '<div id="%s" style="%s">%s</div>' % (id, style, htmlcode)
            result += script
            return result

        else:
            return ""

    def get_error_content(self, text):
        result = """<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" top="{top}" left="{left}">
                    <text top="0" left="5" color="#ff0000" textalign="left">{value}</text>
                </container>
            """.format(id=self.id, vis=self.visible, zind=self.zindex, hierarchy=self.hierarchy, top=self.top, left=self.left, value=text)

        return result

    def get_dropdown_rect(self, width, height):
        btn_width = 15
        btn_height = height
        btn_x = width - btn_width - 1
        btn_y = 0

        triangle_width = 5
        triangle_height = 4
        triangle_x = btn_x + (btn_width - triangle_width) / 2 + 1
        triangle_y = (btn_height - triangle_height) / 2

        color = "#000000"
        result = """<svg>
                    <rect y="0" x="0" width="{width}" height="{height}" fill="#FFFFFF" stroke="{color}"/>
                    <rect x="{btn_x}" y="{btn_y}" width="{btn_width}" height="{btn_height}" fill="#EEEEEE" stroke="{color}"/>
                    <polygon fill="{color}" stroke="{color}" points="{xa},{ya} {xb},{yb} {xc},{yc}"/>
                </svg>
            """.format(
            width=width,
            height=height,
            btn_x=btn_x,
            btn_y=btn_y,
            btn_width=btn_width,
            btn_height=btn_height,
            xa=triangle_x,
            ya=triangle_y,
            xb=triangle_x + triangle_width,
            yb=triangle_y,
            xc=triangle_x + triangle_width / 2,
            yc=triangle_y + triangle_height,
            color=color,
        )

        return result

    def get_max_text_len(self, lang_display, lang_res):
        cur_text = "Select your language"
        max_len = len(cur_text)

        for lang in lang_display:
            key = lang.strip()
            lang = lang_res[key][0] if key in lang_res.keys() else key

            if len(lang) > max_len:
                max_len = len(lang)

        return max_len

    def get_first_lang_value(self, lang_display, lang_res):
        lang = lang_display[0]
        key = lang.strip()
        lang = lang_res[key][0] if key in lang_res.keys() else key

        return lang

    def wysiwyg(self, contents=""):
        if not self.lang_display:
            return VDOM_object.wysiwyg(self, contents=self.get_error_content('Empty attribute "Display languages"'))

        if not self.lang_res:
            return VDOM_object.wysiwyg(self, contents=self.get_error_content('Empty attribute "Language resources"'))

        lang_display = self.lang_display.split(",")

        try:
            lang_res = json.loads(self.lang_res)
        except Exception:
            return VDOM_object.wysiwyg(self, contents=self.get_error_content("No JSON object could be decoded. Check syntax."))

        if len(lang_res) == 0:
            return VDOM_object.wysiwyg(self, contents=self.get_error_content('Empty attribute "Language resources"'))

        if self.layout == "1":  # List
            text_width = self.get_max_text_len(lang_display, lang_res) * 7 + 5
            width = text_width + 25
            height = 20

            result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" 
                                top="{top}" left="{left}" width="{width}" height="{height}">
                        {dropdown_rect}
                        <svg>
                            <text x="5" y="15" width="{text_width}" font-size="14" font-family="tahoma">{lang}</text>
                        </svg>
                    </container>
                """.format(
                id=self.id,
                vis=self.visible,
                name=self.name,
                zind=self.zindex,
                hierarchy=self.hierarchy,
                top=self.top,
                left=self.left,
                text_width=text_width,
                width=width,
                height=height,
                dropdown_rect=self.get_dropdown_rect(width, height),
                lang=self.get_first_lang_value(lang_display, lang_res),
            )

            return VDOM_object.wysiwyg(self, contents=result)

        elif self.layout == "0":  # Icon
            result = """<container name="{name}" id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" top="{top}" left="{left}" width="{width}" height="{height}">
                """.format(
                id=self.id,
                vis=self.visible,
                name=self.name,
                zind=self.zindex,
                hierarchy=self.hierarchy,
                top=self.top,
                left=self.left,
                width=5 + len(lang_display) * 21,
                height=17,
            )

            left = 0
            for key in lang_display:
                key = key.strip()
                res = lang_res[key] if key in lang_res.keys() else None

                if res:
                    img = """<svg>
                                <image href="#Res({image})" x="{x}" y="0" width="16" height="11"/>
                            </svg>
                        """.format(image=res[1], x=left)
                    left += 21
                else:
                    img = """<text top="0" left="{x}" width="30" color="#000000" textalign="center">
                                {value}
                            </text>
                        """.format(x=left, value=key)
                    left += 30

                result += img

            result += """</container>"""

        return VDOM_object.wysiwyg(self, contents=result)