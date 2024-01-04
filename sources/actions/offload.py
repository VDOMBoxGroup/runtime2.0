
import os.path
import managers
import file_access

from .auxiliary.constants import TYPE, APPLICATION, REPOSITORY, TYPES, APPLICATIONS
from .auxiliary import section, show, warn, confirm, search, autocomplete, locate_repository


def run(identifier, location, by_name='false', types='false'):
    """
    offload static resources
    :arg uuid_or_name identifier: uuid or name of application
    :arg location: output file or directory
    :arg by_name: flag to output resources with real name
    :arg types: flag to output types
    """
    application = managers.memory.applications.search(identifier)
    if application is None:
        warn("not found: %s" % identifier)
        return

    if not os.path.isdir(location):
        warn("not a directory: %s" % location)
        return

    if types.lower() == 'false':
        uuids = managers.resource_manager.list_resources(application.id)
        with section("summary"):
            show("location", location)
            show("application", application)
            show("resources", len(uuids))

        with section("writing resources"):
            for uuid in uuids:
                resource = managers.resource_manager.get_resource(application.id, uuid)
                if by_name.lower() == 'true':
                    filename = os.path.join(location, resource.name)
                else:
                    filename = os.path.join(location, "%s.res" % uuid)
                show("write %s resource" % uuid) # resource.name, resource.res_format
                with managers.file_manager.open(file_access.FILE, None, filename, mode="wb") as file:
                    data = resource.get_data()
                    file.write(data)
    else:
        types = sorted(managers.memory.types.itervalues(), key=lambda item: item.name)
        for type in types:
            uuids = managers.resource_manager.list_resources(type.id)
            with section("summary"):
                show("location", location)
                show("application", application)
                show("resources", len(uuids))

            with section("writing types"):
                for uuid in uuids:
                    resource = managers.resource_manager.get_resource(application.id, uuid)
                    if by_name.lower() == 'true':
                        filename = os.path.join(location, resource.name)
                    else:
                        filename = os.path.join(location, "%s.res" % uuid)
                    show("write %s resource" % uuid) # resource.name, resource.res_format
                    with managers.file_manager.open(file_access.FILE, None, filename, mode="wb") as file:
                        data = resource.get_data()
                        file.write(data)

