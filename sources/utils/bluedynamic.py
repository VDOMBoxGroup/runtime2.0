"""BlueDynamic: what a VDOM server needs to show a BlueMail.

A BlueMail is a mail that carries the descriptor of an application of this
server. ProAdmin's mail view shows it in an iframe served from here, with a
short ticket that ProAdmin signed. The contract that fixes every format is
sites/proadmin/CONTRAT_BLUEDYNAMIC.md (ProAdmin's repository); the sections
cited below are its own.

A provider ("fournisseur") is a folder under settings.BLUEDYNAMIC_LOCATION,
named after the id of its manifest:

    <BLUEDYNAMIC_LOCATION>/<id>/fournisseur.json
        {"application": "<guid of the VDOM application that serves it>",
         "manifeste": {...the manifest of §2.2...},
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

MODES = "lire", "composer"
COMMANDES = "new", "reply", "reply_all", "forward"
CONTEXTE = "objet", "de", "a", "cc", "date", "texte"
METHODES = "new", "update", "delete"

LEEWAY = 5  # seconds of clock difference accepted on exp and iat
JWKS_RETRY = 30  # at most one reading a key set this often, on unknown kids
MAIL_LIFETIME = 900  # a composed mail waits this long for ProAdmin
MANIFEST_LIMIT = 64 * 1024  # §2.2


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
        raise BlueDynamicError("rejoue", "This ticket was used already")
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

    def container(self, claims):
        """The container a ticket may open: it must be the one the manifest
        gives for this mode (§4.1, step 2)."""
        name = claims.get("conteneur")
        if not isinstance(name, str) or not name:
            raise BlueDynamicError("conteneur", "No container", 400)
        if claims["mode"] == "lire":
            for each in self.manifest.get("applications") or []:
                if each.get("id") == claims.get("application") and each.get("conteneur") == name:
                    return name
        else:
            for each in self.manifest.get("composeurs") or []:
                if each.get("conteneur") == name and claims.get("commande") in (each.get("commandes") or []):
                    return name
        raise BlueDynamicError("conteneur", "Container %s not declared for %s" % (name, claims["mode"]))

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
        if not isinstance(each, dict) or not each.get("id") or not each.get("conteneur"):
            raise BlueDynamicError("manifeste", "An application needs an id and a container", 400)
    for each in manifest.get("composeurs") or []:
        if not isinstance(each, dict) or not each.get("id") or not each.get("conteneur"):
            raise BlueDynamicError("manifeste", "A composer needs an id and a container", 400)
        if not set(each.get("commandes") or []) <= set(COMMANDES):
            raise BlueDynamicError("manifeste", "commandes is a part of %s" % ", ".join(COMMANDES), 400)
        if not set(each.get("contexte") or []) <= set(CONTEXTE):
            raise BlueDynamicError("manifeste", "contexte is a part of %s" % ", ".join(CONTEXTE), 400)


def post_form(url, fields, bearer, timeout=20.0):
    """POST a form, the answer's JSON. Module level, so a test can replace it."""
    body = urllib.parse.urlencode(fields).encode("ascii")
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": "Bearer %s" % bearer,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"})
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
    provider = Provider.find(manifest["id"])
    if provider is None:
        provider = Provider.create(manifest["id"], application)
    elif provider.application != application:
        raise BlueDynamicError("fournisseur", "Provider %s belongs to another application" % manifest["id"])
    manifest = dict(manifest, cle_publique=provider.public_key())
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
    """The mails a composer rendered, by jeton, until ProAdmin asks for them
    (api=composer) - once."""

    def __init__(self):
        self._lock = threading.Lock()
        self._mails = {}  # jeton: (until, provider id, mail)

    def clear(self):
        with self._lock:
            self._mails.clear()

    def put(self, provider, mail):
        jeton = secrets.token_hex(16)
        now = time.time()
        with self._lock:
            for each in [key for key, value in self._mails.items() if value[0] < now]:
                del self._mails[each]
            self._mails[jeton] = (now + MAIL_LIFETIME, provider, mail)
        return jeton

    def take(self, jeton):
        with self._lock:
            entry = self._mails.pop(jeton, None)
        if entry is None or entry[0] < time.time():
            return None
        return entry[1], entry[2]


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
    """Keep the mail a composer made in a BlueMail session, the jeton the page
    sends to the view (postMessage {bd: "compose", jeton})."""
    if not scope or scope["charge"].get("mode") != "composer":
        raise BlueDynamicError("session", "Only a composer session renders a mail")
    return composed_mails.put(scope["fournisseur"], check_mail(mail))


def compose(bearer, jeton, origins):
    """api=composer: the JWS of the mail kept under `jeton`, signed with its
    provider's key. `bearer` is ProAdmin's typ bd-api token, for this host."""
    if not isinstance(jeton, str) or not RE_JETON.match(jeton):
        raise BlueDynamicError("jeton", "No usable jeton", 400)
    verify(bearer, "bd-api", origins)
    entry = composed_mails.take(jeton)
    if entry is None:
        raise BlueDynamicError("jeton", "Unknown or expired jeton", 404)
    identifier, mail = entry
    provider = Provider.find(identifier)
    if provider is None:
        raise BlueDynamicError("fournisseur", "Unknown provider", 404)
    # the token was for one of this server's origins; the mail must come from
    # the provider ProAdmin knows at that origin
    verify_audience(bearer, provider.origin)
    now = int(time.time())
    return provider.sign(dict(mail, jeton=jeton, iat=now))


def verify_audience(token, expected):
    """The aud of a token already verified is `expected`."""
    claims = jwt.decode(token, options={"verify_signature": False})
    audience = claims.get("aud")
    audiences = audience if isinstance(audience, list) else [audience]
    if not expected or expected not in [origine(each) for each in audiences]:
        raise BlueDynamicError("aud", "Not for this provider")


# the ticket, whole (§4.1, steps 1 and 2)

def open_ticket(ticket, origins):
    """(claims, provider, container name) of a player ticket: verified, its
    jti used, its provider at the origin it was issued for, its container
    declared for its mode."""
    claims = verify_ticket(ticket, origins)
    provider = Provider.find(claims.get("fournisseur"))
    if provider is None:
        raise BlueDynamicError("fournisseur", "Unknown provider %s" % claims.get("fournisseur"), 404)
    verify_audience(ticket, provider.origin)
    return claims, provider, provider.container(claims)


# the session (§4.1, step 3)

def scope(claims, application, container):
    """What a BlueMail session may act on, and until when."""
    return {
        "fournisseur": claims["fournisseur"],
        "application": application,
        "conteneur": container,
        "charge": claims,
        "inactivite": settings.BLUEDYNAMIC_SESSION_IDLE,
        "fin": claims["exp"] + settings.BLUEDYNAMIC_SESSION_GRACE,
    }


def headers(origins):
    """§4.1, step 4."""
    allowed = " ".join(each for each in (origine(value) for value in origins or []) if each)
    return {
        "Content-Security-Policy": "frame-ancestors %s" % (allowed or "'none'"),
        "Referrer-Policy": "no-referrer",
        "Cache-Control": "no-store",
    }
