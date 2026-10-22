"""BlueDynamic on the server side (utils/bluedynamic.py, admin/bluedynamic.py,
admin/e2vdom.py): tickets, proof, composer, the session kept in its container.

ProAdmin is played by a key pair made here and its JWKS, served by a stand-in
for fetch_json; nothing goes on the network.
"""
import base64
import json
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
                    "conteneur": "composeur_vdoodle", "contexte": ["objet", "de"]}],
    "applications": [{"id": "sondage", "conteneur": "lecteur_vdoodle"}],
}


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
                  "fournisseur": "vdoodle", "conteneur": "lecteur_vdoodle",
                  "bd": "bd-6f1c", "application": "sondage", "instance": "i-42", "expire": False,
                  "lecteur": "lec-1", "societe": "soc-1", "origines": [ISS],
                  "iat": now, "exp": now + 300, "jti": "%032x" % int(time.time() * 1e6)}
        claims.update(changes)
        return self.sign(claims)

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
    claims, provider, container = core.open_ticket(proadmin.ticket(), [HOTE])
    assert provider.id == "vdoodle" and provider.application == APPLICATION
    assert container == "lecteur_vdoodle"
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


def test_ticket_conteneur_non_declare(proadmin):
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(conteneur="administration"), [HOTE])
    assert refused.value.motif == "conteneur"
    # the container of a composer is not one a reading ticket may open
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(conteneur="composeur_vdoodle"), [HOTE])
    assert refused.value.motif == "conteneur"


def test_ticket_composer_commande(proadmin):
    _, _, container = core.open_ticket(proadmin.ticket(
        mode="composer", conteneur="composeur_vdoodle", commande="reply", contexte={"objet": "x"}), [HOTE])
    assert container == "composeur_vdoodle"
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(
            mode="composer", conteneur="composeur_vdoodle", commande="forward"), [HOTE])
    assert refused.value.motif == "conteneur"


def test_ticket_emetteur_inconnu(proadmin):
    with pytest.raises(BlueDynamicError) as refused:
        core.open_ticket(proadmin.ticket(iss="https://faux.exemple.fr"), [HOTE])
    assert refused.value.motif == "emetteur"


def test_ticket_mauvaise_cle(proadmin):
    other = Ed25519PrivateKey.generate()
    now = int(time.time())
    forged = proadmin.sign({"iss": ISS, "aud": HOTE, "typ": "bd-ticket", "mode": "lire",
                            "fournisseur": "vdoodle", "conteneur": "lecteur_vdoodle", "application": "sondage",
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
    assert manifest["id"] == "vdoodle"
    assert len(base64.b64decode(manifest["cle_publique"])) == 32
    # replayed, the key and the declaration key stay
    core.declare(APPLICATION, dict(MANIFESTE, version="1.0.1"))
    again = json.loads(core.b64url_decode(proadmin.sent[-1][1]["manifeste"]))
    assert again["cle_publique"] == manifest["cle_publique"] and again["version"] == "1.0.1"
    assert proadmin.sent[-1][2] == bearer


def test_declaration_par_une_autre_application(proadmin):
    with pytest.raises(BlueDynamicError) as refused:
        core.declare("99999999-2222-3333-4444-555555555555", MANIFESTE)
    assert refused.value.motif == "fournisseur"


def test_preuve(proadmin):
    provider = core.Provider.find("vdoodle")
    defi = "0123456789abcdef0123456789abcdef"
    signature = base64.b64decode(provider.proof(defi))
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(provider.manifest["cle_publique"]))
    public.verify(signature, ("bluedynamic-preuve|vdoodle|%s" % defi).encode())  # raises if wrong
    with pytest.raises(BlueDynamicError):
        provider.proof("../../etc")


# the composer (§5)

def composer_scope(proadmin):
    claims, provider, container = core.open_ticket(proadmin.ticket(
        mode="composer", conteneur="composeur_vdoodle", commande="new"), [HOTE])
    return core.scope(claims, APPLICATION, "container-id")


MAIL = {"a": ["marie@exemple.fr"], "objet": "Sondage", "texte": "Votez", "html": "<p>Votez</p>",
        "application": "sondage", "instance": "i-42", "titre": "Nouveau VDoodle",
        "expire": 1798761600, "methode": "new"}


def test_composer(proadmin):
    jeton = core.render_mail(composer_scope(proadmin), MAIL)
    token = core.compose(proadmin.bearer(), jeton, [HOTE])
    provider = core.Provider.find("vdoodle")
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(provider.manifest["cle_publique"]))
    mail = jwt.decode(token, public, algorithms=["EdDSA"])
    assert mail["typ"] == "bd-mail" and mail["jeton"] == jeton
    assert mail["a"] == ["marie@exemple.fr"] and mail["cc"] == [] and mail["expire"] == 1798761600
    # once only
    with pytest.raises(BlueDynamicError) as refused:
        core.compose(proadmin.bearer(), jeton, [HOTE])
    assert refused.value.motif == "jeton"


def test_composer_refus(proadmin):
    scope = composer_scope(proadmin)
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
    claims, _, _ = core.open_ticket(proadmin.ticket(), [HOTE])
    with pytest.raises(BlueDynamicError):
        core.render_mail(core.scope(claims, APPLICATION, "x"), MAIL)


# the HTTP entry point and the session

class Arguments(object):
    def __init__(self, values):
        self.values = values

    def arguments(self, values=None):
        if values is not None:
            self.values.update(values)
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
        self.action_result = StringIO()
        self.shared_variables = {}
        self.next_state = None
        self.last_state = {"#": 0}

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


def node(identifier, parent=None, **more):
    return SimpleNamespace(id=identifier, parent=parent, **more)


@pytest.fixture
def server(monkeypatch, proadmin):
    """An application with the reader container (a button in it) and another
    top level container (a button in it too)."""
    page_type = SimpleNamespace(http_content_type="text/html", render_type="html", container=3, id="t")
    reader = node("c-lecteur", type=page_type, name="lecteur_vdoodle")
    inner = node("o-bouton", reader, type=page_type)
    admin = node("c-admin", type=page_type, name="administration")
    secret = node("o-secret", admin, type=page_type)
    catalog = {each.id: each for each in (reader, inner, admin, secret)}
    executed = []

    def callee(owner):
        return SimpleNamespace(is_action=True, owner=owner)

    events = {("o-bouton", "click"): SimpleNamespace(callees=[callee(inner)]),
              ("o-secret", "click"): SimpleNamespace(callees=[callee(secret)])}
    application = SimpleNamespace(
        id=APPLICATION, active=True, actions={},
        objects=SimpleNamespace(get={"lecteur_vdoodle": reader, "administration": admin}.get, catalog=catalog),
        events=SimpleNamespace(catalog=events))
    sessions = Sessions()
    monkeypatch.setattr(managers, "session_manager", sessions, raising=False)
    monkeypatch.setattr(managers, "memory", SimpleNamespace(applications={APPLICATION: application}), raising=False)
    monkeypatch.setattr(managers, "engine", SimpleNamespace(
        render=lambda container, render_type: "<html>%s</html>" % container.id,
        execute=lambda action, render=0: executed.append(action.owner.id) or {}), raising=False)
    return SimpleNamespace(application=application, sessions=sessions, executed=executed)


def test_page_du_ticket(server, proadmin):
    from admin import bluedynamic as entry
    request = FakeRequest(server.sessions, {"t": [proadmin.ticket()]}, application=server.application)
    visitor = request.session_object
    visitor["connecte"] = "oui"  # the visitor's own session on this site
    entry.run(request)
    assert request.retcode == 200 and request.sent
    assert request.body.getvalue() == b"<html>c-lecteur</html>"
    assert request.out["content-security-policy"] == "frame-ancestors %s" % ISS
    assert request.out["referrer-policy"] == "no-referrer"
    assert request.out["cache-control"] == "no-store"
    session = request.session()
    assert session is not visitor and session.bd_scope["conteneur"] == "c-lecteur"
    assert session["bd"]["fournisseur"] == "vdoodle"
    # the visitor's session is kept, and its cookie is not replaced
    assert server.sessions[visitor.id()] is visitor
    assert "sid" not in request.cookies_out


def test_page_refusee(server, proadmin):
    from admin import bluedynamic as entry
    request = FakeRequest(server.sessions, {"t": [proadmin.ticket(conteneur="administration")]},
                          application=server.application)
    entry.run(request)
    assert request.retcode == 403
    assert json.loads(request.body.getvalue())["motif"] == "conteneur"


def test_api_preuve_http(server, proadmin):
    from admin import bluedynamic as entry
    request = FakeRequest(server.sessions, {"api": ["preuve"], "f": ["vdoodle"], "defi": ["a" * 32]})
    entry.run(request)
    assert request.retcode == 200 and "signature" in json.loads(request.body.getvalue())


def test_api_composer_http(server, proadmin):
    from admin import bluedynamic as entry
    jeton = core.render_mail(composer_scope(proadmin), MAIL)
    request = FakeRequest(server.sessions, {"api": ["composer"], "jeton": [jeton]}, method="post",
                          headers={"authorization": "Bearer " + proadmin.bearer()})
    entry.run(request)
    assert request.retcode == 200 and request.out["content-type"] == "application/jose"
    assert request.body.getvalue().count(b".") == 2
    refused = FakeRequest(server.sessions, {"api": ["composer"], "jeton": [jeton]}, method="post")
    entry.run(refused)
    assert refused.retcode == 401


def datafield(application, sid, source):
    return ("<EVENTS><APPLICATION ID='%s'/><SESSION ID='%s'/>"
            "<EVENT objSrcID='o_%s' name='click'></EVENT><STATE value='0' /></EVENTS>"
            % (application, sid, source.replace("-", "_")))


def test_session_bd_hors_de_son_conteneur(server, proadmin):
    from admin import bluedynamic as entry
    from admin import e2vdom
    page = FakeRequest(server.sessions, {"t": [proadmin.ticket()]}, application=server.application)
    entry.run(page)
    sid = page.session().id()

    # the page's own button: executed
    inside = FakeRequest(server.sessions, {"datafield": [datafield(APPLICATION, sid, "o-bouton")]},
                         method="post", application=server.application)
    e2vdom.run(inside)
    assert server.executed == ["o-bouton"]
    assert inside.session().id() == sid

    # a button of another container, from the same session: not executed
    outside = FakeRequest(server.sessions, {"datafield": [datafield(APPLICATION, sid, "o-secret")]},
                          method="post", application=server.application)
    e2vdom.run(outside)
    assert server.executed == ["o-bouton"]

    # another application: refused as a whole
    other = FakeRequest(server.sessions, {"datafield": [datafield("99999999-2222-3333-4444-555555555555", sid, "o-bouton")]},
                        method="post", application=server.application)
    e2vdom.run(other)
    assert b"SESSIONISOVER" in other.body.getvalue()
    assert server.executed == ["o-bouton"]


def test_session_bd_fin(server, proadmin):
    from admin import bluedynamic as entry
    page = FakeRequest(server.sessions, {"t": [proadmin.ticket()]}, application=server.application)
    entry.run(page)
    session = page.session()
    assert not session.is_expired(1200)
    session.bd_scope["fin"] = time.time() - 1  # past the ticket and its grace
    assert session.is_expired(1200)
    session.bd_scope["fin"] = time.time() + 3600
    session.bd_scope["inactivite"] = -1  # idle
    assert session.is_expired(1200)


def test_session_bd_refusee_ailleurs(server, proadmin, monkeypatch):
    """module/manager.py: a BlueMail session reaches e2vdom.py, bluedynamic.py
    and resources by guid, nothing else."""
    from module.manager import VDOM_module_manager
    from admin import bluedynamic as entry
    page = FakeRequest(server.sessions, {"t": [proadmin.ticket()]}, application=server.application)
    entry.run(page)

    def ask(path):
        request = FakeRequest(server.sessions, application=server.application)
        request.session_object = page.session()
        request.environment = lambda: SimpleNamespace(environment=lambda: {"SCRIPT_NAME": path})
        request.handler = lambda: SimpleNamespace(client_address=("127.0.0.1", 0))
        return VDOM_module_manager().process_request(request)

    for path in ("/lecteur_vdoodle", "/administration.vdom", "/restapi.py", "/upload.py",
                 "/%s/c-admin" % APPLICATION, "/app.css"):
        assert ask(path) == (403, None), path
