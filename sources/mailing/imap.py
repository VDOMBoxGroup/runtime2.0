"""IMAP client, alongside the POP3 one.

Why IMAP and not the POP3 client that was already here - four reasons, and each
of them is a thing POP3 cannot do at all:

  * **stable identifiers.** A POP3 message is designated by its number in the
    session, and that number changes as soon as anything is deleted. IMAP gives
    every message a UID that never moves, which is what makes it possible to
    fetch a mailbox twice without importing everything twice;
  * **folders.** POP3 knows one mailbox. A real account has Sent, Drafts, Spam,
    and often the folder that actually matters;
  * **fetching a range.** A first fetch of a mailbox holding seven thousand
    messages cannot download seven thousand bodies in one go. IMAP lets the
    caller ask for the identifiers first and the bodies by the handful;
  * **reading without consuming.** POP3's model is to take the mail away. Here
    the mailbox is read `readonly`, so the messages stay, and stay unread for
    whoever also reads them from a phone.

Decoding is *not* redone: `Message.fromstring` already turns a MIME string into
subject, sender, body and attachments, and it is what the POP3 path uses. One
decoder, and its quirks are the same everywhere.
"""

import imaplib
import re
import socket
import ssl

from .message import Message

# `(attributs) "separateur" nom` - the separator may be NIL, and the name is
# quoted only when it contains a space.
_LIGNE_DOSSIER = re.compile(r'^\([^)]*\)\s+(?:"(?P<sep>[^"]*)"|NIL)\s+(?P<nom>.+)$')


# A body can be large, and `imaplib` refuses a line above ten thousand bytes by
# default - a base64 attachment on one line goes past that immediately, and the
# failure reads as a protocol error rather than as a size limit.
imaplib._MAXLINE = max(getattr(imaplib, "_MAXLINE", 0), 10 * 1024 * 1024)


class VDOM_Imap_client(object):
    """A mailbox one reads, and does not empty."""

    def __init__(self, server, port=993, secure=True, timeout=30.0, insecure=False):
        self.server = server
        self.port = int(port or (993 if secure else 143))
        self.secure = bool(secure)
        self.connected = False
        self.folder = ""
        self.message_count = 0

        socket.setdefaulttimeout(float(timeout))
        if self.secure:
            context = ssl.create_default_context()
            if insecure:
                # A self-signed certificate is a deliberate choice on a private
                # server, not an accident: refusing it outright would make this
                # client unusable there. It is opt-in, per mailbox.
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            self.connection = imaplib.IMAP4_SSL(self.server, self.port,
                                                ssl_context=context)
        else:
            self.connection = imaplib.IMAP4(self.server, self.port)

    # --- the account -------------------------------------------------------

    def user(self, login, password):
        self.connection.login(login, password)
        self.connected = True

    def quit(self):
        try:
            if self.folder:
                self.connection.close()
            self.connection.logout()
        except Exception:
            # A logout that fails changes nothing for the caller: the socket is
            # going away either way, and raising here would turn a finished
            # fetch into a failed one.
            pass
        self.connected = False

    # --- what the account holds --------------------------------------------

    def folders(self):
        """The folder names, decoded.

        The separator is the server's, not ours - a dot here, a slash
        elsewhere - so the name is handed back whole and never rebuilt.
        """
        state, rows = self.connection.list()
        if state != "OK":
            return []
        out = []
        for row in rows or []:
            if not row:
                continue
            texte = row.decode("utf-8", "replace")
            # `(\HasChildren) "." INBOX.Sent` - three fields: the attributes in
            # parentheses, the separator quoted, then the name, which is quoted
            # only when it needs to be. Splitting on the quote character alone
            # returned `." INBOX`, separator included.
            trouve = _LIGNE_DOSSIER.match(texte)
            nom = (trouve.group("nom").strip() if trouve else texte).strip('"')
            if nom:
                out.append(nom)
        return out

    def select(self, folder="INBOX"):
        """Open a folder **read-only**, and answer how many messages it holds.

        `readonly` is the whole point: fetching is not consuming. Without it the
        server marks as read what we merely looked at, and someone reading the
        same account from a phone finds a mailbox that has been read for them.
        """
        state, rows = self.connection.select(folder, readonly=True)
        if state != "OK":
            raise imaplib.IMAP4.error("cannot select %s: %s" % (folder, rows))
        self.folder = folder
        self.message_count = int(rows[0]) if rows and rows[0] else 0
        return self.message_count

    def uids(self, since=0):
        """The UIDs of the folder, oldest first.

        `since` asks the server for what we do not already have. `UID x:*` is
        the IMAP way of saying "from x onwards"; it can answer the last message
        even when x is past the end, so the caller filters - which costs one
        comparison and saves an assumption about a server's goodwill.
        """
        critere = "UID %d:*" % int(since) if since else "ALL"
        state, rows = self.connection.uid("SEARCH", None, critere)
        if state != "OK":
            return []
        brut = (rows[0] or b"").split()
        out = []
        for u in brut:
            try:
                n = int(u)
            except ValueError:
                continue
            if n >= int(since):
                out.append(n)
        out.sort()
        return out

    # --- the messages ------------------------------------------------------

    def fetch(self, uid):
        """One message, decoded, or `None` if the server no longer has it.

        `BODY.PEEK[]` and not `RFC822`: the second one sets the \\Seen flag as a
        side effect, which is exactly what `readonly` was chosen to avoid.
        """
        state, rows = self.connection.uid("FETCH", str(uid), "(BODY.PEEK[])")
        if state != "OK" or not rows:
            return None
        for row in rows:
            if isinstance(row, tuple) and len(row) > 1 and row[1]:
                brut = row[1]
                if isinstance(brut, bytes):
                    # **latin-1, et non utf-8.** Le message arrive en octets et
                    # `fromstring` attend du texte ; utf-8 avec remplacement
                    # perdrait pour de bon les octets d'un corps latin-1, avant
                    # meme que le decodeur n'ait regarde le charset annonce.
                    # latin-1 fait correspondre chaque octet a un caractere,
                    # sans perte, et `get_payload(decode=True)` retrouve ensuite
                    # les octets d'origine.
                    brut = brut.decode("latin1")
                message = Message.fromstring(brut, str(uid))
                return message
        return None

    def fetch_many(self, uids):
        """A handful of messages.

        One request per message rather than one grouped request: a grouped
        FETCH answers a single stream that has to be cut back apart, and a
        single malformed message then costs the whole batch. Here a message
        that cannot be read costs only itself, and the caller keeps the rest.
        """
        out = []
        for uid in uids:
            try:
                message = self.fetch(uid)
            except Exception:
                message = None
            if message is not None:
                out.append((int(uid), message))
        return out
