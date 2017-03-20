
import os
import os.path

from threading import RLock

import settings
import managers
import file_access

from logs import log
from utils.structure import Structure
from utils.properties import roproperty  # rwproperty
from utils.tracing import format_exception_trace
from utils.parsing import Parser, ParsingException

from .constants import APPLICATION_START_CONTEXT
from .type import type_builder, MemoryTypes
from .application import application_builder, MemoryApplications
from .daemon import MemoryWriter


class AlreadyExistsError(Exception):
    pass


class Memory(object):

    def __init__(self):
        self._lock = RLock()
        self._queue = set()
        self._daemon = None

        self._types = MemoryTypes(self)
        self._applications = MemoryApplications(self)

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

    lock = roproperty("_lock")
    types = roproperty("_types")
    applications = roproperty("_applications")

    # threading

    def start_daemon(self):
        if self._daemon is None:
            self._daemon = MemoryWriter(self)
            self._daemon.start()
        return self._daemon

    def work(self):
        with self._lock:
            entities = tuple(self._queue)
            self._queue.clear()

        for entity in entities:
            try:
                entity.save()
            except:
                log.error("Unable to save %s, details below\n%s" %
                    (entity, format_exception_trace(locals=True, separate=True)))

    # scheduling

    def schedule(self, entity):
        with self._lock:
            self._queue.add(entity)
            if self._daemon is None:
                self.start_daemon()

    def unschedule(self, entity):
        with self._lock:
            self._queue.discard(entity)

    # cleanupping

    def cleanup_type(self, uuid):
        entities = (file_access.TYPE, file_access.RESOURCE)
        for category in entities:
            managers.file_manager.cleanup_directory(category, uuid, remove=True)

    def cleanup_application(self, uuid, remove_databases=True, remove_storage=True):
        entities = [file_access.APPLICATION, file_access.RESOURCE, file_access.LIBRARY, file_access.CACHE]
        if remove_databases:
            entities.append(file_access.DATABASE)
            managers.database_manager.delete_database(uuid)
        if remove_storage:
            entities.append(file_access.STORAGE)
        for category in entities:
            managers.file_manager.cleanup_directory(category, uuid, remove=True)

    # installation

    def install_type(self, filename, into=None):

        def cleanup(uuid):
            if uuid:
                self.cleanup_type(uuid)

        def on_information(type):
            if managers.file_manager.exists(file_access.TYPE, type.id):
                raise AlreadyExistsError("Type already installed")
            context.uuid = type.id
            managers.resource_manager.invalidate_resources(type.id)
            for category in (file_access.TYPE, file_access.RESOURCE):
                managers.file_manager.prepare_directory(category, type.id, cleanup=True)

        log.write("Install type from %s" % filename)
        parser = Parser(builder=type_builder, notify=True, options=on_information)
        context = Structure(uuid=None)
        try:
            type = parser.parse(filename=filename)
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
            raise Exception("Unable to parse %s, line %s: %s" % (os.path.basename(filename), error.lineno, error))
        except IOError as error:
            cleanup(context.uuid)
            raise Exception("Unable to read from \"%s\": %s" % (os.path.basename(filename), error.strerror))
        except:
            cleanup(context.uuid)
            raise

    def install_application(self, filename, into=None):

        def cleanup(uuid):
            if uuid:
                self.cleanup_application(uuid)

        def on_information(application):
            if managers.file_manager.exists(file_access.APPLICATION, application.id):
                raise AlreadyExistsError("Application already installed")
            context.uuid = application.id
            managers.resource_manager.invalidate_resources(application.id)
            managers.database_manager.delete_database(application.id)
            for category in (file_access.APPLICATION, file_access.RESOURCE, file_access.DATABASE,
                    file_access.LIBRARY, file_access.CACHE, file_access.STORAGE):
                managers.file_manager.prepare_directory(category, application.id, cleanup=True)
            # TODO: ENABLE THIS LATER
            # if application.server_version and VDOM_server_version < application.server_version:
            #     raise Exception("Server version %s is unsuitable for this application %s" % (VDOM_server_version, application.server_version))
            # TODO: License key...

        log.write("Install application from %s" % filename)
        try:
            file = managers.file_manager.open(file_access.FILE, None, filename, mode="rb")
        except IOError as error:
            log.error("Unable to open file: %s" % error)
        parser = Parser(builder=application_builder, notify=True, options=on_information)
        context = Structure(uuid=None)
        try:
            application = parser.parse(file=file)
            if parser.report:
                if into is None:
                    log.warning("Install application notifications")
                    for lineno, message in parser.report:
                        log.warning("    %s, line %s" % (message, lineno))
                else:
                    for lineno, message in parser.report:
                        into.append((lineno, message))
            application.unimport_libraries()
            application.save()
            return application
        except AlreadyExistsError as error:
            raise
        except ParsingException as error:
            cleanup(context.uuid)
            raise Exception("Unable to parse \"%s\", line %s: %s" % (os.path.basename(filename), error.lineno, error))
        except IOError as error:
            cleanup(context.uuid)
            raise Exception("Unable to read \"%s\": %s" % (os.path.basename(filename), error.strerror))
        except:
            cleanup(context.uuid)
            raise

    # loading

    def load_type(self, uuid, silently=False):
        log.write("Load type %s" % uuid)
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
        log.write("Load application %s" % uuid)
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

    # auxiliary

    def __repr__(self):
        return "<memory at 0x%08X>" % id(self)


VDOM_memory = Memory
