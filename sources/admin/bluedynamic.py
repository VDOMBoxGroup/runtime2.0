"""/bluedynamic.py: the entry point of BlueDynamic on this server.

    ?t=<ticket>              the player: a BlueMail, or a composer, in an iframe
                             of ProAdmin's mail view (contract §4.1)
    ?api=preuve&f=&defi=     the proof of the host (§2.3)
    ?api=composer            the mail a composer made, signed (§5)

Everything that does not need a request lives in utils/bluedynamic.py, where
the providers, the keys and the formats are described.
"""
import json

import managers
import settings
from utils import bluedynamic
from utils.bluedynamic import BlueDynamicError
from utils.exception import VDOM_exception
from utils.tracing import show_exception_trace


def origins(request):
    """The public origins of this server: the setting, or else the Host the
    request came to (behind a proxy, set the setting)."""
    configured = [bluedynamic.origine(each) for each in settings.BLUEDYNAMIC_ORIGINS]
    configured = [each for each in configured if each]
    if configured:
        return configured
    host = request.environment().environment().get("HTTP_HOST", "")
    own = bluedynamic.origine("https://" + host)
    return [own] if own else []


def answer(request, code, body, content_type="application/json", headers=None):
    """Send the whole response now, with its status. Binary, so the handler
    adds nothing after it (see request.send_file)."""
    if isinstance(body, str):
        body = body.encode("utf-8")
    for name, value in (headers or {}).items():
        request.add_header(name, value)
    request.add_header("Content-Type", content_type)
    request.add_header("Content-Length", str(len(body)))
    request.binary(True)
    request.write(body)
    request.retcode = code
    request.set_nocache()


def refuse(request, error):
    debug("BlueDynamic: %s (%s)" % (error, error.motif))
    answer(request, error.code, json.dumps({"ok": False, "motif": error.motif}),
           headers={"Cache-Control": "no-store"})


def argument(request, name):
    value = request.arguments().arguments().get(name)
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    return value


def disposable(session):
    """A session nothing used yet: the one made for this very request."""
    return session is not None and not session.on_start_executed \
        and not session.user and not session.bd_scope and len(session) == 0


def bluedynamic_session(request, claims, application, container):
    """A new session for this ticket alone (§4.1, step 3). The visitor's own
    session, if the iframe carried its cookie, is kept and its cookie is not
    overwritten: the BlueMail session travels in the page (SESSION_ID)."""
    previous = request.session()
    sid = managers.session_manager.create_session()
    request.set_session_id(sid, remove_old=disposable(previous))
    request.sid = sid
    session = request.session()
    session.context["application_id"] = application.id
    session.bd_scope = bluedynamic.scope(claims, application.id, container.id)
    session["bd"] = claims
    cookies = request.response_cookies()
    if "sid" in cookies:
        del cookies["sid"]
    return session


def play(request, ticket):
    allowed = origins(request)
    claims, provider, name = bluedynamic.open_ticket(ticket, allowed)

    try:
        application = managers.memory.applications[provider.application]
    except Exception:
        raise BlueDynamicError("application", "Application of %s not installed" % provider.id, 404)
    if not application.active:
        raise BlueDynamicError("application", "Application not active", 503)
    container = application.objects.get(name) or application.objects.get(name.lower())
    if container is None or container.parent is not None:
        raise BlueDynamicError("conteneur", "Container %s is not a top level container" % name, 404)
    if not container.type.http_content_type:
        raise BlueDynamicError("conteneur", "Container %s has no content type" % name, 404)

    request.set_application_id(application.id)
    session = bluedynamic_session(request, claims, application, container)
    request.container_id = container.id
    request.request_type = "vdom"

    action = application.actions.get("sessiononstart")
    if action and action.source_code:
        managers.engine.execute(action)
    session.on_start_executed = True

    try:
        result = managers.engine.render(container, render_type=container.type.render_type.lower())
    except VDOM_exception as error:
        show_exception_trace(caption="BlueDynamic: render exception", locals=True)
        raise BlueDynamicError("rendu", str(error), 500)

    headers = bluedynamic.headers(claims.get("origines"))
    if request.redirect_to:
        # a page that sends the visitor elsewhere leaves its container: a
        # BlueMail session would be refused there anyway
        request.redirect_to = None
        raise BlueDynamicError("rendu", "The container redirected", 500)
    if request.fh:
        raise BlueDynamicError("rendu", "The container sent a file", 500)
    output = request.output()
    if not output:
        output = (result or "").encode("utf-8")
    answer(request, 200, output, container.type.http_content_type.lower(), headers)


def prove(request):
    provider = bluedynamic.Provider.find(argument(request, "f"))
    if provider is None or not provider.manifest:
        raise BlueDynamicError("fournisseur", "Unknown provider", 404)
    signature = provider.proof(argument(request, "defi"))
    answer(request, 200, json.dumps({"signature": signature}), headers={"Cache-Control": "no-store"})


def compose(request):
    if request.method != "post":
        raise BlueDynamicError("methode", "POST only", 405)
    authorization = request.headers().headers().get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise BlueDynamicError("signature", "No bearer token", 401)
    jeton = argument(request, "jeton")
    token = bluedynamic.compose(authorization[len("Bearer "):].strip(), jeton, origins(request))
    answer(request, 200, token, "application/jose", {"Cache-Control": "no-store"})


def run(request):
    try:
        api = argument(request, "api")
        ticket = argument(request, "t")
        if ticket:
            play(request, ticket)
        elif api == "preuve":
            prove(request)
        elif api == "composer":
            compose(request)
        else:
            raise BlueDynamicError("requete", "Nothing asked", 400)
    except BlueDynamicError as error:
        refuse(request, error)
