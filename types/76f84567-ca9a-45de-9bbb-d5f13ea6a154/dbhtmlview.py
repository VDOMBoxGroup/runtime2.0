class VDOM_dbhtmlview(VDOM_object):
    def contains_word(self, str, word):
        if (str.lower()).find(word.lower()) == -1:
            return False
        else:
            return True

    def get_html_data(self):
        data = ""
        try:
            from database.dbobject import VDOM_sql_query

            query = self.sqlquery
            if self.limit and not self.contains_word(query, "limit") and str(self.limit) != "":
                query += " LIMIT " + self.limit
            if self.offset and not self.contains_word(query, "offset"):
                query += " OFFSET " + self.offset

            table = VDOM_sql_query(application.id, self.database, query)
            data = ""
            if table:
                data = self.declaration
                import re

                rexp = re.compile(r"\$\((?P<Attribute>[\w-]+),(?P<Type>\d)\)", re.DOTALL)
                # for match in re.finditer(r"(?s)<!-- / -->(?P<RepeatArea>.*?)<!-- \\ -->", subject)
                match = re.search(r"<!-- / -->(?P<RepeatArea>.*?)<!-- \\ -->", data, re.DOTALL)

                repeat_area = match.group("RepeatArea")
                tag_list = []

                for match in rexp.finditer(repeat_area):
                    tag_list.append((match.group(), match.group("Attribute"), match.group("Type")))
                ready_area = ""
                for row in table.rows():
                    tmp_area = repeat_area
                    for tag, attr, type in tag_list:
                        if attr in table.headersindex:
                            val = row[table.headersindex[attr]]
                            if val is None:
                                val = ""
                            tmp_area = tmp_area.replace(tag, str(val))
                    ready_area += tmp_area
                data = data.replace(repeat_area, ready_area)
        except Exception as e:
            debug("DBHtmlView error:" + str(e))
        return data

    def render(self, contents=""):
        if self.visible == "1" and self.database and self.sqlquery:
            data = self.get_html_data()
            style = (
                "position: absolute; z-index: "
                + self.zindex
                + "; overflow: auto; top: "
                + self.top
                + "px; left: "
                + self.left
                + "px; width: "
                + self.width
                + "px; height: "
                + self.height
                + "px"
            )
            id = "o_" + (self.id).replace("-", "_")
            return '<div id="%s" style="%s">%s</div>' % (id, style, data)
        else:
            return ""

    # def wysiwyg(self, parent, contents=""):
    def wysiwyg(self, contents=""):
        representation = self.get_html_data()

        result = '<container id="%s" zindex="%s" hierarchy="%s" top="%s" left="%s" width="%s" height="%s">' % (
            self.id,
            self.zindex,
            self.hierarchy,
            self.top,
            self.left,
            self.width,
            self.height,
        )

        result += '<svg><rect x="%s" y="%s" width="%s" height="%s" fill="#FFFFFF" stroke="#000000"/></svg>' % (0, 0, int(self.width) - 1, int(self.height) - 1)

        if representation == "":
            text_size = 0
        else:
            text_size = int(self.width) - 2

        result += '<htmltext top="%s" left="%s" width="%s" height="%s">%s</htmltext>' % (
            0,
            0,
            text_size,
            int(self.height) - 2,
            "<![CD" + "ATA[" + representation + "]" + "]>",
        )

        result += "</container>"
        return VDOM_object.wysiwyg(self, contents=result)
        # return VDOM_object.wysiwyg(self, parent, contents=result)