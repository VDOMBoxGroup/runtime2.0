from poplib import POP3, POP3_SSL, POP3_SSL_PORT
from ssl import PROTOCOL_SSLv23, PROTOCOL_TLSv1, SSLContext
import socket
from .message import MailHeader, Message
from utils.exception import VDOM_mailserver_invalid_index


class VDOM_POP3_SSL(POP3_SSL):
    def __init__(self, host, port=POP3_SSL_PORT, keyfile=None, certfile=None, ssl_version=2, timeout=30.0):
        self.host = host
        self.port = port
        self.keyfile = keyfile
        self.certfile = certfile
        self.buffer = ""
        msg = "getaddrinfo returns an empty list"
        self.sock = None
        for res in socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                self.sock.settimeout(timeout)
                self.sock.connect(sa)
            except OSError:
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise (socket.error, msg)
        self.file = self.sock.makefile("rb")
        self.sslobj = SSLContext.wrap_socket(self.sock, self.keyfile, self.certfile, ssl_version=ssl_version)
        self._debugging = 0
        self.welcome = self._getresp()


class VDOM_Pop3_client:
    def __init__(self, server, port=110, secure=False):
        self.server = server
        self.port = port
        self.secure = secure
        self.message_count = 0
        self.read_mails_count = 0

        if not self.secure:
            ssl_version = PROTOCOL_SSLv23 if self.secure == 1 or self.secure else PROTOCOL_TLSv1
            self.connection = VDOM_POP3_SSL(self.server, self.port, ssl_version=ssl_version, timeout=30.0)

        else:
            self.connection = POP3(self.server, self.port, 30.0)
        self.connected = False

    def user(self, login, passw):
        self.connection.user(login.encode("utf8"))
        self.connection.pass_(passw.encode("utf8"))
        try:
            self.message_count = self.connection.stat()[0]
        except Exception:
            self.connected = False
        else:
            self.connected = True
            self.__user = login
            self.__password = passw

    def __len__(self):
        "Return the number of messages at POP-server"
        try:
            self.message_count = self.connection.stat()[0]
        except Exception:
            self.connected = False

    def quit(self):
        self.connection.quit()
        self.connected = False

    def fetch_message(self, id, delete=False):
        if not self.connected:
            return None
        if id >= self.message_count:
            raise VDOM_mailserver_invalid_index(id)
        email_id = str(self.connection.uidl(id + 1).split()[2])
        # email_size = str(self.connection.list(id + 1).split(" ")[2])
        # email_content_decode = ""
        email_content = "\n".join(self.connection.retr(id + 1)[1])
        msg = Message.fromstring(email_content, email_id)
        if delete:
            self.connection.dele(id + 1)
        return msg

    def fetch_all_messages(self, offset=0, limit=0, delete=False):
        if not self.connected:
            return []
        emails = []
        mail_number = -1
        for i in range(offset, min(limit or self.message_count, self.message_count)):
            mail_number = i + 1
            emails.append(self.fetch_message(i, delete))
        self.read_mails_count = mail_number
        return emails

    def list(self):
        if not self.connected:
            return None
        result = []
        _headers = self.connection.list()
        for h in _headers[1]:
            id, size = h.split(" ")
            result.append(MailHeader(id, size))
        return result

    def delete(self, which):
        if not self.connected:
            return None
        self.connection.dele(which)
