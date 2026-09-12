"""Authentication for the WebDAV shares of a VDOM application.

Ported to the wsgidav 4 domain controller interface.

Two things changed shape, and both broke WebDAV outright:

* wsgidav 4 takes a domain controller **class** and instantiates it itself, as
  `dc(wsgidav_app, config)`. The old code handed it a ready-made instance, so
  `make_domain_controller` refused it with

      Could not resolve domain controller class (got <...VDOM_domain_controller object...>)

  and `WsgiDAVApp` was never built. Every share was dead, silently: the
  exception was caught and printed while the server carried on.

  A controller here needs to know which application it serves, which is why the
  instance existed. The application id now travels in the config, under
  `vdom_appid`, and the class reads it - the way wsgidav expects a controller to
  be configured.

* the methods were the wsgidav 1 names: getDomainRealm, requireAuthentication,
  isRealmUser, getRealmUserPassword, authDomainUser. Version 4 calls
  get_domain_realm, require_authentication, basic_auth_user,
  supports_http_digest_auth and digest_auth_user.

The digest middleware that used to live here is gone with them. It existed
because wsgidav 1 computed the digest response itself and had to be told where
to find A1; version 4 asks the controller for A1 through `digest_auth_user`,
which is also where the session is established now.
"""
import json

import managers
from wsgidav.dc.base_dc import BaseDomainController
from wsgidav.mw.base_mw import BaseMiddleware


def already_signed_in(session):
    """Whether the application already holds a user for this session.

    Two keys, because the application has two ways in: `ProAdmin.login` - what
    a password check goes through - leaves `current_user`, while
    `ProAdmin.set_user`, used when the password was proved elsewhere, leaves
    `sudo`. `current_user()` reads both, so anything asking "is someone logged
    in" has to read both too. Reading only one is how the Digest path looked
    signed in to wsgidav and empty to the application.

    `dav_user` is deliberately not in this list: it says an HTTP credential was
    seen, not that the application accepted anyone.
    """
    if session is None:
        return False
    return bool(session.get("sudo") or session.get("current_user"))


def current_session():
    """The current session, or None when there is no request.

    wsgidav asks whether a share is anonymous while it is building the
    application - wsgidav_app calls is_share_anonymous for each share, which
    calls require_authentication(share, None). That happens on the startup
    thread, where request_manager.current raises "No request associated with
    current thread". Raising there cost every share: the exception came out of
    WsgiDAVApp(), no application ever got a wsgidav_app, and WebDAV was dead.
    """
    try:
        return managers.request_manager.current.session()
    except Exception:
        return None


def authAppUser(app_id, obj_id, user, password):
    try:
        xml_data = """{"user": "%s","password": "%s"}""" % (user, password)
        return managers.dispatcher.dispatch_action(app_id, obj_id, "authentication", "", xml_data)
    except Exception as e:
        debug("DAV auth error: %s" % e)
        return False


def authGetDigest(app_id, obj_id, user):
    try:
        xml_data = json.dumps({"user": user})
        return managers.dispatcher.dispatch_action(app_id, obj_id, "getDigest", "", xml_data)
    except Exception as e:
        debug("DAV auth error: %s" % e)
        return ""


class VDOM_domain_controller(BaseDomainController):
    """The realm is the id of the object that owns the share.

    Authentication is delegated to that object: the application decides who may
    mount it, through its own `authentication` and `getDigest` actions.
    """

    def __init__(self, wsgidav_app, config):
        super().__init__(wsgidav_app, config)
        # Which application this controller speaks for. Put here by
        # VDOM_webdav_manager, because wsgidav owns the construction and cannot
        # be given a pre-built instance.
        appid = config.get("vdom_appid")
        try:
            self._application = managers.memory.applications.get(appid)
        except Exception:
            self._application = None

    def __str__(self):
        app = self._application.id if self._application else "?"
        return "%s(%s)" % (self.__class__.__name__, app)

    def get_domain_realm(self, path_info, environ):
        """The realm of a share is the id of the object publishing it."""
        provider = environ.get("wsgidav.provider") if environ else None
        if not provider:
            return None
        obj_name = provider.share_path.strip("/")
        if obj_name == "":
            return ""
        if not self._application:
            return None
        obj = self._application.objects.get(obj_name)
        return obj.id if obj else None

    def require_authentication(self, realm, environ):
        """A session that already carries a user does not authenticate again.

        Asked outside a request - see _session - the answer is yes: nothing has
        proved who is calling, and a share that answers "anonymous" there would
        be published without a password.
        """
        session = current_session()
        if session is None:
            return True
        return not already_signed_in(session)

    def supports_http_digest_auth(self):
        # The application stores a digest for its users - see getDigest - so we
        # can answer A1 without ever holding a plain password.
        return True

    def basic_auth_user(self, realm, user_name, password, environ):
        obj_id = realm
        if not self._application:
            return False
        session = current_session()
        if session is None:
            return False
        known = (self._application.id, obj_id, user_name, password)
        if session.get("dav_user") == known:
            return True
        if authAppUser(self._application.id, obj_id, user_name, password):
            session["dav_user"] = known
            return True
        return False

    def digest_auth_user(self, realm, user_name, environ):
        """The A1 hash for this user, from the application.

        Also what establishes the session: under wsgidav 1 a middleware called
        authDomainUser after the digest was checked, for that side effect
        alone. There is no such hook in version 4, and this is the only place
        the controller is asked about the user.
        """
        obj_id = realm
        if not self._application:
            return False
        if obj_id == "/":
            shares = managers.webdav_manager.list_webdav(self._application.id)
            if not shares:
                return False
            obj_id = shares[0]

        session = current_session()
        if session is None:
            return False
        digest = session.get("dav_digest")
        if not digest:
            digest = authGetDigest(self._application.id, obj_id, user_name)
            if digest:
                session["dav_digest"] = digest
        # Rien n'est pose dans la session ici. wsgidav demande A1 AVANT de
        # verifier la reponse du client : marquer l'utilisateur a cet instant
        # revient a croire quiconque sait nommer un utilisateur. La ligne qui
        # posait dav_user ne donnait pas l'acces aux donnees - l'application
        # n'etait pas connectee pour autant - mais elle faisait repondre oui a
        # require_authentication, donc toute la suite de la session passait sans
        # aucune authentification, et echouait en 500 au lieu de 401.
        return digest or False


class VDOM_application_login(BaseMiddleware):
    """Log the user wsgidav has authenticated into the application itself.

    Two notions of "logged in" meet here. wsgidav proves who is calling, over
    Basic or Digest. The actions behind every share ask the application -
    `ProAdmin.current_user()` - and refuse the read when it answers nothing:

        AuthorisationError: No one is logged in.
        path .................. '/'
        user .................. None

    The Basic path happens to establish both at once: `basic_auth_user` checks
    the password by calling the share's `authentication` action, and that action
    logs the user in as a side effect. That is why a browser worked and the
    Windows client did not - Windows refuses Basic over plain HTTP and uses
    Digest, and nothing on the Digest path ever calls `authentication`.

    Under wsgidav 1 a digest middleware called authDomainUser once the response
    had been checked, for that side effect alone. Version 4 has no such hook:
    `digest_auth_user` is asked for A1 *before* the client's response is
    verified, so logging the user in there would hand the share to anyone who
    can name a user - no password needed. It has to happen after.

    So it happens here, right after HTTPAuthenticator and before anything
    reaches the provider. `wsgidav.auth.user_name` is set only once the
    credentials have been checked, which is exactly the guarantee that was
    missing.
    """

    def __call__(self, environ, start_response):
        try:
            self._ouvrir(environ)
        except Exception as e:
            debug("WebDAV: ouverture de session impossible: %s" % e)
        return self.next_app(environ, start_response)

    def _ouvrir(self, environ):
        user = environ.get("wsgidav.auth.user_name")
        if not user:
            # Anonymous share, or authentication skipped because the session
            # already carries a user - see require_authentication.
            return
        session = current_session()
        if session is None or already_signed_in(session):
            return
        provider = environ.get("wsgidav.provider")
        obj = getattr(provider, "obj", None)
        app = getattr(provider, "application", None)
        if not obj or not app:
            return
        # An empty password on purpose: the action reads the Authorization
        # scheme and, for Digest, sets the user without one. The password has
        # already been proved - by the digest, or by basic_auth_user.
        authAppUser(app.id, obj.id, user, "")
