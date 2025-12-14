
import sqlite3
import re
from xml.dom import Node
from xml.dom.minidom import parseString  # parse,
from StringIO import StringIO
import managers
import file_access
from utils.exception import VDOM_exception, VDOMDatabaseAccessError
from utils.semaphore import VDOM_semaphore

class VDOM_database_object:
    """database object class"""

    def __init__(self, owner_id, id):
        """constructor"""
        self.owner_id = owner_id
        self.id = id
        self.name = str(id)
        self.filename = str(id)#str(uuid.uuid4())
        self.is_ready = False
        self.tables_list = None
        self.tables_index = {}
        self.data = None

    def set_wal_mode(self):
        sql_string = "PRAGMA journal_mode=WAL;"
        query = VDOM_sql_query(self.owner_id, self.id, sql_string)
        query.commit()
        query.close()

    def open(self, simple_rows=False, timeout=20.0):
        """open database"""
        # if self.__conn: return True
        try:
            # conn = sqlite3.connect(managers.file_manager.get_path(file_access.database, self.owner_id, None, self.filename), timeout=timeout)
            conn = sqlite3.connect(managers.file_manager.locate(file_access.database, self.owner_id, self.filename), timeout=timeout)
            if not simple_rows:
                conn.row_factory = sqlite3.Row
        except Exception, e:
            self.is_ready = False
            debug("Database open failed:" + str(e))
            return None

        self.is_ready = True
        return conn

    def get_connection(self, simple_rows=False):
        """Getting connection to database"""
        return self.open(simple_rows)

    def get_table(self, table_id, table_name, table_diffinition=""):
        """Create or read object representation for database table"""
        table = VDOM_database_table(self.owner_id, self.id, table_id, table_name)
        if not self.tables_list:
            self.tables_list = self.get_tables_list()

        if table_id in self.tables_index:
            if self.tables_index[table_id] != table_name:
                table.rename(self.tables_index[table_id])
                self.tables_index[table_id] = table_name
                self.tables_list = self.get_tables_list()
                managers.database_manager.save_index()
        else:
            if self.tables_list.count(table_name) == 0:
                table.create(table_diffinition)
                self.tables_list = self.get_tables_list()
            self.tables_index[table_id] = table_name
            managers.database_manager.save_index()
        return table

    def get_tables_list(self):
        tables = []
        cur = self.get_connection().cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type=\'table\' ORDER BY name")
        for row in cur:
            tables.append(row["name"])
        return tables

    def backup_data(self, tgt_connection):
        try:
            import sqlitebck
            sqlitebck.copy(self.get_connection(), tgt_connection)
        except ImportError:
            print ("ERROR: No module sqlitebck - databases could not be exported")


class VDOM_database_table:
    """Object representation of database table"""
    def __init__(self, owner_id, db_id, id, name):
        """constructor"""
        self.id = id
        self.owner_id = owner_id
        self.database_id = db_id
        self.name = name
        self.__reset_sem = VDOM_semaphore()
        self.__is_prepared = False
        self.structure = None
        self.__cur = None
        self.headers = []
        self.headersindex = {}

    def create(self, fields_list):
        """Create new table in DB"""
        if fields_list == "" or fields_list == "()":
            fields_list = "(id INTEGER PRIMARY KEY AUTOINCREMENT)"
        #fields_list = ""
        # if fields and len(fields)>0:
            #fields_list = "("
            # for key in fields:
                # if fields_list != "(":
                            #fields_list +=", "
                #fields_list += str(key)
            #fields_list += ")"
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        cur = database.get_connection().cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS \'%s\'%s" % (self.name, fields_list))
        self.restore_structure(True)

    def remove(self):
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        cur = database.get_connection().cursor()
        cur.execute("DROP TABLE IF EXISTS \'%s\'" % (self.name,))
        database.tables_list = database.get_tables_list()
        del database.tables_index[self.id]

    def get_structure(self):
        """geting XML representation of table structure"""
        if len(self.headers) == 0:
            self.restore_structure()
        columns = self.parse_declaration()
        result = "<tablestructure>\n"
        result += "\t<table id=\"%s\" name=\"%s\">\n" % (self.id, self.name)
        result += "\t<header>\n"
        for header in self.headers:
            result += "\t\t%s\n" % columns[header].to_xml()
        result += "\t</header>\n"
        result += "\t</table>\n"
        result += "</tablestructure>"
        return result

    def restore_structure(self, internal_usage=False):
        """restoring XML representation from database"""
        self.headers = []
        self.headersindex = {}
        i = 0
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        cur = database.get_connection().cursor()
        cur.execute("select * from `%s`" % self.name)
        for fieldDesc in cur.description:
            # if len(fieldDesc[0])>20:
            #	text = fieldDesc[0].ljust(20)
            # else:
            text = fieldDesc[0]
            try:
                self.headers.append(text.decode("UTF-8"))
                self.headersindex[text.decode("UTF-8")] = i
            except:
                self.headers.append(text)
                self.headersindex[text] = i
            i += 1
        if not internal_usage:
            managers.request_manager.get_request().session().value("headers", self.headers)

    def parse_declaration(self):
        """Parsing table declaration"""
        # based on sql grammar from http://www.sqlite.org/lang_createtable.html
        columns = {}
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        cur = database.get_connection().cursor()
        cur.execute("SELECT sql FROM sqlite_master WHERE type=\'table\' and upper(name)=?", (self.name.upper(),))
        for row in cur:
            table_def = re.search(r"""create table [\`'\"]?(?P<tbl_name>\w*)[\`'\"]?\s*\((?P<declaration>.+)\)""", row[0], re.DOTALL | re.IGNORECASE)
            if (not table_def) or (table_def.group("tbl_name").lower() != self.name.lower()):
                #raise VDOM_exception("Invalid database info")
                continue
            declaration = table_def.group("declaration")
            for column in map(unicode.strip, declaration.split(',')):
                constraints = {}
                match = re.search(r"""\A[`'"]?(?P<col_name>[\w_]+|\'.*?\')[`'"]?(?:\s+(?P<type>(?:INTEGER|TEXT|NUMERIC|BLOB|REAL)\(?\d*(?:,\d+)?\)?))?(?:\s+(?:(?P<notnull>NOT NULL)|(?P<unique>UNIQUE)|(?P<primarykeyauto>PRIMARY KEY AUTOINCREMENT)|(?P<primarykey>PRIMARY KEY)|(?P<default>DEFAULT (?:(?:')[\S ]+(?:')|\w+))))*""", column, re.DOTALL | re.IGNORECASE)
                if match:
                    col_name = un_quote(match.group("col_name"))
                    if col_name.upper() in ("PRIMARY", "UNIQUE", "CHECK", "FOREIGN"):
                        continue
                    col_type = match.group("type")
                    if not col_type:
                        col_type = "TEXT"
                    constraints["type"] = col_type
                    if match.group("notnull"):
                        constraints["not null"] = True
                    if match.group("primarykeyauto"):
                        constraints["primary key"] = "autoincrement"
                    elif match.group("primarykey"):
                        constraints["primary key"] = True
                    if match.group("unique"):
                        constraints["unique"] = True
                    if match.group("default"):
                        default = match.group("default")[8:]  # missing default word
                        if default[0] == "'" and default[-1] == "'":
                            constraints["default"] = default[1:-1]
                        else:
                            constraints["default"] = default
                    columns[col_name] = VDOM_db_column(col_name, constraints)
        return managers.request_manager.get_request().session().value("columns", columns)

    def update_structure(self, xmldata):
        """Updating table structure from xml"""
        # if xmldata:
            # try:
                #dom3 = parseString(xmldata)
                #changelog = dom3.getElementsByTagName("ChangeLog")
                # if len(changelog) == 1:
                    # for child in changelog[0].childNodes:
                        # if child.nodeName == "ColumnInsert":
                            #self.addcolumn(child.attributes["name"].value+ " " + child.attributes["type"].value)
                    # self.restore_structure()
            # except Exception, e:
                #debug("Database open failed:"+ str(e))
        return self.get_structure()

    def addcolumn(self, column):
        """Insert row in table"""
        if column not in self.headersindex:
            database = managers.database_manager.get_database(self.owner_id, self.database_id)
            cur = database.get_connection().cursor()
            cur.execute("ALTER TABLE \'%s\' ADD COLUMN %s" % (self.name, column.to_declaration()))

    def addcolumn_from_xml(self, xmldata):
        """Insert row in table from xml"""
        num_added = 0
        if xmldata:
            dom = parseString(xmldata.encode("UTF-8"))
            for column in dom.getElementsByTagName("column"):
                columns = managers.request_manager.get_request().session().value("columns")
                if not columns:
                    columns = self.parse_declaration()
                name = un_quote(column.getAttribute("name"))
                if not name:
                    continue
                if name in columns:
                    continue  # column already exists
                declaration = name
                constraints = {}
                cid = column.getAttribute("id")
                type = column.getAttribute("type")
                if not type or type == "INTEGER" or type == "REAL" or type == "TEXT" or type == "BLOB":
                    constraints["type"] = type
                if column.getAttribute("notnull") == "true":
                    constraints["not null"] = True
                if column.getAttribute("primary") == "true":
                    if column.getAttribute("autoincrement") == "true":
                        constraints["primary key"] = "autoincrement"
                    else:
                        constraints["primary key"] = True
                if column.getAttribute("unique") == "true":
                    constraints["unique"] = True

                if column.getAttribute("default") and column.getAttribute("default") != "" and column.getAttribute("default") != "NULL":
                    constraints["default"] = column.getAttribute("default")

                column_obj = VDOM_db_column(name, constraints)
                column_obj.id = cid
                columns[name] = column_obj
                self.addcolumn(column_obj)
                managers.request_manager.get_request().session().value("columns", columns)
                num_added += 1
        return num_added

    def delete_column(self, col_id):
        """Deliting column by id"""
        columns = managers.request_manager.get_request().session().value("columns")
        headers = managers.request_manager.get_request().session().value("headers")
        if not columns:
            return False
        column = None
        for col in columns:
            if columns[col].id == col_id:
                column = columns[col]
                break
        if not column:
            return False
        newtable = "%s_new(" % self.name
        oldtable = "%s(" % self.name
        for col in headers:
            if oldtable[-1] != "(":
                oldtable += ", "
            oldtable += columns[col].to_declaration()

            if columns[col].id == col_id:
                continue
            if newtable[-1] != "(":
                newtable += ", "
            newtable += columns[col].to_declaration()
        newtable += ")"
        if newtable[-2] == "(":
            return False
        newcols = []
        newcols.extend(headers)
        newcols.remove(column.name)
        newcols_decl = ""
        for ctr in newcols:
            newcols_decl += ", `%s`" % ctr

        sql = """BEGIN TRANSACTION;
CREATE TABLE %(newtable)s;
INSERT INTO  `%(newtablename)s` SELECT %(newcols)s FROM '%(oldtablename)s';
DROP TABLE `%(oldtablename)s`;
ALTER TABLE `%(newtablename)s` RENAME TO `%(oldtablename)s`;
END TRANSACTION;""" % {"newtable": newtable, "newtablename": self.name + "_new", "oldtablename": self.name, "newcols": newcols_decl[2:]}
        query = VDOM_sql_query(self.owner_id, self.database_id, sql, None, True)
        query.commit()
        columns.pop(column.name)
        managers.request_manager.get_request().session().value("columns", columns)
        return True

    def update_column(self, xmldata):
        """Recreating row with new attributes"""
        columns = managers.request_manager.get_request().session().value("columns")
        headers = managers.request_manager.get_request().session().value("headers")
        if not columns:
            return False
        if xmldata:
            # Parsing of column declaration
            dom = parseString(xmldata.encode("UTF-8"))
            column = dom.getElementsByTagName("column")[0]
            name = un_quote(column.getAttribute("name"))
            if not name:
                return False
            declaration = name
            constraints = {}
            cid = column.getAttribute("id")
            type = column.getAttribute("type")
            if not type or type == "INTEGER" or type == "REAL" or type == "TEXT" or type == "BLOB":
                constraints["type"] = type
            if column.getAttribute("notnull") == "true":
                constraints["not null"] = True
            if column.getAttribute("primary") == "true":
                if column.getAttribute("autoincrement") == "true":
                    constraints["primary key"] = "autoincrement"
                else:
                    constraints["primary key"] = True
            if column.getAttribute("unique") == "true":
                constraints["unique"] = True

            if column.getAttribute("default") and column.getAttribute("default") != "" and column.getAttribute("default") != "NULL":
                constraints["default"] = column.getAttribute("default")

            column_obj = VDOM_db_column(name, constraints)
            column_obj.id = cid

            # praparing SQL code
            old_column = None
            for col in columns:
                if columns[col].id == cid:
                    old_column = columns[col]
                    break
            if not old_column:
                return False

            newtable = "%s_new(" % self.name
            oldtable = "%s(" % self.name
            for col in headers:
                if oldtable[-1] != "(":
                    oldtable += ", "
                oldtable += columns[col].to_declaration()

                if columns[col].id == cid:
                    if newtable[-1] != "(":
                        newtable += ", "
                    newtable += column_obj.to_declaration()

                else:
                    if newtable[-1] != "(":
                        newtable += ", "
                    newtable += columns[col].to_declaration()
            newtable += ")"
            if newtable[-2] == "(":
                return False
            newcols = []
            newcols.extend(headers)
            newcols.remove(old_column.name)
            newcols_decl = ""
            for ctr in newcols:
                newcols_decl += ", `%s`" % ctr

            sql = """BEGIN TRANSACTION;
CREATE TABLE %(newtable)s;
INSERT INTO `%(newtablename)s` (%(newcols)s) SELECT %(newcols)s FROM `%(oldtablename)s`;
DROP TABLE `%(oldtablename)s`;
ALTER TABLE `%(newtablename)s` RENAME TO `%(oldtablename)s`;
END TRANSACTION;""" % {"newtable": newtable, "newtablename": self.name + "_new", "oldtablename": self.name, "newcols": newcols_decl[2:]}
            query = VDOM_sql_query(self.owner_id, self.database_id, sql, None, True)
            query.commit()
            columns.pop(old_column.name)
            columns[column_obj.name] = column_obj
            managers.request_manager.get_request().session().value("columns", columns)
            self.restore_structure()
            return True

    def delete_row_from_xml(self, xmldata):
        """Deleting row in table from xml"""
        if xmldata:
            dom = parseString(xmldata)
            for row in dom.getElementsByTagName("row"):
                cid = row.getAttribute("id")
                if cid:
                    query = VDOM_sql_query(self.owner_id, self.database_id, "DELETE FROM \'%s\' WHERE id = \'%s\'" % (self.name, cid))
                    query.commit()

    def update_row_from_xml(self, xmldata):
        """Updating rows from the xml"""
        if xmldata:
            dom = parseString(xmldata.encode("UTF-8"))
            for row in dom.getElementsByTagName("row"):
                if row.nodeType != Node.ELEMENT_NODE:
                    continue
                cid = row.getAttribute("id")
                if not cid:
                    continue
                assignment = ""
                params = []
                for cell in row.childNodes:
                    if cell.nodeType != Node.ELEMENT_NODE:
                        continue
                    name = cell.getAttribute("name")
                    if not name or name == "id":
                        continue
                    if not cell.firstChild:
                        value = ""
                    elif cell.firstChild.nodeValue == "NULL":
                        value = None
                    else:
                        value = cell.firstChild.nodeValue

                    if assignment != "":
                        assignment += ", "
                    assignment += "`%s` = ?" % name
                    params.append(value)
                params.append(cid)
                if assignment and params:
                    query = VDOM_sql_query(self.owner_id, self.database_id, "UPDATE `%s` SET %s WHERE id = ?" % (self.name, assignment), params)
                    query.commit()

    def get_data_xml(self, limit=None, offset=None, filter_query=None, order_by=(None, None)):
        range = ""
        filter_sql = ""
        oreder_sql = ""
        if limit and limit.isdigit():
            range = " LIMIT " + str(int(limit))
            if offset and offset.isdigit():
                range += " OFFSET " + str(int(offset))
        if filter_query:
            filter_sql = " where %s" % filter_query
        if order_by and order_by[0]:
            oreder_sql = " order by %s %s" % order_by
        query = VDOM_sql_query(self.owner_id, self.database_id, "select * from `%s` %s%s%s" % (self.name, filter_sql, oreder_sql, range))
        data = query.fetchall_xml()
        del(query)
        return data

    def update_data(self, xmldata):
        if xmldata:
            try:
                dom3 = parseString(xmldata)
                changelog = dom3.getElementsByTagName("ChangeLog")
                if len(changelog) == 1:
                    for child in changelog[0].childNodes:
                        if child.nodeName == "DataInsert":
                            self.addrow(child.attributes["values"].value)
                    self.restore_structure()
            except Exception, e:
                debug("Database update failed:" + str(e))
        return self.get_data_xml()

    def addrow(self, newrow):
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        con = database.get_connection()
        cur = con.cursor()
        sql = "INSERT INTO \'%s\'  VALUES(%s)" % (self.name, newrow)
        cur.execute(sql)
        con.commit()

    def addrow_from_list(self, list):
        """Adding new row from the list of values"""
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        con = database.get_connection()
        cur = con.cursor()
        arg = "(?"
        for i in xrange(len(list) - 1):
            arg += ", ?"
        arg += ")"
        sql = "INSERT INTO \'%s\'  VALUES %s" % (self.name, arg)
        cur.execute(sql, tuple(list))
        con.commit()

    def addrow_from_xml(self, xmldata):
        """Adding new row from the xml"""
        num_added = 0
        if xmldata:
            dom = parseString(xmldata.encode("UTF-8"))
            for row in dom.getElementsByTagName("row"):
                if row.nodeType != Node.ELEMENT_NODE:
                    continue
                values = []
                for cell in row.childNodes:
                    if cell.nodeType != Node.ELEMENT_NODE:
                        continue
                    if not cell.firstChild or cell.firstChild.nodeValue == "NULL":
                        values.append(None)
                    else:
                        values.append(cell.firstChild.nodeValue)
                if values:
                    self.addrow_from_list(values)
                    num_added += 1
        return num_added

    def rename(self, old_name):
        """Renameing table"""
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        cur = database.get_connection().cursor()
        cur.execute("ALTER TABLE \'%s\' RENAME TO \'%s\'" % (old_name, self.name))

    def get_count(self):
        """Getting count of rows"""
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        cur = database.get_connection().cursor()
        cur.execute("SELECT COUNT(*) FROM `%s`" % (self.name,))
        return cur.fetchone()[0]

    def reset(self):
        """prepare for usage"""
        # loading database header
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        if not database:
            return False

        self.__reset_sem.lock()
        try:
            self.__cur = database.get_connection().cursor()
            self.__cur.execute("select * from `%s`" % self.name)
            if not self.structure:
                self.restore_structure()

        except Exception, e:
            debug("Database reset failed")
            self.__reset_sem.unlock()
            self.__is_prepared = False
            debug(str(e))
            return False

        self.__is_prepared = True
        self.__reset_sem.unlock()
        return True

    def rows(self):
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        if not database or (not database.is_ready and not database.open()):
            return
        del(database)

        if not self.__is_prepared:
            if not self.reset():
                return

        for row in self.__cur:
            yield row

        self.__is_prepared = False


class VDOM_sql_query:
    """Class with main functionality of quering SQL"""
    def __init__(self, owner_id, database_id, query, params=None, executescript=False, executemany=False, simple_rows=False):
        """constructor"""
        self.query = query
        self.finished = False
        self.headers = []
        self.headersindex = {}
        self.__cur = None
        self.__conn = None
        self.owner_id = owner_id
        self.database_id = database_id
        if not managers.database_manager.check_database(self.owner_id, self.database_id):
            raise VDOMDatabaseAccessError("database not exist")
        database = managers.database_manager.get_database(self.owner_id, self.database_id)
        if not database or (not database.is_ready and not database.open()):
            raise VDOMDatabaseAccessError("database not ready")
        self.__conn = database.get_connection(simple_rows)
        self.__cur = self.__conn.cursor()
        if executescript:
            self.__cur.executescript(query)
        else:
            if params:
                if executemany:
                    self.__cur.executemany(query, params)
                else:
                    self.__cur.execute(query, params)
            else:
                self.__cur.execute(query)
        i = 0
        if self.__cur.description:
            for fieldDesc in self.__cur.description:
                if len(fieldDesc[0]) > 20:
                    text = fieldDesc[0].ljust(20)
                else:
                    text = fieldDesc[0]
                self.headers.append(text)
                self.headersindex[text] = i
                i += 1

    def close(self):
        self.__conn.close()
    def commit(self):
        if self.__conn:
            self.__conn.commit()
    def rows(self):
        if not self.finished:
            for row in self.__cur:
                yield row
        self.finished = True

    def fetchone(self):
        return self.__cur.fetchone()

    def fetchall(self):
        allrows = []
        for row in self.__cur:
            allrows.append(row)
        return allrows

    def fetchall_xml(self):
        result = StringIO()
        result.write(u"<queryresult>\n")
        result.write("\t<table>\n")
        result.write("\t\t<header>\n")
        for header in self.headers:
            result.write("\t\t\t<column id=\"\" name=\"%s\"/>\n" % header.decode("UTF-8"))
        result.write("\t\t</header>\n")
        result.write("\t\t<data>\n")
        for row in self.__cur:
            result.write("\t\t\t<row>\n")
            for column in self.headers:
                data = row[column]
                if data == None or data == "None":
                    data = "NULL"
                result.write("\t\t\t\t<cell>%s</cell>\n" % unicode(data).encode("xml"))
            result.write("\t\t\t</row>\n")
        result.write("\t\t</data>\n")
        result.write("\t</table>\n")
        result.write("</queryresult>")
        return result.getvalue()

    def __get_lastrowid(self):
        return self.__cur.lastrowid

    def __set_lastrowid(self, value):
        raise AttributeError
    lastrowid = property(__get_lastrowid, __set_lastrowid)

    def __get_rowcount(self):
        return self.__cur.rowcount

    def __set_rowcount(self, value):
        raise AttributeError
    rowcount = property(__get_rowcount, __set_rowcount)


class VDOM_db_column:
    """VDOM representation of single DB column"""
    def __init__(self, name, constraints={}):
        """Constructor"""
        self.name = name
        self.id = name  # str(utils.uuid.uuid4())

        if "type" in constraints:
            self.type = constraints["type"]
        else:
            self.type = "TEXT"

        if "not null" in constraints and constraints["not null"] == True:
            self.notnull = True
        else:
            self.notnull = False

        if "primary key" in constraints and constraints["primary key"] == "autoincrement":
            self.primary = True
            self.autoincrement = True
        elif "primary key" in constraints and constraints["primary key"] == True:
            self.primary = True
            self.autoincrement = False
        else:
            self.primary = False
            self.autoincrement = False

        if "unique" in constraints and constraints["unique"] == True:
            self.unique = True
        else:
            self.unique = False

        if "default" in constraints:
            self.default = constraints["default"]
        else:
            self.default = None
    def to_xml(self):
        """Returning xml representation of column definition"""
        declaration = "<column id=\"%s\" name=\"%s\" type=\"%s\"" % (self.id, self.name, self.type)
        if self.notnull:
            declaration += " notnull=\"true\""
        if self.primary:
            declaration += " primary=\"true\""
        if self.autoincrement:
            declaration += " autoincrement=\"true\""
        if self.unique:
            declaration += " unique=\"true\""
        if self.default:
            declaration += " default=\"%s\"" % self.default.replace("<", "&lt;").replace(">", "&gt;")
        declaration += "/>"
        return declaration
    def to_declaration(self):
        """Returning sql declaration representation of column definition"""
        declaration = "\'" + self.name + "\'"
        declaration += " " + self.type
        if self.notnull:
            declaration += " NOT NULL"
        if self.primary:
            if self.autoincrement:
                declaration += " PRIMARY KEY AUTOINCREMENT"
            else:
                declaration += " PRIMARY KEY"
        if self.unique:
            declaration += " UNIQUE"
        if self.default:
            declaration += " DEFAULT \'%s\'" % self.default
        return declaration


def un_quote(param):
    """Delete all quotes from param"""
    return param.replace("\'", "").replace("\"", "").replace("\\", "")
