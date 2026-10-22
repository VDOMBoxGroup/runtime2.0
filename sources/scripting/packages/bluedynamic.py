"""bluedynamic: what a plugin calls to be a BlueDynamic provider.

From a python action:

    from scripting.packages import bluedynamic
    bluedynamic.declarer(manifeste)          # at each start or update
    charge = bluedynamic.ticket()            # in the container a ticket opened
    jeton = bluedynamic.rendre_mail(mail)    # at the end of a composer

From VScript, the same as BlueDynamic_Declarer, BlueDynamic_Ticket and
BlueDynamic_Rendre (vscript/wrappers/bluedynamic.py), with JSON strings.

The formats are those of ProAdmin's contract (CONTRAT_BLUEDYNAMIC.md); the
providers' folders are described in utils/bluedynamic.py.
"""
import managers
from utils import bluedynamic as core


def _application_id():
    application = managers.engine.application
    if application is None:
        application = managers.request_manager.current.application()
    if application is None:
        raise core.BlueDynamicError("application", "No application is running")
    return application.id


def _scope():
    try:
        session = managers.request_manager.current.session()
    except Exception:  # noqa - no request: no BlueMail session either
        return None
    return session.bd_scope if session is not None else None


def declarer(manifeste, cle_declaration=None, proadmin=None):
    """Record the manifest (a dict, or its JSON) of a provider served by the
    running application and declare it to ProAdmin (§2.2). The declaration
    key, once given, is kept in the provider's folder: the next calls can
    leave it out. Returns ProAdmin's answer, or {"ok": False, "motif": ...}."""
    try:
        return core.declare(_application_id(), manifeste, cle_declaration, proadmin)
    except core.BlueDynamicError as error:
        return {"ok": False, "motif": error.motif, "message": str(error)}


def ticket():
    """The claims of the ticket that opened this session (§4), or None out
    of a BlueMail session. A copy: changing it changes nothing."""
    scope = _scope()
    return dict(scope["charge"]) if scope else None


def rendre_mail(mail):
    """Keep the mail a composer made (§5: a, cc, objet, texte, html,
    application, instance, titre, expire in epoch seconds, methode, bd) and
    return the jeton the page sends to ProAdmin's view:

        window.parent.postMessage({bd: "compose", jeton: jeton}, origine)

    where origine is one of the ticket's "origines"."""
    return core.render_mail(_scope(), mail)
