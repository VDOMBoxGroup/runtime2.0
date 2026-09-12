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

    def _session(self):
        """The current session, or None when there is no request.

        wsgidav asks whether a share is anonymous while it is building the
        application - wsgidav_app calls is_share_anonymous for each share, which
        calls require_authentication(share, None). That happens on the startup
        thread, where request_manager.current raises "No request associated with
        current thread". Raising there cost every share: the exception came out
        of WsgiDAVApp(), no application ever got a wsgidav_app, and WebDAV was
        dead.
        """
        try:
            return managers.request_manager.current.session()
        except Exception:
            return None

    def require_authentication(self, realm, environ):
        """A session that already carries a user does not authenticate again.

        Asked outside a request - see _session - the answer is yes: nothing has
        proved who is calling, and a share that answers "anonymous" there would
        be published without a password.
        """
        session = self._session()
        if session is None:
            return True
        return "current_user" not in session and "dav_user" not in session

    def supports_http_digest_auth(self):
        # The application stores a digest for its users - see getDigest - so we
        # can answer A1 without ever holding a plain password.
        return True

    def basic_auth_user(self, realm, user_name, password, environ):
        obj_id = realm
        if not self._application:
            return False
        session = self._session()
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

        session = self._session()
        if session is None:
            return False
        digest = session.get("dav_digest")
        if not digest:
            digest = authGetDigest(self._application.id, obj_id, user_name)
            if digest:
                session["dav_digest"] = digest
        if not digest:
            return False
        session["dav_user"] = (self._application.id, obj_id, user_name, None)
        return digest
