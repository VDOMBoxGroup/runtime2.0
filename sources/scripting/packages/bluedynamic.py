"""bluedynamic: what a plugin, and the application that hosts it, call.

The plugin (any application that manages plugins: Tekitisy, LimeOS, ...):

    from scripting.packages import bluedynamic
    bluedynamic.declarer(manifeste)          # at each start or update
    charge = bluedynamic.ticket()            # while serving a BlueMail
    jeton = bluedynamic.rendre_mail(mail)    # the end of a composition, if
                                             # not answered by event or compose
    bluedynamic.evenement(charge)            # an event of a service (§9.4)
    charge = bluedynamic.verifier(jeton, typ)  # a receipt from ProAdmin (§9.6)

The host application, in the actions of its API container that the manifest
names (api.get, api.event, api.compose, contract §8), routes to its plugin:

    from scripting.packages import bluedynamic
    bluedynamic.recevoir("event", lambda fournisseur: mes_plugins[fournisseur])

From VScript: BlueDynamic_Declarer, BlueDynamic_Ticket, BlueDynamic_Rendre,
BlueDynamic_Evenement and BlueDynamic_Verifier
(vscript/wrappers/bluedynamic.py), with JSON strings.

The formats are those of ProAdmin's contract (CONTRAT_BLUEDYNAMIC.md); the
providers' folders are described in utils/bluedynamic.py.
"""
import json

import managers
from utils import bluedynamic as core


ACTIONS = "get", "event", "compose", "service"


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
    """Record the manifest (a dict, or its JSON) of a provider of the running
    application and declare it to ProAdmin (§2.2). Its api.application is
    this application. The declaration key, once given, is kept in the
    provider's folder: the next calls can leave it out. Returns ProAdmin's
    answer, or {"ok": False, "motif": ...}."""
    try:
        return core.declare(_application_id(), manifeste, cle_declaration, proadmin)
    except core.BlueDynamicError as error:
        return {"ok": False, "motif": error.motif, "message": str(error)}


def ticket():
    """The claims of the ticket of this BlueMail session (§4), or None out of
    one. A copy: changing it changes nothing."""
    scope = _scope()
    return dict(scope["charge"]) if scope else None


def rendre_mail(mail):
    """Keep the mail a composer made (§5: a, cc, objet, texte, html,
    application, instance, titre, expire in epoch seconds, methode, bd) and
    return the jeton the page sends to ProAdmin's view:

        window.parent.postMessage({bd: "compose", jeton: jeton}, origine)

    where origine is one of the ticket's "origines". Answering an event with
    {"bd": "compose", "mail": ...} does the same, page included."""
    return core.render_mail(_scope(), mail)


def evenement(charge):
    """Tell ProAdmin of an event of a service (§9.4): charge = {abonnement
    (bda-...), id (bde-..., the same if the event is sent again), evenement,
    donnees}. Signed with the provider's key and sent to the ProAdmin of this
    session's ticket. Returns ProAdmin's answer, or {"ok": False, "motif"}."""
    try:
        return core.event(_scope(), charge)
    except core.BlueDynamicError as error:
        return {"ok": False, "motif": error.motif, "message": str(error)}


def verifier(jeton, typ):
    """The claims of a JWS of ProAdmin (typ bd-recu, bd-destinataire or
    bd-depot) made for this session's provider, or None: what the page
    relays (a deposit receipt, the recipient a reader proved to be) is
    trusted only once verified here (§9.6)."""
    try:
        return core.verify_for_provider(_scope(), jeton, typ)
    except core.BlueDynamicError:
        return None


def recevoir(action, plugin):
    """The whole of an API action of the host (§8), for its plugin.

    `action` is "get", "event", "compose" or "service" (§9.3: donnees
    are {service, parametres, contexte}, the ticket is {mode: "service", ...}). `plugin` gives, for the provider
    id of the ticket, a function plugin(action, donnees) -> answer, where the
    answer is a WHOLEXML (text), a mail (dict), or {"bd": "compose", "mail":
    {...}} at the end of a composition; it may raise to refuse. `plugin` is
    that function's dictionary by provider id, or a function of the id.

    donnees is what the server sent (§8), with the ticket it holds: the
    ticket in the call itself is not trusted. A call made out of a BlueMail
    session (by /restapi.py, say) is refused.

    The answer goes to session["response"], as the API's usual JSON:
    ["success", answer] or ["error", motif]."""
    request = managers.request_manager.current
    session = request.session()
    scope = session.bd_scope if session is not None else None
    try:
        if action not in ACTIONS:
            raise core.BlueDynamicError("action", "Unknown action %s" % action)
        if not scope:
            raise core.BlueDynamicError("session", "Not a BlueMail session")
        try:
            donnees = json.loads(_argument(request, "xml_data") or "{}")
        except ValueError:
            raise core.BlueDynamicError("donnees", "xml_data is not JSON")
        if not isinstance(donnees, dict):
            raise core.BlueDynamicError("donnees", "xml_data is not an object")
        donnees["ticket"] = dict(scope["charge"])
        donnees["session"] = session.id()
        handler = plugin.get(scope["fournisseur"]) if isinstance(plugin, dict) else plugin(scope["fournisseur"])
        if handler is None:
            raise core.BlueDynamicError("fournisseur", "No plugin for %s" % scope["fournisseur"])
        result = ["success", handler(action, donnees)]
    except core.BlueDynamicError as error:
        result = ["error", error.motif, str(error)]
    except Exception as error:  # noqa - the plugin's own failure, said to the server
        result = ["error", "plugin", str(error)]
    session["response"] = json.dumps(result, ensure_ascii=False)
    return result


def _argument(request, name):
    value = request.arguments().arguments().get(name)
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    return value
