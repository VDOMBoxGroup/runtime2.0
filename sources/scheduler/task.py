import managers

class VDOM_scheduler_task(object):
    
    def run(self):
        pass
    
class VDOM_backup_task(VDOM_scheduler_task):
    
    

    def __init__(self, drv_id, apps, rot):
        self.__driver_id = drv_id
        self.__app_list = apps
        self.__rotation = rot
    
    def run(self):
        for app in self.__app_list:
            managers.backup_manager.backup(app, self.__driver_id)
    
    def __get_drv_id(self):
        return self.__driver_id
    def __get_app_list(self):
        return self.__app_list
    def __set_app_list(self, value):
        self.__app_list = value
    def __get_rotation(self):
        return self.__rotation
    def __set_rotation(self, value):
        self.__rotation = value
   
    driver = property(__get_drv_id)
    applications = property(__get_app_list, __set_app_list)
    rotation = property(__get_rotation, __set_rotation)
            
