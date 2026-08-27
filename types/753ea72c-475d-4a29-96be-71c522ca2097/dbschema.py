import managers


class VDOM_dbschema(VDOM_object):
    def render(self, contents=""):
        return VDOM_object.render(self, contents=contents)

    def wysiwyg(self, contents=""):
        result = '<container name="%s" id="%s" visible="%s" hierarchy="%s" >%s</container>' % (self.name, self.id, self.visible, self.hierarchy, contents)
        return VDOM_object.wysiwyg(self, contents=result)


# def set_name(application_id, object_id, param):
def on_rename(object, name):
    # database_manager = obsolete_request.database_manager
    database_manager = managers.database_manager
    # if not database_manager.check_database(application.id, object_id):
    if not database_manager.check_database(object.application.id, object.id):
        # database_manager.create_database(application_id, object_id, param["name"])
        database_manager.create_database(object.application.id, object.id, name)
    else:
        # database_manager.rename_database(application_id, object_id, param["name"])
        database_manager.rename_database(object.application.id, object.id, name)


def on_delete(object):
    # obsolete_request.database_manager.delete_database(application_id, object_id)
    managers.database_manager.delete_database(object.application.id, object.id)
    return ""


# def execute_query(object, param):
# 	if param:
# 		from database.dbobject import VDOM_sql_query
# 		q = VDOM_sql_query(object.application.id, object.id, param)
# 		q.commit()
# 		query = q.fetchall()
# 		return (query)
# 	else:
# 		# return "Error, query filed: %s"%str(e)
# 		return "NO PARAM"


def execute_query_xml(object, xml_param):
    if xml_param:
        from xml.dom.minidom import parseString

        dom_param = parseString(xml_param.encode("UTF-8"))
        query = dom_param.getElementsByTagName("query_sql")
        if query:
            from database.dbobject import VDOM_sql_query

            # q = VDOM_sql_query(application_id, object_id, query[0].firstChild.nodeValue)
            q = VDOM_sql_query(object.application.id, object.id, query[0].firstChild.nodeValue)
            q.commit()
            query_xml = q.fetchall_xml()
            return query_xml
    else:
        # return "<Error>Query failed: %s</Error>"%str(e)
        return "NO XML PARAM"