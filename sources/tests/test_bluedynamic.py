"""BlueDynamic on the server side (utils/bluedynamic.py, admin/bluedynamic.py,
admin/e2vdom.py, scripting/packages/bluedynamic.py): tickets, proof, the
plugin's WHOLEXML rendered and its events, the composed mail, the session
kept to its own interface.

ProAdmin is played by a key pair made here and its JWKS, served by a stand-in
for fetch_json; nothing goes on the network. The host application and its
plugin are stand-ins too: the API action calls recevoir() as a real host
would, and the engine renders a VDOMXML as its own text (the evaluation by
the real engine is not what these tests look at).
"""
import base64
import json
import secrets
import time
from io import BytesIO, StringIO
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

import managers
import settings
from utils import bluedynamic as core
from utils.bluedynamic import BlueDynamicError
from session.session import VDOM_session


ISS = "https://proadmin.exemple.test"
JWKS = ISS + "/bluedynamic/jwks"
HOTE = "https://apps.exemple.fr"
APPLICATION = "11111111-2222-3333-4444-555555555555"
KID = "bdk-0123456789abcdef"

MANIFESTE = {
    "id": "vdoodle", "version": "1.0.0", "nom": {"fr": "VDoodle"},
    "hote": HOTE,
    "composeurs": [{"id": "nouveau", "nom": {"fr": "Sondage"}, "commandes": ["new", "reply"],
                    "taille": {"largeur": 720, "hauteur": 560}, "contexte": ["objet", "de"]}],
    "applications": [{"id": "sondage"}],
    "blueapps": [{"id": "gestion", "nom": {"fr": "Gestion"}}],
    "api": {"conteneur": "API"},
}

MAIL = {"a": ["marie@exemple.fr"], "objet": "Sondage", "texte": "Votez", "html": "<p>Votez</p>",
        "application": "sondage", "instance": "i-42", "titre": "Nouveau VDoodle",
        "expire": 1798761600, "methode": "new"}


def wholexml(vdomxml, events=""):
    return "<WHOLEXML><VDOMXML><![CDATA[%s]]></VDOMXML><EVENTS><![CDATA[%s]]></EVENTS></WHOLEXML>" % (vdomxml, events)


def raw(public_key):
    return public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


class ProAdmin(object):
    """The issuer: its key, its JWKS, its tokens."""

    def __init__(self):
        self.key = Ed25519PrivateKey.generate()
        self.kid = KID
        self.jwks_reads = 0

    def jwks(self):
        self.jwks_reads += 1
        return {"keys": [{"kty": "OKP", "crv": "Ed25519", "x": core.b64url(raw(self.key.public_key())),
                          "kid": self.kid, "use": "sig", "alg": "EdDSA"}]}

    def sign(self, claims, key=None, kid=None):
        return jwt.encode(claims, key or self.key, algorithm="EdDSA",
                          headers={"kid": kid or self.kid, "typ": "JWT"})

    def ticket(self, **changes):
        now = int(time.time())
        claims = {"iss": ISS, "aud": HOTE, "typ": "bd-ticket", "mode": "lire",
                  "fournisseur": "vdoodle",
                  "bd": "bd-6f1c", "application": "sondage", "instance": "i-42", "expire": False,
                  "lecteur": "lec-1", "societe": "soc-1", "origines": [ISS],
                  "iat": now, "exp": now + 300, "jti": secrets.token_hex(16)}
        claims.update(changes)
        return self.sign(claims)

    def composer(self, **changes):
        claims = dict({"mode": "composer", "commande": "new", "contexte": {"objet": "x"}}, **changes)
        return self.ticket(**claims)

    def bearer(self, **changes):
        now = int(time.time())
        claims = {"iss": ISS, "aud": HOTE, "typ": "bd-api", "iat": now, "exp": now + 60}
        claims.update(changes)
        return self.sign(claims)


@pytest.fixture
def proadmin(monkeypatch, tmp_path):
    issuer = ProAdmin()
    monkeypatch.setattr(settings, "BLUEDYNAMIC_ISSUERS", {ISS: JWKS}, raising=False)
    monkeypatch.setattr(settings, "BLUEDYNAMIC_ORIGINS", [HOTE], raising=False)
    monkeypatch.setattr(settings, "BLUEDYNAMIC_LOCATION", str(tmp_path / "bluedynamic"), raising=False)
    monkeypatch.setattr(core, "fetch_json", lambda url, timeout=10.0: issuer.jwks())
    sent = []
    monkeypatch.setattr(core, "post_form", lambda url, fields, bearer, timeout=20.0:
                        sent.append((url, fields, bearer)) or {"ok": True, "fournisseur": "bdf-0", "etat": "a_prouver"})
    issuer.sent = sent
    core.key_sets.clear()
    core.used_tickets.clear()
    core.composed_mails.clear()
    core.declare(APPLICATION, MANIFESTE, "bdd-" + "x" * 32)
    return issuer


# the ticket (§4.1)

def test_ticket_valide(proadmin):
    claims, provider = core.open_ticket(proadmin.ticket(), [HOTE])
    assert provider.id == "vdoodle" and provider.application == APPLICATION
    assert provider.api == {"application": APPLICATION, "conteneur": "API",
                            "get": "bd_get", "event": "bd_event", "compose": "bd_compose",
                            "service": "bd_service"}
    assert claims["lecteur"] == "lec-1"


def test_ticket_expire(proadmin):
    past = int(time.time()) - 600
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(iat=past, exp=past + 300), [HOTE])
    assert refused.value.motif == "expire"


def test_ticket_mauvais_aud(proadmin):
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(aud="https://ailleurs.exemple.fr"), [HOTE])
    assert refused.value.motif == "aud"


def test_ticket_pour_ce_serveur_mais_un_autre_fournisseur(proadmin):
    # this server answers for two origins; the ticket names one that is not
    # the provider's own
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(aud="https://autre.exemple.fr"), [HOTE, "https://autre.exemple.fr"])
    assert refused.value.motif == "aud"


def test_ticket_jti_rejoue(proadmin):
    ticket = proadmin.ticket()
    core.open_ticket(ticket, [HOTE])
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(ticket, [HOTE])
    assert refused.value.motif == "rejoue"
    # the claims go with the refusal: the frame may show it, and ask for a new ticket
    assert refused.value.claims["jti"]


def test_ticket_non_declare(proadmin):
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(application="agenda"), [HOTE])
    assert refused.value.motif == "application"
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.composer(commande="forward"), [HOTE])
    assert refused.value.motif == "commande"


def test_ticket_blueapp(proadmin):
    """A BlueApp (PLAN_BLUEAPP.md): declared in the manifest, refused otherwise."""
    claims, provider = core.open_ticket(proadmin.ticket(mode="app", blueapp="gestion", portee="miennes", droits=["lire"]), [HOTE])
    assert claims["mode"] == "app" and claims["blueapp"] == "gestion"
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(mode="app", blueapp="autre"), [HOTE])
    assert refused.value.motif == "blueapp"
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(mode="admin"), [HOTE])
    assert refused.value.motif == "mode"


def test_ticket_emetteur_inconnu(proadmin):
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(iss="https://faux.exemple.fr"), [HOTE])
    assert refused.value.motif == "emetteur"


def test_ticket_mauvaise_cle(proadmin):
    other = Ed25519PrivateKey.generate()
    now = int(time.time())
    forged = proadmin.sign({"iss": ISS, "aud": HOTE, "typ": "bd-ticket", "mode": "lire",
                            "fournisseur": "vdoodle", "application": "sondage",
                            "iat": now, "exp": now + 300, "jti": "f" * 32}, key=other)
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(forged, [HOTE])
    assert refused.value.motif == "signature"


def test_jwks_relu_sur_kid_inconnu(proadmin):
    core.open_ticket(proadmin.ticket(), [HOTE])
    reads = proadmin.jwks_reads
    # ProAdmin turns its key: a new kid; read again, at most once in JWKS_RETRY
    proadmin.key, proadmin.kid = Ed25519PrivateKey.generate(), "bdk-fedcba9876543210"
    core.key_sets._sets[ISS] = (time.time() - core.JWKS_RETRY - 1, core.key_sets._sets[ISS][1])
    core.open_ticket(proadmin.ticket(), [HOTE])
    assert proadmin.jwks_reads == reads + 1
    # an invented kid right after: no new reading
    invented = proadmin.sign({"iss": ISS, "aud": HOTE, "typ": "bd-ticket", "iat": 1, "exp": 2 ** 31},
                             kid="bdk-0000000000000000")
    with pytest.raises(BlueDynamicError):
        core.verify(invented, "bd-ticket", [HOTE])
    assert proadmin.jwks_reads == reads + 1


# the declaration and the proof (§2.2, §2.3)

def test_declaration(proadmin):
    url, fields, bearer = proadmin.sent[-1]
    assert url == ISS + "/bluedynamic/declarer"
    assert bearer == "bdd-" + "x" * 32
    manifest = json.loads(core.b64url_decode(fields["manifeste"]))
    assert manifest["id"] == "vdoodle" and manifest["api"]["application"] == APPLICATION
    assert len(base64.b64decode(manifest["cle_publique"])) == 32
    # replayed, the key and the declaration key stay
    core.declare(APPLICATION, dict(MANIFESTE, version="1.0.1"))
    again = json.loads(core.b64url_decode(proadmin.sent[-1][1]["manifeste"]))
    assert again["cle_publique"] == manifest["cle_publique"] and again["version"] == "1.0.1"
    assert proadmin.sent[-1][2] == bearer


def test_declaration_refusee(proadmin):
    other = "99999999-2222-3333-4444-555555555555"
    with pytest.raises(BlueDynamicError) as refused:
        core.declare(other, MANIFESTE)
    assert refused.value.motif == "fournisseur"
    # the api cannot send this server's calls to another application
    with pytest.raises(BlueDynamicError) as refused:
        core.declare(APPLICATION, dict(MANIFESTE, api={"application": other, "conteneur": "API"}))
    assert refused.value.motif == "manifeste"
    with pytest.raises(BlueDynamicError):
        core.declare(APPLICATION, dict(MANIFESTE, api={}))


def test_preuve(proadmin):
    provider = core.Provider.find("vdoodle")
    defi = "0123456789abcdef0123456789abcdef"
    signature = base64.b64decode(provider.proof(defi))
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(provider.manifest["cle_publique"]))
    public.verify(signature, ("bluedynamic-preuve|vdoodle|%s" % defi).encode())  # raises if wrong
    with pytest.raises(BlueDynamicError):
        provider.proof("../../etc")


# what the plugin answers (§8)

def test_reponses_du_plugin():
    assert core.parse_reply(wholexml("<CONTAINER/>", '{"ok:click": ["ok:click"]}')) == \
        ("wholexml", "<CONTAINER/>", '{"ok:click": ["ok:click"]}')
    assert core.parse_reply(json.dumps(["success", wholexml("<CONTAINER/>")]))[0] == "wholexml"
    assert core.parse_reply(json.dumps(["success", {"bd": "compose", "mail": MAIL}]))[0] == "compose"
    assert core.parse_reply(json.dumps(["success", MAIL]))[0] == "mail"
    for bad in (json.dumps(["error", "plugin", "en panne"]), "", "du texte", "<WHOLEXML/>",
                "<html/>", json.dumps({"rien": 1})):
        with pytest.raises(BlueDynamicError):
            core.parse_reply(bad)
    # an event bound to server code (a bare string) is refused
    with pytest.raises(BlueDynamicError):
        core.parse_reply(wholexml("<CONTAINER/>", '{"ok:click": "import os"}'))
    with pytest.raises(BlueDynamicError):
        core.parse_reply(wholexml("<CONTAINER/>", '{"ok:click": [["ok:hide", 1]]}'))


# the server, the host application and its plugin

class Arguments(object):
    def __init__(self, values):
        self.values = values

    def arguments(self, values=None):
        if values:
            self.values = values
        return self.values


class FakeRequest(object):
    """What admin/bluedynamic.py and admin/e2vdom.py use of VDOM_request."""

    def __init__(self, sessions, args=None, method="get", headers=None, application=None):
        self.sessions = sessions
        self.session_object = sessions.make()
        self.sid = self.session_object.id()
        self.args = Arguments(dict(args or {}, sid=self.sid))
        self.method = method
        self.incoming = headers or {}
        self.out = {}
        self.body = BytesIO()
        self.cookies_out = {"sid": "cookie"}
        self.retcode = 200
        self.sent = False
        self.is_binary = False
        self.app = application
        self.redirect_to = None
        self.fh = None
        self.container_id = None
        self.action_result = StringIO()
        self.shared_variables = {}
        self.next_state = None
        self.last_state = {"#": 0}
        managers.request_manager.current = self

    def arguments(self):
        return self.args

    def headers(self):
        return SimpleNamespace(headers=lambda: self.incoming)

    def environment(self):
        return SimpleNamespace(environment=lambda: {"HTTP_HOST": "apps.exemple.fr"})

    def add_header(self, name, value):
        self.out[name.lower()] = value

    def binary(self, value=None):
        if value is not None:
            self.is_binary = value
        return self.is_binary

    def write(self, data):
        self.body.write(data)

    def output(self):
        value, self.body = self.body.getvalue(), BytesIO()
        return value

    def set_nocache(self):
        self.sent = True

    def session(self):
        return self.session_object

    def set_session_id(self, sid, remove_old=True):
        old = self.session_object
        self.session_object = self.sessions[sid]
        self.args.values["sid"] = sid
        if remove_old:
            self.sessions.pop(old.id(), None)

    def response_cookies(self):
        return self.cookies_out

    def application(self):
        return self.app

    def set_application_id(self, application_id):
        self.app = managers.memory.applications[application_id]


class Sessions(dict):
    counter = 0

    def make(self):
        Sessions.counter += 1
        session = VDOM_session("s%04d" % Sessions.counter)
        self[session.id()] = session
        return session

    def create_session(self):
        return self.make().id()

    def __getitem__(self, sid):
        return dict.get(self, sid)


class VirtualObject(object):
    """The page's virtual objects, as far as the transport touches them."""

    def __init__(self, identifier, container):
        self.id = identifier
        self.type = SimpleNamespace(container=container, id="type-" + identifier)
        self.values = {}
        self.attributes = SimpleNamespace(update=self.values.update)
        self.objects = {}  # what the engine loaded for the previous interface


class Plugin(object):
    """The plugin in its host: what recevoir() hands it, and its answers."""

    def __init__(self):
        self.calls = []

    def __call__(self, action, donnees):
        self.calls.append((action, donnees))
        if action == "get":
            return wholexml('<CONTAINER name="sondage"><TEXT value="Bonjour %s"/></CONTAINER>'
                            % donnees["ticket"]["lecteur"], '{"suivant:click": ["bouton:suivant"]}')
        if action == "compose":
            return dict(MAIL, objet="Par compose")
        nom = donnees["evenement"]["nom"]
        if nom == "suivant":
            return wholexml('<CONTAINER name="sondage"><TEXT value="Page 2 %s"/></CONTAINER>'
                            % donnees["evenement"]["donnees"].get("choix"))
        if nom == "valider":
            return {"bd": "compose", "mail": MAIL}
        raise RuntimeError("en panne")


@pytest.fixture
def server(monkeypatch, proadmin):
    from scripting.packages import bluedynamic as package
    from admin import bluedynamic as entry
    plugin = Plugin()

    def action(name, kind):
        return SimpleNamespace(name=name, run=lambda: package.recevoir(kind, {"vdoodle": plugin}))

    api = SimpleNamespace(id="c-api", actions={"bd_get": action("bd_get", "get"),
                                                "bd_event": action("bd_event", "event"),
                                                "bd_compose": action("bd_compose", "compose")})
    application = SimpleNamespace(id=APPLICATION, active=True, actions={},
                                  objects=SimpleNamespace(get={"API": api}.get, catalog={"c-api": api}))
    sessions = Sessions()
    pages = []

    def make_page(application, width, height):
        root, dynamic = VirtualObject("page", 3), VirtualObject("dyn", 2)
        pages.append((root, dynamic, width, height))
        return root, dynamic

    def render(obj, parent=None, render_type=None):
        dynamic = pages[-1][1]
        inner = "<div>%s|%s</div>" % (dynamic.values.get("vdomxml"), dynamic.values.get("vdomactions"))
        return "<html>%s</html>" % inner if obj is pages[-1][0] else inner

    monkeypatch.setattr(entry, "make_page", make_page)
    monkeypatch.setattr(managers, "session_manager", sessions, raising=False)
    monkeypatch.setattr(managers, "request_manager", SimpleNamespace(current=None), raising=False)
    monkeypatch.setattr(managers, "memory", SimpleNamespace(applications={APPLICATION: application}), raising=False)
    monkeypatch.setattr(managers, "engine", SimpleNamespace(
        application=application, render=render, execute=lambda executable, render=0: executable.run()),
        raising=False)
    return SimpleNamespace(application=application, sessions=sessions, plugin=plugin, pages=pages)


def open_page(server, ticket):
    from admin import bluedynamic as entry
    request = FakeRequest(server.sessions, {"t": [ticket]}, application=server.application)
    entry.run(request)
    return request


def datafield(sid, source, custom, parameters=None):
    return ("<EVENTS><APPLICATION ID='%s'/><SESSION ID='%s'/>"
            "<EVENT objSrcID='o_%s' name='eventcaught'>"
            "<PARAMETER name='customName'><![CDATA[%s]]></PARAMETER>"
            "<PARAMETER name='parameters'><![CDATA[%s]]></PARAMETER>"
            "</EVENT><STATE value='0' /></EVENTS>"
            % (APPLICATION, sid, source.replace("-", "_"), custom, json.dumps(parameters or {})))


def send_event(server, sid, source, custom, parameters=None):
    from admin import e2vdom
    request = FakeRequest(server.sessions, {"datafield": [datafield(sid, source, custom, parameters)]},
                          method="post", application=server.application)
    e2vdom.run(request)
    return request


def test_get_rendu(server, proadmin):
    request = open_page(server, proadmin.ticket())
    assert request.retcode == 200 and request.sent
    body = request.body.getvalue().decode()
    assert '<TEXT value="Bonjour lec-1"/>' in body and '{"suivant:click": ["bouton:suivant"]}' in body
    # la page dit sa hauteur au cadre, aux seules origines du ticket
    assert 'bd:"hauteur"' in body and 'var O=["%s"]' % ISS in body
    assert request.out["content-security-policy"] == "frame-ancestors %s" % ISS
    assert request.out["referrer-policy"] == "no-referrer"
    assert request.out["cache-control"] == "no-store"
    action, donnees = server.plugin.calls[-1]
    assert action == "get" and donnees["ticket"]["lecteur"] == "lec-1"
    assert donnees["session"] == request.session().id() and donnees["langue"] == "fr"
    session = request.session()
    assert session["bd"]["fournisseur"] == "vdoodle" and session.bd_scope["dynamique"].id == "dyn"
    assert "sid" not in request.cookies_out


def test_session_du_visiteur_gardee(server, proadmin):
    from admin import bluedynamic as entry
    request = FakeRequest(server.sessions, {"t": [proadmin.ticket()]}, application=server.application)
    visitor = request.session_object
    visitor["connecte"] = "oui"  # the visitor's own session on this site
    entry.run(request)
    assert request.session() is not visitor and server.sessions[visitor.id()] is visitor


def test_evenement_aller_retour(server, proadmin):
    page = open_page(server, proadmin.ticket())
    sid = page.session().id()
    request = send_event(server, sid, "dyn", "bouton:suivant", {"choix": "mardi"})
    action, donnees = server.plugin.calls[-1]
    assert action == "event"
    assert donnees["evenement"] == {"objet": "bouton", "nom": "suivant", "donnees": {"choix": "mardi"}}
    body = request.body.getvalue().decode()
    assert '<OBJECT ID="dyn" PARENT="page" CONTAINER="2" TYPE="type-dyn">' in body
    assert "Page 2 mardi" in body
    assert request.session().id() == sid


def test_evenement_hors_de_son_interface(server, proadmin):
    page = open_page(server, proadmin.ticket())
    sid = page.session().id()
    calls = len(server.plugin.calls)
    request = send_event(server, sid, "c-api", "bouton:suivant")
    assert len(server.plugin.calls) == calls
    assert "<OBJECT" not in request.body.getvalue().decode()
    # another application: refused as a whole
    from admin import e2vdom
    other = FakeRequest(server.sessions, {"datafield": [datafield(sid, "dyn", "bouton:suivant")
                        .replace(APPLICATION, "99999999-2222-3333-4444-555555555555")]},
                        method="post", application=server.application)
    e2vdom.run(other)
    assert b"SESSIONISOVER" in other.body.getvalue() and len(server.plugin.calls) == calls


def test_erreur_du_plugin(server, proadmin):
    page = open_page(server, proadmin.ticket())
    request = send_event(server, page.session().id(), "dyn", "bouton:casser")
    assert "ne peut pas être affiché" in request.body.getvalue().decode()
    # get answering an error: the page says so, in the iframe
    server.plugin.__class__ = type("Broken", (Plugin,), {"__call__": lambda self, action, donnees: ["error", "x"]})
    refused = open_page(server, proadmin.ticket())
    assert refused.retcode == 502
    assert "ne peut pas être affiché" in refused.body.getvalue().decode()
    assert refused.out["content-security-policy"] == "frame-ancestors %s" % ISS


def test_ticket_invalide_refuse(server, proadmin):
    for ticket, code in ((proadmin.ticket(aud="https://ailleurs.exemple.fr"), 403),
                         (proadmin.ticket(iat=1, exp=2), 403),
                         ("pas.un.jws", 400)):
        calls = len(server.plugin.calls)
        request = open_page(server, ticket)
        assert request.retcode == code
        assert len(server.plugin.calls) == calls
    request = open_page(server, proadmin.ticket(iat=1, exp=2))
    assert "a expiré" in request.body.getvalue().decode()


def test_fin_de_composition_par_event(server, proadmin):
    from admin import bluedynamic as entry
    page = open_page(server, proadmin.composer())
    scope = page.session().bd_scope
    assert server.pages[-1][2:] == (720, 560)
    assert server.plugin.calls[-1][1]["jeton"] == scope["jeton"]
    request = send_event(server, page.session().id(), "dyn", "bouton:valider")
    body = request.body.getvalue().decode()
    assert '"bd": "compose", "jeton": "%s"' % scope["jeton"] in body.replace("&quot;", '"')
    # ProAdmin takes the mail, once
    api = FakeRequest(server.sessions, {"api": ["composer"], "jeton": [scope["jeton"]]}, method="post",
                      headers={"authorization": "Bearer " + proadmin.bearer()})
    entry.run(api)
    assert api.retcode == 200 and api.out["content-type"] == "application/jose"
    provider = core.Provider.find("vdoodle")
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(provider.manifest["cle_publique"]))
    mail = jwt.decode(api.body.getvalue().decode(), public, algorithms=["EdDSA"])
    assert mail["typ"] == "bd-mail" and mail["jeton"] == scope["jeton"] and mail["objet"] == "Sondage"
    again = FakeRequest(server.sessions, {"api": ["composer"], "jeton": [scope["jeton"]]}, method="post",
                        headers={"authorization": "Bearer " + proadmin.bearer()})
    entry.run(again)
    assert again.retcode == 404


def test_fin_de_composition_par_compose(server, proadmin):
    from admin import bluedynamic as entry
    page = open_page(server, proadmin.composer())
    jeton = page.session().bd_scope["jeton"]
    api = FakeRequest(server.sessions, {"api": ["composer"], "jeton": [jeton]}, method="post",
                      headers={"authorization": "Bearer " + proadmin.bearer()})
    entry.run(api)
    assert api.retcode == 200
    assert server.plugin.calls[-1][0] == "compose"
    assert jwt.decode(api.body.getvalue().decode(), options={"verify_signature": False})["objet"] == "Par compose"
    unsigned = FakeRequest(server.sessions, {"api": ["composer"], "jeton": [jeton]}, method="post")
    entry.run(unsigned)
    assert unsigned.retcode == 401


def test_composer_refus(server, proadmin):
    page = open_page(server, proadmin.composer())
    scope = page.session().bd_scope
    jeton = core.render_mail(scope, MAIL)
    for bearer, motif in ((proadmin.bearer(typ="bd-ticket"), "typ"),
                          (proadmin.bearer(aud="https://ailleurs.exemple.fr"), "aud"),
                          (proadmin.bearer(iat=1, exp=2), "expire")):
        with pytest.raises(BlueDynamicError) as refused:
            core.compose(bearer, jeton, [HOTE])
        assert refused.value.motif == motif
    # dates are epoch seconds
    with pytest.raises(BlueDynamicError):
        core.render_mail(scope, dict(MAIL, expire="2026-12-31T00:00:00Z"))
    # update needs the BlueMail it replaces
    with pytest.raises(BlueDynamicError):
        core.render_mail(scope, dict(MAIL, methode="update"))
    # a reading session composes nothing
    reading = open_page(server, proadmin.ticket())
    with pytest.raises(BlueDynamicError):
        core.render_mail(reading.session().bd_scope, MAIL)


def test_recevoir_hors_session_bluemail(server, proadmin):
    """The host's API action called by /restapi.py, a forged ticket in its
    data: refused, the plugin never called."""
    from scripting.packages import bluedynamic as package
    request = FakeRequest(server.sessions, application=server.application)
    request.args = Arguments({"xml_data": [json.dumps({"ticket": {"lecteur": "faux"}})]})
    result = package.recevoir("get", {"vdoodle": server.plugin})
    assert result[0] == "error" and result[1] == "session"
    assert json.loads(request.session()["response"])[0] == "error"
    assert server.plugin.calls == []


def test_session_bd_fin(server, proadmin):
    session = open_page(server, proadmin.ticket()).session()
    assert not session.is_expired(1200)
    session.bd_scope["fin"] = time.time() - 1  # past the ticket and its grace
    assert session.is_expired(1200)
    session.bd_scope["fin"] = time.time() + 3600
    session.bd_scope["inactivite"] = -1  # idle
    assert session.is_expired(1200)


def test_session_bd_refusee_ailleurs(server, proadmin):
    """module/manager.py: a BlueMail session reaches e2vdom.py, bluedynamic.py
    and resources by guid, nothing else."""
    from module.manager import VDOM_module_manager
    page = open_page(server, proadmin.ticket())

    def ask(path):
        request = FakeRequest(server.sessions, application=server.application)
        request.session_object = page.session()
        request.environment = lambda: SimpleNamespace(environment=lambda: {"SCRIPT_NAME": path})
        request.handler = lambda: SimpleNamespace(client_address=("127.0.0.1", 0))
        return VDOM_module_manager().process_request(request)

    for path in ("/api", "/index.vdom", "/restapi.py", "/upload.py",
                 "/%s/c-api" % APPLICATION, "/app.css"):
        assert ask(path) == (403, None), path


# the services (§9)

SERVICES = [{"id": "demander_fichiers", "nature": "action", "nom": {"fr": "Demander des fichiers"},
             "parametres": {"type": "object"}, "evenements": ["piece_deposee"]},
            {"id": "etat_demande", "nature": "lecture"}]
ABONNEMENT = "bda-0123456789abcdef"


def with_services(server):
    """The provider declares services; the host routes bd_service to the plugin."""
    from scripting.packages import bluedynamic as package
    core.declare(APPLICATION, dict(MANIFESTE, services=SERVICES))
    calls = []

    def plugin(action, donnees):
        calls.append((action, donnees))
        if donnees["service"] == "etat_demande":
            return ["success", {"resultat": {"etat": "ouverte"}}]
        if donnees["parametres"].get("panne"):
            return ["error", "parametres"]
        return {"resultat": {"demande": "bdr-1"}, "mail": MAIL}

    api = server.application.objects.get("API")
    api.actions["bd_service"] = SimpleNamespace(name="bd_service",
                                                run=lambda: package.recevoir("service", {"vdoodle": plugin}))
    return calls


def demande(**changes):
    value = {"fournisseur": "vdoodle", "service": "demander_fichiers", "parametres": {"a": ["marie@exemple.fr"]},
             "contexte": {"abonnement": ABONNEMENT, "societe": "soc-1", "demandeur": "lec-9"}}
    value.update(changes)
    return core.b64url(json.dumps(value).encode())


def call_service(server, proadmin, value, bearer=True):
    from admin import bluedynamic as entry
    headers = {"authorization": "Bearer " + proadmin.bearer()} if bearer else {}
    request = FakeRequest(server.sessions, {"api": ["service"], "demande": [value]}, method="post", headers=headers,
                          application=server.application)
    entry.run(request)
    return request


def provider_claims(request):
    provider = core.Provider.find("vdoodle")
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(provider.manifest["cle_publique"]))
    return jwt.decode(request.body.getvalue().decode(), public, algorithms=["EdDSA"])


def test_service_aller_retour(server, proadmin):
    calls = with_services(server)
    request = call_service(server, proadmin, demande())
    assert request.retcode == 200 and request.out["content-type"] == "application/jose"
    claims = provider_claims(request)
    assert claims["typ"] == "bd-service" and claims["service"] == "demander_fichiers"
    assert claims["abonnement"] == ABONNEMENT and claims["resultat"] == {"demande": "bdr-1"}
    assert claims["mail"]["typ"] == "bd-mail" and claims["mail"]["application"] == "sondage"
    action, donnees = calls[-1]
    assert action == "service" and donnees["parametres"] == {"a": ["marie@exemple.fr"]}
    # the plugin sees a service session, with the pseudonyms ProAdmin gave, never a reader's ticket
    assert donnees["ticket"]["mode"] == "service" and donnees["ticket"]["lecteur"] == "lec-9"
    assert donnees["ticket"]["iss"] == ISS
    # a reading service answers without a mail
    lecture = provider_claims(call_service(server, proadmin, demande(service="etat_demande")))
    assert lecture["resultat"] == {"etat": "ouverte"} and "mail" not in lecture


def test_service_refus(server, proadmin):
    with_services(server)
    assert call_service(server, proadmin, demande(), bearer=False).retcode == 401
    assert call_service(server, proadmin, demande(service="inconnu")).retcode == 404
    assert call_service(server, proadmin, demande(contexte={"abonnement": "x"})).retcode == 400
    assert call_service(server, proadmin, "pas du base64 !").retcode == 400
    assert call_service(server, proadmin, demande(parametres={"panne": 1})).retcode == 502
    for bearer, motif in ((proadmin.bearer(typ="bd-ticket"), "typ"), (proadmin.bearer(aud="https://ailleurs.exemple.fr"), "aud")):
        with pytest.raises(BlueDynamicError) as refused:
            core.service(bearer, demande(), [HOTE], lambda *a: {"resultat": 1})
        assert refused.value.motif == motif


def test_service_manifeste_controle(proadmin):
    for mauvais in ([{"id": "Mauvais", "nature": "action"}], [{"id": "ok_id", "nature": "autre"}],
                    [{"id": "ok_id", "nature": "lecture", "evenements": ["Pas bon"]}], [{"id": "x%d" % i, "nature": "lecture"} for i in range(21)]):
        with pytest.raises(BlueDynamicError):
            core.declare(APPLICATION, dict(MANIFESTE, services=mauvais))
    assert core.Provider.find("vdoodle").services == {}


def test_evenement_signe(server, proadmin):
    page = open_page(server, proadmin.ticket())
    scope = page.session().bd_scope
    sent = []
    charge = {"abonnement": ABONNEMENT, "id": "bde-" + "a" * 32, "evenement": "piece_deposee", "donnees": {"piece": 0}}
    answer = core.event(scope, charge, post=lambda url, fields, bearer: sent.append((url, fields, bearer)) or {"ok": 1})
    assert answer == {"ok": 1}
    url, fields, bearer = sent[-1]
    assert url == ISS + "/bluedynamic/evenement" and bearer is None
    provider = core.Provider.find("vdoodle")
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(provider.manifest["cle_publique"]))
    claims = jwt.decode(fields["evenement"], public, algorithms=["EdDSA"])
    assert claims["typ"] == "bd-evenement" and claims["fournisseur"] == "vdoodle" and claims["id"] == charge["id"]
    assert claims["donnees"] == {"piece": 0} and len(claims["jti"]) == 32
    for mauvais in (dict(charge, id="bde-1"), dict(charge, abonnement="bda-x"), dict(charge, evenement="Mal"),
                    dict(charge, donnees="texte")):
        with pytest.raises(BlueDynamicError):
            core.event(scope, mauvais, post=lambda *a: {"ok": 1})
    with pytest.raises(BlueDynamicError):
        core.event(None, charge, post=lambda *a: {"ok": 1})
    # from the plugin, in its BlueMail session: the package sends it to the ticket's ProAdmin
    from scripting.packages import bluedynamic as package
    managers.request_manager.current = page
    proadmin.sent.clear()
    assert package.evenement(charge)["ok"] is True and proadmin.sent[-1][0] == ISS + "/bluedynamic/evenement"
    # out of a BlueMail session: a refusal, not an exception
    managers.request_manager.current = None
    assert package.evenement(charge)["ok"] is False


def test_verifier_ce_que_proadmin_donne_au_plugin(server, proadmin):
    page = open_page(server, proadmin.ticket())
    scope = page.session().bd_scope
    now = int(time.time())
    recu = proadmin.sign({"iss": ISS, "aud": HOTE, "typ": "bd-recu", "fournisseur": "vdoodle", "document": "cf-1",
                          "iat": now, "exp": now + 300})
    assert core.verify_for_provider(scope, recu, "bd-recu")["document"] == "cf-1"
    refus = [(recu, "bd-destinataire"),                                         # not the type asked
             (proadmin.sign({"iss": ISS, "aud": "https://ailleurs.exemple.fr", "typ": "bd-recu", "iat": now, "exp": now + 300}), "bd-recu"),
             (proadmin.sign({"iss": ISS, "aud": HOTE, "typ": "bd-recu", "fournisseur": "autre", "iat": now, "exp": now + 300}), "bd-recu"),
             (proadmin.sign({"iss": ISS, "aud": HOTE, "typ": "bd-recu", "iat": now, "exp": now + 300}, key=Ed25519PrivateKey.generate()), "bd-recu"),
             (proadmin.sign({"iss": ISS, "aud": HOTE, "typ": "bd-ticket", "iat": now, "exp": now + 300}), "bd-ticket")]
    for jeton, typ in refus:
        with pytest.raises(BlueDynamicError):
            core.verify_for_provider(scope, jeton, typ)
    from scripting.packages import bluedynamic as package
    managers.request_manager.current = page
    assert package.verifier(recu, "bd-recu")["document"] == "cf-1"
    assert package.verifier(refus[1][0], "bd-recu") is None
    managers.request_manager.current = None
    assert package.verifier(recu, "bd-recu") is None
