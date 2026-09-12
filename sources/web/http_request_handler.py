"""server request handler module"""

import sys
import io
import shutil
import socket
import traceback
import time
import SOAPpy
import threading
import urllib.parse
import select
import http.server
from wsgiref.util import guess_scheme
from io import BytesIO
# import mimetypes
# import re
# import time
# import SocketServer
# import os
# import posixpath

# import webdav_server
# from wsgidav.wsgidav_app import WsgiDAVApp
from request.request import VDOM_request
import settings
import managers


from version import SERVER_NAME, SERVER_VERSION
from soap.wsdl import methods as soap_methods
from utils.pages import compose_page, compose_trace

# A class to describe how header messages are handled


THREAD_ATTRIBUTE_NAME = "vdom_web_server_request"


class HeaderHandler(object):
    # Initially fail out if there are any problems.
    def __init__(self, header, attrs):
        for i in list(header.__dict__.keys()):
            if i[0] == "_":
                continue

            d = getattr(header, i)

            try:
                fault = int(attrs[id(d)][(SOAPpy.NS.ENV, "mustUnderstand")])
            except Exception:  # noqa
                fault = 0

            if fault:
                raise SOAPpy.faultType("%s:MustUnderstand" % SOAPpy.NS.ENV_T, "Required Header Misunderstood", "%s" % i)


# for the soap handler
_contexts = dict()


class VDOM_bounded_input(object):
    """wsgi.input, bounded by Content-Length.

    The WSGI specification asks for an input stream that returns b"" at the end
    of the request body. We passed self.rfile, the raw socket, which never ends:
    past the body, read() waits for the next request.

    wsgidav reads a PUT body with

        while True:
            buf = environ["wsgi.input"].read(block_size)
            if buf == b"": break

    so a PUT stayed blocked until the client gave up - five minutes, measured -
    and the file only arrived when the connection closed. This is not specific
    to wsgidav: any WSGI application reading its body that way would have
    stopped there.
    """

    def __init__(self, stream, length):
        self._stream = stream
        self._left = max(0, int(length or 0))

    def read(self, size=-1):
        if self._left <= 0:
            return b""
        if size is None or size < 0:
            size = self._left
        data = self._stream.read(min(size, self._left))
        self._left -= len(data)
        return data

    def readline(self, size=-1):
        if self._left <= 0:
            return b""
        if size is None or size < 0:
            size = self._left
        data = self._stream.readline(min(size, self._left))
        self._left -= len(data)
        return data

    def readlines(self, hint=-1):
        lines = []
        while True:
            line = self.readline()
            if not line:
                return lines
            lines.append(line)

    def __iter__(self):
        while True:
            line = self.readline()
            if not line:
                return
            yield line

    def drain(self, ceiling):
        """Consume what is left of the body. Say whether the connection is safe.

        Past the ceiling we give up: draining a hundred megabytes to recover one
        connection costs more than opening another.
        """
        while self._left > 0:
            if self._left > ceiling:
                return False
            block = self._stream.read(min(65536, self._left))
            if not block:
                return False
            self._left -= len(block)
        return True


def _readable_path(environ):
    """PATH_INFO as text, for the log.

    It carries the URL's bytes read back as latin-1 - the WSGI convention - so
    writing it as is would put "rA(c)sultats.docx" in the log, and an accented
    name would be impossible to match against what the client shows.
    """
    path = environ.get("PATH_INFO") or ""
    try:
        return path.encode("iso-8859-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return path


class VDOM_http_request_handler(http.server.SimpleHTTPRequestHandler):
    """VDOM http request handler"""

    server_version = SERVER_NAME  # server version string

    # HTTP/1.1, not http.server's HTTP/1.0 default.
    #
    # parse_request gates TWO things on this attribute, and it runs before any
    # do_* method: persistent connections, and "Expect: 100-continue". Under 1.0
    # the server closed after every response - one TCP connection and one thread
    # per request - and a client uploading 500 MB sent all of it before learning
    # it had no write permission.
    #
    # What 1.1 demands in return: a response with no Content-Length would leave
    # the client waiting for a body that never ends, where under 1.0 closing the
    # connection served as the end of the message. That rule lives in
    # end_headers, the one place where it can still be announced in time.
    protocol_version = "HTTP/1.1"

    # Nagle holds a small send back hoping for the next one, while the delayed
    # acknowledgement at the other end waits for the opposite: both wait, and a
    # short response can idle for tens of milliseconds for nothing. A WebDAV
    # response almost always fits in one or two sends, with headers going out
    # before the body - exactly where that pair bites.
    disable_nagle_algorithm = True

    def __init__(self, request, client_address, server, args=None):
        """constructor"""
        setattr(threading.current_thread(), THREAD_ATTRIBUTE_NAME, self)
        # debug("Creating RequestHandler object")
        self.__reject = args["reject"]
        self.__deny = args["deny"]
        self.__card = args["card"]
        self.__limit = args["limit"]
        self.__connections = args["connections"]
        """call base class constructor"""
        try:
            http.server.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
        except Exception:  # noqa
            raise

    def _write_body(self, source):
        """The response body, in bounded blocks - see utils/body."""
        from utils.body import write_in_blocks
        expected = getattr(self, "_length_expected", None)
        written = write_in_blocks(source, self.wfile, announced=expected,
                                  where=self.path, trace=debug)
        if expected is not None and written != expected:
            self.close_connection = True
        return written

    def body_fully_read(self):
        """Say that the request body has been consumed in full.

        Called by whatever reads it - see request.py. The WebDAV path goes
        through VDOM_bounded_input, which can count what is left; the others
        read a number of bytes they already know straight from rfile, and only
        the caller knows it went to the end.
        """
        self._body_read = True

    def _body_drained(self, ceiling=1 << 20):
        """Drain the rest of the request body; say whether the connection is safe.

        Three cases. With no announced body there is nothing to do. With a body
        we bounded ourselves - the WebDAV path - we can drain it and keep the
        connection. Otherwise we cannot prove it was read in full, and a
        connection kept on a doubt is worth less than one reopened: that is what
        HTTP/1.0 did for all of them.

        A chunked body (Transfer-Encoding) is not supported here and announces
        no length: the connection closes too.
        """
        encoding = (self.headers.get("transfer-encoding") or "").strip().lower()
        if encoding and encoding != "identity":
            return False
        try:
            declared = int(self.headers.get("content-length") or 0)
        except ValueError:
            return False
        if declared <= 0:
            return True
        if getattr(self, "_body_read", False):
            return True
        body = getattr(self, "_body", None)
        if body is None:
            return False
        return body.drain(ceiling)

    def end_headers(self):
        """The client must learn of the close BEFORE the body, not after.

        A response that announces no length cannot be followed by another on the
        same connection: closing is its end. We did decide that, but after the
        fact - the headers had already gone out, so the client kept the
        connection in its pool and picked it up dead on the next request. One
        request in eight failed that way, instantly, with nothing truncated:
        `ConnectionError`, on a connection the server had closed without saying
        so.

        Here it is still in time: the header goes out with the others.
        """
        if not getattr(self, "_length_announced", False):
            self.close_connection = True
            self.send_header("Connection", "close")
        return http.server.SimpleHTTPRequestHandler.end_headers(self)

    def send_header(self, keyword, value):
        """As the base class, remembering whether a length was announced."""
        if keyword.lower() == "content-length":
            self._length_announced = True
            try:
                self._length_expected = int(value)
            except (TypeError, ValueError):
                self._length_expected = None
        return http.server.SimpleHTTPRequestHandler.send_header(self, keyword, value)

    def start_response(self, status, response_headers, exc_info=None):
        if exc_info:
            try:
                raise exc_info[0](exc_info[1], exc_info[2])
                # do stuff w/exc_info here
            finally:
                exc_info = None  # Avoid circular ref.
        status_code = int(status.split(" ")[0])
        status_message = status[status.find(" ") + 1 :]
        #       print (">>>%s %s"%(status_code,status_message))
        try:
            self.send_response(status_code, status_message)
        except socket.error as e:  # TODO: find why socket already closed when error in Webdav
            print("socket.error on start_response: %s" % e)
            return
        for header in response_headers:
            if header[0] != "Date":
                self.send_header(header[0], header[1])

        cookies = self.__request.response_cookies()
        if "sid" in cookies:
            cookies["sid"]["path"] = "/"
            # send_header, not a direct write into wfile: that one passed a str
            # to a binary stream, so
            #     TypeError: a bytes-like object is required, not 'str'
            # was raised in the middle of sending the headers. The worker thread
            # died there, the client saw the connection closed with no response,
            # and WebDAV did not work at all - this was the last link.
            #
            # cookies.output() returns one "Set-Cookie: ..." line per cookie;
            # each becomes a header, which also avoids writing into the header
            # block by hand.
            for line in cookies.output().split("\r\n"):
                name, _, value = line.partition(":")
                if value:
                    self.send_header(name.strip(), value.strip())

        self.end_headers()
        # print response_headers
        # _str = '\n'.join( traceback.format_stack() )
        # print _str
        return self.wfile.write

    def get_environ(self):
        env = self.__request.environment().environment().copy()
        # env = {}
        # Bounded by Content-Length: see VDOM_bounded_input.
        env["wsgi.input"] = self._body = VDOM_bounded_input(
            self.rfile, self.headers.get("content-length") or 0)
        env["wsgi.errors"] = sys.stderr
        env["wsgi.version"] = (1, 0)
        env["wsgi.run_once"] = False
        env["wsgi.url_scheme"] = guess_scheme(env)
        env["wsgi.multithread"] = True
        env["wsgi.multiprocess"] = True
        env["SERVER_PROTOCOL"] = self.request_version
        env["REQUEST_METHOD"] = self.command
        if "?" in self.path:
            path, query = self.path.split("?", 1)
        else:
            path, query = self.path, ""

        # The URL's bytes read back as latin-1 - the WSGI convention of
        # PEP 3333 - not text. unquote() decodes as UTF-8 by default, so an
        # accented name arrived here already as text; wsgidav then applies
        # re_encode_wsgi, that is encode("iso-8859-1").decode("utf-8"), and
        # "resultats.docx" with an acute e failed on
        #     'utf-8' codec can't decode byte 0xe9 ... invalid continuation byte
        # A copy from Windows Explorer does not survive the first accent, and
        # the PROPFIND is replayed forever.
        env["PATH_INFO"] = urllib.parse.unquote(path, encoding="iso-8859-1")
        env["QUERY_STRING"] = query
        host = self.address_string()
        if host != self.client_address[0]:
            env["REMOTE_HOST"] = host
        env["REMOTE_ADDR"] = self.client_address[0]

        # The Host header verbatim, port included. VDOM's own environment
        # stores it with the port stripped, and a WSGI environ must carry the
        # header as sent: wsgidav compares a MOVE or COPY "Destination" against
        # HTTP_HOST, so "127.0.0.1" against "127.0.0.1:8082" did not match and
        # every move answered
        #     502 Source and destination must have the same host name.
        # A real client - Windows Explorer, the Finder - always sends an
        # absolute destination, so renaming a file never worked.
        host_header = self.headers.get("host")
        if host_header:
            env["HTTP_HOST"] = host_header

        # py3: mimetools.Message is gone. typeheader, type, getheader and
        # headers.headers were all its API; email.message.Message has none of
        # them, so this raised AttributeError the moment it ran - which is the
        # whole WebDAV path, since do_WebDAV() calls get_environ(). Measured
        # before the fix: OPTIONS /dav and PROPFIND /dav/ both closed the
        # connection with no response at all.
        declared = self.headers.get("content-type")
        env["CONTENT_TYPE"] = declared if declared else self.headers.get_content_type()

        length = self.headers.get("content-length")
        if length:
            env["CONTENT_LENGTH"] = length
        script_name = env.get("SCRIPT_NAME")
        if script_name:
            env["SCRIPT_NAME"] = script_name.rstrip("/")

        for name, value in self.headers.items():
            k = name.replace("-", "_").upper()
            v = value.strip()
            if k in env:
                continue  # skip content length, type,etc.
            if "HTTP_" + k in env:
                if "HTTP_" + k not in self.__request.environment().environment():
                    # comma-separate multiple headers
                    env["HTTP_" + k] += "," + v
            else:
                env["HTTP_" + k] = v
        return env

    def handle_one_request(self):
        """Handle a single HTTP request.
        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.
        """
        try:
            self.raw_requestline = self.rfile.readline()
            if len(self.raw_requestline) > 65536:
                self.requestline = ""
                self.request_version = ""
                self.command = ""
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return

            mname = "do_" + self.command
            host = self.headers.get("host")
            vh = self.server.virtual_hosting()
            app_id = (vh.get_site(host.lower()) if host else None) or vh.get_def_site()
            if not app_id:
                app_id = managers.memory.applications.default.id if managers.memory.applications.default else None
            self.wsgidav_app = None
            if app_id:
                try:
                    # if app_id not in managers.memory.applications:
                    #    managers.memory.load_application(app_id)
                    appl = managers.memory.applications[app_id]
                    self.wsgidav_app = getattr(appl, "wsgidav_app", None)
                except KeyError as e:
                    debug(e)
                else:
                    # dav_map = getattr(appl,"dav_map",None)
                    # if not dav_map:
                    # appl.dav_map = set()
                    # dav_map = appl.dav_map
                    # for obj in appl.get_objects_list():
                    # if obj.type.id == '1a43b186-5c83-92fa-7a7f-5b6c252df941':
                    # dav_map.add("/" + obj.name)
                    # for realm in dav_map:
                    # if self.path.startswith(realm):
                    # mname = 'do_WebDAV'
                    realm = self.path.strip("/").split("/").pop(0)
                    if managers.webdav_manager.check_webdav_share_path(appl.id, realm):
                        mname = "do_WebDAV"

            if self.command not in ("GET", "POST"):
                mname = "do_WebDAV"

            if mname == "do_WebDAV" and self.wsgidav_app is None:
                managers.webdav_manager.load_webdav(app_id)
                self.wsgidav_app = appl.wsgidav_app

            if not hasattr(self, mname):
                self.send_error(501, "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            self._length_announced = False
            self._body = None
            self._body_read = False
            self._length_expected = None
            method()
            # An unread request body must not be left in the connection.
            #
            # A request refused before its body was read - a 401 on a PUT, a
            # 409, a 403 - leaves that body in the socket. Under HTTP/1.0 the
            # connection closed right after and those bytes went with it; kept
            # alive, they stick to the front of the next request, whose first
            # line then reads, for example,
            #
            #     xGET /folder/file.txt HTTP/1.1
            #
            # where the "x" is the previous PUT's body. The request after that
            # answers something arbitrary - a refusal, an "already exists" -
            # about a file that did nothing. Measured: that is exactly what the
            # log showed, "WebDAV xGET".
            if not self._body_drained():
                self.close_connection = True
            # actually send the response if not already done.
            self.wfile.flush()
        except socket.timeout as e:
            # a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return

    def handle(self):
        """Handle multiple requests if necessary."""
        # self.close_connection = 1
        # self.handle_one_request()
        # while self.server.active and not self.close_connection:
        #     ready = select.select([self.request], [], [], 0.5)
        #     if not ready[0]:
        #         continue
        #     self.handle_one_request()
        self.close_connection = 0
        deadline = time.time() + settings.CONNECTION_INITIAL_TIMEOUT
        while not self.close_connection:
            ready = select.select([self.request], [], [], settings.QUANTUM)
            if self.server.unavailable or not self.server.active:
                break
            elif ready[0]:
                self.handle_one_request()
                deadline = time.time() + settings.CONNECTION_SUBSEQUENT_TIMEOUT
            elif time.time() > deadline:
                break

    def do_WebDAV(self):
        if self.__reject:
            self.send_error(503, self.responses[503][0])
            return None
        self.create_request(self.command.lower())
        environ = self.get_environ()
        application = self.wsgidav_app
        if not application:
            self.send_error(404, self.responses[404][0])
            return
        elif environ["REQUEST_METHOD"] == "OPTIONS" and environ["PATH_INFO"] in ("/", "*"):
            import wsgidav.util as util

            self.start_response(
                "200 OK",
                [
                    ("Content-Type", "text/html"),
                    ("Content-Length", "0"),
                    ("DAV", "1,2"),
                    ("Server", "DAV/2"),
                    ("Date", util.get_rfc1123_time()),
                ],
            )
            return

        if environ["REQUEST_METHOD"] == "PROPFIND" and environ["PATH_INFO"] in ("/", "*"):
            providers = list(self.wsgidav_app.provider_map.keys())
            if providers:
                # Need some testing if this approach will work
                # Same convention as above: this path goes back to wsgidav,
                # which will read it as latin-1.
                environ["PATH_INFO"] = providers[0].encode("utf-8").decode("iso-8859-1")
            else:
                self.send_error(404, self.responses[404][0])
                return
        # One line per request, whatever happens. A WebDAV request that fails
        # cleanly - 405 "already exists", 412, 423 locked - used to write nothing
        # at all: only exceptions left a trace. A file client, meanwhile, shows
        # only "cannot copy", without saying which or why, and there was no way
        # to match the two.
        started = time.time()
        state = {"code": "?", "bytes": 0}

        def start_response(status, headers, exc_info=None):
            state["code"] = status.split(" ")[0]
            return self.start_response(status, headers, exc_info)

        # The WSGI loop, guarded. Without this, an exception raised by wsgidav
        # or by the provider killed the worker thread: the client got "Remote
        # end closed connection without response" and the log carried nothing.
        # That is how this port was debugged blind.
        try:
            for v in application(environ, start_response):
                state["bytes"] += len(v)
                self.wfile.write(v)
        except Exception as error:
            from utils.tracing import format_exception_trace
            state["code"] = "EXC"
            debug("WebDAV %s %s: %s" % (environ.get("REQUEST_METHOD"),
                                        _readable_path(environ), error))
            debug(format_exception_trace())
            raise
        finally:
            # Received as well as sent: without the first, a 400 MB upload reads
            # as a few kilobytes - a PUT's response weighs nothing - and the real
            # throughput stays invisible.
            debug("WebDAV %s %s -> %s received %s b sent %d b %.0f ms" % (
                environ.get("REQUEST_METHOD"), _readable_path(environ),
                state["code"], self.headers.get("content-length") or 0,
                state["bytes"], 1000 * (time.time() - started)))

    def do_GET(self):
        """serve a GET request"""
        # create request object
        # debug("DO GET %s"%self)
        self.create_request("get")
        f = self.on_request("get")
        if f:
            self._write_body(f)
            f.close()
        try:
            # nokeepalive is set by set_nocache, so by EVERY send_file: each
            # resource served closed its connection that way - and, since the
            # decision comes after the headers, without telling the client, who
            # kept it in the pool and picked it up dead.
            #
            # The real question is not the cache but the framing: a response
            # that announces its size says where it ends, and the connection can
            # serve again. With no announced size, closing IS the end of the
            # message - and end_headers has already announced it.
            if self.__request.nokeepalive and not getattr(
                    self, "_length_announced", False):
                self.close_connection = 1
        except Exception:  # noqa
            # debug("EXCEPTION WHEN DO GET %s"%self)
            # print dir(self)
            raise

    def do_HEAD(self):
        """serve a HEAD request"""
        # create request object
        self.create_request("get")
        f = self.on_request("get")
        if f:
            f.close()

    def do_POST(self):
        """serve a POST request"""
        # create request object
        # debug("DO POST %s"%self)
        self.create_request("post")
        # if POST to SOAP-POST-URL call do_SOAP
        if self.__request.environment().environment()["REQUEST_URI"] == VDOM_CONFIG["SOAP-POST-URL"]:
            if self.__card:
                self.do_SOAP()
            return
        f = self.on_request("post")
        if f:
            original_switchinterval = sys.getswitchinterval()  # Save the original switch interval
            sys.setswitchinterval(1e-6)  # Use a very small interval instead of 0
            shutil.copyfileobj(f, self.wfile)
            sys.setswitchinterval(original_switchinterval)
            # self.copyfile(f, self.wfile)
            f.close()

    def create_request(self, method):
        """initialize request, <method> is either 'post' or 'get'"""

        # debug("CREATE REQUEST %s"%self)
        # import gc
        # debug("\nGarbage: "+str(len(gc.garbage))+"\n")
        # debug("Creating request object")
        args = {}
        args["headers"] = self.headers
        args["handler"] = self
        args["method"] = method
        self.__request = VDOM_request(args)
        self.__request.number_of_connections = self.__connections
        # debug("Creating request object complete")
        # put request to the manager
        managers.request_manager.current = self.__request

        if "127.0.0.1" != self.client_address[0]:
            debug("Session is " + self.__request.sid)

    def on_request(self, method):
        """request handling code the method <method>"""
        # debug("ON REQUEST %s"%self)
        # check if we should send 503 or 403 errors
        if self.__reject:
            self.send_error(503, self.responses[503][0])
            return None
        if self.__deny:
            self.send_error(403, self.responses[403][0])
            return None
        if not self.__card:
            data = _("Please insert your card")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            return BytesIO(data)
        if not self.__limit:
            data = _("License exceeded")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            return BytesIO(data)
        # check if requested for wsdl file - then return it
        if self.__request.environment().environment()["REQUEST_URI"] == VDOM_CONFIG["WSDL-FILE-URL"]:
            wsdl = self.server.get_wsdl()
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-Length", str(len(wsdl)))
            self.end_headers()
            return BytesIO(wsdl)
        if self.__request.environment().environment()["REQUEST_URI"] == "/crossdomain.xml":
            data = """<?xml version="1.0"?>
<cross-domain-policy>
     <allow-access-from domain="*"/>
</cross-domain-policy>"""
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            return BytesIO(data)
        # management
        if self.__request.environment().environment()["REQUEST_URI"] == VDOM_CONFIG["MANAGEMENT-URL"]:
            return self.redirect("/index.py")
        # process requested URI, call module manager
        try:
            (code, ret) = managers.module_manager.process_request(self.__request)
            self.__request.collect_files()
        except Exception as e:
            # raise  # CHECK: TODO: ONLY FOR DEBUG
            requestline = "<br>"
            if hasattr(self, "requestline"):
                requestline = "<br>" + self.requestline + "<br>" + "-" * 80
            if not hasattr(self, "request_version"):
                self.request_version = "HTTP/1.1"
            fe = "".join(["<br><br>", "-" * 80, requestline, "<br>Exception happened during processing of request:", traceback.format_exc(), "-" * 40])
            self.__request.collect_files()
            self.send_error(500, excinfo=fe)
            debug(e)
            return None

        # check redirect
        if self.__request.redirect_to:
            return self.redirect(self.__request.redirect_to)
        elif ret:
            self.send_response(200)
            ret_len = None
            # if isinstance(ret, file):
            if isinstance(ret, io.IOBase):
                ret.seek(0, 2)
                ret_len = str(ret.tell())
                ret.seek(0)
            else:
                ret_len = str(len(ret))
            self.__request.add_header("Content-Length", ret_len)
            if self.__request.nokeepalive:
                self.__request.add_header("Connection", "Close")
            else:
                self.__request.add_header("Connection", "Keep-Alive")
            # cookies
            # if len(self.__request.cookies())>0:
            #   for key in self.__request.cookies():
            #       self.__request.add_header("Set-cookie",self.__request.cookies()[key].output())
            # self.__request.add_header("Set-cookie",self.__request.cookies().output())
            # if len(self.__request.cookies().cookies()) > 0:
            # self.__request.add_header("Set-cookie", self.__request.cookies().get_string())
            self.send_headers()
            self.end_headers()
            # if isinstance(ret, file):
            if isinstance(ret, io.IOBase):
                if sys.platform.startswith("freebsd"):
                    # vdomlib.sendres(self.wfile.fileno(), ret.fileno(), int(ret_len))
                    ret.close()
                    return None
                else:
                    return ret
            elif isinstance(ret, str):
                return BytesIO(ret.encode("utf8"))
            else:
                return BytesIO(ret)
        elif code:
            self.send_error(code, self.responses[code][0])
            return None
        elif "" == ret and not self.__request.binary():
            if self.__request.retcode == 200:
                self.send_response(204)
                self.send_headers()
                self.end_headers()
            return None
        elif self.__request.binary():
            return None
        else:
            self.send_error(404, self.responses[404][0])
            return None

    def send_headers(self):
        """send all headers"""
        headers = self.__request.headers_out().headers()
        cookies = self.__request.response_cookies().output()
        # debug("Outgoing headers---")
        # for h in headers:
        #   debug(h + ": " + headers[h])
        # debug('-'*40)
        for hh in headers:
            # debug(hh + " : " + headers[hh])
            self.send_header(hh, headers[hh])
        if len(cookies) > 0:
            cookies_header, cookies_value = cookies.split(": ", 1)
            self.send_header(cookies_header, cookies_value.strip())

    def finish(self):
        """finish processing request"""
        # debug("FINISH REQUEST %s"%self)
        http.server.SimpleHTTPRequestHandler.finish(self)
        """tell the server that processing is finished"""
        self.server.notify_finish(self.client_address)

        # remove request
        del managers.request_manager.current
        try:
            del self.__request.vdom
            del self.__request
        except Exception:  # noqa
            pass

    def redirect(self, to):
        self.send_response(302)
        # if len(self.__request.cookies)>0:
        #   for key in self.__request.cookies():
        #           self.__request.add_header("Set-cookie",self.__request.cookies()[key].output())
        # self.__request.add_header(self.__request.cookies.output())
        # if len(self.__request.cookies().cookies()) > 0:
        #   self.__request.add_header("Set-cookie", self.__request.cookies().get_string())
        self.__request.add_header("Location", to)
        self.send_headers()
        self.end_headers()
        return BytesIO()

    def log_message(self, format, *args):
        """log an arbitrary message to stderr"""
        if "127.0.0.1" != self.client_address[0]:
            debug("%s %s {%d}" % (self.address_string(), format % args, self.server.get_cur_con()))
        # sys.stderr.write("%s - Thread %d - [%s] %s {%d}\n" % (self.address_string(), threading.ident, self.log_date_time_string(), format%args, self.server.get_cur_con()))

    def print_list(self, list, f):
        """print contents of the dictionary in the form of list"""
        for k in list(list.keys()):
            f.write('%s: "%s"<br>\n' % (k.upper(), list[k]))
        f.write("<hr>")

    def address_string(self):
        """Return the client address formatted for logging"""
        host, port = self.client_address[:2]
        # TODO: Sometimes we do not have self.headers
        headers = getattr(self, "headers", {})
        remote_ip = headers.get("X-Real-IP") or headers.get("X-Forwarded-For") or host
        return remote_ip

    def sample_page(self, method):
        """generate sample output page"""
        debug("Returning sample page")
        f = BytesIO()
        f.write("<b>Application id:</b> %s<br>" % str(self.__request.app_id()))
        f.write("<b>Registered types:</b><br>")
        mngr = managers.memory
        typelst = mngr.get_types()
        for typeid in typelst:
            tp = None
            try:
                tp = mngr.get_type(typeid)
            except Exception:  # noqa
                pass
            if tp:
                typename = tp.name
                if "" == typename:
                    typename = _("Not specified")
                f.write("%s %s<br>" % (typename, typeid))
        f.write("<b>Registered applications:</b><br>")
        applst = mngr.get_applications()
        for appid in applst:
            app = None
            try:
                app = mngr.get_application(appid)
            except Exception:  # noqa
                pass
            if app:
                appname = app.name
                if "" == appname:
                    appname = _("Not specified")
                f.write("%s %s&nbsp;" % (appname, appid))
                f.write("[")
                for o in app.get_objects_list():
                    f.write("%s&nbsp;" % o.id)
                f.write("]<br>")
        f.write("<hr>\n")
        f.write("<h2>Sample output for the %s method:</h2><hr>\n" % method.upper())
        f.write("<h2>Request headers:</h2>\n")
        self.print_list(self.__request.headers().headers(), f)
        f.write("<h2>Cookies:</h2>\n")
        self.print_list(self.__request.cookies().cookies(), f)
        f.write("<h2>Environment:</h2>\n")
        self.print_list(self.__request.environment().environment(), f)
        f.write("<h2>Request arguments:</h2>\n")
        f.write(str(self.__request.arguments().arguments()))
        f.write("<hr>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def do_SOAP(self):
        global _contexts
        status = 500

        # VDOM_debug = 0
        dumpSOAPIn = 0
        dumpSOAPOut = 0
        dumpHeadersIn = 0
        dumpHeadersOut = 0
        start_time = time.time()
        # cf = VDOM_config()
        # No more alot of debug while soap
        # if "1" == cf.get_opt("DEBUG"):
        #   VDOM_debug = 1
        #   dumpSOAPIn = 1
        #   dumpSOAPOut = 1
        #   dumpHeadersIn = 1
        #   dumpHeadersOut = 1

        if True:  # try:
            if dumpHeadersIn:
                s = "Incoming HTTP headers"
                SOAPpy.debugHeader(s)
                debug(self.raw_requestline.strip())
                debug("\n".join([x.strip() for x in self.headers.headers]))
                SOAPpy.debugFooter(s)
            data = self.__request.postdata
            if dumpSOAPIn:
                s = "Incoming SOAP"
                SOAPpy.debugHeader(s)
                debug(data)
                SOAPpy.debugFooter(s)

            (r, header, body, attrs) = SOAPpy.parseSOAPRPC(data, header=1, body=1, attrs=1)

            method = r._name
            args = r._aslist()
            kw = r._asdict()

            # TODO:
            # check if there are list items in args or kw
            # and leave only the first element

            if SOAPpy.Config.simplify_objects:
                args = SOAPpy.simplify(args)
                kw = SOAPpy.simplify(kw)

            # Handle mixed named and unnamed arguments by assuming
            # that all arguments with names of the form "v[0-9]+"
            # are unnamed and should be passed in numeric order,
            # other arguments are named and should be passed using
            # this name.

            # This is a non-standard exension to the SOAP protocol,
            # but is supported by Apache AXIS.

            # It is enabled by default.  To disable, set
            # Config.specialArgs to False.
            SOAPpy.Config.specialArgs = False

            if True:  # SOAPpy.Config.specialArgs:
                ordered_args = {}
                named_args = {}
                ordered_args = {}

                for k, v in list(kw.items()):
                    if k[0] == "v":
                        try:
                            i = int(k[1:])
                            ordered_args[i] = v
                        except ValueError:
                            named_args[k.decode()] = v

                    else:
                        named_args[k.decode()] = v

            # We have to decide namespace precedence
            # I'm happy with the following scenario
            # if r._ns is specified use it, if not check for
            # a path, if it's specified convert it and use it as the
            # namespace. If both are specified, use r._ns.

            ns = r._ns

            if len(self.path) > 1 and not ns:
                ns = self.path.replace("/", ":")
                if ns[0] == ":":
                    ns = ns[1:]

            # authorization method
            a = None

            keylist = list(ordered_args.keys())
            keylist.sort()

            # create list in proper order w/o names
            tmp = [ordered_args[x] for x in keylist]
            ordered_args = tmp

            #           print '<-> Argument Matching Yielded:'
            #           print '<-> Ordered Arguments:' + str(ordered_args)
            #           print '<-> Named Arguments  :' + str(named_args)

            arg_names = soap_methods[method]
            if "sid" in arg_names:
                _i = arg_names.index("sid")
                if _i < len(ordered_args):
                    managers.request_manager.current.set_session_id(ordered_args[_i])
                elif "sid" in named_args:
                    managers.request_manager.current.set_session_id(named_args["sid"])
            if "appid" in arg_names:
                _i = arg_names.index("appid")
                if _i < len(ordered_args):
                    managers.request_manager.current.set_application_id(ordered_args[_i])
                elif "appid" in named_args:
                    managers.request_manager.current.set_application_id(named_args["appid"])

            resp = ""

            # For fault messages
            if ns:
                nsmethod = "%s:%s" % (ns, method)
            else:
                nsmethod = method

            if True:  # try:
                # First look for registered functions
                if ns in self.server.funcmap and method in self.server.funcmap[ns]:
                    f = self.server.funcmap[ns][method]

                    # look for the authorization method
                    if self.server.config.authMethod is not None:
                        authmethod = self.server.config.authMethod
                        if ns in self.server.funcmap and authmethod in self.server.funcmap[ns]:
                            a = self.server.funcmap[ns][authmethod]
                else:
                    # Now look at registered objects
                    # Check for nested attributes. This works even if
                    # there are none, because the split will return
                    # [method]
                    f = self.server.objmap[ns]

                    # Look for the authorization method
                    if self.server.config.authMethod is not None:
                        authmethod = self.server.config.authMethod
                        if hasattr(f, authmethod):
                            a = getattr(f, authmethod)

                    # then continue looking for the method
                    for i in method.split("."):
                        f = getattr(f, i)
            try:
                pass  # DEBUG
            except Exception:  # noqa
                info = sys.exc_info()
                try:
                    resp = SOAPpy.buildSOAP(
                        SOAPpy.faultType("%s:Client" % SOAPpy.NS.ENV_T, "Method Not Found", "%s : %s %s %s" % (nsmethod, info[0], info[1], info[2])),
                        encoding=self.server.encoding,
                        config=self.server.config,
                    )
                finally:
                    del info
                status = self.__request.fault_type_http_code
            else:
                if True:  # try:
                    if header:
                        x = HeaderHandler(header, attrs)  # noqa

                    fr = 1

                    # call context book keeping
                    # We're stuffing the method into the soapaction if there
                    # isn't one, someday, we'll set that on the client
                    # and it won't be necessary here
                    # for now we're doing both

                    if "SOAPAction".lower() not in list(self.headers.keys()) or self.headers["SOAPAction"] == '""':
                        self.headers["SOAPAction"] = method

                    thread_id = threading.current_thread().ident
                    _contexts[thread_id] = SOAPpy.SOAPContext(header, body, attrs, data, self.connection, self.headers, self.headers["SOAPAction"])

                    # Do an authorization check
                    if a is not None:
                        if not a(None, **{"_SOAPContext": _contexts[thread_id]}):
                            raise SOAPpy.faultType("%s:Server" % SOAPpy.NS.ENV_T, "Authorization failed.", "%s" % nsmethod)

                    # If it's wrapped, some special action may be needed
                    if isinstance(f, SOAPpy.MethodSig):
                        c = None

                        if f.context:  # retrieve context object
                            c = _contexts[thread_id]

                        # log
                        if c:
                            info = c.connection.getpeername()
                            debug("Web service request from %s:%s - %s" % (info[0], info[1], c.soapaction))
                        #######

                        if SOAPpy.Config.specialArgs:
                            if c:
                                named_args["_SOAPContext"] = c
                            fr = f(*ordered_args, **named_args)
                        elif f.keywords:
                            # This is lame, but have to de-unicode
                            # keywords

                            strkw = {}

                            for k, v in list(kw.items()):
                                strkw[str(k)] = v
                            if c:
                                strkw["_SOAPContext"] = c
                            fr = f(None, **strkw)
                        elif c:
                            fr = f(*args, **{"_SOAPContext": c})
                        else:
                            fr = f(*args, **{})

                    else:
                        if SOAPpy.Config.specialArgs:
                            fr = f(*ordered_args, **named_args)
                        else:
                            fr = f(*args, **{})

                    if type(fr) == type(self) and isinstance(fr, SOAPpy.voidType):  # noqa
                        resp = SOAPpy.buildSOAP(
                            kw={'%sResponse xmlns="http://services.vdom.net/VDOMServices"' % method: fr},
                            encoding=self.server.encoding,
                            config=self.server.config,
                        )
                    else:
                        resp = SOAPpy.buildSOAP(
                            kw={"Result": fr},
                            encoding=self.server.encoding,
                            config=self.server.config,
                            method=method + "Response",
                            namespace=("", "http://services.vdom.net/VDOMServices"),
                        )

                    # Clean up _contexts
                    if thread_id in _contexts:
                        del _contexts[thread_id]
                try:
                    pass  # fake for debug
                except Exception as e:
                    info = sys.exc_info()

                    try:
                        if self.server.config.dumpFaultInfo and not isinstance(e, SOAPpy.faultType):
                            s = "Method %s exception" % nsmethod
                            SOAPpy.debugHeader(s)
                            traceback.print_exception(info[0], info[1], info[2])
                            SOAPpy.debugFooter(s)

                        if isinstance(e, SOAPpy.faultType):
                            f = e
                        else:
                            f = SOAPpy.faultType("%s:Server" % SOAPpy.NS.ENV_T, "Method Failed", "%s" % nsmethod)

                        if self.server.config.returnFaultInfo:
                            f._setDetail("".join(traceback.format_exception(info[0], info[1], info[2])))
                        elif not hasattr(f, "detail"):
                            f._setDetail("%s %s" % (info[0], info[1]))
                    finally:
                        del info

                    # method failed - return soap fault (no method tag needed)
                    resp = SOAPpy.buildSOAP(f, encoding=self.server.encoding, config=self.server.config, namespace="http://services.vdom.net/VDOMServices")
                    status = self.__request.fault_type_http_code
                else:
                    status = 200
        try:
            pass  # DEBUG
        except SOAPpy.faultType as e:
            info = sys.exc_info()
            try:
                if self.server.config.dumpFaultInfo:
                    s = "Received fault exception"
                    SOAPpy.debugHeader(s)
                    traceback.print_exception(info[0], info[1], info[2])
                    SOAPpy.debugFooter(s)

                if self.server.config.returnFaultInfo:
                    e._setDetail("".join(traceback.format_exception(info[0], info[1], info[2])))
                elif not hasattr(e, "detail"):
                    e._setDetail("%s %s" % (info[0], info[1]))
            finally:
                del info

            # method failed - return soap fault (no method tag needed)
            resp = SOAPpy.buildSOAP(e, encoding=self.server.encoding, config=self.server.config, namespace="http://services.vdom.net/VDOMServices")
            status = self.__request.fault_type_http_code
        except Exception as e:
            # internal error, report as HTTP server error

            if self.server.config.dumpFaultInfo:
                s = "Internal exception %s" % e
                SOAPpy.debugHeader(s)
                info = sys.exc_info()
                try:
                    traceback.print_exception(info[0], info[1], info[2])
                finally:
                    del info

                SOAPpy.debugFooter(s)

            self.send_response(self.__request.fault_type_http_code)
            self.end_headers()

            if dumpHeadersOut and self.request_version != "HTTP/0.9":
                s = "Outgoing HTTP headers"
                SOAPpy.debugHeader(s)
                if status in self.responses:
                    s = " " + self.responses[status][0]
                else:
                    s = ""
                debug("%s %d%s" % (self.protocol_version, self.__request.fault_type_http_code, s))
                debug("Server: %s" % self.version_string())
                debug("Date: %s" % self.__last_date_time_string)
                SOAPpy.debugFooter(s)
        else:
            # got a valid SOAP response
            self.send_response(status)
            t = "text/xml"
            if self.server.encoding is not None:
                t += '; charset="%s"' % self.server.encoding
            self.send_header("Content-type", t)
            self.send_header("Content-length", str(len(resp)))
            self.end_headers()

            if dumpHeadersOut and self.request_version != "HTTP/0.9":
                s = "Outgoing HTTP headers"
                SOAPpy.debugHeader(s)
                if status in self.responses:
                    s = " " + self.responses[status][0]
                else:
                    s = ""
                debug("%s %d%s" % (self.protocol_version, status, s))
                debug("Server: %s" % self.version_string())
                debug("Date: %s" % self.__last_date_time_string)
                debug("Content-type: %s" % t)
                debug("Content-length: %d" % len(resp))
                SOAPpy.debugFooter(s)

            if dumpSOAPOut:
                try:
                    s = "Outgoing SOAP"
                    SOAPpy.debugHeader(s)
                    debug(resp)

                    SOAPpy.debugFooter(s)
                except Exception:  # noqa
                    pass

            # resp = xml.sax.saxutils.unescape(resp)
            print("Soap method call: %s, respsize: %s,resptime:%s" % (nsmethod.split(":")[-1], len(resp), time.time() - start_time))
            self.wfile.write(resp)
            self.wfile.flush()

            # We should be able to shut down both a regular and an SSL
            # connection, but under Python 2.1, calling shutdown on an
            # SSL connections drops the output, so this work-around.
            # This should be investigated more someday.

            if self.server.config.SSLserver:
                from OpenSSL import SSL  # type: ignore

                if isinstance(self.connection, SSL.Connection):
                    self.connection.set_shutdown(SSL.SENT_SHUTDOWN | SSL.RECEIVED_SHUTDOWN)
            else:
                # self.connection.shutdown(1)
                pass

    def date_time_string(self):
        self.__last_date_time_string = http.server.BaseHTTPRequestHandler.date_time_string(self)
        return self.__last_date_time_string

    def send_error(self, code, message=None, excinfo=None):
        """send error"""
        try:
            short, explanation = self.responses[code]
        except KeyError:
            short, explanation = "???", "???"
        if message is None:
            message = short

        self.log_error("code %d, message %s", code, message)

        self.send_response(code, message)
        self.send_header("Connection", "close")

        if code < 200 or code in (204, 205, 304):
            content = None
        else:
            content = compose_page(
                explanation, title="Error", heading="Error %d: %s" % (code, message), extra=compose_trace if settings.SHOW_PAGE_DEBUG else None
            )
            self.send_header("Content-Type", self.error_content_type)

        self.end_headers()
        if self.command != "HEAD" and content:
            self.wfile.write(content.encode())

        ###

        # NOTE: obsolete implementation

        # try:
        #     accept_language = self.headers.get("Accept-Language", "")
        #     separator = accept_language.find("-")
        #     if separator < 0:
        #         language = VDOM_CONFIG["DEFAULT-LANGUAGE"]
        #     language = accept_language[0:]
        # except:
        #     language = VDOM_CONFIG["DEFAULT-LANGUAGE"]

        # # filename=VDOM_CONFIG["HTTP-ERROR-PAGES-DIRECTORY"]+"/"+str(code)+".htm"

        # # if os.path.exists(filename):
        # #   file=open(filename, "rb")
        # #   content=file.read()
        # #   file.close()

        # #   self.send_response(code, message)
        # #   self.send_header("Content-Type", "text/html")
        # #   self.send_header('Connection', 'close')
        # #   self.end_headers()
        # #   if self.command!='HEAD' and code>=200 and code not in (204, 304):
        # #       self.wfile.write(content)
        # #   else:
        # #       pass
        # # else:
        # self.requestline = ""
        # SimpleHTTPServer.SimpleHTTPRequestHandler.send_error(self, code, message)
        # if excinfo:
        #     page_debug = VDOM_CONFIG_1["ENABLE-PAGE-DEBUG"]
        #     if "1" == page_debug or True:
        #         e = "<br>".join(excinfo.splitlines(True))
        #         self.wfile.write(e)
        #         self.wfile.flush()
        #         self.finish()

    def log_error(self, *args):
        pass

    def version_string(self):
        """Return the server software version string."""
        return "VDOM v3 server " + SERVER_VERSION + " " + self.sys_version
