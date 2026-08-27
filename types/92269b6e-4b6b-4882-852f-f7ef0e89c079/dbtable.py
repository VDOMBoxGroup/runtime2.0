import managers


class VDOM_dbtable(VDOM_object):
    def compute(self):
        self.structure = "not modified"
        self.data = "not modified"
        # database_manager = obsolete_request.database_manager
        database_manager = managers.database_manager
        parent_obj = application.objects.search(self.id).parent
        database_id = parent_obj.id
        db = database_manager.get_database(application.id, database_id)
        if db:
            table = db.get_table(self.id, self.name)
            if self.name != table.name:
                table.rename(self.name)
                database_manager.save_index()
            # try:

            # if not self.structure or self.structure == "":
            # self.structure = table.get_structure()
            # else:
            # self.structure = table.update_structure(self.structure)
            # except Exception as e:
            # debug("Getting structure error!")
            # debug(str(e))
            # try:
            # self.data = "not modified"
            # if not self.data or self.data == "":
            # self.data = table.get_data_xml()
            # else:
            # self.data = table.update_data(self.data)
            # from src.database.dbobject import VDOM_sql_query
            # query = VDOM_sql_query(application.id, database_id, "select * from %s"%self.name)
            # self.data = str(query.fetchall_xml())
            # del(query)
            # except Exception as e:
            # debug("Getting data error!")
            # debug(str(e))

    def render(self, contents=""):
        return VDOM_object.render(self, contents=contents)

    def wysiwyg(self, contents=""):
        result = ""
        # try:
        from xml.dom.minidom import parseString

        # table = get_table(application.id,self.id)
        table = get_table(application.objects.search(self.id))

        structure = table.get_structure()
        dom3 = parseString(structure.encode("UTF-8"))
        res = dom3.getElementsByTagName("column")

        result = ""
        result += '<container name="%s" id="%s" zindex="%s" hierarchy="%s" top="%s" left="%s" width="%s" height="%s">' % (
            self.name,
            self.id,
            self.zindex,
            self.hierarchy,
            self.top,
            self.left,
            int(self.width),
            self.height,
        )

        result += (
            "<svg>"
            '<rect x="%s" y="%s" width="%s" height="%s" fill = "#E6E6E6" stroke="#000000" stroke-width="2" />'
            '<rect x="%s" y="%s" width="%s" height="%s" fill = "#9691F9"/>'
            '<rect x="%s" y="%s" width="%s" height="%s" fill = "#E6E6E6" stroke="#000000" stroke-width="2"/>'
            "</svg>"
            % (2, 0, int(self.width) - 3, int(self.height) - 2, 3, 1, str(int(self.width) - 5), 24, 2, 24, str(int(self.width) - 3), str(int(self.height) - 26))
        )

        result += '<text top="2" left="3" width="%s" height="20" fontweight="bold" fontfamily="Tahoma" fontsize="13" textalign="center">%s</text>' % (
            str(int(self.width) - 8),
            self.name[:25],
        )

        if len(res) > 0:
            result += '<table top="%s" left="%s" height="%s">' % (26, 2, str(int(self.height) - 28))

            for column in res:
                result += '<row height="18">'

                try:
                    if column.attributes["primary"].value == "true":
                        font = """ fontweight="bold" fontsize="11" """
                        shift = 7
                    else:
                        font = """ fontsize="11" """
                        shift = 5
                except Exception:
                    font = """ fontsize="11" """
                    shift = 5

                try:
                    type = "[ " + column.attributes["type"].value + " ]"
                except Exception:
                    type = ""

                result += (
                    "<cell>"
                    '<text top="0" left="3" height="%s" %s>%s</text>'
                    "</cell>"
                    "<cell>"
                    '<text top="0" left="0" height="%s" fontsize="9">%s</text>'
                    "</cell>"
                    % (str(int(self.height) / 2 - 4), font, "<![CDATA[ " + column.attributes["name"].value + "]" + "]>", str(int(self.height) / 2 - 4), type)
                )
                result += "</row>"
            result += "</table>"
        result += "</container>"
        # except Exception as e:
        # debug("!!!!!!!!"+str(e))

        return VDOM_object.wysiwyg(self, contents=result)


# def on_delete(app_id, object_id, param):
def on_delete(object):
    # import managers
    # object = application.objects.search(object_id)
    if managers.database_manager.check_database(object.application.id, object.parent.id):
        db = managers.database_manager.get_database(object.application.id, object.parent.id)
        if db:
            # table = db.get_table(object_id,object.name)
            table = db.get_table(object.id, object.name)
            table.remove()
    return ""


# def get_table(app_id, object_id):
def get_table(object):
    # object = application.objects.search(object_id)
    # db = obsolete_request.database_manager.get_database(application.id, object.parent.id)
    db = managers.database_manager.get_database(object.application.id, object.parent.id)
    # return db.get_table(object_id,object.name)
    return db.get_table(object.id, object.name)


# def get_structure(app_id, object_id, xml_param):
def get_structure(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        structure = table.get_structure()
        return "<Result>%s</Result>" % structure
    except Exception as e:
        return "<Error>Getting structure failed: %s</Error>" % str(e)


# def get_data(app_id, object_id, xml_param):
def get_data(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        limit_num = None
        offset_num = None
        filter_query = None
        order = (None, None)
        if xml_param:
            from xml.dom.minidom import parseString

            dom_param = parseString(xml_param.encode("UTF-8"))
            limit = dom_param.getElementsByTagName("limit")
            if limit:
                limit_num = limit[0].firstChild.nodeValue
                offset = dom_param.getElementsByTagName("offset")
                if offset:
                    offset_num = offset[0].firstChild.nodeValue
            filter = dom_param.getElementsByTagName("where")
            if filter:
                filter_query = filter[0].firstChild.nodeValue
            orderby = dom_param.getElementsByTagName("orderby")
            if orderby:
                order_direct = orderby[0].getAttribute("sort")
                order_query = orderby[0].firstChild.nodeValue
                order = (order_query, order_direct)

        data = table.get_data_xml(limit_num, offset_num, filter_query, order)
        return "<Result>%s</Result>" % data
    except Exception as e:
        return "<Error>Getting data failed: %s</Error>" % str(e)


# def get_count(app_id, object_id, xml_param):
def get_count(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        count = table.get_count()
        return "<Result>%s</Result>" % count
    except Exception as e:
        return "<Error>Getting row count failed: %s</Error>" % str(e)


# def add_row(app_id, object_id, xml_param):
def add_row(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        num_added = table.addrow_from_xml(xml_param)
        return "<Result>OK. Added rows:%s</Result>" % num_added
    except Exception as e:
        return "<Error>Adding row failed: %s</Error>" % str(e)


# def add_column(app_id, object_id, xml_param):
def add_column(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        num_added = table.addcolumn_from_xml(xml_param)
        return "<Result>OK. Added columns:%s</Result>" % num_added
    except Exception as e:
        return "<Error>Adding column failed: %s</Error>" % str(e)


# def delete_column(app_id, object_id, xml_param):
def delete_column(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        if xml_param:
            from xml.dom.minidom import parseString

            dom_param = parseString(xml_param)
            delete_node = dom_param.getElementsByTagName("column")
            id = delete_node[0].getAttribute("id")
            if table.delete_column(id):
                return "<Result>OK. Deleting column %s ok</Result>" % str(id)
            return "<Error>No such column for delete: %s</Error>" % str(id)
    except Exception as e:
        return "<Error>Deleting column failed: %s</Error>" % str(e)


# def delete_row(app_id, object_id, xml_param):
def delete_row(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        table.delete_row_from_xml(xml_param)
        return "<Result>OK. Deleting row ok</Result>"
    except Exception as e:
        return "<Error>Deleting row failed: %s</Error>" % str(e)


# def update_column(app_id, object_id, xml_param):
def update_column(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        table.update_column(xml_param)
        return "<Result>OK. Updating column ok</Result>"
    except Exception as e:
        return "<Error>Updating column failed: %s</Error>" % str(e)


# def update_row(app_id, object_id, xml_param):
def update_row(object, xml_param):
    try:
        # table = get_table(app_id,object_id)
        table = get_table(object)
        table.update_row_from_xml(xml_param)
        return "<Result>OK. Updating row ok</Result>"
    except Exception as e:
        return "<Error>Updating row failed: %s</Error>" % str(e)