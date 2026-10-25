"""/bluedynamic.py: the transport and the rendering of BlueDynamic.

    ?t=<ticket>              the player: a BlueMail, or a composer, in an iframe
                             of ProAdmin's mail view (contract §4.1)
    ?api=preuve&f=&defi=     the proof of the host (§2.3)
    ?api=composer            the mail a composer made, signed (§5)
    ?api=service             a service of a provider, for an application (§9.3)

The interface is the plugin's, as the EAC of ProMail had it: the plugin
answers a WHOLEXML (VDOMXML and E2VDOM actions), which travels as data and is
evaluated here by the VDOM engine, nothing installed beforehand. The page is a
virtual tree made for the session (an htmlcontainer holding a dynamicvdom, the
type ProMail's eacviewer is made of); the dynamicvdom loads the plugin's
VDOMXML and actions on the fly. An event the plugin declared reaches the
dynamicvdom through its catchEvent, which raises "eventcaught" to the server:
e2vdom.py hands it here, the plugin answers the next WHOLEXML, and the
dynamicvdom is rendered again in place.

The plugin is reached by an ordinary VDOM API call to its application (§8),
in this very request: the API container's action runs with the BlueMail
session, reads its JSON in xml_data and answers in session["response"] (or
returns its answer), as for /restapi.py.

Everything that does not need a request lives in utils/bluedynamic.py.
"""
import json
from xml.sax.saxutils import escape as xml_escape

import managers
import settings
from utils import bluedynamic
from utils.bluedynamic import BlueDynamicError


# the page made for a BlueMail session: the plugin's interface goes into the
# dynamicvdom's vdomxml and vdomactions attributes. rendererrormsg: a VDOMXML
# the engine cannot evaluate shows these words, not the trace and the source
# that the type shows by default.
PAGE = ('<HTMLCONTAINER name="bluemail" title="BlueMail">'
        '<DYNAMICVDOM name="bluedynamic" top="0" left="0" width="{width}" height="{height}" overflow="3"'
        ' rendererrormsg="Ce BlueMail ne peut pas &#234;tre affich&#233;."/>'
        '</HTMLCONTAINER>')
DYNAMIC_NAME = "bluedynamic"
CAUGHT_EVENT = "eventcaught"
DEFAULT_SIZE = 800, 600

# what the dynamicvdom shows when the plugin fails, and once a composition
# is over (the page then tells ProAdmin's view, §4.2)
MESSAGE = ('<CONTAINER name="bluedynamic_message" top="0" left="0" width="{width}" height="80">'
           '<HYPERTEXT name="texte" top="10" left="10" width="{inner}" height="60">'
           '<Attribute Name="htmlcode">{html}</Attribute></HYPERTEXT></CONTAINER>')
COMPOSED = ('<script>(function(){{var m={message};{origins}.forEach(function(o){{'
            'try{{window.parent.postMessage(m,o)}}catch(e){{}}}});}})();</script>')
# the height of what the plugin shows, told to the frame (§4.2, "hauteur"): the
# page itself is as tall as its dynamicvdom, so the leaves are measured; the
# frame then fits them, and the page does not scroll. A leaf in a fixed element
# (the "Loading..." of the runtime, a dialog) follows the frame, not the content:
# measured, it would grow the frame by 16 px at each round.
SIZER = ('<style>html,body{{overflow:hidden;margin:0}}</style><script>(function(){{var O={origins},d=-1,t=0;'
         'function f(e){{for(;e&&e!==document.body;e=e.parentElement)if(getComputedStyle(e).position==="fixed")return 1;return 0;}}'
         'function h(){{var b=0,a=document.body.getElementsByTagName("*");'
         'for(var i=0;i<a.length;i++){{if(a[i].children.length)continue;var r=a[i].getBoundingClientRect();'
         'if(r.width&&r.height&&r.bottom>b&&!f(a[i]))b=r.bottom;}}'
         'b=Math.ceil(b+window.scrollY+16);if(b===d)return;d=b;'
         'O.forEach(function(o){{try{{window.parent.postMessage({{bd:"hauteur",px:b}},o)}}catch(e){{}}}});}}'
         'function p(){{clearTimeout(t);t=setTimeout(h,60);}}'
         'window.addEventListener("load",p);window.addEventListener("resize",p);'
         'new MutationObserver(p).observe(document.body,{{childList:true,subtree:true,characterData:true}});p();}})();</script>')


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


def refuse(request, error, page=False, claims=None):
    debug("BlueDynamic: %s (%s)" % (error, error.motif))
    if page:
        # in the iframe: a few words a person can read. A genuine ticket opened
        # again carries its claims: the frame may show it, and asks its view
        # for a new ticket ({bd: "rafraichir"}).
        claims = claims or getattr(error, "claims", None)
        again = ""
        if error.motif == "rejoue" and claims:
            allowed = [each for each in (bluedynamic.origine(value) for value in claims.get("origines") or []) if each]
            again = COMPOSED.format(message=json.dumps({"bd": "rafraichir"}), origins=json.dumps(allowed))
        body = ("<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>BlueMail</title></head>"
                "<body style=\"font-family:sans-serif;color:#555\"><p>%s</p>%s</body></html>"
                % (xml_escape(message_for(error)), again))
        headers = bluedynamic.headers((claims or {}).get("origines"))
        answer(request, error.code, body, "text/html; charset=utf-8", headers)
    else:
        answer(request, error.code, json.dumps({"ok": False, "motif": error.motif}),
               headers={"Cache-Control": "no-store"})


def message_for(error):
    if error.motif == "expire":
        return "Ce BlueMail a expiré."
    if error.motif == "rejoue":
        return "Ouverture du BlueMail… Si rien ne s'affiche, rouvrez le message."
    if error.motif in ("plugin", "wholexml", "rendu", "application"):
        return "Ce BlueMail ne peut pas être affiché pour le moment."
    return "Ce BlueMail ne peut pas être ouvert (%s)." % error.motif


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


def language(request):
    value = request.headers().headers().get("accept-language") or ""
    value = value.split(",")[0].split("-")[0].strip().lower()
    return value if value.isalpha() and len(value) == 2 else "fr"


# the plugin (§8)

def call_plugin(request, provider, action, data):
    """call(api.conteneur, api[action], JSON) on api.application, in this
    request: what the plugin answered, unparsed."""
    api = provider.api
    try:
        application = managers.memory.applications[api["application"]]
    except Exception:
        raise BlueDynamicError("application", "Application of %s not installed" % provider.id, 503)
    if not application.active:
        raise BlueDynamicError("application", "Application of %s not active" % provider.id, 503)
    container = application.objects.get(api["conteneur"]) or application.objects.catalog.get(api["conteneur"])
    if container is None:
        raise BlueDynamicError("application", "No container %s" % api["conteneur"], 503)
    executable = container.actions.get(api[action])
    if executable is None:
        raise BlueDynamicError("application", "No action %s in %s" % (api[action], api["conteneur"]), 503)

    arguments = request.arguments()
    saved_arguments, saved_container = arguments.arguments(), request.container_id
    session = request.session()
    session.remove("response")
    arguments.arguments({"xml_param": [""], "xml_data": [json.dumps(data, ensure_ascii=False)]})
    request.container_id = container.id
    try:
        result = managers.engine.execute(executable)
        reply = session.value("response") or result
        written = request.output()  # an action that wrote its answer
        if not reply and written:
            reply = written
    except BlueDynamicError:
        raise
    except Exception as error:
        debug("BlueDynamic: %s of %s failed: %s" % (action, provider.id, error))
        raise BlueDynamicError("plugin", "The plugin failed: %s" % error, 502)
    finally:
        session.remove("response")
        arguments.arguments(saved_arguments)
        request.container_id = saved_container
    return reply


def plugin_data(request, scope, **more):
    data = {"ticket": scope["charge"], "session": request.session().id(), "langue": language(request)}
    if scope.get("jeton"):
        data["jeton"] = scope["jeton"]
    data.update(more)
    return data


# the page

def size(provider, claims):
    """The composer's declared size when composing (the ticket names it; an
    older ticket, the first one taking its command); the default otherwise."""
    if claims.get("mode") == "composer":
        for each in provider.manifest.get("composeurs") or []:
            if (each.get("id") == claims["composeur"]) if claims.get("composeur") else (claims.get("commande") in (each.get("commandes") or [])):
                taille = each.get("taille") or {}
                try:
                    return int(taille.get("largeur") or DEFAULT_SIZE[0]), int(taille.get("hauteur") or DEFAULT_SIZE[1])
                except (TypeError, ValueError):
                    break
    return DEFAULT_SIZE


def make_page(application, width, height):
    """The virtual page of a session: an htmlcontainer and its dynamicvdom,
    whose "eventcaught" goes to the server. Nothing is stored: a virtual
    object lives as long as the session that holds it."""
    from memory import vdomxml
    root = vdomxml.loads(PAGE.format(width=width, height=height), application)
    dynamic = root.objects.get(DYNAMIC_NAME)
    action = dynamic.actions.new(DYNAMIC_NAME)
    dynamic.events.new(CAUGHT_EVENT).callees.append(action)
    return root, dynamic


def show(dynamic, vdomxml, events=""):
    """The plugin's interface into the dynamicvdom. What it loaded for the
    previous one goes first: being virtual as it is, those objects are its
    children, and would be rendered beside the new ones."""
    for identifier in list(dynamic.objects):
        del dynamic.objects[identifier]
    dynamic.attributes.update({"vdomxml": vdomxml, "vdomactions": events or ""})


def message(dynamic, html, width=DEFAULT_SIZE[0]):
    show(dynamic, MESSAGE.format(width=width, inner=max(width - 20, 100), html=xml_escape(html)))


def sized(output, allowed):
    """The page with SIZER before its </body> (or at its end)."""
    script = SIZER.format(origins=json.dumps(allowed)).encode("utf-8")
    at = output.rfind(b"</body>")
    return output[:at] + script + output[at:] if at >= 0 else output + script


def follow(scope, dynamic, reply):
    """Put what the plugin answered into the page."""
    kind = reply[0]
    if kind == "wholexml":
        show(dynamic, reply[1], reply[2])
    elif kind in ("compose", "mail"):
        jeton = bluedynamic.render_mail(scope, reply[1])
        allowed = [each for each in (bluedynamic.origine(value) for value in scope["charge"].get("origines") or []) if each]
        script = COMPOSED.format(message=json.dumps({"bd": "compose", "jeton": jeton}), origins=json.dumps(allowed))
        message(dynamic, script + "<p>Le BlueMail est prêt.</p>", scope["taille"][0])


def bluedynamic_session(request, claims, provider, application):
    """A new session for this ticket alone (§4.1, step 3). The visitor's own
    session, if the iframe carried its cookie, is kept and its cookie is not
    overwritten: the BlueMail session travels in the page (SESSION_ID)."""
    previous = request.session()
    sid = managers.session_manager.create_session()
    request.set_session_id(sid, remove_old=disposable(previous))
    request.sid = sid
    session = request.session()
    session.context["application_id"] = application.id
    session.bd_scope = bluedynamic.scope(claims, application.id, sid)
    session["bd"] = claims
    cookies = request.response_cookies()
    if "sid" in cookies:
        del cookies["sid"]
    return session


def play(request, ticket):
    claims = None
    try:
        claims, provider = bluedynamic.open_ticket(ticket, origins(request))
        try:
            application = managers.memory.applications[provider.api["application"]]
        except Exception:
            raise BlueDynamicError("application", "Application of %s not installed" % provider.id, 503)
        request.set_application_id(application.id)
        session = bluedynamic_session(request, claims, provider, application)
        scope = session.bd_scope

        reply = bluedynamic.parse_reply(call_plugin(request, provider, "get", plugin_data(request, scope)))
        if reply[0] != "wholexml":
            raise BlueDynamicError("plugin", "get answers a WHOLEXML", 502)
        scope["taille"] = size(provider, claims)
        root, dynamic = make_page(application, *scope["taille"])
        scope["page"], scope["dynamique"] = root, dynamic
        show(dynamic, reply[1], reply[2])

        request.container_id = root.id
        request.request_type = "vdom"
        result = managers.engine.render(root)
        if request.redirect_to:
            request.redirect_to = None
            raise BlueDynamicError("rendu", "The page redirected", 500)
        output = request.output() or (result or "").encode("utf-8")
        allowed = [each for each in (bluedynamic.origine(value) for value in claims.get("origines") or []) if each]
        answer(request, 200, sized(output, allowed), "text/html; charset=utf-8", bluedynamic.headers(claims.get("origines")))
    except BlueDynamicError as error:
        refuse(request, error, page=True, claims=claims)


def events(request, ev, scope):
    """The events of a BlueMail page (from e2vdom.py): each "eventcaught" of
    its dynamicvdom goes to the plugin's event action, and the dynamicvdom is
    rendered again with the answer. Returns e2vdom's result: {object id:
    (html, parent id, container kind, type id)}. Nothing else of the page,
    and nothing of any other object, is acted on."""
    dynamic = scope.get("dynamique")
    result = {}
    if dynamic is None:
        return result
    provider = bluedynamic.Provider.find(scope["fournisseur"])
    for event_info in ev.events:
        if event_info.event_source_id != dynamic.id or event_info.event_name != CAUGHT_EVENT:
            debug("Event: BlueMail session used out of its interface")
            continue
        parameters = event_info.event_parameters
        name = _parameter(parameters, "customName")
        try:
            values = json.loads(_parameter(parameters, "parameters") or "{}")
        except ValueError:
            values = {}
        objet, _, nom = name.rpartition(":")
        evenement = {"objet": objet, "nom": nom, "donnees": values}
        try:
            if provider is None:
                raise BlueDynamicError("fournisseur", "Provider gone", 404)
            reply = bluedynamic.parse_reply(call_plugin(
                request, provider, "event", plugin_data(request, scope, evenement=evenement)))
            follow(scope, dynamic, reply)
        except BlueDynamicError as error:
            debug("BlueDynamic: event %s: %s (%s)" % (name, error, error.motif))
            message(dynamic, message_for(error), scope["taille"][0])
        html = managers.engine.render(dynamic)
        result[dynamic.id] = (html, scope["page"].id, dynamic.type.container, dynamic.type.id)
    return result


def _parameter(parameters, name):
    value = parameters.get(name) or [b""]
    value = value[0] if isinstance(value, list) else value
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)


# the API ProAdmin calls

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

    def ask_plugin(provider, sid):
        # the plugin's compose action, in the composer's own session
        session = managers.session_manager[sid] if sid else None
        if session is None or not session.bd_scope:
            raise BlueDynamicError("session", "The composition is over", 410)
        request.set_session_id(sid, remove_old=disposable(request.session()))
        request.sid = sid
        cookies = request.response_cookies()
        if "sid" in cookies:
            del cookies["sid"]
        reply = bluedynamic.parse_reply(call_plugin(request, provider, "compose", plugin_data(request, session.bd_scope)))
        if reply[0] not in ("mail", "compose"):
            raise BlueDynamicError("plugin", "compose answers a mail", 502)
        return reply[1]

    token = bluedynamic.compose(authorization[len("Bearer "):].strip(), argument(request, "jeton"),
                                origins(request), ask_plugin)
    answer(request, 200, token, "application/jose", {"Cache-Control": "no-store"})


def serve(request):
    """api=service (§9.3): the plugin's service action, in a session of its
    own (no page, no reader), its answer signed with the provider's key."""
    if request.method != "post":
        raise BlueDynamicError("methode", "POST only", 405)
    authorization = request.headers().headers().get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise BlueDynamicError("signature", "No bearer token", 401)

    def ask_plugin(provider, charge, donnees):
        try:
            application = managers.memory.applications[provider.api["application"]]
        except Exception:
            raise BlueDynamicError("application", "Application of %s not installed" % provider.id, 503)
        request.set_application_id(application.id)
        previous = request.session()
        sid = managers.session_manager.create_session()
        request.set_session_id(sid, remove_old=disposable(previous))
        request.sid = sid
        session = request.session()
        session.context["application_id"] = application.id
        session.bd_scope = bluedynamic.service_scope(provider, charge)
        session["bd"] = charge
        cookies = request.response_cookies()
        if "sid" in cookies:
            del cookies["sid"]
        return call_plugin(request, provider, "service", donnees)

    token = bluedynamic.service(authorization[len("Bearer "):].strip(), argument(request, "demande"),
                                origins(request), ask_plugin)
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
        elif api == "service":
            serve(request)
        else:
            raise BlueDynamicError("requete", "Nothing asked", 400)
    except BlueDynamicError as error:
        refuse(request, error)
