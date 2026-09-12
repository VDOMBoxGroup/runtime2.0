"""request module represents the request got by the VDOM server"""
import sys
import tempfile
import urllib.parse
from io import BytesIO, StringIO

from cgi import FieldStorage
import json

from http.cookies import BaseCookie

from .environment import VDOM_environment
from .headers import VDOM_headers
from .arguments import VDOM_request_arguments


# from memory.interface import MemoryInterface
from utils.file_argument import File_argument
from utils.properties import weak
import managers
import settings


def content_disposition_name(filename):
    """The filename parameters of a Content-Disposition header.

    Returns both forms, because neither alone is enough:

        filename="devis.pdf"; filename*=UTF-8''devis%20%C3%A9t%C3%A9.pdf

    A header goes onto the socket through BaseHTTPRequestHandler.send_header,
    which encodes it latin-1. So a name with an accent cannot travel in the
    plain `filename` - it raises UnicodeEncodeError after the response has
    started, which the client sees as a connection dropped mid-download. The
    plain form is therefore reduced to ASCII, and the real name travels in
    `filename*` (RFC 5987), which every browser prefers when both are present.

    Bytes are accepted and decoded. Under Python 2 a caller wrote
    `node.name.encode('utf8')` and the raw bytes went into the header; under
    Python 3 the same line makes "%s" produce b'devis.pdf', quotes included, so
    files arrived named after their own repr. Four call sites did it, three of
    them without ever raising. Decoding here means no caller has to know how an
    HTTP header is encoded - which is the reason they got it wrong.
    """
    if isinstance(filename, bytes):
        filename = filename.decode("utf-8", "replace")
    else:
        filename = str(filename)
    # A quote or a backslash would end the quoted string early, and a path
    # separator would let a caller propose a name that is not one.
    filename = filename.replace("\\", "_").replace('"', "_")
    filename = filename.replace("/", "_")
    filename = "".join(" " if character < " " else character for character in filename)
    plain = filename.encode("ascii", "replace").decode("ascii")
    quoted = urllib.parse.quote(filename, safe="")
    return "filename=\"%s\"; filename*=UTF-8''%s" % (plain, quoted)


class MFSt(FieldStorage):
    def make_file(self, binary=None):
        # cgi keeps a part in memory until it passes 1000 bytes, then calls
        # this and copies what it has into the result. Which mode that file
        # needs is not ours to choose: cgi writes str for an ordinary field and
        # bytes for an uploaded file, and it says which through _binary_file.
        #
        # Returning a binary file for both meant an ordinary field larger than
        # 1000 bytes raised
        #     TypeError: a bytes-like object is required, not 'str'
        # while cgi was parsing, before any application code ran. The exception
        # left the request without a response and the connection was closed, so
        # the browser reported only "TypeError: Failed to fetch" and nothing was
        # written to server.log. Measured: a multipart body went through at
        # 1134 bytes and died at 1139. Uploads were unaffected - a file part is
        # binary - which is why this looked like a size limit on posting rather
        # than a mode error.
        #
        # No delete_on_close: it only exists from python 3.12 and this runtime is
        # pinned to 3.11 by js2py, so passing it raised TypeError here and lost
        # every upload over cgi's 1000-byte in-memory threshold. It is redundant
        # anyway - delete=False already keeps the file after close.
        if self._binary_file:
            return tempfile.NamedTemporaryFile(
                "w+b", prefix="vdomupload",
                dir=VDOM_CONFIG["TEMP-DIRECTORY"], delete=False)
        return tempfile.NamedTemporaryFile(
            "w+", prefix="vdomupload", dir=VDOM_CONFIG["TEMP-DIRECTORY"],
            delete=False, encoding=self.encoding, newline="\n")


@weak("_handler")
class VDOM_request(object):
    """VDOM server request object"""

    # ------------------------------------------------------------
    def __init__(self, arguments):
        """ Constructor, create headers, cookies, request and environment """

        headers = arguments["headers"]
        handler = arguments["handler"]

        # debug("Incoming headers---")
        # for h in headers:
        # debug(h + ": " + headers[h])
        # debug('-'*40)

        self.__headers = VDOM_headers(headers)
        self.__headers_out = VDOM_headers({})

        self.__cookies = BaseCookie(headers.get("cookie"))
        self.__response_cookies = BaseCookie()
        self.__environment = VDOM_environment(headers, handler)
        self.files = {}
        args = {}
        env = self.__environment.environment()
        # parse request data depenging on the request method
        try:
            if arguments["method"] == "post":
                if env.get("HTTP_CONTENT-TYPE", "").startswith(r'application/json'):
                    try:
                        request_body_size = int(
                            env.get('HTTP_CONTENT-LENGTH', 0))
                    except ValueError:
                        request_body_size = 0

                    request_body = handler.rfile.read(request_body_size)
                    # The body has been read in full: the connection stays
                    # reusable. Without this witness, handle_one_request cannot
                    # prove it and closes as a precaution, which brings back a
                    # throwaway connection per call - exactly what HTTP/1.1 had
                    # just removed.
                    handler.body_fully_read()
                    params = json.loads(request_body)
                    # Shape a JSON body like the form branch below: every value
                    # a list. Everything downstream assumes list-shaped args -
                    # `args["sid"][0]` indexes one a few lines down, and a macro
                    # reads Event.Data, which surfaces only a list-shaped value.
                    # Left as scalars, a JSON field read back empty: a Custom GPT
                    # posting application/json reached its macro with an empty
                    # body, indistinguishable from no body at all.
                    if isinstance(params, dict):
                        args = {
                            key: value if isinstance(value, list) else [value]
                            for key, value in params.items()}
                    else:
                        args["rawdata"] = request_body

                # TODO: check situation with SOAP and SOAP-POST-URL
                elif env["REQUEST_URI"] != VDOM_CONFIG["SOAP-POST-URL"]:
                    storage = MFSt(handler.rfile, headers, b"", env, True)
                    # The body has been read in full: the connection stays
                    # reusable. Without this witness, handle_one_request cannot
                    # prove it and closes as a precaution, which brings back a
                    # throwaway connection per call - exactly what HTTP/1.1 had
                    # just removed.
                    handler.body_fully_read()
                    if storage.list is None and storage.value:
                        args["rawdata"] = storage.value
                    else:
                        for key in storage.keys():
                            # Access to file name after uploading
                            filename = getattr(storage[key], "filename", "")
                            if filename and storage[key].file:
                                args[key] = File_argument(
                                    storage[key].file, filename)
                                self.files[key] = args[key]
                            else:
                                args[key] = storage.getlist(key)
                            if filename:
                                args[key + "_filename"] = [filename]
                else:
                    self.postdata = handler.rfile.read(
                        int(self.__headers.header("Content-length")))
                    # The body has been read in full: the connection stays
                    # reusable. Without this witness, handle_one_request cannot
                    # prove it and closes as a precaution, which brings back a
                    # throwaway connection per call - exactly what HTTP/1.1 had
                    # just removed.
                    handler.body_fully_read()
        except Exception as e:
            # Log before re-raising. The bare raise that used to be here left
            # the debug() below unreachable, so a body that failed to parse
            # produced no line anywhere: no response, connection closed,
            # nothing in server.log, no macro fired - and the browser saying
            # only "TypeError: Failed to fetch". That silence is what made the
            # multipart mode defect above cost an afternoon.
            debug("Error while reading request body: %s: %s"
                  % (type(e).__name__, e))
            raise

        try:
            args.update(urllib.parse.parse_qs(env["QUERY_STRING"], True))

        except Exception as e:
            debug("Error while reading arguments: %s" % e)

        self.fault_type_http_code = 500
        if "user-agent" in self.__headers.headers():
            if "adobeair" in self.__headers.headers()["user-agent"].lower():
                self.fault_type_http_code = 200

        # session
        sid = ""
        if "sid" in args:
            # debug("Got session from arguments "+str(args["sid"]))
            sid = args["sid"][0]
        elif "sid" in self.__cookies:
            # debug("Got session from cookies "+cookies["sid"].value)
            sid = self.__cookies["sid"].value
        if sid == "":
            sid = managers.session_manager.create_session()
            # debug("Created session " + sid)
        else:
            x = managers.session_manager[sid]
            if x is None:
                # debug("Session " + sid + " expired")
                sid = managers.session_manager.create_session()
        # debug("Session ID "+str(sid))
        self.__cookies["sid"] = sid

        #  if sid not in args.get('sid', []):
        self.__response_cookies["sid"] = sid
        if settings.SAME_SITE_NONE:
            self.__response_cookies["sid"]["secure"] = True
            self.__response_cookies["sid"]["samesite"] = "None"
        args["sid"] = sid
        self.__session = managers.session_manager[sid]
        self.__arguments = VDOM_request_arguments(args)
        self.__server = handler.server
        self._handler = handler
        self.app_vhname = env["HTTP_HOST"].lower()
        vhosts = handler.server.virtual_hosting()
        self.__app_id = vhosts.get_site(self.app_vhname)
        if not self.__app_id:
            self.__app_id = vhosts.get_def_site()
        self.__stdout = BytesIO()
        self.action_result = StringIO()

        self.wholeAnswer = None
        self.application_id = self.__app_id

        self.sid = sid
        self.method = arguments["method"]
        self.vdom = None  # MemoryInterface(self) #CHECK: Not used??

        self.args = self.__arguments
        self.__app = None
        if self.__app_id:
            self.__session.context["application_id"] = self.__app_id
            try:
                self.__app = managers.memory.applications[self.__app_id]
            except Exception:
                sys.excepthook(*sys.exc_info())

        # special flags
        self.redirect_to = None
        self.wfile = handler.wfile
        self.__nocache = False
        self.nokeepalive = False
        self.retcode = 200
        self.__binary = False
        self.fh = None
        self.shared_variables = {}
        self.render_type = "html"
        self.dyn_libraries = {}
        self.container_id = None

        self.last_state = self.__session.states[0]
        self.next_state = None

    def collect_files(self):
        """Replacement for destructor needed for temp files cleanup"""
        for file_attach in self.files.values():
            if file_attach.autoremove:
                file_attach.remove()

    def add_client_action(self, obj_id, data):
        self.action_result.write(str(data))

    def binary(self, set_binary=None):
        """switch output mode to binary"""
        if set_binary is not None:
            self.__binary = set_binary
        return self.__binary

    def set_nocache(self):
        """switch output to no cache mode

        The status line is `retcode`, which is 200 until something sets it.
        It used to be the literal 200, so every answer that went out this way -
        send_file among them - was a success whatever it carried. A health
        endpoint could then report that a site was broken, with a 200, and no
        monitoring system had anything to alert on.
        """
        if not self.__nocache:
            self._handler.send_response(self.retcode or 200)
            self._handler.send_headers()
            self._handler.end_headers()  # TODO!
            self.wfile.write(self.output())
            # self.wfile.write('\n')
        self.__nocache = True
        self.nokeepalive = True

    def send_htmlcode(self, code=200):
        """reply with http code with custom output"""
        if not self.__nocache:
            self._handler.send_response(code)
            self._handler.send_headers()
            self._handler.end_headers()
            self.wfile.write(self.output())
        self.__nocache = True
        self.nokeepalive = True
        self.retcode = code

    def set_application_id(self, application_id):
        self.__app_id = application_id
        self.application_id = application_id
        # try: self.__app = managers.xml_manager.get_application(self.__app_id)
        try:
            self.__app = managers.memory.applications[self.__app_id]
        except Exception:
            sys.excepthook(*sys.exc_info())

    def write(self, string=None):
        """save output"""
        if string:
            if self.__nocache:
                self.wfile.write(string)
                # self.wfile.write('\n')
            else:
                self.__stdout.write(string)
                # The newline separates successive writes when a page is
                # rendered from many fragments. In binary it is corruption: a
                # 7858-byte PNG written by a macro came back as 7859 bytes, the
                # image intact with a stray 0x0A after IEND, and nothing
                # anywhere said why. Guarded on binary mode, so only a caller
                # that asked for binary is affected and no page rendering
                # changes.
                if not self.__binary:
                    self.__stdout.write(b'\n')

    def write_handler(self, handler):
        """writing into stream from file handler"""
        self.fh = handler

    def content_length(self):
        """get output length"""
        return self.__stdout.tell()

    def output(self):
        """get output"""
        value = self.__stdout.getvalue()
        del self.__stdout
        self.__stdout = BytesIO()
        return value

    def server(self, server=None):
        """ server object """
        return self.__server

    def session(self):
        """session object"""
        return self.__session

    def set_session_id(self, sid):
        """override session id"""
        old_sid = self.__session.id()
        self.__cookies["sid"] = sid
        self.args.arguments()["sid"] = sid
        self.__session = managers.session_manager[sid]
        managers.session_manager.remove_session(old_sid)

    def headers(self, headers=None):
        """ Server headers. """
        return self.__headers

    def headers_out(self, headers=None):
        """ Server headers. """
        return self.__headers_out

    def environment(self, environment=None):
        """ Server environment """
        return self.__environment

    def arguments(self, args=None):
        """ request arguments """
        return self.__arguments

    def cookies(self):
        """ Server cookies """
        return self.__cookies

    def response_cookies(self):
        """ Server response cookies """
        return self.__response_cookies

    def application(self):
        """get application object"""
        return self.__app

    def handler(self):
        return self._handler

    def app_id(self):
        """get application identifier"""
        return self.__app_id

    def redirect(self, url_to):
        """specify redirection to some url"""
        self.redirect_to = url_to

    def add_header(self, name, value):
        """add header

        The name is lowercased, as everywhere else in VDOM_dictionary - push,
        remove, add and __contains__ all do it. This method was the one place
        that did not, and it wrote straight into the dictionary.

        A header name is case-insensitive by definition, but the dictionary is
        not: `Content-type` and `content-type` were two entries, and
        `send_headers` iterates entries. Both went out on the wire. Chrome
        refuses such a response - `fetch` fails with "Failed to fetch" and an
        `<img>` never loads - while a tolerant client merges them, which is why
        the fault was invisible from a script and fatal from a browser.
        """
        headers = self.__headers_out.headers()
        headers[name.lower()] = value

    def send_file(self, filename, length, handler, content_type=None, cache_control=True):
        """send response as a downloadable file

        The Content-Disposition below is a default, not a decision: a caller
        that already set one keeps it.

        It matters because this method is the point of no return. It ends in
        `set_nocache()`, which calls `send_response`, `send_headers` and
        `end_headers` - the headers go out on the socket here. Anything set
        afterwards is written to a dictionary nobody reads again, silently.

        So a caller had no way to choose how its body is presented: setting the
        header before was overwritten here, and setting it after was too late.
        Concretely, a vhtml macro serving a file could never offer a download -
        with a content type given, which is the normal case, the `inline`
        branch was taken whatever the macro asked - and the name came from
        `filename`, which its caller derives from the URL. On a route like
        /file/{node} that is the node's guid, so downloads arrived named after
        an identifier.
        """
        f_content_type = content_type if content_type else "application/octet-stream"
        self.add_header("Content-type", f_content_type)
        if "content-disposition" not in self.__headers_out.headers():
            disposition = "inline" if content_type else "attachment"
            self.add_header("Content-Disposition",
                            "%s; %s" % (disposition, content_disposition_name(filename)))

        # Cache-Control is a default here too, for the same reason as the
        # disposition above: a caller that already set one knows something this
        # method does not. A thumbnail named after its node, its page and its
        # dpi never changes, so it asks for a year; without this it was handed
        # no-store and re-fetched on every scroll.
        deja_pose = "cache-control" in self.__headers_out.headers()
        if cache_control is None or deja_pose:
            pass
        elif cache_control is True:
            self.add_header("Cache-Control", "max-age=86400")
        elif cache_control is False:
            self.add_header("Cache-Control",
                            "no-cache, no-store, must-revalidate")
        elif isinstance(cache_control, int):
            self.add_header("Cache-Control", "max-age=%s" % cache_control)

        self.add_header("Content-Length", str(length))
        self.set_nocache()
        self.binary(True)
        self.write_handler(handler)
