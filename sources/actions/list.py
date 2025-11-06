
import managers
from .auxiliary import section, show


def run():
    """
    show installed applications and types
    """
    with section("types"):
        types = sorted(iter(managers.memory.types.values()), key=lambda item: item.name)
        for vdomtype in types:
            show("%s:%s" % (vdomtype.id, vdomtype.name.lower()))

    with section("applications"):
        applications = sorted(iter(managers.memory.applications.values()), key=lambda item: item.name)
        for application in applications:
            show("%s:%s" % (application.id, application.name.lower()))
