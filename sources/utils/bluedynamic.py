"""BlueDynamic: what a VDOM server needs to show a BlueMail.

A BlueMail is a mail that carries the descriptor of an application served
by a plugin of this server. ProAdmin's mail view shows it in an iframe served
from here, with a short ticket that ProAdmin signed. The contract that fixes
every format is sites/proadmin/CONTRAT_BLUEDYNAMIC.md (ProAdmin's
repository); the sections cited below are its own.

As the EAC of ProMail did, the plugin serves VDOM: a WHOLEXML (the VDOMXML
of the interface and its E2VDOM actions) that travels as data, which this
server's engine evaluates on the fly (admin/bluedynamic.py). The plugin lives
in any application that manages plugins; the server reaches it by an
ordinary VDOM API call to that application: call(api.conteneur, action, JSON)
on api.application, with the actions get, event and compose (§8).

A provider ("fournisseur") is a folder under settings.BLUEDYNAMIC_LOCATION,
named after the id of its manifest:

    <BLUEDYNAMIC_LOCATION>/<id>/fournisseur.json
        {"application": "<guid of the VDOM application that declared it>",
         "manifeste": {...the manifest of §2.2, with its api (§8)...},
         "cle_declaration": "bdd-...",            (optional, a secret)
         "proadmin": "https://proadmin..."}       (optional, where to declare)
    <BLUEDYNAMIC_LOCATION>/<id>/cle_privee.pem
        the provider's Ed25519 key, PKCS8 PEM, made on first need

Nothing of it lives in the application itself: a plugin's code can be shared
or exported without its key. The plugin writes its manifest by declaring
itself (declarer), which is replayed at each start or update.

This module is plain python: no manager is needed, so the tests can drive it.
"""
import base64
import json
import os
import re
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

import settings


RE_FOURNISSEUR = re.compile(r"^[a-z][a-z0-9_-]{1,39}$")
RE_JTI = re.compile(r"^[0-9a-f]{32}$")
RE_JETON = re.compile(r"^[0-9a-f]{32}$")
RE_HOTE = re.compile(r"^https://[a-z0-9.-]+(:[0-9]{1,5})?$")
RE_GUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
RE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,99}$")

MODES = "lire", "composer", "app"   # app: a BlueApp, the provider's management screen (PLAN_BLUEAPP.md)
COMMANDES = "new", "reply", "reply_all", "forward"
CONTEXTE = "objet", "de", "a", "cc", "date", "texte", "modele"   # modele: "send this template" from a BlueApp
METHODES = "new", "update", "delete"

LEEWAY = 5  # seconds of clock difference accepted on exp and iat
JWKS_RETRY = 30  # at most one reading a key set this often, on unknown kids
MAIL_LIFETIME = 900  # a composed mail waits this long for ProAdmin
MANIFEST_LIMIT = 64 * 1024  # §2.2
API_ACTIONS = {"get": "bd_get", "event": "bd_event", "compose": "bd_compose", "service": "bd_service"}  # §8, §9, defaults
NATURES = "lecture", "action"  # §9.1
RE_SERVICE = re.compile(r"^[a-z][a-z0-9_]{1,39}$")
RE_ABONNEMENT = re.compile(r"^bda-[0-9a-f]{16}$")
RE_EVENEMENT = re.compile(r"^bde-[0-9a-f]{32}$")
SERVICE_LIMIT = 1024 * 1024  # what a service call or answer may carry
SERVICE_LIFETIME = 120  # seconds a service session lives
WHOLEXML_LIMIT = 4 * 1024 * 1024  # what a plugin may answer


class BlueDynamicError(Exception):
    """A refusal: `motif` is a short word for the log and the caller, `code`
    the HTTP status to answer with."""

    def __init__(self, motif, message="", code=403):
        Exception.__init__(self, message or motif)
        self.motif = motif
        self.code = code


# base64

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(text):
    if isinstance(text, str):
        text = text.encode("ascii")
    return base64.urlsafe_b64decode(text + b"=" * (-len(text) % 4))


def origine(value):
    """An origin as written in a manifest or a claim: lower case, no slash at
    the end. None when it is not https://host[:port]."""
    if not isinstance(value, str):
        return None
    value = value.strip().rstrip("/").lower()
    return value if RE_HOTE.match(value) else None


# ProAdmin's public keys (§1.1)

def fetch_json(url, timeout=10.0):
    """GET a JSON document. Module level, so a test can replace it."""
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as answer:
        return json.loads(answer.read().decode("utf-8"))


class KeySets(object):
    """The key sets of the accepted issuers, kept BLUEDYNAMIC_JWKS_LIFETIME
    and read again on a kid they do not hold - at most once in JWKS_RETRY, so
    that tickets with invented kids cannot make this server hammer ProAdmin."""

    def __init__(self):
        self._lock = threading.Lock()
        self._sets = {}  # issuer: (read at, {kid: key})

    def clear(self):
        with self._lock:
            self._sets.clear()

    def _read(self, issuer):
        url = settings.BLUEDYNAMIC_ISSUERS[issuer]
        document = fetch_json(url)
        keys = {}
        for each in document.get("keys") or []:
            if each.get("kty") != "OKP" or each.get("crv") != "Ed25519" or not each.get("kid"):
                continue
            try:
                keys[each["kid"]] = Ed25519PublicKey.from_public_bytes(b64url_decode(each["x"]))
            except Exception:  # noqa - one bad key does not hide the others
                continue
        return keys

    def key(self, issuer, kid):
        now = time.time()
        with self._lock:
            read_at, keys = self._sets.get(issuer, (0, {}))
            fresh = now - read_at < settings.BLUEDYNAMIC_JWKS_LIFETIME
            if fresh and kid in keys:
                return keys[kid]
            if not fresh or now - read_at >= JWKS_RETRY:
                try:
                    keys = self._read(issuer)
                except Exception as error:
                    if not keys:
                        raise BlueDynamicError("jwks", "ProAdmin's keys cannot be read: %s" % error, 503)
                else:
                    self._sets[issuer] = (now, keys)
            if kid in keys:
                return keys[kid]
        raise BlueDynamicError("signature", "Unknown key %s" % kid)


key_sets = KeySets()


# tickets used once (§4.1)

class UsedTickets(object):
    """jti seen, each kept until its ticket expires."""

    def __init__(self):
        self._lock = threading.Lock()
        self._seen = {}

    def clear(self):
        with self._lock:
            self._seen.clear()

    def use(self, jti, expires):
        now = time.time()
        with self._lock:
            for each in [key for key, until in self._seen.items() if until + LEEWAY < now]:
                del self._seen[each]
            if jti in self._seen:
                return False
            self._seen[jti] = expires
            return True


used_tickets = UsedTickets()


# ProAdmin's signatures

def verify(token, typ, audiences):
    """The claims of a JWS from ProAdmin (§1): EdDSA, an accepted issuer, its
    key by kid, one of `audiences`, not expired, of type `typ`."""
    if not isinstance(token, str) or token.count(".") != 2 or len(token) > 16384:
        raise BlueDynamicError("signature", "Not a compact JWS", 400)
    try:
        header = jwt.get_unverified_header(token)
        unverified = jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError as error:
        raise BlueDynamicError("signature", str(error), 400)
    if header.get("alg") != "EdDSA":
        raise BlueDynamicError("signature", "Algorithm %s refused" % header.get("alg"))
    issuer = unverified.get("iss")
    if not isinstance(issuer, str) or issuer not in settings.BLUEDYNAMIC_ISSUERS:
        raise BlueDynamicError("emetteur", "Issuer %s not accepted" % issuer)
    key = key_sets.key(issuer, header.get("kid"))
    try:
        claims = jwt.decode(token, key, algorithms=["EdDSA"], audience=list(audiences),
                            issuer=issuer, leeway=LEEWAY,
                            options={"require": ["iss", "aud", "exp", "iat"]})
    except jwt.ExpiredSignatureError:
        raise BlueDynamicError("expire", "Expired")
    except jwt.InvalidAudienceError:
        raise BlueDynamicError("aud", "Not for this server")
    except jwt.PyJWTError as error:
        raise BlueDynamicError("signature", str(error))
    if claims.get("typ") != typ:
        raise BlueDynamicError("typ", "A %s where a %s was expected" % (claims.get("typ"), typ))
    return claims


def verify_ticket(ticket, origins):
    """The claims of a player ticket (§4), its jti now used. `origins` are
    the public origins of this server."""
    claims = verify(ticket, "bd-ticket", origins)
    jti = claims.get("jti")
    if not isinstance(jti, str) or not RE_JTI.match(jti):
        raise BlueDynamicError("jti", "No usable jti", 400)
    if claims.get("mode") not in MODES:
        raise BlueDynamicError("mode", "Unknown mode", 400)
    if not used_tickets.use(jti, claims["exp"]):
        # a genuine ticket opened again (a view showing a message again):
        # its claims go with the refusal, so the frame may show it
        error = BlueDynamicError("rejoue", "This ticket was used already")
        error.claims = claims
        raise error
    return claims


# providers

def location():
    return os.path.abspath(settings.BLUEDYNAMIC_LOCATION)


class Provider(object):
    """A provider of this server: its folder, its configuration, its key."""

    def __init__(self, identifier, folder, configuration):
        self.id = identifier
        self.folder = folder
        self.configuration = configuration

    @classmethod
    def find(cls, identifier):
        if not isinstance(identifier, str) or not RE_FOURNISSEUR.match(identifier):
            return None
        folder = os.path.join(location(), identifier)
        try:
            with open(os.path.join(folder, "fournisseur.json"), "r", encoding="utf-8") as file:
                configuration = json.load(file)
        except (OSError, ValueError):
            return None
        if not isinstance(configuration, dict):
            return None
        return cls(identifier, folder, configuration)

    @classmethod
    def create(cls, identifier, application):
        folder = os.path.join(location(), identifier)
        os.makedirs(folder, exist_ok=True)
        provider = cls(identifier, folder, {"application": application})
        provider.save()
        return provider

    def save(self):
        path = os.path.join(self.folder, "fournisseur.json")
        temporary = path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(self.configuration, file, ensure_ascii=False, indent=2)
        os.replace(temporary, path)

    @property
    def application(self):
        return self.configuration.get("application")

    @property
    def manifest(self):
        return self.configuration.get("manifeste") or {}

    @property
    def origin(self):
        return origine(self.manifest.get("hote"))

    @property
    def api(self):
        """How to reach the plugin (§8): the host application, its API
        container, and the name of each action there."""
        api = self.manifest.get("api") or {}
        result = {"application": api.get("application"), "conteneur": api.get("conteneur")}
        for action, default in API_ACTIONS.items():
            result[action] = api.get(action) or default
        return result

    def check(self, claims):
        """What a ticket names must be in the manifest (§4.1, step 2): its
        application when reading, a composer for its command when composing."""
        if claims["mode"] == "lire":
            if any(each.get("id") == claims.get("application") for each in self.manifest.get("applications") or []):
                return
            raise BlueDynamicError("application", "Application %s not declared" % claims.get("application"))
        if claims["mode"] == "app":
            if any(each.get("id") == claims.get("blueapp") for each in self.manifest.get("blueapps") or [] if isinstance(each, dict)):
                return
            raise BlueDynamicError("blueapp", "BlueApp %s not declared" % claims.get("blueapp"))
        for each in self.manifest.get("composeurs") or []:
            if claims.get("commande") in (each.get("commandes") or []):
                return
        raise BlueDynamicError("commande", "No composer declared for %s" % claims.get("commande"))

    @property
    def services(self):
        """{id: service} of the services the manifest declares (§9.1)."""
        return {each["id"]: each for each in self.manifest.get("services") or [] if isinstance(each, dict) and each.get("id")}

    # the key

    def private_key(self):
        path = os.path.join(self.folder, "cle_privee.pem")
        try:
            with open(path, "rb") as file:
                return serialization.load_pem_private_key(file.read(), password=None)
        except FileNotFoundError:
            pass
        key = Ed25519PrivateKey.generate()
        pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                serialization.NoEncryption())
        # exclusive creation: two first uses at once keep the same key
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return self.private_key()
        with os.fdopen(descriptor, "wb") as file:
            file.write(pem)
        return key

    def public_key(self):
        """The public key as the manifest gives it: 32 bytes, base64."""
        raw = self.private_key().public_key().public_bytes(serialization.Encoding.Raw,
                                                            serialization.PublicFormat.Raw)
        return base64.b64encode(raw).decode("ascii")

    def sign(self, claims):
        """A JWS of `claims`, signed with the provider's key (§5)."""
        return jwt.encode(claims, self.private_key(), algorithm="EdDSA")

    def proof(self, challenge):
        """§2.3: the signature of bluedynamic-preuve|<id>|<defi>, base64."""
        if not isinstance(challenge, str) or not re.match(r"^[0-9a-f]{32}$", challenge):
            raise BlueDynamicError("defi", "Challenge not of 32 hexadecimal digits", 400)
        message = ("bluedynamic-preuve|%s|%s" % (self.id, challenge)).encode("ascii")
        return base64.b64encode(self.private_key().sign(message)).decode("ascii")


# the declaration (§2.2)

def check_manifest(manifest):
    if not isinstance(manifest, dict):
        raise BlueDynamicError("manifeste", "The manifest is not an object", 400)
    if not isinstance(manifest.get("id"), str) or not RE_FOURNISSEUR.match(manifest["id"]):
        raise BlueDynamicError("manifeste", "id must match %s" % RE_FOURNISSEUR.pattern, 400)
    if not origine(manifest.get("hote")):
        raise BlueDynamicError("manifeste", "hote must be https://host[:port], without a path", 400)
    for each in manifest.get("applications") or []:
        if not isinstance(each, dict) or not each.get("id"):
            raise BlueDynamicError("manifeste", "An application needs an id", 400)
    for each in manifest.get("composeurs") or []:
        if not isinstance(each, dict) or not each.get("id"):
            raise BlueDynamicError("manifeste", "A composer needs an id", 400)
        if not set(each.get("commandes") or []) <= set(COMMANDES):
            raise BlueDynamicError("manifeste", "commandes is a part of %s" % ", ".join(COMMANDES), 400)
        if not set(each.get("contexte") or []) <= set(CONTEXTE):
            raise BlueDynamicError("manifeste", "contexte is a part of %s" % ", ".join(CONTEXTE), 400)
    services = manifest.get("services") or []
    if not isinstance(services, list) or len(services) > 20:
        raise BlueDynamicError("manifeste", "services is a list of 20 services at most", 400)
    for each in services:
        if not isinstance(each, dict) or not isinstance(each.get("id"), str) or not RE_SERVICE.match(each["id"]):
            raise BlueDynamicError("manifeste", "A service needs an id matching %s" % RE_SERVICE.pattern, 400)
        if each.get("nature") not in NATURES:
            raise BlueDynamicError("manifeste", "The nature of service %s is one of %s" % (each["id"], ", ".join(NATURES)), 400)
        evenements = each.get("evenements") or []
        if not isinstance(evenements, list) or len(evenements) > 20 \
                or not all(isinstance(e, str) and RE_SERVICE.match(e) for e in evenements):
            raise BlueDynamicError("manifeste", "The events of service %s are 20 ids at most" % each["id"], 400)
    blueapps = manifest.get("blueapps") or []
    if not isinstance(blueapps, list) or len(blueapps) > 5             or not all(isinstance(e, dict) and isinstance(e.get("id"), str) and RE_SERVICE.match(e["id"]) for e in blueapps):
        raise BlueDynamicError("manifeste", "blueapps is a list of 5 BlueApps at most, each with an id matching %s" % RE_SERVICE.pattern, 400)
    api = manifest.get("api")
    if not isinstance(api, dict) or not isinstance(api.get("conteneur"), str) \
            or not (RE_NAME.match(api["conteneur"]) or RE_GUID.match(api["conteneur"].lower())):
        raise BlueDynamicError("manifeste", "api.conteneur names the container of the host's API", 400)
    for action in API_ACTIONS:
        if api.get(action) is not None and not (isinstance(api[action], str) and RE_NAME.match(api[action])):
            raise BlueDynamicError("manifeste", "api.%s is the name of an action" % action, 400)


def post_form(url, fields, bearer=None, timeout=20.0):
    """POST a form, the answer's JSON. Module level, so a test can replace it."""
    body = urllib.parse.urlencode(fields).encode("ascii")
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    if bearer:
        headers["Authorization"] = "Bearer %s" % bearer
    request = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as answer:
            return json.loads(answer.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            return json.loads(error.read().decode("utf-8"))
        except Exception:  # noqa
            return {"ok": False, "motif": "http %s" % error.code}


def declare(application, manifest, declaration_key=None, proadmin=None):
    """Record the manifest of a provider served by `application`, then
    declare it to ProAdmin. Replayed at each start or update of the plugin:
    ProAdmin keeps the last one.

    The provider's folder belongs to the application that made it: another
    application of this server cannot take its id. `cle_publique` is the
    provider's own, whatever the manifest said. Without a declaration key
    (given here or in fournisseur.json) the manifest is recorded and nothing
    is sent."""
    if isinstance(manifest, str):
        try:
            manifest = json.loads(manifest)
        except ValueError:
            raise BlueDynamicError("manifeste", "The manifest is not JSON", 400)
    check_manifest(manifest)
    # the plugin is reached through the application that declares it: the
    # manifest cannot send this server's calls to another one
    api = dict(manifest["api"])
    if not api.get("application"):
        api["application"] = application
    if str(api["application"]).lower() != str(application).lower():
        raise BlueDynamicError("manifeste", "api.application is the application that declares", 400)
    provider = Provider.find(manifest["id"])
    if provider is None:
        provider = Provider.create(manifest["id"], application)
    elif provider.application != application:
        raise BlueDynamicError("fournisseur", "Provider %s belongs to another application" % manifest["id"])
    manifest = dict(manifest, api=api, cle_publique=provider.public_key())
    encoded = b64url(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    if len(encoded) > MANIFEST_LIMIT:
        raise BlueDynamicError("manifeste", "The manifest is over 64 KiB", 400)
    provider.configuration["manifeste"] = manifest
    if declaration_key:
        provider.configuration["cle_declaration"] = declaration_key
    if proadmin:
        provider.configuration["proadmin"] = proadmin
    provider.save()
    key = provider.configuration.get("cle_declaration")
    if not key:
        return {"ok": False, "motif": "cle_declaration"}
    target = provider.configuration.get("proadmin") or next(iter(settings.BLUEDYNAMIC_ISSUERS), None)
    if not target:
        return {"ok": False, "motif": "proadmin"}
    return post_form(target.rstrip("/") + "/bluedynamic/declarer", {"manifeste": encoded}, key)


# the composed mail (§5)

class ComposedMails(object):
    """The jeton of each composer session, and the mail once the plugin made
    it; ProAdmin takes it (api=composer) once."""

    def __init__(self):
        self._lock = threading.Lock()
        self._entries = {}  # jeton: {"until", "fournisseur", "session", "mail"}

    def clear(self):
        with self._lock:
            self._entries.clear()

    def _prune(self, now):
        for each in [key for key, value in self._entries.items() if value["until"] < now]:
            del self._entries[each]

    def open(self, provider, session_id, until=None):
        """A jeton for a composer session, before any mail: it lasts as long
        as the session may (`until`), the mail then MAIL_LIFETIME more."""
        jeton = secrets.token_hex(16)
        now = time.time()
        with self._lock:
            self._prune(now)
            self._entries[jeton] = {"until": until or now + MAIL_LIFETIME, "fournisseur": provider,
                                    "session": session_id, "mail": None}
        return jeton

    def put(self, jeton, mail):
        with self._lock:
            entry = self._entries.get(jeton)
            if entry is None:
                raise BlueDynamicError("jeton", "This composition is over", 404)
            entry["mail"] = mail
            entry["until"] = max(entry["until"], time.time() + MAIL_LIFETIME)

    def take(self, jeton):
        with self._lock:
            entry = self._entries.pop(jeton, None)
        if entry is None or entry["until"] < time.time():
            return None
        return entry

    def give_back(self, jeton, entry):
        """The plugin could not make the mail: the composition goes on."""
        with self._lock:
            self._entries.setdefault(jeton, entry)


composed_mails = ComposedMails()


def _addresses(value, name):
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not all(isinstance(each, str) for each in value):
        raise BlueDynamicError("mail", "%s is a list of addresses" % name, 400)
    return value


def check_mail(mail):
    """The mail a composer renders, shaped as §5 asks. Dates are epoch
    seconds, integers."""
    if isinstance(mail, str):
        try:
            mail = json.loads(mail)
        except ValueError:
            raise BlueDynamicError("mail", "The mail is not JSON", 400)
    if not isinstance(mail, dict):
        raise BlueDynamicError("mail", "The mail is not an object", 400)
    result = {"typ": "bd-mail", "a": _addresses(mail.get("a"), "a"), "cc": _addresses(mail.get("cc"), "cc")}
    for name in ("objet", "texte", "html", "application", "instance", "titre"):
        value = mail.get(name, "")
        if not isinstance(value, str):
            raise BlueDynamicError("mail", "%s is a string" % name, 400)
        result[name] = value
    if not result["application"]:
        raise BlueDynamicError("mail", "application is missing", 400)
    expire = mail.get("expire")
    if isinstance(expire, float) and expire.is_integer():
        expire = int(expire)
    if isinstance(expire, bool) or not isinstance(expire, int):
        raise BlueDynamicError("mail", "expire is a date in epoch seconds", 400)
    result["expire"] = expire
    methode = mail.get("methode") or "new"
    if methode not in METHODES:
        raise BlueDynamicError("mail", "methode is one of %s" % ", ".join(METHODES), 400)
    result["methode"] = methode
    if methode != "new":
        if not isinstance(mail.get("bd"), str) or not mail["bd"].startswith("bd-"):
            raise BlueDynamicError("mail", "bd is needed to %s a BlueMail" % methode, 400)
        result["bd"] = mail["bd"]
    return result



def render_mail(scope, mail):
    """Keep the mail a composer made in a BlueMail session, under the jeton of
    that session: the jeton the page sends to the view (postMessage
    {bd: "compose", jeton})."""
    if not scope or scope["charge"].get("mode") != "composer" or not scope.get("jeton"):
        raise BlueDynamicError("session", "Only a composer session renders a mail")
    composed_mails.put(scope["jeton"], check_mail(mail))
    return scope["jeton"]


def compose(bearer, jeton, origins, ask_plugin=None):
    """api=composer: the JWS of the mail of `jeton`, signed with its
    provider's key. `bearer` is ProAdmin's typ bd-api token, for this host.
    When the plugin made no mail yet, ask_plugin(provider, session id) asks
    its compose action (§8)."""
    if not isinstance(jeton, str) or not RE_JETON.match(jeton):
        raise BlueDynamicError("jeton", "No usable jeton", 400)
    verify(bearer, "bd-api", origins)
    entry = composed_mails.take(jeton)
    if entry is None:
        raise BlueDynamicError("jeton", "Unknown or expired jeton", 404)
    provider = Provider.find(entry["fournisseur"])
    if provider is None:
        raise BlueDynamicError("fournisseur", "Unknown provider", 404)
    # the token was for one of this server's origins; the mail must come from
    # the provider ProAdmin knows at that origin
    verify_audience(bearer, provider.origin)
    mail = entry["mail"]
    if mail is None:
        if ask_plugin is None:
            composed_mails.give_back(jeton, entry)
            raise BlueDynamicError("mail", "The composer made no mail yet", 409)
        try:
            mail = check_mail(ask_plugin(provider, entry["session"]))
        except BlueDynamicError:
            composed_mails.give_back(jeton, entry)
            raise
    now = int(time.time())
    return provider.sign(dict(mail, jeton=jeton, iat=now))


# the services (§9)

def _service_demand(demande):
    """The demand of an api=service call: base64url of its JSON (§9.3)."""
    if not isinstance(demande, str) or len(demande) > SERVICE_LIMIT * 2:
        raise BlueDynamicError("demande", "No usable demand", 400)
    try:
        value = json.loads(b64url_decode(demande).decode("utf-8"))
    except Exception:  # noqa - whatever is wrong, the demand is unusable
        raise BlueDynamicError("demande", "The demand is not base64url JSON", 400)
    if not isinstance(value, dict):
        raise BlueDynamicError("demande", "The demand is not an object", 400)
    for name in ("parametres", "contexte"):
        if not isinstance(value.get(name, {}), dict):
            raise BlueDynamicError("demande", "%s is an object" % name, 400)
    if not isinstance(value.get("service"), str) or not RE_SERVICE.match(value["service"]):
        raise BlueDynamicError("demande", "service is the id of a service", 400)
    contexte = value.get("contexte") or {}
    if not isinstance(contexte.get("abonnement"), str) or not RE_ABONNEMENT.match(contexte["abonnement"]):
        raise BlueDynamicError("demande", "contexte.abonnement is bda- and 16 hexadecimal digits", 400)
    return value


def service_scope(provider, charge):
    """The scope of a service session (§9.3): no page, no reader's ticket;
    it lives the time of the call."""
    now = int(time.time())
    return {"fournisseur": provider.id, "application": provider.application, "charge": charge,
            "page": None, "dynamique": None, "jeton": None, "taille": (800, 600),
            "inactivite": SERVICE_LIFETIME, "fin": now + SERVICE_LIFETIME}


def parse_service_reply(reply):
    """What the plugin's service action answered: {resultat, mail?}, or the
    API's usual ["success", {...}] / ["error", ...]."""
    if isinstance(reply, bytes):
        reply = reply.decode("utf-8", "replace")
    if isinstance(reply, str):
        if len(reply) > SERVICE_LIMIT:
            raise BlueDynamicError("plugin", "The plugin answered too much", 502)
        try:
            reply = json.loads(reply.strip() or "null")
        except ValueError:
            raise BlueDynamicError("plugin", "The plugin's service answer is not JSON", 502)
    if isinstance(reply, list) and reply:
        if reply[0] == "error":
            raise BlueDynamicError("plugin", "The plugin refused: %s" % " ".join(str(each) for each in reply[1:]), 502)
        if reply[0] == "success":
            return parse_service_reply(reply[1] if len(reply) > 1 else None)
    if not isinstance(reply, dict) or "resultat" not in reply:
        raise BlueDynamicError("plugin", "A service answers {resultat, mail?}", 502)
    result = {"resultat": reply["resultat"]}
    if reply.get("mail"):
        result["mail"] = check_mail(reply["mail"])
    return result


def service(bearer, demande, origins, ask_plugin):
    """api=service (§9.3): the JWS, signed with the provider's key, of what
    its service answered. `bearer` is ProAdmin's typ bd-api token for this
    host; ask_plugin(provider, charge, donnees) runs the plugin's service
    action in a session of its own."""
    claims = verify(bearer, "bd-api", origins)
    value = _service_demand(demande)
    provider = Provider.find(value.get("fournisseur"))
    if provider is None or not provider.api.get("conteneur"):
        raise BlueDynamicError("fournisseur", "Unknown provider", 404)
    verify_audience(bearer, provider.origin)
    if value["service"] not in provider.services:
        raise BlueDynamicError("service", "Service %s not declared" % value["service"], 404)
    contexte = value.get("contexte") or {}
    charge = {"mode": "service", "fournisseur": provider.id, "service": value["service"], "iss": claims["iss"],
              "contexte": contexte, "lecteur": contexte.get("demandeur") or "", "societe": contexte.get("societe") or ""}
    donnees = {"service": value["service"], "parametres": value.get("parametres") or {}, "contexte": contexte}
    result = parse_service_reply(ask_plugin(provider, charge, donnees))
    now = int(time.time())
    return provider.sign(dict(result, typ="bd-service", service=value["service"], abonnement=contexte["abonnement"],
                              iat=now, exp=now + 300))


def event(scope, charge, post=None):
    """BlueDynamic_Evenement (§9.4): sign an event of the provider of this
    session with its key and send it to the ProAdmin that issued the
    session's ticket. ProAdmin's answer."""
    if not scope:
        raise BlueDynamicError("session", "Not a BlueMail session")
    provider = Provider.find(scope["fournisseur"])
    if provider is None:
        raise BlueDynamicError("fournisseur", "Unknown provider", 404)
    issuer = (scope.get("charge") or {}).get("iss")
    if not isinstance(issuer, str) or issuer not in settings.BLUEDYNAMIC_ISSUERS:
        raise BlueDynamicError("emetteur", "No ProAdmin to tell")
    if not isinstance(charge, dict):
        raise BlueDynamicError("evenement", "The event is an object", 400)
    if not isinstance(charge.get("abonnement"), str) or not RE_ABONNEMENT.match(charge["abonnement"]):
        raise BlueDynamicError("evenement", "abonnement is bda- and 16 hexadecimal digits", 400)
    if not isinstance(charge.get("id"), str) or not RE_EVENEMENT.match(charge["id"]):
        raise BlueDynamicError("evenement", "id is bde- and 32 hexadecimal digits", 400)
    if not isinstance(charge.get("evenement"), str) or not RE_SERVICE.match(charge["evenement"]):
        raise BlueDynamicError("evenement", "evenement is the id of an event", 400)
    donnees = charge.get("donnees") or {}
    if not isinstance(donnees, dict) or len(json.dumps(donnees)) > 16384:
        raise BlueDynamicError("evenement", "donnees is an object of 16 KiB at most", 400)
    now = int(time.time())
    token = provider.sign({"typ": "bd-evenement", "fournisseur": provider.id, "abonnement": charge["abonnement"],
                           "id": charge["id"], "evenement": charge["evenement"], "donnees": donnees,
                           "iat": now, "exp": now + 300, "jti": os.urandom(16).hex()})
    return (post or post_form)(issuer.rstrip("/") + "/bluedynamic/evenement", {"evenement": token}, None)


# what ProAdmin hands a plugin through its page (§9.6): a receipt, a recipient

PROADMIN_TYPES = "bd-recu", "bd-destinataire", "bd-depot"


def verify_for_provider(scope, token, typ):
    """BlueDynamic_Verifier: the claims of a JWS of ProAdmin of type `typ`
    (one of PROADMIN_TYPES), made for the provider of this session (aud =
    its host): a plugin trusts what its page relays only once verified."""
    if not scope:
        raise BlueDynamicError("session", "Not a BlueMail session")
    if typ not in PROADMIN_TYPES:
        raise BlueDynamicError("typ", "Not a type ProAdmin hands a plugin", 400)
    provider = Provider.find(scope["fournisseur"])
    if provider is None or not provider.origin:
        raise BlueDynamicError("fournisseur", "Unknown provider", 404)
    claims = verify(token, typ, [provider.origin])
    if claims.get("fournisseur") not in (None, provider.id):
        raise BlueDynamicError("fournisseur", "Made for another provider")
    return claims


def verify_audience(token, expected):
    """The aud of a token already verified is `expected`."""
    claims = jwt.decode(token, options={"verify_signature": False})
    audience = claims.get("aud")
    audiences = audience if isinstance(audience, list) else [audience]
    if not expected or expected not in [origine(each) for each in audiences]:
        raise BlueDynamicError("aud", "Not for this provider")



# the ticket, whole (§4.1, steps 1 and 2)

def open_ticket(ticket, origins):
    """(claims, provider) of a player ticket: verified, its jti used, its
    provider at the origin it was issued for, what it names declared."""
    claims = verify_ticket(ticket, origins)
    provider = Provider.find(claims.get("fournisseur"))
    if provider is None or not provider.api.get("conteneur"):
        raise BlueDynamicError("fournisseur", "Unknown provider %s" % claims.get("fournisseur"), 404)
    verify_audience(ticket, provider.origin)
    provider.check(claims)
    return claims, provider


# what the plugin answers (§8)

def parse_wholexml(text):
    """(vdomxml, events) of a WHOLEXML: <WHOLEXML> with its <VDOMXML> and
    its <EVENTS> (the E2VDOM actions, JSON), as the EAC had them."""
    from defusedxml.minidom import parseString
    try:
        document = parseString(text.encode("utf-8") if isinstance(text, str) else text)
    except Exception as error:
        raise BlueDynamicError("wholexml", "The WHOLEXML cannot be read: %s" % error, 502)
    root = document.documentElement
    if root.tagName.upper() != "WHOLEXML":
        raise BlueDynamicError("wholexml", "Not a WHOLEXML", 502)

    def text_of(name):
        for each in root.childNodes:
            if getattr(each, "tagName", "").upper() == name:
                return "".join(node.data for node in each.childNodes
                               if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE)).strip()
        return ""

    vdomxml, events = text_of("VDOMXML"), text_of("EVENTS")
    if not vdomxml:
        raise BlueDynamicError("wholexml", "The WHOLEXML has no VDOMXML", 502)
    check_events(events)
    return vdomxml, events


def check_events(events):
    """The E2VDOM actions of a WHOLEXML: {"object:event": [step, ...]} where
    a step is a client action ["object:action", parameter, ...] or a name the
    server hears (the plugin's event). A bare string would be server code
    run by this server (memory/vdomjson): refused."""
    if not events:
        return
    try:
        declared = json.loads(events)
    except ValueError:
        raise BlueDynamicError("wholexml", "EVENTS is not JSON", 502)
    if not isinstance(declared, dict):
        raise BlueDynamicError("wholexml", "EVENTS is an object", 502)
    for key, steps in declared.items():
        if not isinstance(key, str) or key.count(":") != 1 or not isinstance(steps, list):
            raise BlueDynamicError("wholexml", "EVENTS: %s is not object:event with a list" % key, 502)
        for step in steps:
            if isinstance(step, str):
                continue
            if not (isinstance(step, list) and step and all(isinstance(each, str) for each in step)
                    and step[0].count(":") == 1):
                raise BlueDynamicError("wholexml", "EVENTS: a step of %s is not usable" % key, 502)


def parse_reply(reply):
    """What the plugin answered, as one of
        ("wholexml", vdomxml, events)
        ("compose", mail)              {"bd": "compose", "mail": {...}}
        ("mail", mail)                 a mail (the compose action)
    It answers a WHOLEXML as is, or the API's usual JSON: ["success", data],
    ["error", motif...], or the data itself."""
    if isinstance(reply, bytes):
        reply = reply.decode("utf-8", "replace")
    if isinstance(reply, str):
        if len(reply) > WHOLEXML_LIMIT:
            raise BlueDynamicError("plugin", "The plugin answered too much", 502)
        text = reply.strip()
        if not text:
            raise BlueDynamicError("plugin", "The plugin answered nothing", 502)
        if text[:20].upper().startswith("<WHOLEXML") or text.startswith("<?xml"):
            return ("wholexml",) + parse_wholexml(text)
        try:
            reply = json.loads(text)
        except ValueError:
            raise BlueDynamicError("plugin", "The plugin answered neither a WHOLEXML nor JSON", 502)
    if isinstance(reply, list) and reply:
        if reply[0] == "error":
            raise BlueDynamicError("plugin", "The plugin refused: %s" % " ".join(str(each) for each in reply[1:]), 502)
        if reply[0] == "success":
            return parse_reply(reply[1] if len(reply) > 1 else "")
    if isinstance(reply, dict):
        if reply.get("bd") == "compose":
            return "compose", check_mail(reply.get("mail"))
        if "application" in reply:
            return "mail", check_mail(reply)
    raise BlueDynamicError("plugin", "The plugin's answer is not usable", 502)


# the session (§4.1, step 3)

def scope(claims, application, session_id=None):
    """What a BlueMail session may act on, and until when. The page and its
    dynamic object are set once the page is made (admin/bluedynamic.py)."""
    result = {
        "fournisseur": claims["fournisseur"],
        "application": application,
        "charge": claims,
        "page": None,
        "dynamique": None,
        "jeton": None,
        "taille": (800, 600),
        "inactivite": settings.BLUEDYNAMIC_SESSION_IDLE,
        "fin": claims["exp"] + settings.BLUEDYNAMIC_SESSION_GRACE,
    }
    if claims.get("mode") == "composer":
        result["jeton"] = composed_mails.open(claims["fournisseur"], session_id, result["fin"])
    return result


def headers(origins):
    """§4.1, step 4."""
    allowed = " ".join(each for each in (origine(value) for value in origins or []) if each)
    return {
        "Content-Security-Policy": "frame-ancestors %s" % (allowed or "'none'"),
        "Referrer-Policy": "no-referrer",
        "Cache-Control": "no-store",
    }
