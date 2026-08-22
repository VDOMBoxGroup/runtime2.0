
import managers
from .auxiliary import section, confirm, warn


def run(identifier):
    """
    delete (broken) application
    :arg uuid identifier: application uuid
    """
    if not confirm("cleanup %s" % identifier):
        return

    with section():
        try:
            managers.memory.cleanup_application_infrastructure(identifier)
        except Exception:  # noqa
            warn("unable to delete application")
            raise
