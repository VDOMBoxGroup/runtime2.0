
from builtins import str
from builtins import object
import copy
import managers
import file_access
from .res_object import VDOM_resource_descriptor


class VDOM_resource_manager(object):

    def __init__(self):
        """constructor"""
        self.__label_index = {}
        self.save_index = True
        self.__name_index = {}
        self.__name_index = {}

    def restore(self):
        """Restoring resources from last session.(After reboot or power off)"""
        self.__old_index = managers.storage.read_object(VDOM_CONFIG["RESOURCE-MANAGER-INDEX-STORAGE-RECORD"])

        already_exist = managers.storage.make_resources_index()

        if self.__old_index and not already_exist:
            # Transfering index to new format
            for resource in self.__old_index:
                self.__main_index[resource] = VDOM_resource_descriptor.convert(self.__old_index[resource])
                self.__name_index[self.__old_index[resource].name.lower()] = resource
        else:
            res_list = managers.storage.list_resource_index()
            self.__main_index = {res_id: VDOM_resource_descriptor(owner_id, res_id,res_format, name) for (owner_id, res_id, res_format, name) in res_list}
            self.__name_index = {name.lower(): res_id for (owner_id, res_id, res_format, name) in res_list}            
        del self.__old_index
        # TODO: check for not existing or temporary resources
        if not self.__main_index:
            self.remove_resources()

    def collect_unused(self):
        """Removing unused resources with no dependences"""
        pass

    def check_resource(self, owner_id, attributes, crc=None):
        if "id" not in attributes:
            return False
        if not attributes["id"] in self.__main_index:
            return False
        resource = self.__main_index[attributes["id"]]
        if resource.application_id != owner_id:  # and owner_id not in resource.dependences:
            return False
        #if not resource.filename:
        #    return False

        # if resource.application_id != owner_id and owner_id not in resource.dependences:
            # return False
        # if not resource.filename:
            # return False
        # if crc != managers.file_manager.compute_crc(file_access.resource,resource.application_id,resource.object_id, resource.filename):
            # return False
        return True

    def add_resource(self, owner_id, object_id, attributes, bin_data, optimize=1):
        "new version of Add resource"
        if attributes.get("id") in self.__main_index and optimize:  # TODO: Verify this behaviour
            # We have such resource already
            return attributes.get("id")
        else:
            assert(isinstance(attributes, dict))
            write_async = False
            # object_owner = None
            if "label" in attributes and (object_id, attributes["label"]) in self.__label_index:
                return self.__label_index[(object_id, attributes["label"])].id
            res_descriptor = VDOM_resource_descriptor(owner_id, attributes.get("id"),attributes.get("res_format"))

            
            if "label" in attributes:
                self.__label_index[(object_id, attributes["label"])] = res_descriptor
                res_descriptor.object_id = object_id
            #else:
            #    res_descriptor = copy.copy(res_descriptor)
            for key in attributes:
                if key == "name":
                    setattr(res_descriptor, "name", ''.join(char for char in str(attributes["name"]) if ord(char) < 128))
                    self.__name_index[res_descriptor.name.lower()] = res_descriptor.id
                elif key == "save_async":
                    write_async = True
                elif key != "id":
                    setattr(res_descriptor, key, attributes[key])
            if "res_type" not in attributes:
                res_descriptor.res_type = "permanent"
            if "res_format" not in attributes:
                res_descriptor.res_format = ""
                
            self.__main_index[res_descriptor.id] = res_descriptor
            # managers.file_manager.write(file_access.resource,
            #     res_descriptor.application_id, object_id, res_descriptor.filename, bin_data, None, write_async)
            managers.file_manager.write(file_access.resource,
                                        res_descriptor.application_id, res_descriptor.filename, bin_data, write_async=write_async)

            if "label" not in attributes:
                res_descriptor.save_record()
        return res_descriptor.id

    def get_resource(self, owner_id, res_id):
        """Getting resource object"""
        return self.__main_index.get(res_id.split(".")[0]) or self.__main_index.get(self.__name_index.get(res_id.lower()))
        #return res.load_copy() if res else None

    def get_resource_by_label(self, object_id, label):
        """Getting resource object"""
        return self.__label_index.get((object_id, label))

    def list_resources(self, owner_id):
        """listing of all resources of application"""
        return [res.id for res in self.__main_index.values() if not owner_id or res.application_id == owner_id]

    def update_resource(self, owner_id, resource_id, bin_data):
        """Adding a new resource"""
        if resource_id in self.__main_index and self.__main_index[resource_id].application_id == owner_id:
            res = self.__main_index[resource_id]
            # managers.file_manager.write(file_access.resource, owner_id, None, res.filename, bin_data)
            managers.file_manager.write(file_access.resource, owner_id, res.filename, bin_data)

    def delete_resource(self, object_id, res_id, remove=False):
        """Removing resource object and it's content"""
        # TODO: remove resource from label_index
        if res_id in self.__main_index:
            resource = self.__main_index[res_id]
            resource.decrease(object_id, remove)
            if remove:
                if getattr(resource, "object_id", None):
                    self.__label_index.pop((resource.object_id, resource.label), None)  # TODO: fix labels resources
                self.__main_index.pop(res_id)
                if resource.name in self.__name_index:
                    self.__name_index.pop(resource.name.lower())                

    def remove_resources(self):
        """Clearing resource cache on startup"""
        self.__main_index = {}
        self.__label_index = {}
        # managers.file_manager.clear(file_access.resource, None, None)
        managers.file_manager.cleanup_directory(file_access.RESOURCE, None)

        # storage.clear_resources_index()
        managers.storage.clear_resources_index()  # ?????

    def invalidate_resources(self, object_id, cleanup=True):
        """Invalidate and clear all resources by object_id"""
        need_clean = False
        for (obj_id, label) in list(self.__label_index.keys()):
            if obj_id == object_id:
                need_clean = True
                res_descriptor = self.__label_index.pop((obj_id, label))
                #f self.__main_index[res_descriptor.id].application_id == object_id:
                del self.__main_index[res_descriptor.id]

        if cleanup and need_clean:
            # managers.file_manager.clear(file_access.resource, None, object_id)
            managers.file_manager.cleanup_directory(file_access.resource, object_id)


    def save_index_off(self):
        """Turning flag of index saving OFF"""
        self.save_index = False

    def save_index_on(self, forced_save=False):
        """Turning flag of index saving ON"""
        self.save_index = True
