"""database manager"""
# import string
# import sys
# import uuid
import managers
import file_access
# from utils.exception import VDOM_exception
from dbobject import VDOM_database_object, VDOM_database_table
from xml.dom.minidom import parseString
from xml.dom import Node
# import time
import sqlite3,os.path


class VDOM_database_manager(object):
    """database manager class"""

    def __init__(self):
        """constructor"""
        self.__index = {}
        self.__database_by_name = {}

    def restore(self):
        """Restoring databases from last session.(After reboot or power off)"""
        self.__index = managers.storage.read_object(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"])
        if self.__index:
            remove_list = []
            is_dirty_index = False
            for id in self.__index:  # check for not existing or temporary resources
                database = self.__index[id]
                try:
                    database.set_wal_mode()
                except Exception:
                    remove_list.append(id)
                if managers.file_manager.exists(file_access.database, database.owner_id, database.filename):
                    self.__database_by_name[(database.owner_id, database.name)] = database
                else:
                    remove_list.append(id)

            for id in remove_list:
                self.__index.pop(id, None)
                is_dirty_index = True

            if is_dirty_index:
                managers.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"], self.__index)
        else:
            #self.remove_databases()
            pass

    def add_database(self, owner_id, attributes, data):
        """Adding a new database"""
        if "id" in attributes and attributes["id"] in self.__index and self.__index[attributes["id"]].owner_id == owner_id:
            pass
        else:
            database = VDOM_database_object(owner_id, attributes["id"])

            try:
                for key in attributes:
                    if key not in ("id", "type"):
                        setattr(database, key, attributes[key])
                        #exec "database." + key + " = \"" + attributes[key] + "\""
            except:
                pass

            self.__index[database.id] = database
            self.__database_by_name[(database.owner_id, database.name)] = database
            if attributes["type"] == "sqlite":
                managers.file_manager.write(file_access.database, database.owner_id, database.filename, data)
            elif attributes["type"] == "xml":
                self.create_from_xml(database, data)
            elif attributes["type"] == "multifile":
                self.create_from_tar(database, data)
            database.set_wal_mode()
            managers.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"], self.__index)
        return attributes["id"]

    def check_database(self, owner_id, id):
        """Check a database"""
        if id not in self.__index:
            return False
        database = self.__index[id]
        if database.owner_id != owner_id:
            return False
        if not database.filename:
            return False
        return True

    def get_database(self, owner_id, db_id):
        """Getting database object"""
        database = None
        if db_id in self.__index:
            return self.__index[db_id]

            # if database.application_id == owner_id:
        # else:
            # no more database is created after first access
            #database = self.create_database(owner_id, db_id)
        # return database

    def get_database_by_name(self, owner_id, db_name):
        if (owner_id, db_name) in self.__database_by_name:
            return self.__database_by_name[(owner_id, db_name)]
        else:
            managers.log_manager.info_server("Database lookup by name  failed. name: %s, owner: %s" % (db_name, owner_id), "db_manager")

    def get_database_by_name_old(self, owner_id, db_name):
        """Getting database object by name"""
        database = None
        db = []
        for db_id, db_obj in self.__index.items():
            if db_obj.name == db_name and db_obj.owner_id == owner_id:
                db.append(self.__index[db_id])
        #managers.log_manager.info_server("list of databases by name %s. name: %s, owner: %s" % (str(db), db_name, owner_id), "db_manager")
        if len(db) == 1:
            database = db[0]
            return database
        else:
            managers.log_manager.info_server("Database lookup by name  failed %s. name: %s, owner: %s" % (str(db), db_name, owner_id), "db_manager")

    def create_database(self, owner_id, id, name):
        """Creation of new database"""
        database = VDOM_database_object(owner_id, id)
        database.name = name
        self.__index[database.id] = database
        self.__database_by_name[(database.owner_id, database.name)] = database
        # managers.file_manager.create_database_directory(owner_id)
        managers.file_manager.prepare_directory(file_access.DATABASE, owner_id, cleanup=False)
        managers.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"], self.__index)
        return database

    def create_from_xml(self, database, xml_data):
        """Creation of database from xml representation"""
        #managers.file_manager.create_database_directory(database.owner_id)
        managers.file_manager.prepare_directory(file_access.DATABASE, database.owner_id)
        dom_db = parseString(xml_data)
        database.id = dom_db.firstChild.getAttribute("ID")
        database.name = dom_db.firstChild.getAttribute("Name")
        values = []
        for table in dom_db.firstChild.childNodes:
            if table.nodeType != Node.ELEMENT_NODE:
                continue
            tbl = VDOM_database_table(database.owner_id, database.id, table.getAttribute("id"), table.getAttribute("name"))
            field_list = ""
            id_field = False
            for column in table.getElementsByTagName("header")[0].childNodes:
                if column.nodeType != Node.ELEMENT_NODE:
                    continue
                if un_quote(column.getAttribute("name")) == "id":
                    id_field = True
                declaration = "\'" + un_quote(column.getAttribute("name")) + "\'"
                type = column.getAttribute("type")
                if not type or type == "INTEGER" or type == "REAL" or type == "TEXT" or type == "BLOB":
                    declaration += " " + type
                if column.getAttribute("notnull") == "true":
                    declaration += " NOT NULL"
                if column.getAttribute("primary") == "true":
                    if column.getAttribute("autoincrement") == "true":
                        declaration += " PRIMARY KEY AUTOINCREMENT"
                    else:
                        declaration += " PRIMARY KEY"
                if column.getAttribute("unique") == "true":
                    declaration += " UNIQUE"

                if len(field_list):
                    field_list += ", " + declaration
                else:
                    field_list = declaration
            if not id_field:
                if field_list:
                    field_list = "id INTEGER PRIMARY KEY AUTOINCREMENT, " + field_list
                else:
                    field_list = "id INTEGER PRIMARY KEY AUTOINCREMENT"
            tbl.create("(" + field_list + ")")
            for row in table.getElementsByTagName("data")[0].childNodes:
                if row.nodeType != Node.ELEMENT_NODE:
                    continue
                values = []
                for cell in row.childNodes:
                    if cell.nodeType != Node.ELEMENT_NODE:
                        continue
                    if not cell.firstChild or cell.firstChild.nodeValue == "None":
                        values.append(None)
                    else:
                        values.append(cell.firstChild.nodeValue)
                if values:
                    tbl.addrow_from_list(values)
        database.get_connection().commit()

    def create_from_tar(self, database, xml_data):
        """Creation of database from tar archive"""
        raise NotImplementedError
        # managers.file_manager.create_database_directory("%s/%s" % (database.owner_id, database.id))
        managers.file_manager.prepare_directory(file_access.DATABASE, database.owner_id)
        # managers.file_manager.get_path(file_access.database, database.owner_id, database.id)
        managers.file_manager.locate(file_access.database, database.owner_id)

    def rename_database(self, owner_id, db_id, new_name):
        if db_id in self.__index:
            database = self.__index[db_id]
            if owner_id == database.owner_id and database.name != new_name:
                del self.__database_by_name[(database.owner_id, database.name)]
                database.name = new_name
                self.__database_by_name[(database.owner_id, database.name)] = database
                self.save_index()

    def remove_databases(self):
        """Clearing all databases"""
        #Keep old databases for potential recovery
        #managers.file_manager.cleanup_directory(file_access.database, None)
        if self.__index or self.__database_by_name:
            self.__index = {}
            self.__database_by_name = {}
            managers.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"], self.__index)

    def list_databases(self, owner_id):
        """listing of all resources of application"""
        result = {}
        for key in self.__index:
            if self.__index[key].owner_id == owner_id:
                result[key] = self.__index[key].name
        return result

    def list_names(self, owner_id):
        """listing of all resources of application"""
        result = {}
        for key in self.__index:
            if self.__index[key].owner_id == owner_id and self.__index[key].name:
                result[self.__index[key].name] = self.__index[key].id
        return result

    def delete_database(self, owner_id, db_id=None):
        """Remove one or all databases of given owner"""
        remove_list = []
        database = None
        is_dirty_index = True
        if self.__index:
            for key in self.__index:
                database = self.__index[key]
                if database.owner_id == owner_id and (db_id is None or db_id == database.id):
                    self.__database_by_name.pop((database.owner_id, database.name), None)
                    remove_list.append(key)

            is_dirty_index = False
            for key in remove_list:
                self.__index.pop(key)
                is_dirty_index = True
        else:
            self.__index = {}
        if is_dirty_index:
            managers.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"], self.__index)
        if db_id and database:
            # managers.file_manager.delete(file_access.database, owner_id, None, database.filename)
            managers.file_manager.delete(file_access.database, owner_id, database.filename)
        else:
            # managers.file_manager.clear(file_access.database, owner_id, None)
            managers.file_manager.cleanup_directory(file_access.database, owner_id)

    def save_index(self):
        """Saving changes in database index to Storage"""
        managers.storage.write_object_async(VDOM_CONFIG["DATABASE-MANAGER-INDEX-STORAGE-RECORD"], self.__index)

    def backup_database(self, owner_id, db_id):
        if db_id not in self.__index:
            return None
        orig_db = self.get_database(owner_id, db_id)
        temppath = managers.file_manager.create_temporary_directory("db_")
        try:
            tgt_connection = sqlite3.connect(os.path.join(temppath,"copydb"))
            orig_db.backup_data(tgt_connection)
            tgt_connection.execute("VACUUM")
            tgt_connection.commit()
            tgt_connection.close()
            data = managers.file_manager.read(file_access.FILE, None, os.path.join(temppath,"copydb"))
        finally:
            managers.file_manager.delete_temporary_directory(temppath)
        return data


def un_quote(param):
    """Delete all quotes from param"""
    return param.replace("\'", "").replace("\"", "").replace("\\", "")
