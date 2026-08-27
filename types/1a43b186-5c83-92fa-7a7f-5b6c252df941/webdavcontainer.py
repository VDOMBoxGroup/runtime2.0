import managers


class VDOM_webdavcontainer(VDOM_object):

    def wysiwyg(self, contents=""):
        result = "<container name=\"%s\" id=\"%s\" visible=\"%s\" hierarchy=\"%s\" >%s</container>" % (
            self.name, self.id, self.visible, self.hierarchy, contents)
        return VDOM_object.wysiwyg(self, contents=result)


# def set_name(application_id, object_id, param):
def on_rename(object):
    actions = {"authentication": ["path", "user", "password"],
               "getResourseProperties": ["path"],
               "isCollection": ["path"],
               "getMembers": ["path"],
               "open": ["path"]
               }
    application_id = object.application.id
    object_id = object.id
    # object = managers.xml_manager.search_object(application_id, object_id)
    for act in actions:
        # if act not in object.actions["name"]:
        if act not in object.actions:
            # object.create_action(act, "")
            object.actions.new(act)
    sharePath = "/" + object.name
    oldSharePath = managers.webdav_manager.get_webdav_share_path(
        application_id, object_id)
    if oldSharePath and oldSharePath != sharePath:
        managers.webdav_manager.del_webdav(
            application_id, object_id, oldSharePath)
    managers.webdav_manager.add_webdav(application_id, object_id, sharePath)


# def on_delete(application_id, object_id, param):
def on_delete(object):
    application_id = object.application.id
    object_id = object.id
    SharePath = managers.webdav_manager.get_webdav_share_path(
        application_id, object_id)
    if SharePath:
        managers.webdav_manager.del_webdav(
            application_id, object_id, SharePath)