from collections import namedtuple
import datetime
import threading
import time
import email
# `import email` ne garantit pas ses sous-modules : `email.header` est
# utilise par `entete_lisible`, et compter sur un import indirect est le
# genre de dependance qui tient jusqu'au jour ou elle ne tient plus.
import email.header
import email.utils
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from uuid import uuid4
import base64
import quopri
import re

# MailAttachment = namedtuple("MailAttachment","data, filename, content_type, content_subtype")
MailContentType = namedtuple("MailContentType", "type, charset, params")


def entete_lisible(brut, codecs=["utf8", "cp1252", "latin1"]):
    """An RFC 2047 header, put back together as text.

    `=?UTF-8?B?RGV2aXM=?= <a@b.fr>` is **several** pieces, some encoded and some
    not, and a subject in two languages has two of the first kind. Taking only
    `[0]`, as this file used to, kept the first word of a subject and dropped
    the rest.

    It used to call `email.Header.decode_header`, which is Python 2 - the name
    is `email.header` now. The AttributeError was swallowed by the `except`
    below, so nothing broke: subject, sender and recipient simply came back
    **empty**, and had been doing so since the port.
    """
    if not brut:
        return ""
    morceaux = []
    for texte, codec in email.header.decode_header(brut):
        if isinstance(texte, bytes):
            morceaux.append(decode_strings(texte, [codec] + codecs if codec else codecs))
        else:
            morceaux.append(texte)
    return "".join(morceaux)


def _quand(entete):
    """The instant a message was sent, in UTC, as `YYYY-MM-DD HH:MM:SS`.

    Three things were wrong with what stood here, and each of them shows only
    on real mail:

      * the format was `%d %b %Y`, so **the time of day was dropped**. A mailbox
        sorted by date then had every message of a day arrive at midnight, in
        an order that was not theirs;
      * `parsedate` answers `None` on a header it cannot read - and there are
        such headers in any real mailbox - and `strftime(None)` raises. One
        malformed date failed the whole fetch;
      * `mktime` reads the tuple as *local* time, ignoring the offset the
        header carries. A message sent at 09:00 in Tokyo was filed at 09:00
        here.

    `parsedate_to_datetime` keeps the offset, so the instant is preserved and
    converted once, to UTC - which is what SQLite's `datetime('now')` writes,
    so the two are comparable.
    """
    quand = None
    if entete:
        try:
            quand = email.utils.parsedate_to_datetime(entete)
        except (TypeError, ValueError):
            quand = None
    if quand is None:
        quand = datetime.datetime.now(datetime.timezone.utc)
    elif quand.tzinfo is None:
        # A date without an offset is the sender's local time, and we have no
        # way to know which one that is. Reading it as UTC is a choice, and the
        # only one that does not invent an offset.
        quand = quand.replace(tzinfo=datetime.timezone.utc)
    quand = quand.astimezone(datetime.timezone.utc)
    return quand.strftime("%Y-%m-%d %H:%M:%S"), str(int(quand.timestamp()))


def mail_to_dict(mail, codecs=["utf8", "cp1252", "latin1"]):
    result = {}
    result["subject"] = entete_lisible(mail.get("Subject"), codecs)
    result["from_email"] = entete_lisible(mail.get("From"), codecs)
    result["to_email"] = entete_lisible(mail.get("To"), codecs)

    result["date"], result["date_in_sec"] = _quand(mail.get("Date"))

    # try:
    # mail_type = email.Header.decode_header(mail.get('Content-Type'))
    # if mail_type and "plain" in mail_type[0][0]:
    # mail_type = "plain"
    # else:
    # mail_type = "html"
    # except Exception, ex:
    # mail_type = "html"

    if "X-Priority" in mail:
        priority = re.search(r"\d", mail["X-Priority"])
        if priority:
            result["priority"] = "high" if priority.group(0) == "1" else "normal"

    return result


class MIME_VDOM(MIMENonMultipart):
    def __init__(self, _data, _type, _subtype, _encoder=encoders.encode_base64, **_params):
        MIMENonMultipart.__init__(self, _type, _subtype, **_params)
        self.set_payload(_data)
        _encoder(self)


class MailAttachment:
    def __init__(
        self,
        data=None,
        filename="",
        content_type="application",
        content_subtype="octet-stream",
        _encoder=encoders.encode_base64,
        contentid=None,
        inline_disposition=False,
        **_params,
    ):
        self.data = data
        self.filename = filename
        self.content_type = content_type
        self.content_subtype = content_subtype
        self.inline_disposition = inline_disposition
        self.encoder = _encoder
        self.__params = _params
        self.content_id = contentid

    @classmethod
    def fromtuple(self, t):
        attach = None
        # attach = self()
        # if len(t)==4:
        # attach.data, attach.filename, attach.content_type, attach.content_subtype = t
        if isinstance(t, tuple):
            attach = self(*t)
        return attach

    def as_mime(self):
        attach = MIME_VDOM(self.data, self.content_type, self.content_subtype, self.encoder, **self.__params)
        if self.filename:
            if self.inline_disposition:
                attach.add_header("content-disposition", "inline", filename=self.filename)
            else:
                attach.add_header("content-disposition", "attachment", filename=self.filename)
            attach.add_header("content-location", self.filename)
        if self.content_id:
            attach.add_header("Content-ID", self.content_id)
        return attach


conn = threading.local()


class MailHeader:
    def __init__(self, mail_id="", octets_number="", client=None):
        self.id = mail_id
        self.size = octets_number


# self.__client = client
# self.__attr = ["from_email", "to_email", "subject", "date"]
# if self.__client is not None:
# self.__pop3_config = {"user":client.user,
# "passwd":client.password,
# "host":client.server,
# "port":client.port,
# "secure":client.secure}

# def __getattribute__(self, name):
# try:
# return object.__getattribute__(self, name)
# except:
# if name in self.__attr:
# parts = self.__lazyLoad()
# for item in self.__attr:
# value = parts[item]
# setattr(self, item, value)
# return object.__getattribute__(self, name)
# else:
# raise AttributeError
#
# def __lazyLoad(self):
# from .pop import VDOM_Pop3_client
# if getattr(conn, "current_conn", None) is None:
# if not self.__client.connected:
# self.__client = VDOM_Pop3_client(self.__pop3_config["host"], self.__pop3_config["port"],
# self.__pop3_config["secure"])
# self.__client.user(self.__pop3_config["user"], self.__pop3_config["passwd"])
# if self.__client.connected:
# conn.current_conn = self.__client.connection
# else: return None
#
# headers = conn.current_conn.top(self.id, 0)[1]
# mimestring = "\n".join(headers)
# mail = email.message_from_string(mimestring)
# return mail_to_dict(mail)


class Message:
    def __init__(self, **kw):
        self.id = 0
        self.subject = None
        self.sender = None  # seems not used
        self.from_email = None
        self.reply_to = None
        self.to_email = ""
        self.attach = []
        self.body = None
        self.date = None
        self.nomultipart = False
        self.headers = {}
        self.content_type = "text/html"
        self.content_charset = "utf-8"
        self.content_params = {}
        self.multipart_subtype = "mixed"
        self.ttl = 50
        self.priority = "normal"
        convertmap = {
            "id": "id",
            "sender": "sender",
            "from": "from_email",
            "to": "to_email",
            "subj": "subject",
            "msg": "body",
            "attach": "attach",
            "ttl": "ttl",
            "reply": "reply_to",
            "headers": "headers",
            "no_multipart": "nomultipart",
            "content_type": "content_type",
            "content_charset": "content_charset",
            "content_params": "content_params",
            "multipart_subtype": "multipart_subtype",
        }
        for key, value in kw.items():
            if key in convertmap:
                if key == "attach":
                    value = [msg if isinstance(msg, MailAttachment) else MailAttachment.fromtuple(msg) for msg in value]
                if key == "content_type":
                    if isinstance(value, tuple):
                        if len(value) > 1:
                            self.content_charset = value[1]
                        if len(value) > 2 and value[2]:
                            self.content_params = value[2]
                        value = value[0]
                setattr(self, convertmap[key], value)
        # Not needed as library do it itself
        # if isinstance(self.to_email, list) and len(self.to_email)>0:
        # self.to_email = ", ".join(self.to_email)

    def append(self, attachment):
        if self.nomultipart:
            raise Exception("Non Multipart message cannot have attachment")
        if isinstance(attachment, MailAttachment):
            self.attach.append(attachment)
        elif isinstance(attachment, tuple):
            self.attach.append(MailAttachment.fromtuple(attachment))

    def as_mime(self):
        # rewrite this code to return MIME object

        if self.nomultipart:
            msgbody = self.body
            msg = MIMEText(msgbody)
            # if len(self.content_type)>1: #item["content_type"] == (type, charset, params={})
            msg.set_type(self.content_type)
            msg.set_charset(self.content_charset)
            if self.content_params:
                for key, value in self.content_params.items():
                    msg.set_param(key, value)
            # else:
            # msg.set_type("text/html")
            # msg.set_charset("utf-8")
        else:
            msg = MIMEMultipart(_subtype=self.multipart_subtype)
            msgbody = self.body
            if msgbody:
                text2 = MIMEText(msgbody)
                text2.set_type("text/html")
                text2.set_charset("utf-8")
                msg.attach(text2)
            attach = self.attach
            for a in attach:
                msg.attach(a.as_mime())

        subject = self.subject
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = self.to_email
        if self.reply_to:
            msg["Reply-to"] = self.reply_to
        if self.headers:
            for key, value in self.headers.items():
                msg[key] = value

        # `Message-ID` and `Date` are required by RFC 5322, and nothing here
        # wrote either of them. It is not a formality: Gmail refuses outright -
        #
        #   550-5.7.1 Messages missing a valid Message-ID header are not accepted
        #
        # so every message this server has ever sent to a Gmail address bounced.
        # The local SMTP relay accepts them, which is why it looks like sending
        # works right up until the recipient is at a strict provider.
        #
        # Set only when absent, so a caller that threads a conversation by
        # supplying its own identifiers keeps them.
        if "Message-ID" not in msg:
            # The domain is taken from the sender, so the identifier belongs to
            # the domain that sent it - a Message-ID pointing somewhere else is
            # exactly what spam filters look for.
            _, adresse = email.utils.parseaddr(self.from_email or "")
            domaine = adresse.split("@")[-1] if "@" in adresse else None
            msg["Message-ID"] = email.utils.make_msgid(domain=domaine)
        if "Date" not in msg:
            msg["Date"] = email.utils.formatdate(localtime=True)

        return msg.as_string()

    @classmethod
    def fromstring(self, mimestring, email_id):
        msg = Message()
        msg.id = email_id
        mail = email.message_from_string(mimestring)
        msg.parse_body(mail)
        codecs = [msg.content_charset, "utf8", "cp1252", "latin1"]
        kw = mail_to_dict(mail, codecs)
        for k, v in kw.items():
            if hasattr(msg, k):
                setattr(msg, k, v)

        # try:
        # subject = email.Header.decode_header(mail.get('Subject'))
        # msg.subject        = subject[0][0].decode(subject[0][1]) if subject[0][1] else decode_strings(subject[0][0], codecs)
        # except Exception, ex:
        # msg.subject = ""

        # try:
        # from_email = email.Header.decode_header(mail.get('From'))
        # msg.from_email    = from_email[0][0].decode(from_email[0][1]) if from_email[0][1] else decode_strings(from_email[0][0], codecs)
        # except Exception, ex:
        # msg.from_email = ""

        # try:
        # to_email = email.Header.decode_header(mail.get('To'))
        # msg.to_email    = to_email[0][0].decode(to_email[0][1]) if to_email[0][1] else decode_strings(to_email[0][0], codecs)
        # except Exception, ex:
        # msg.to_email = ""

        # if mail.get('Date'):
        # date = mail.get('Date')
        # msg.date = time.strftime("%d %b %Y",email.utils.parsedate(date))
        # msg.date_in_sec    = str(time.mktime(email.utils.parsedate(date)))
        # else:
        # msg.date = time.strftime("%d %b %Y")
        # msg.date_in_sec    = str(time.mktime(time.localtime()))

        # try:
        # mail_type = email.Header.decode_header(mail.get('Content-Type'))
        # if mail_type and "plain" in mail_type[0][0]:
        # msg.mail_type = "plain"
        # else:
        # msg.mail_type = "html"
        # except Exception, ex:
        # msg.mail_type = "html"

        # if "X-Priority" in mail:
        # priority = re.search('\d', mail["X-Priority"])
        # if priority:
        # msg.priority = "high" if priority.group(0) == "1" else "normal"

        return msg

    def parse_body(self, mail):
        """The body, and the attachments, out of a parsed message.

        Rewritten rather than patched, and the reason is in one line of the
        version before: `body += base64.b64decode(...)`. In Python 3 that
        returns **bytes**, `body` is a `str`, and the concatenation raises -
        into an `except: pass`. So a base64 message, which is most of them,
        arrived with an empty body and no complaint.

        `get_payload(decode=True)` does what those branches were doing by hand -
        base64, quoted-printable, 7bit - and it does it right. What is left to
        decide here is what belongs to the body and what is an attachment.
        """
        self.attach = []
        morceaux = []

        for part in mail.walk():
            if part.get_content_maintype() == "multipart":
                continue

            disposition = str(part.get("Content-Disposition") or "")
            nom = part.get_filename()

            # An attachment is one that says so, or one that carries a file
            # name. The second half matters: plenty of senders attach a PDF
            # with no disposition at all.
            if "attachment" in disposition.lower() or nom:
                piece = MailAttachment()
                piece.guid = str(uuid4())
                try:
                    piece.data = part.get_payload(decode=True) or b""
                except Exception:
                    piece.data = b""
                piece.filename = entete_lisible(nom) or ("piece-" + piece.guid[:8])
                piece.content_type = part.get_content_maintype() or "application"
                piece.content_subtype = part.get_content_subtype() or "octet-stream"
                piece.mail_id = ""
                piece.location = "inbox"
                # `inline` with a content-id is an image *of* the body - a
                # signature logo, a chart - and not a document someone meant to
                # send. The distinction is kept so the screen can resolve
                # `cid:` references instead of listing them as files.
                piece.inline_disposition = ("inline" in disposition.lower()
                                            or bool(part.get("Content-ID")))
                piece.content_id = str(part.get("Content-ID") or "").strip("<>")
                self.attach.append(piece)
                continue

            sorte = part.get_content_type()
            if sorte not in ("text/plain", "text/html"):
                continue

            try:
                octets = part.get_payload(decode=True)
            except Exception:
                octets = None
            if octets is None:
                continue

            codec = part.get_content_charset() or self.content_charset or "utf8"
            morceaux.append((sorte, decode_strings(octets, [codec, "utf8", "cp1252", "latin1"])))

        # HTML wins when both are there: a sender who writes both means the
        # plain part as a fallback, and showing the fallback to someone whose
        # screen can render the other is showing them the lesser of the two.
        html = [t for (s2, t) in morceaux if s2 == "text/html"]
        plein = [t for (s2, t) in morceaux if s2 == "text/plain"]
        if html:
            self.body = "".join(html)
            self.content_type = "text/html"
        elif plein:
            self.body = "".join(plein)
            self.content_type = "text/plain"
        else:
            self.body = ""

        self.content_charset = mail.get_content_charset() or "utf-8"


def decode_strings(text, codecs_list):
    """Bytes to text, trying the codecs in order.

    **Strictly**, and that is the whole fix. This used to decode with
    `"ignore"`, which never raises: decoding latin-1 bytes as UTF-8 silently
    *dropped* every byte it could not read and returned a shortened string. The
    loop therefore always stopped on the first codec, and the ones after it were
    dead code. Measured: `b"La Vénitienne"` with `["utf8", "latin1"]` came
    back as `"La Vnitienne"` - an accent gone, and no error anywhere.

    Strict decoding makes a wrong codec fail, so the next one gets its turn.
    `"replace"` is kept for the end, because a message that cannot be decoded at
    all should still be readable-ish rather than empty.
    """
    if type(text) is str:
        return text
    if text is None:
        return ""

    vus = []
    for codec in list(codecs_list) + ["utf8", "cp1252", "latin1"]:
        if not codec or codec in vus:
            continue
        vus.append(codec)
        try:
            return text.decode(codec)
        except (UnicodeDecodeError, LookupError):
            continue

    return text.decode("utf8", "replace")
