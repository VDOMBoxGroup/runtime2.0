
import settings
import managers
import file_access

from .auxiliary.constants import TYPE
from .auxiliary import section, show, locate_repository
from .install import run as install
from .uninstall import run as uninstall
from .index import run as index


def run(renew=False):
    """
    deploy runtime on the system
    :key switch renew: renew current installation
    """
    LOCATIONS = (
        ("applications", (file_access.APPLICATION, None)),
        ("types", (file_access.TYPE, None)),
        ("cache", (file_access.CACHE, None)),
        ("resources", (file_access.RESOURCE, None)),
        ("data", (file_access.FILE, None, settings.DATA_LOCATION)),
        ("databases", (file_access.DATABASE, None)),
        ("storage", (file_access.STORAGE, None)),
        ("temporary", (file_access.FILE, None, settings.TEMPORARY_LOCATION))
    )

    if renew:
        uninstall("all", yes=True)

    with section("%sinitialize directories" % ("re" if renew else "")):
        for caption, segments in LOCATIONS:
            show("prepare %s directory\n" % caption)
            managers.file_manager.prepare_directory(*segments, cleanup=False)

    install(locate_repository(TYPE))
    index()
