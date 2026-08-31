# import os
# import time
import random
import socket
import select
import socketserver
# import BaseHTTPServer
# import SimpleHTTPServer
import SOAPpy

# import managers
from utils.pid import VDOM_server_pid
from utils.semaphore import VDOM_semaphore
from .vhosting import VDOM_vhosting
from soap.functions import *
from soap.wsdl import gen_wsdl
from soap.wsdl import methods as wsdl_methods


class VDOM_http_server(socketserver.ThreadingTCPServer):
    """VDOM threading http server class"""

    # The listen backlog. `socketserver` defaults it to 5, and this class never
    # said otherwise - so the server listened with `listen(5)`.
    #
    # Five is not the number of clients, it is the number of connections the
    # kernel will hold *while waiting to be accepted*. Beyond it, the OS answers
    # new connections with an RST, and the browser reports
    # `net::ERR_CONNECTION_RESET` on whichever resources happened to be in that
    # burst - the large ones first, because they hold their connection longest.
    #
    # One page opening another in an iframe is enough to exceed it: both fetch
    # from the same host at the same moment, and a modern browser opens six
    # sockets per host for each of them. Measured here on a page of 28 scripts
    # and 5 stylesheets loaded inside the desktop shell: two scripts reset out
    # of thirty-three, intermittently, while the very same page loaded on its
    # own was always fine.
    #
    # 128 is the usual figure for a server socket, and the kernel caps it at
    # `somaxconn` anyway. It costs nothing: an entry in the accept queue is a
    # few bytes, and threads are still created one per accepted connection.
    request_queue_size = 128

    def __init__(self, server_address, request_handler_class):
        """constructor"""
        self.__server_address = server_address
        self.__current_connections = 0
        self.__stop = False
        self.restart = False

        # sys.stderr.write(("WSDL file available at %s\n" % VDOM_CONFIG["WSDL-FILE-URL"]))

        # initialize random generator
        random.seed()

        # initialize virtual hosting
        self.__vhosting = VDOM_vhosting()

        # drop pid to file
        self.__pidfile = VDOM_CONFIG["SERVER-PIDFILE"]
        if self.__pidfile != "":
            VDOM_server_pid(self.__pidfile)

        # init SOAP
        encoding = 'UTF-8'
        # Test the encoding, raising an exception if it's not known
        if encoding is not None:
            ''.encode(encoding)
        config = SOAPpy.Config
        self.config = config

        # soap debug options
        self.config.debug = 0
        self.config.VDOM_debug = 0
        self.config.dumpSOAPIn = 0
        self.config.dumpSOAPOut = 0
        self.config.dumpHeadersIn = 0
        self.config.dumpHeadersOut = 0

        self.config.buildWithNamespacePrefix = False

        ssl_context = None
        if ssl_context is not None and not config.SSLserver:
            raise AttributeError(
                "SSL server not supported by this Python installation")
        namespace = "http://services.vdom.net/VDOMServices"
        log = 0
        self.namespace = namespace
        self.objmap = {}
        self.funcmap = {}
        self.ssl_context = ssl_context
        self.encoding = encoding
        self.log = log
        self.allow_reuse_address = 1

        # call base class constructor
        socketserver.ThreadingTCPServer.__init__(
            self, server_address, request_handler_class)

        # create semaphore
        self.__sem = VDOM_semaphore()

        # register soap methods
        for method in list(wsdl_methods.keys()):
            exec("""self.registerFunction(SOAPpy.MethodSig(%s, keywords = 0, context = 1), namespace = "http://services.vdom.net/VDOMServices")""" % method)

# self.registerFunction(SOAPpy.MethodSig(login, keywords = 0, context = 1), namespace = "http://services.vdom.net/VDOMServices")
# self.registerFunction(SOAPpy.MethodSig(create_application, keywords = 0, context = 1), namespace = "http://services.vdom.net/VDOMServices")
# self.registerFunction(SOAPpy.MethodSig(set_application_info, keywords = 0, context = 1), namespace = "http://services.vdom.net/VDOMServices")

        # generate wsdl file
        gen_wsdl()
        # send_to_card("online")

        self.active = True
        self.unavailable = False

    def __del__(self):
        """destructor, remove pid file"""
        VDOM_server_pid(self.__pidfile, False, True)

    def get_request(self):
        """get the request and client address from the socket"""
        while True:
            ret = select.select([self.socket], [], [])
            for r in ret[0]:
                if r == self.socket:
                    sock, addr = self.socket.accept()
                    if self.ssl_context:
                        from OpenSSL import SSL  # type: ignore
                        sock = SSL.Connection(self.ssl_context, sock)
                        sock._setup_ssl(addr)
                        if sock.accept_ssl() != 1:
                            raise socket.error(
                                "Couldn't accept SSL connection")
                    return sock, addr

    def current_connections(self):
        """access current_connections property"""
        return self.__current_connections

# def access_log(self):
# """get access log"""
# return self.__access_log

# def error_log(self):
# """get error log"""
# return self.__error_log

    def virtual_hosting(self):
        """get virtual hosting"""
        return self.__vhosting

    def server_address(self):
        """access server address"""
        return self.__server_address

    # def process_request_thread(self, request, client_address):
    #     setattr(current_thread(), THREAD_ATTRIBUTE_NAME, None)
    #     return SocketServer.ThreadingTCPServer.process_request_thread(self, request, client_address)

    def serve_forever(self):
        """handle each request in separate thread"""
        # while not self.__stop:
        #   self.handle_request()

        socketserver.ThreadingTCPServer.serve_forever(self)

        # while self.__current_connections:
        # while self.active:
        #     time.sleep(0.1)

    def shutdown(self):
        self.active = False
        socketserver.ThreadingTCPServer.shutdown(self)

    def verify_request(self, request, client_address):
        """verify the request by matching client address with the stored regexp"""
        self.__deny = 0
        return True

    def finish_request(self, request, client_address, thread=None):
        """finish one request by instantiating RequestHandlerClass"""
        self.__sem.lock()
        try:
            # debug("FINISH REQUEST")
            card = True
            limit = True
            # if system_options.get("object_amount", "") is "":
            # pass#card = False
            # else:
            # l = 0
            # try: l = int(system_options["object_amount"])
            # except: pass
            # if "1" != system_options["server_license_type"] and l < managers.xml_manager.obj_count:
            # limit = False
            self.__reject = 0
    # if self.__current_connections >= self.__maximum_connections: self.__reject = 1
    # else:
            self.__current_connections += 1
            self.client_address = client_address
            if "127.0.0.1" != client_address[0]:
                debug("Increase: %d (from %s:%d)" % (
                    self.__current_connections, client_address[0], client_address[1]))
        finally:
            self.__sem.unlock()

            self.RequestHandlerClass(request, client_address, self, {
                                     "reject": self.__reject, "deny": self.__deny, "card": card, "limit": limit, "connections": self.__current_connections})
        try:
            pass  # TODO: PY3
        except Exception as e:
            do_handle = True
            if isinstance(e, socket.error):
                do_handle = False
            if self.__current_connections > 0:
                self.__current_connections -= 1
                if True or "127.0.0.1" != client_address[0]:
                    if do_handle:
                        debug("Decrease: %d (exception %s, from %s:%d)" % (
                            self.__current_connections, e, client_address[0], client_address[1]))
                    else:
                        debug("Decrease: %d (socket error, from %s:%d)" % (
                            self.__current_connections, client_address[0], client_address[1]))

                    # import gc
                    # debug("\nGarbage: "+str(len(gc.garbage))+"\n", "vdomsvr")
                    # if len(gc.garbage) > 0:
                    # print str(gc.garbage)
            if do_handle:
                self.handle_error(request, client_address)

    def notify_finish(self, client_address):
        """must be called by the handler to notify the server about the end of the request processing"""
        self.__sem.lock()
        try:
            # debug("NOTIFY REQUEST")
            if self.__current_connections > 0:
                self.__current_connections -= 1
                if "127.0.0.1" != client_address[0]:
                    debug("Decrease: %d (from %s:%d)" % (
                        self.__current_connections, client_address[0], client_address[1]))
                    # import gc
                    # debug("\nGarbage: "+str(len(gc.garbage))+"\n", "vdomsvr")
                    # if len(gc.garbage) > 0:
                    # print str(gc.garbage)
        finally:
            self.__sem.unlock()

    def get_cur_con(self):
        return self.__current_connections

    def get_wsdl(self):
        """get wsdl data"""
        # !!! TODO: cache wsdl
        ff = open(VDOM_CONFIG["WSDL-FILE-LOCATION"], "rb")
        data = ff.read()
        ff.close()
        return data

    def handle_error(self, request, client_address):
        """handle an error"""
        # self.__error_logger.error("VDOM_http_server", os.getpid(), "Exception happened during processing of request from \"%s\"", client_address)
        # fe = "".join(['-' * 40, "Exception happened during processing of request from ",
        #         str(client_address), traceback.format_exc(), '-' * 40])
        # debug(fe)
        # sys.excepthook(*sys.exc_info()) #TODO: PY

    # soap handler registration methods
    def registerObject(self, object, namespace='', path=''):
        if namespace == '' and path == '':
            namespace = self.namespace
        if namespace == '' and path != '':
            namespace = path.replace("/", ":")
            if namespace[0] == ":":
                namespace = namespace[1:]
        self.objmap[namespace] = object

    def registerFunction(self, function, namespace='', funcName=None, path=''):
        if not funcName:
            funcName = function.__name__
        if namespace == '' and path == '':
            namespace = self.namespace
        if namespace == '' and path != '':
            namespace = path.replace("/", ":")
            if namespace[0] == ":":
                namespace = namespace[1:]
        if namespace in self.funcmap:
            self.funcmap[namespace][funcName] = function
        else:
            self.funcmap[namespace] = {funcName: function}

    def registerKWObject(self, object, namespace='', path=''):
        if namespace == '' and path == '':
            namespace = self.namespace
        if namespace == '' and path != '':
            namespace = path.replace("/", ":")
            if namespace[0] == ":":
                namespace = namespace[1:]
        for i in dir(object.__class__):
            if i[0] != "_" and callable(getattr(object, i)):
                self.registerKWFunction(getattr(object, i), namespace)

    # convenience  - wraps your func for you.
    def registerKWFunction(self, function, namespace='', funcName=None, path=''):
        if namespace == '' and path == '':
            namespace = self.namespace
        if namespace == '' and path != '':
            namespace = path.replace("/", ":")
            if namespace[0] == ":":
                namespace = namespace[1:]
        self.registerFunction(SOAPpy.MethodSig(
            function, keywords=1), namespace, funcName)

    def unregisterObject(self, object, namespace='', path=''):
        if namespace == '' and path == '':
            namespace = self.namespace
        if namespace == '' and path != '':
            namespace = path.replace("/", ":")
            if namespace[0] == ":":
                namespace = namespace[1:]

        del self.objmap[namespace]
