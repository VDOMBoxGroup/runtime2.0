import re
import threading

import requests
# from suds.client import Client   # replaced: suds wants a WSDL, not a namespace kwarg
# import SOAPpy

from utils.exception import VDOMServiceCallError
from utils.exception import exception_message


__version__ = '0.1.6'


session_id_re = re.compile(r"\<SessionId\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionId\>")
session_key_re = re.compile(r"\<SessionKey\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionKey\>")
hash_string_re = re.compile(r"\<HashString\>\<\!\[CDATA\[(\S+)\]\]\>\<\/HashString\>")
key_re = re.compile(r"\<Key\>(\S+)_\d+\<\/Key\>")


class _RawSoapProxy(object):
    """A plain requests-based SOAP client for the VDOM /SOAP endpoint.

    It replaces the suds ``Client``, which this module called SOAPpy-style with
    a ``namespace=`` kwarg it does not accept (suds needs a WSDL). The VDOM
    server speaks a fixed, WSDL-less SOAP: one operation per server method, its
    parameters named, markup carried as CDATA, and the answer returned in a
    ``Result`` element. This talks exactly that, so ``VDOMServiceSingleThread``
    keeps calling ``self._server.open_session(...)`` / ``.remote_call(...)``
    unchanged. Ported from the standalone client proven against the real PIS.

    The caller passes positional arguments; the server wants them named. The
    signature table maps position to name per method (see sources/soap/
    functions.py); an unlisted method falls back to positional ``vN`` names.
    """

    _NS = "http://services.vdom.net/VDOMServices"
    _ENV_NS = "http://schemas.xmlsoap.org/soap/envelope/"
    _SIG = {
        "open_session": ("name", "pwd_md5"),
        "close_session": ("sid",),
        "list_applications": ("sid", "skey"),
        "get_top_objects": ("sid", "skey", "appid"),
        "get_server_actions_list": ("sid", "skey", "appid", "objid"),
        "remote_call": ("sid", "skey", "appid", "objid",
                        "func_name", "xml_param", "xml_data"),
        "keep_alive": ("sid", "skey"),
    }

    def __init__(self, url):
        self._soap_url = url.rstrip("/") + "/SOAP"
        self._http = requests.Session()
        # Local instances sit behind a TLS-inspecting proxy and PIS answers on
        # a cert this box does not chain; the SOAP payload carries its own
        # session security, so certificate pinning buys nothing here.
        self._http.verify = False

    def __getattr__(self, method):
        names = self._SIG.get(method)

        def _call(*args):
            if names is not None:
                params = list(zip(names, args))
            else:
                params = [("v%d" % (i + 1), a) for i, a in enumerate(args)]
            return self._send(method, params)

        return _call

    def _send(self, method, params):
        import xml.etree.ElementTree as ET

        parts = []
        for name, value in params:
            value = u"" if value is None else u"%s" % (value,)
            if ("<" in value) or (">" in value) or ("&" in value):
                parts.append(u"<%s><![CDATA[%s]]></%s>" % (name, value, name))
            else:
                parts.append(u"<%s>%s</%s>" % (name, value, name))
        body = u"".join(parts)
        envelope = (
            u'<?xml version="1.0" encoding="UTF-8"?>'
            u'<soap:Envelope xmlns:soap="%s" xmlns:s0="%s">'
            u'<soap:Body><s0:%s>%s</s0:%s></soap:Body></soap:Envelope>'
            % (self._ENV_NS, self._NS, method, body, method)
        )
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": '"%s/%s"' % (self._NS, method),
        }
        resp = self._http.post(
            self._soap_url, data=envelope.encode("utf-8"), headers=headers)

        try:
            root = ET.fromstring(resp.text)
        except Exception:
            return resp.text
        result_el = root.find(".//{%s}Result" % self._NS)
        if result_el is None:
            result_el = root.find(".//Result")
        if result_el is not None and result_el.text is not None:
            return result_el.text
        body_el = root.find(".//{%s}Body" % self._ENV_NS)
        if body_el is not None:
            return ET.tostring(body_el, encoding="unicode")
        return resp.text


class VDOMServiceSingleThread(object):
    def __init__(self, url, login, md5hexpass, application_id):
        self._url = url
        self._login = login
        self._md5hexpass = md5hexpass
        self._application_id = application_id

        self._request_num = 0
        self._skey = None
        self._sid = None
        self._skey = None

        self._server = self.__create_soap_proxy(url)
        self._protector = None

    def __create_soap_proxy(self, url):
        if '://' not in url:
            url = 'http://' + url

        if url.lower().startswith('https://'):
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context

        self._url = url
        return _RawSoapProxy(url)

    def __request_skey(self):
        return '{0}_{1:d}'.format(self._skey, self._request_num)

    def open_session(self):
        login_result = self._server.open_session(self._login, self._md5hexpass)

        self._request_num = 0

        self._sid = str(session_id_re.search(login_result, 1).group(1))
        skey = str(session_key_re.search(login_result, 1).group(1))
        hash_string = str(hash_string_re.search(login_result, 1).group(1))

        self._protector = VDOM_session_protector(hash_string)
        self._skey = self._protector.next_session_key(skey)

        return self

    def call(self, container_id, action_name, xml_data):
        xml_param = "<Arguments><CallType>server_action</CallType></Arguments>"
        ret = None

        try:
            ret = self._server.remote_call(self._sid, self.__request_skey(
            ), self._application_id, container_id, action_name, xml_param, xml_data)

        except Exception as ex:
            if ret:
                raise VDOMServiceCallError(str(ret))
            else:
                raise VDOMServiceCallError(exception_message(ex))

        if ret == 'None':
            raise VDOMServiceCallError('Session is closed')

        self._skey = self._protector.next_session_key(self._skey)
        self._request_num += 1

        return key_re.sub('', ret)

    def remote(self, method_name, params=None, no_app_id=False):
        params = params or []

        if not no_app_id:
            params.insert(0, self._application_id)

        ret = None
        try:
            soap_method = getattr(self._server, method_name)
            ret = soap_method(self._sid, self.__request_skey(), *params)

        except Exception as ex:
            if ret:
                raise VDOMServiceCallError(str(ret))
            else:
                raise VDOMServiceCallError(getattr(ex, "message", None) or getattr(
                    ex, "faultstring", None) or str(ex))

        self._skey = self._protector.next_session_key(self._skey)
        self._request_num += 1

        return key_re.sub('', ret)

    @classmethod
    def connect(cls, url, login, md5_hexpass, application_id):
        service = cls(url, login, md5_hexpass, application_id)
        return service.open_session()


class VDOMServiceMultiThread(VDOMServiceSingleThread):
    def __init__(self, url, login, md5hexpass, application_id):
        VDOMServiceSingleThread.__init__(
            self, url, login, md5hexpass, application_id)
        self.__thread = threading.local()

    def api(self):
        if getattr(self.__thread, 'api', None) is None:
            self.__thread.api = VDOMServiceSingleThread(
                self._url, self._login, self._md5hexpass, self._application_id)
            self.__thread.api.open_session()
        return self.__thread.api

    def open_session(self):
        self.api().open_session()
        return self

    def call(self, container_id, action_name, xml_data):
        return self.api().call(container_id, action_name, xml_data)

    def remote(self, method_name, params=None, no_app_id=False):
        return self.api().remote(method_name, params, no_app_id)


VDOMService = VDOMServiceMultiThread
VDOM_service = VDOMServiceMultiThread


try:
    from soap.soaputils import VDOM_session_protector
except ImportError:
    from scripting.soap.soaputils import VDOM_session_protector
