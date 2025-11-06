from __future__ import absolute_import
from . import install
from . import uninstall

from .auxiliary.constants import TYPE, APPLICATION, EXTENSION, TYPES
from .auxiliary import section, show, warn, detect, locate_repository, is_entity_name


def updatetype(filename, select=False):
    # entity = detect(filename)
    # if entity is TYPE:
    uninstall.run(filename, select)
    install.run(filename, select)
    # else:
    #     warn("not an type %s" % filename)


def run(location, select=False):
    """
    reinstall application or type
    :arg location: input filename with application or type or directory to search
    :key switch select: select application as default
    """
    if not location:
        warn("no such type in repository: %s" % location)
        return
    updatetype(location, select=select)