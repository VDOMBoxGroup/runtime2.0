from builtins import str
from builtins import object
import gc
import os
import os.path
import re
import shutil
import sqlite3
import tempfile
from distutils.dir_util import copy_tree
from threading import RLock
from weakref import ref

import file_access
import managers
import settings
from logs import log
from utils.parsing import Parser, ParsingException
from utils.properties import roproperty  # rwproperty
from utils.structure import Structure
from utils.tracing import format_exception_trace, describe_object, format_referrers

from .application import application_builder, MemoryApplications
from .constants import DEFAULT_APPLICATION_NAME
from .daemon import MemoryWriter, MemoryCleaner
from .type import type_builder, MemoryTypes


class AlreadyExistsError(Exception):
    pass


class Memory(object):

    def __init__(self):
        self._lock = RLock()
        self._queue = set()
        self._release_queue = set()
        self._daemon = None
        self._cleaner = None

        self._types = MemoryTypes(self)
        self._applications = MemoryApplications(self)

        self._operations = 0
        self._primaries = {}
        self._primaries_cache = {}

        # obsolete
        # managers.resource_manager.save_index_off()

        managers.resource_manager.restore()
        managers.database_manager.restore()
        # managers.scheduler_manager.restore()

        # obsolete
        # managers.resource_manager.collect_unused()
        # managers.resource_manager.save_index_on(True)

        # applications = managers.storage.read_object(VDOM_CONFIG["XML-MANAGER-APP-STORAGE-RECORD"])
        # if applications:
        #     for application in applications:
        #         # managers.source_cache.clear_container_swap(item)
        #         # managers.file_manager.clear(file_access.cache, application, None)
        #         managers.file_manager.cleanup_directory(file_access.cache, application)
        # types = managers.storage.read_object(VDOM_CONFIG["XML-MANAGER-TYPE-STORAGE-RECORD"])
        # if types:
        #     for type in types:
        #         # managers.source_cache.clear_type_sources(item)
        #         # managers.file_manager.clear(file_access.type_source, type, None)
        #         managers.file_manager.cleanup_directory(file_access.type_source, type)

        if settings.MANUAL_GARBAGE_COLLECTING:
            gc.disable()
            self.start_cleaner()

    lock = roproperty("_lock")
    types = roproperty("_types")
    applications = roproperty("_applications")

    # threading

    def start_daemon(self):
        if self._daemon is None:
            self._daemon = MemoryWriter(self)
            self._daemon.start()
        return self._daemon

    def start_cleaner(self):
        if self._cleaner is None:
            self._cleaner = MemoryCleaner(self)
            self._cleaner.start()
        return self._cleaner

    def work(self):
        with self._lock:
            entities = tuple(self._queue)
            self._queue.clear()

        for entity in entities:
            try:
                entity.save()
            except:  # noqa
                log.error("Unable to save %s, details below\n%s" %
                    (entity, format_exception_trace(locals=True, separate=True)))

    def clean(self, everything=False):
        if everything:
            if settings.DETAILED_LOGGING:
                log.write("Release objects")
            while 1:
                try:
                    object, reference = self._primaries.popitem()
                except KeyError:
                    break
                else:
                    object._collection.on_delete(object)
        else:
            if self._operations:
                self._operations = 0
                return
            self._operations = 0

            while 1:
                try:
                    object = self._release_queue.pop()
                except KeyError:
                    break
                else:
                    if self._primaries.pop(object, None) is not None:
                        if settings.DETAILED_LOGGING:
                            log.write("Release %s" % object)
                        object._collection.on_delete(object)

            if settings.DETAILED_LOGGING and settings.SHOW_TRACKED_PRIMARIES:
                primaries = self._primaries.copy()
                if primaries != self._primaries_cache:
                    if primaries:
                        lines = []
                        lines.append("Tracked primary objects:")
                        for primary, reference in primaries.items():
                            lines.append("    %s" % primary)
                            if reference:
                                referent = reference()
                                if referent is None:
                                    lines.append("        sync: weakreaf no more available")
                                else:
                                    format_referrers(referent, limit=4,
                                        caption="sync: %s, references:" % describe_object(referent),
                                        indent="        ", into=lines)
                            break
                        log.write("\n".join(lines))
                    else:
                        log.write("No primary objects to track")
                    self._primaries_cache = primaries

            if settings.MANUAL_GARBAGE_COLLECTING:
                gc.collect()

    # scheduling

    def schedule(self, entity):
        with self._lock:
            self._queue.add(entity)
            if self._daemon is None:
                self.start_daemon()

    def unschedule(self, entity):
        with self._lock:
            self._queue.discard(entity)

    # preparing

    def prepare_type_infrastructure(self, uuid):
        managers.resource_manager.invalidate_resources(uuid)
        for category in (file_access.TYPE, file_access.RESOURCE):
            managers.file_manager.prepare_directory(category, uuid, cleanup=True)

    def prepare_application_infrastructure(self, uuid):
        managers.resource_manager.invalidate_resources(uuid)
        managers.database_manager.delete_database(uuid)
        for category in (file_access.APPLICATION, file_access.RESOURCE, file_access.DATABASE,
                file_access.LIBRARY, file_access.CACHE, file_access.STORAGE):
            managers.file_manager.prepare_directory(category, uuid, cleanup=True)

    # cleanupping

    def cleanup_type_infrastructure(self, uuid):
        entities = (file_access.TYPE, file_access.RESOURCE)
        for category in entities:
            managers.file_manager.cleanup_directory(category, uuid, remove=True)

    def cleanup_application_infrastructure(self, uuid, remove_databases=True, remove_storage=True):
        entities = [file_access.APPLICATION, file_access.RESOURCE, file_access.LIBRARY, file_access.CACHE]
        if remove_databases:
            entities.append(file_access.DATABASE)
            managers.database_manager.delete_database(uuid)
        if remove_storage:
            entities.append(file_access.STORAGE)
        for category in entities:
            managers.file_manager.cleanup_directory(category, uuid, remove=True)

    # creation

    def create_application(self, name=DEFAULT_APPLICATION_NAME):

        def cleanup(uuid):
            self.cleanup_application_infrastructure(uuid)
            if uuid in self._applications:
                del self._applications[uuid]

        application = self._applications.new(name=name)
        log.write("create new application %s" % application)
        try:
            self.prepare_application_infrastructure(application.id)
            return application
        except BaseException:
            cleanup(application.id)
            raise

    # updating

    def update_application(self, filename):
        tmpldapdir = ""
        tmpdbdir = ""  # directory for saving databases
        tmpstordir = ""  # directory for saving storage
        tmpresdir = ""  # directory for saving resources
        tmpappdir = ""  # directory for saving application
        err_mess = ""

        try:
            f = open(filename, "rb")
            some = f.read(1024)
            f.close()
            rexp = re.compile(r"\<id\>(.+)\<\/id\>", re.IGNORECASE)
            subject = rexp.search(some)
            if subject:
                appid = subject.groups()[0].strip()
                debug("Update application id=\"%s\"" % appid)
            else:
                raise Exception("Application XML-file is corrupted - unable to find application ID")

            debug("Check application...")
            err_mess = ". Try to INSTALL the new version instead of UPDATE"
            try:
                app = managers.memory.applications[appid]
            except Exception as e:
                raise Exception(str(e))

            # temporal copy of installed application
            debug("Save installed version...")
            err_mess = ". Unable to save previous version of application"
            tmpappdir = tempfile.mkdtemp("", "appupdate_", VDOM_CONFIG["TEMP-DIRECTORY"])
            app.export(filename=os.path.join(tmpappdir, app.id + ".xml"))
        except Exception as e:
            if tmpappdir:
                shutil.rmtree(tmpappdir, ignore_errors=True)
            import traceback
            traceback.print_exc(file=debugfile)
            raise Exception(str(e) + err_mess)

        # save databases in temp dir
        debug("Save current databases...")
        dbs = {}
        try:
            tmpdbdir = tempfile.mkdtemp("", "appupdate_", VDOM_CONFIG["TEMP-DIRECTORY"])
            r = managers.database_manager.list_databases(appid)
            for item in r:
                try:
                    obj = managers.database_manager.get_database(appid, item)
                    con = sqlite3.connect(tmpdbdir + "/" + obj.filename)
                    obj.backup_data(con)
                    con.close()
                    dbs[tmpdbdir + "/" + obj.filename] = {
                        "id": obj.id,
                        "name": obj.name,
                        "owner_id": obj.owner_id,
                        "type": "sqlite"
                    }
                    debug("Database %s saved" % obj.name)
                except:
                    pass
        except:
            pass

        debug("Save storage...")
        try:
            tmpstordir = tempfile.mkdtemp("", "appupdate_", VDOM_CONFIG["TEMP-DIRECTORY"])
            storage_dir = os.path.join(settings.STORAGE_LOCATION, appid)
            copy_tree(storage_dir, tmpstordir)
        except:
            pass

        # save resources in temp dir
        debug("Save current resources...")
        res_numb = 0
        try:
            tmpresdir = tempfile.mkdtemp("", "appupdate_", VDOM_CONFIG["TEMP-DIRECTORY"])
            rpath1 = os.path.join(settings.RESOURCES_LOCATION, appid)
            lst = managers.resource_manager.list_resources(appid)
            for ll in lst:
                try:
                    ro = managers.resource_manager.get_resource(appid, ll)
                    if not ro.dependences:
                        shutil.copy2(rpath1 + "/" + ro.filename, tmpresdir)
                        res_numb += 1
                except:
                    pass
        except:
            pass
        debug("%s resources saved" % str(res_numb))

        # save ldap in temp dir
        debug("Save current ldap...")
        from subprocess import Popen, PIPE
        import shlex
        try:
            tmpldapdir = tempfile.mkdtemp("", "appupdate_", VDOM_CONFIG["TEMP-DIRECTORY"])
            cmd = """sh /opt/boot/ldap_backup.sh -g %s -b -o %s""" % (appid, os.path.abspath(tmpldapdir))
            out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
            out.wait()
        except:
            pass

        # uninstall application but keep databases
        debug("Uninstall current version...")
        try:
            app.uninstall()
        except Exception:
            # nothing deleted (no del rights) - temp folders to be removed
            if tmpappdir:
                shutil.rmtree(tmpappdir, ignore_errors=True)
            if tmpdbdir:
                shutil.rmtree(tmpdbdir, ignore_errors=True)
            if tmpstordir:
                shutil.rmtree(tmpldapdir, ignore_errors=True)
            if tmpresdir:
                shutil.rmtree(tmpresdir, ignore_errors=True)
            if tmpldapdir:
                shutil.rmtree(tmpldapdir, ignore_errors=True)
            raise

        # install new version
        debug("Install new version...")
        try:
            subject = self.install_application(filename=filename)
        except Exception as e:
            import traceback
            traceback.print_exc(file=debugfile)
        if subject is None:
            if tmpappdir:
                shutil.rmtree(tmpappdir, ignore_errors=True)
            if tmpdbdir:
                shutil.rmtree(tmpdbdir, ignore_errors=True)
            if tmpstordir:
                shutil.rmtree(tmpldapdir, ignore_errors=True)
            if tmpresdir:
                shutil.rmtree(tmpresdir, ignore_errors=True)
            if tmpldapdir:
                shutil.rmtree(tmpldapdir, ignore_errors=True)

        app_exist = True
        keep_backup = False
        if subject is None:  # update error, restore previous version
            debug("Install error, restore previous version...")
            err_mess = "Unable to install new version - previous version seems to be not removed"
            app_exist = False
            try:
                rest_path = os.path.join(tmpappdir, "%s.xml" % appid)
                subject = managers.xml_manager.import_application(rest_path, ignore_version=True)
                if not subject[0]:
                    subject = (None, err_mess + ". " + subject[1] + ". Please, contact your dealer")
                    keep_backup = True
                else:
                    debug("Restored successfully")
                    app_exist = True
                    subject = (None, err_mess + ". Previous version restored successfully")
            except Exception as e:
                import traceback
                traceback.print_exc(file=debugfile)
                subject = (None, err_mess + str(e))

        else:  # update successful
            debug("Installed successfully")

        if app_exist:
            # restore databases
            debug("Restore databases...")
            try:
                # removing databases that we already had before
                for old_db in dbs.values():
                    if managers.database_manager.check_database(appid, old_db["id"]):
                        pass #keep old db for safety reasons
                        #managers.database_manager.delete_database(appid, old_db["id"])
            except:
                pass
            for path in dbs:
                try:
                    f = open(path, "rb")
                    data = f.read()
                    f.close()
                    managers.database_manager.add_database(appid, dbs[path], data)
                except:
                    pass

            debug("Restore storage...")
            try:
                storage_dir = os.path.join(settings.STORAGE_LOCATION, appid)
                copy_tree(tmpstordir, storage_dir)
            except:
                pass

            # restore resources
            debug("Restore resources...")
            try:
                os.mkdir(rpath1)
            except:
                pass
            r2 = os.listdir(tmpresdir)
            for item in r2:
                try:
                    shutil.copy2(os.path.join(tmpresdir, item), os.path.join(rpath1, item))
                except:
                    pass
            # restore ldap
            try:
                cmd = """sh /opt/boot/ldap_backup.sh -g %s -r -i %s""" % (appid, tmpldapdir)
                out = Popen(shlex.split(cmd), stdin=PIPE, bufsize=-1, stdout=PIPE, stderr=PIPE, close_fds=True)
                out.wait()
            except:
                pass

        if tmpappdir and not keep_backup:
            shutil.rmtree(tmpappdir, ignore_errors=True)
        if tmpstordir and not keep_backup:
            shutil.rmtree(tmpldapdir, ignore_errors=True)
        if tmpresdir and not keep_backup:
            shutil.rmtree(tmpresdir, ignore_errors=True)
        if tmpldapdir and not keep_backup:
            shutil.rmtree(tmpldapdir, ignore_errors=True)
        return subject

    # installation

    def install_type(self, value=None, file=None, filename=None, into=None):

        def cleanup(uuid):
            if uuid:
                self.cleanup_type_infrastructure(uuid)
                if uuid in self._types:
                    del self._types[uuid]

        def on_information(type):
            if managers.file_manager.exists(file_access.TYPE, type.id):
                raise AlreadyExistsError("Type already installed")
            context.uuid = type.id
            self.prepare_type_infrastructure(type.id)

        if value:
            description = "string"
        elif filename:
            description = os.path.basename(filename)
        else:
            try:
                description = file.name
            except AttributeError:
                description = "file"

        log.write("Install type from %s" % description)
        parser = Parser(builder=type_builder, notify=True, options=on_information)
        context = Structure(uuid=None)
        try:
            if value:
                type = parser.parse(value.encode("utf8") if isinstance(value, str) else value)
            elif filename:
                type = parser.parse(filename=filename)
            else:
                type = parser.parse(file=file)

            if parser.report:
                if into is None:
                    log.warning("Install type notifications")
                    for lineno, message in parser.report:
                        log.warning("    %s, line %s" % (message, lineno))
                else:
                    for lineno, message in parser.report:
                        into.append((lineno, message))

            type.save()
            self._types.save()
            return type
        except AlreadyExistsError as error:
            raise
        except ParsingException as error:
            cleanup(context.uuid)
            raise Exception("Unable to parse %s, line %s: %s" % (description, error.lineno, error))
        except IOError as error:
            cleanup(context.uuid)
            raise Exception("Unable to read from %s: %s" % (description, error.strerror))
        except:  # noqa
            cleanup(context.uuid)
            raise

    def install_application(self, value=None, file=None, filename=None, into=None):

        def cleanup(uuid):
            if uuid:
                self.cleanup_application_infrastructure(uuid)
                if uuid in self._applications:
                    del self._applications[uuid]

        def on_information(application):
            if managers.file_manager.exists(file_access.APPLICATION, application.id):
                raise AlreadyExistsError("Application already installed")
            context.uuid = application.id
            self.prepare_application_infrastructure(application.id)
            # TODO: ENABLE THIS LATER
            # if application.server_version and VDOM_server_version < application.server_version:
            #     raise Exception("Server version %s is unsuitable for this application %s" % (VDOM_server_version, application.server_version))
            # TODO: License key...

        if value:
            description = "string"
        elif filename:
            description = os.path.basename(filename)
        else:
            try:
                description = file.name
            except AttributeError:
                description = "file"

        log.write("Install application from %s" % description)
        parser = Parser(builder=application_builder, notify=True, options=on_information)
        context = Structure(uuid=None)
        try:
            if value:
                application = parser.parse(value.encode("utf8") if isinstance(value, str) else value)
            elif filename:
                application = parser.parse(filename=filename)
            else:
                application = parser.parse(file=file)

            if parser.report:
                if into is None:
                    log.warning("Install application notifications")
                    for lineno, message in parser.report:
                        log.warning("    %s, line %s" % (message, lineno))
                else:
                    for lineno, message in parser.report:
                        into.append((lineno, message))

            # TODO: check this later - why?
            application.unimport_libraries()
            application.save()
            return application
        except AlreadyExistsError as error:
            raise
        except ParsingException as error:
            cleanup(context.uuid)
            raise Exception("Unable to parse %s, line %s: %s" % (description, error.lineno, error))
        except IOError as error:
            cleanup(context.uuid)
            raise Exception("Unable to read %s: %s" % (description, error.strerror))
        except:  # noqa
            cleanup(context.uuid)
            raise

    # loading

    def load_type(self, uuid, silently=False):
        log.write("Load type %s \n" % uuid)
        location = managers.file_manager.locate(file_access.TYPE, uuid, settings.TYPE_FILENAME)
        parser = Parser(builder=type_builder, notify=True)
        try:
            type = parser.parse(filename=location)
            if not silently:
                log.write("Load %s as %s" % (type, type.name))
            if parser.report:
                log.warning("Load %s notifications" % type)
                for lineno, message in parser.report:
                    log.warning("    %s at line %s" % (message, lineno))
            return type
        except IOError as error:
            raise Exception("Unable to read from \"%s\": %s" % (os.path.basename(location), error.strerror))
        except ParsingException as error:
            raise Exception("Unable to parse \"%s\", line %s: %s" % (os.path.basename(location), error.lineno, error))

    def load_application(self, uuid, silently=False):
        log.write("Load application %s\n" % uuid)
        location = managers.file_manager.locate(file_access.APPLICATION, uuid, settings.APPLICATION_FILENAME)
        parser = Parser(builder=application_builder, notify=True)
        try:
            application = parser.parse(filename=location)
            if not silently or parser.report:
                log.write("Load %s" % application)
                for lineno, message in parser.report:
                    log.warning("    %s at line %s" % (message, lineno))
            return application
        except IOError as error:
            raise Exception("Unable to read from \"%s\": %s" % (os.path.basename(location), error.strerror))
        except ParsingException as error:
            raise Exception("Unable to parse \"%s\", line %s: %s" % (os.path.basename(location), error.lineno, error))

    # cleaning

    def track(self, object, sync=None):
        if object.primary is object:
            if sync is not None:
                sync = ref(sync, lambda reference: self._release_queue.add(object))
            managers.memory._primaries[object] = sync
            if self._cleaner is None:
                self.start_cleaner()

    def release(self, object):
        self._release_queue.add(object)
        if self._cleaner is None:
            self.start_cleaner()

    # auxiliary

    def __repr__(self):
        return "<memory at 0x%08X>" % id(self)


VDOM_memory = Memory
