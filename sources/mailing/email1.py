import managers
from collections import namedtuple
import copy
from daemon import VDOM_mailer
from message import Message
from smtplib import SMTP, SMTPConnectError, SMTPHeloError, SMTPAuthenticationError, SMTPException,\
     SMTPRecipientsRefused, SMTPSenderRefused, SMTPDataError, SSLFakeFile
from socket import create_connection, error as socket_error
from ssl import PROTOCOL_SSLv23, wrap_socket
from storage.storage import VDOM_config
from utils.semaphore import VDOM_semaphore


from traceback import print_exc

MailAttachment = namedtuple("MailAttachment", "data, filename, content_type, content_subtype")


class VDOM_SMTP(SMTP):
    def __init__(self, host='', port=0, local_hostname=None, config=VDOM_config()):
        self.tout = config.get_opt("SMTP-SENDMAIL-TIMEOUT")
        if self.tout is None:
            self.tout = 30.0
        self.tout = float(self.tout)
        self.use_ssl = config.get_opt("SMTP-OVER-SSL")
        if self.use_ssl is None:
            self.use_ssl = 0
        self.set_debuglevel(1)
        SMTP.__init__(self, host='', port=0, local_hostname=None)

    def getreply(self):
        self.sock.settimeout(self.tout)
        return SMTP.getreply(self)

    def _get_socket(self, host, port, timeout):
        new_socket = create_connection((host, port), timeout)
        if self.use_ssl in (1, -1):
            new_socket = wrap_socket(new_socket, ssl_version=PROTOCOL_SSLv23)
            self.file = SSLFakeFile(new_socket)
        return new_socket

    def connect(self, host='localhost', port=0):
        (code, msg) = SMTP.connect(self, host, port)
        if self.use_ssl == 2:
            print ("starttls")
            (resp, reply) = self.starttls()
            print ((resp, reply))
        print ((code, msg))
        return (code, msg)


class VDOM_email_manager(object):
    def __init__(self, config=VDOM_config(), daemon=True):
        self.__sem = VDOM_semaphore()
        self.__queue = []
        self.__errors = {}
        self.__error = ""
        self.__id = 0
        self.__config = config
        self.__load_config()
        if daemon:
            self.__daemon = VDOM_mailer(self)
            self.__daemon.start()

    def __load_config(self):
        self.smtp_server = self.__config.get_opt("SMTP-SERVER-ADDRESS")
        self.smtp_port = self.__config.get_opt("SMTP-SERVER-PORT")
        self.smtp_user = self.__config.get_opt("SMTP-SERVER-USER")
        self.smtp_pass = self.__config.get_opt("SMTP-SERVER-PASSWORD")
        self.use_ssl = self.__config.get_opt("SMTP-OVER-SSL")
        self.smtp_sender = self.__config.get_opt("SMTP-SERVER-SENDER")
        if not self.smtp_server:
            self.smtp_server = "smtp.gmail.com"
            if not self.smtp_port:
                self.smtp_port = 465
            if not self.smtp_user:
                self.smtp_user = "Vdom.Server@gmail.com"
            if not self.smtp_pass and self.smtp_user == "Vdom.Server@gmail.com":
                self.smtp_pass = "VDMNK22YK"
            if not self.use_ssl:
                self.use_ssl = 1
        else:
            if not self.smtp_port:
                self.smtp_port = 25
            if not self.smtp_user:
                self.smtp_user = ""
            if not self.smtp_pass:
                self.smtp_pass = ""
            if not self.use_ssl:
                self.use_ssl = 0

        if not self.smtp_sender:
            self.smtp_sender = ""

        try:
            self.smtp_port = int(self.smtp_port)
        except ValueError:
            self.smtp_port = 25

    def send(self, fr, to=[], subj="", msg="", attach=[], ttl=50, reply="", headers={}, no_multipart=False, content_type=[]):
        """attach item must be a tuple (data, filename, content_type, content_subtype)"""

        self.__load_config()
        if not self.smtp_server:
            return None
        self.__sem.lock()
        try:
            x = self.__id

            if self.smtp_sender and self.smtp_sender.find("@") != -1:
                sender = self.smtp_sender
            else:
                sender = self.smtp_user
            if isinstance(fr, Message):
                m = fr
                if '@' not in m.from_email or m.from_email != sender:
                    m.from_email = "%s <%s>"%(m.from_email, sender)

            else:
                if '@' not in fr or fr != sender:
                    sender = "%s <%s>" % (fr, sender)

                m = {"from": sender, "to": to, "subj": subj, "msg": msg, "attach": attach,
                                     "ttl": ttl, "headers": headers, "no_multipart": no_multipart}
                if reply:
                    m['reply'] = reply
                if len(content_type) > 0:
                    m['content_type'] = content_type[0]
                    if len(content_type) > 1:
                        m['content_charset'] = content_type[1]
                        if len(content_type) > 2:
                            m['content_params'] = content_type[2]
                m = Message(**m)
            m.id = x
            self.__queue.append(m)
            self.__id += 1
            return x
        finally:
            self.__sem.unlock()

    def check(self, _id):
        # check if there was error when sending message, pass here the value returned by .send
        """return string if there was error, return None if no error"""
        self.__sem.lock()
        try:
            x = None
            if _id in self.__errors:
                x = self.__errors[_id]
            return x
        finally:
            self.__sem.unlock()

    def check_connection(self):
        self.__sem.lock()
        try:
            self.__load_config()
            s = VDOM_SMTP(config=self.__config)
            #connecting
            s.connect(self.smtp_server, self.smtp_port)
            self.__error = ""
            #authentification
            if "" != self.smtp_user:
                s.login(self.smtp_user, self.smtp_pass)
                self.__error = ""
            s.quit()
            del s
        except (SMTPConnectError, SMTPHeloError, socket_error) as e:  # Connect error
            debug("SMTP connect error: %s:%d" % (self.smtp_server, self.smtp_port))
            self.__error = "SMTP connect error: %s:%d" % (self.smtp_server, self.smtp_port)
            managers.log_manager.error_server("SMTP connect error: %s on %s:%d" % (e, self.smtp_server, self.smtp_port), "email")
        except SMTPAuthenticationError as e:
            #debug("Authentication error: %s" % str(e))
            self.__error = "SMTP Authentication error: %s" % str(e)
            managers.log_manager.error_server("SMTP authentication error: %s" % str(e), "email")
        except SMTPException, e:
            self.__error = "General SMTP error: %s" % str(e)
        except Exception, e:
            self.__error = "Unknown error: %s" % str(e)
        finally:
            self.__sem.unlock()
        return self.status()

    def cancel(self, _id):
        """cancel email if it has not been sent, return True if email has been successfully cancelled"""
        x = False
        self.__sem.lock()
        try:
            i = -1
            for q in self.__queue:
                if _id == q["id"]:
                    i = self.__queue.index(q)
                    break
            if i >= 0:
                self.__queue.pop(i)
                self.__errors.pop(_id, 0)
                x = True
            return x
        finally:
            self.__sem.unlock()

    def status(self):
        """check is there was smtp connect or authentication error"""
        self.__sem.lock()
        try:
            return copy.deepcopy(self.__error)
        finally:
            self.__sem.unlock()

    def clear_queue(self):
        self.__sem.lock()
        self.__queue = []
        self.__errors = []
        self.__error = ""
        self.__id = 0
        self.__sem.unlock()

    def get_queue(self):
        self.__sem.lock()
        try:
            return copy.deepcopy(self.__queue)
        finally:
            self.__sem.unlock()

    def work(self):
        ts = 0.1
        if len(self.__queue) > 0:
            self.__sem.lock()
            try:
                self.__load_config()
                if not self.smtp_server:
                    raise SMTPConnectError(0, "No server adress in config")
                s = VDOM_SMTP(config=self.__config)
                s.connect(self.smtp_server, self.smtp_port)
                self.__error = ""
                #authentification
                if "" != self.smtp_user:
                    s.login(str(self.smtp_user), str(self.smtp_pass))
                    self.__error = ""

                self.__queue_tmp = []
                ts = 0.1
                while len(self.__queue) > 0:
                    mes = self.__queue.pop(0)
                    mes.ttl -= 1

                    try:
                        s.sendmail(mes.from_email, mes.to_email, mes.as_mime())
                        self.__errors.pop(mes.id, 0)
                    except (SMTPRecipientsRefused, SMTPSenderRefused, SMTPDataError) as e:
                        debug("SMTP send to %s error: %s" % (mes.to_email, str(e)))
                        managers.log_manager.error_server("SMTP send to %s error: %s" % (mes.to_email, str(e)), "email")
                        self.__errors[mes.id] = str(e)
                        # move this mail to the temp queue
                        if mes.ttl > 0:
                            self.__queue_tmp.append(mes)
                    except Exception as e:
                        self.__errors[mes.id] = str(e)
                        print_exc()
                        # move this mail to the temp queue
                        if mes.ttl > 0:
                            self.__queue_tmp.append(mes)
                        self.__queue_tmp.append(mes)
                        raise
                if len(self.__queue_tmp) > 0:
                    self.__queue = self.__queue_tmp  # [item for item in self.__queue_tmp if item["attempt"]<50]
                    del self.__queue_tmp
                    ts = 30
                s.quit()
                del s

            except (SMTPConnectError, SMTPHeloError, socket_error) as e:  # Connect errors
                debug("SMTP connect error: %s:%d" % (self.smtp_server, self.smtp_port))
                self.__error = "SMTP connect error: %s:%d" % (self.smtp_server, self.smtp_port)
                managers.log_manager.error_server("SMTP connect error: %s on %s:%d" % (e, self.smtp_server, self.smtp_port), "email")
                ts = 360
            except SMTPAuthenticationError as e:
                #debug("Authentication error: %s" % str(e))
                self.__error = "SMTP Authentication error: %s" % str(e)
                managers.log_manager.error_server("SMTP authentication error: %s" % str(e), "email")
                ts = 360

            except SMTPException as e:
                self.__error = "General SMTP error: %s" % str(e)
                ts = 30

            except Exception as e:
                self.__error = "Unknown error: %s" % str(e)
                print_exc()
                ts = 5

            finally:
                self.__sem.unlock()
        else:
            ts = 10
        if self.__error:
            print (self.__error)
        return ts
