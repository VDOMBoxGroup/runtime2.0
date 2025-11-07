
import managers


class MemoryInterface(object):
    """This class is used as interface to VDOM memory"""

    def __init__(self, request_object):
        """constructor"""
        self.__request = request_object

    def create_object(self):
        pass

    def get_object(self):
        pass

    def delete_object(self):
        pass

    def set_object_attribute(self):
        pass

    def set_object_value(self):
        pass

    def set_object_script(self):
        pass

    def search_object(self, obj_id):
        # app = managers.xml_manager.get_application(self.__request.application_id)
        app = managers.memory.applications[self.__request.application_id]
        # object=app.search_object(obj_id)
        object = app.objects.catalog.get(obj_id)
        return object

    def __repr__(self):
        return "<memory interface at 0x%08X>" % id(self)


VDOM_memory_interface = MemoryInterface
