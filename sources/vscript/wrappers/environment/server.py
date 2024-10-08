
import re
import managers
import uuid
from utils.exception import VDOM_mailserver_invalid_index
from mailing.message import Message, MailAttachment
from mailing.email1 import VDOM_email_manager
from ... import errors
from ...subtypes import binary, generic, string, integer, boolean, array, error, v_mismatch, v_nothing, v_empty
from ..scripting import v_vdomobject, v_vdomapplication
from ...variables import variant


default_text_encoding="utf-16"


class mailserver_error(errors.generic):

    def __init__(self, message, line=None):
        errors.generic.__init__(self, message=u"Mailserver error: %s"%message, line=line)


class mailserver_already_connected(mailserver_error):

    def __init__(self, line=None):
        mailserver_error.__init__(self, message=u"Already connected", line=line)


class mailserver_closed_connection(mailserver_error):

    def __init__(self, line=None):
        mailserver_error.__init__(self, message=u"Connection closed", line=line)


class mailserver_no_message_index(mailserver_error):

    def __init__(self, index=None, line=None):
        mailserver_error.__init__(self, message=u"No messege with index %s"%(index if index is not None else "'invalid'",), line=line)


v_mailservererror = error(mailserver_error)
v_mailserveralreadyconnectederror = error(mailserver_already_connected)
v_mailserverclosedconnectionerror = error(mailserver_closed_connection)
v_mailservernomessageindexerror = error(mailserver_no_message_index)


class v_mailattachment(generic):

    def __init__(self, attachment=None):
        generic.__init__(self)
        self._value = attachment or MailAttachment()
        self._data_type = binary

    value = property(lambda self: self._value)

    def v_data(self, **keywords):
        if "let" in keywords:
            var = keywords["let"]
            self._data_type = type(var.subtype)
            self._value.data = var.as_binary if isinstance(var.subtype, binary) else \
                            var.as_string

        elif "set" in keywords:
            raise errors.object_has_no_property("data")
        else:
            return self._data_type(self._value.data)	

    def v_filename(self, **keywords):
        if "let" in keywords:
            self._value.filename=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("filename")
        else:
            return string(self._value.filename)	

    def v_contenttype(self, **keywords):
        if "let" in keywords:
            self._value.content_type=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("contenttype")
        else:
            return string(self._value.content_type)	

    def v_contentsubtype(self, **keywords):
        if "let" in keywords:
            self._value.content_subtype=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("contentsubtype")
        else:
            return string(self._value.content_subtype)


class v_mailattachmentcollection(generic):

    def __init__(self, value):
        generic.__init__(self)
        self._value = value

    def __call__(self, index, **keywords):
        if "let" in keywords:
            raise errors.object_has_no_property
        elif "set" in keywords:
            raise errors.object_has_no_property
        else:
            try:
                return v_mailattachment(self._value.attach[index.as_integer])
            except KeyError:
                return errors.subscript_out_of_range

    def __iter__(self):
        for attachment in self._value:
            yield variant(v_mailattachment(attachment))

    def __len__(self):
        return integer(len(self._value))


class v_mailmessage(generic):

    def __init__(self, message=None):
        generic.__init__(self)
        self._value=message or Message()


    value=property(lambda self: self._value)


    def v_id(self, **keywords):
        if "let" in keywords:
            self._value.id=keywords["let"].as_integer
        elif "set" in keywords:
            raise errors.object_has_no_property("id")
        else:
            return integer(self._value.id)

    def v_subject(self, **keywords):
        if "let" in keywords:
            self._value.subject=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("subject")
        else:
            return v_empty if self._value.subject is None else string(self._value.subject)

    def v_sender(self, **keywords):
        if "let" in keywords:
            self._value.from_email=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("sender")
        else:
            return v_empty if self._value.from_email is None else string(self._value.from_email)

    def v_replyto(self, **keywords):
        if "let" in keywords:
            self._value.reply_to=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("replyto")
        else:
            return v_empty if self._value.reply_to is None else string(self._value.reply_to)

    def v_recipients(self, **keywords):
        if "let" in keywords:
            self._value.to_email=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("recipients")
        else:
            return v_empty if self._value.to_email is None else string(self._value.to_email)

    def v_body(self, **keywords):
        if "let" in keywords:
            self._value.body=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("body")
        else:
            return v_empty if self._value.body is None else string(self._value.body)

    def v_nomultipart(self, **keywords):
        if "let" in keywords:
            self._value.nomultipart=keywords["let"].as_boolean
        elif "set" in keywords:
            raise errors.object_has_no_property("nomultipart")
        else:
            return boolean(self._value.nomultipart)

    def v_priority(self, **keywords):
        if "let" in keywords:
            self._value.priority=keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("priority")
        else:
            return string(self._value.priority)

    def v_contenttype(self, **keywords):
        if "let" in keywords:
            keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("contenttype")
        else:
            return string("")

    def v_charset(self, **keywords):
        if "let" in keywords:
            keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("charset")
        else:
            return string("")

    def v_ttl(self, **keywords):
        if "let" in keywords:
            self._value.ttl=keywords["let"].as_integer
        elif "set" in keywords:
            raise errors.object_has_no_property("priority")
        else:
            return integer(self._value.ttl)

    def v_attachments(self, index=None, **keywords):
        if index is not None:
            if "let" in keywords or "set" in keywords:
                raise errors.object_has_no_property("attachments")
            else:
                return v_mailattachment(self._value.attach[index.as_integer])
        else:
            return v_mailattachmentcollection(self._value.attach)

    def v_addattachment(self, attachment):
        self._value.attach.append(attachment.as_specific(v_mailattachment).value)
        return v_mismatch

    def v_addheader(self, key, value):
        self._value.headers[key.as_string] = value.as_string
        return v_mismatch



class v_mailconnection(generic):

    def __init__(self, client=None):
        generic.__init__(self)
        self._client=client

    def v_isconnected(self, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property("isconnected")
        else:
            return boolean(self._client.connected)

    def v_connect(self, server, port, secure=None):
        from mailing.pop import VDOM_Pop3_client
        if self._client:
            raise mailserver_already_connected
        self._client = VDOM_Pop3_client(server.as_string, port.as_integer,
                                      secure=False if secure is None else secure.as_boolean)
        return v_mismatch

    def v_user(self, login, password):
        if not self._client:
            raise mailserver_closed_connection
        self._client.user(login.as_string, password.as_string)
        return v_mismatch

    def v_receive(self, index=None, delete=None):
        if not self._client:
            raise errors.mailserver_closed_connection
        message = self._client.fetch_message(0 if index is None else index.as_integer,
                                           False if delete is None else delete.as_boolean)
        return v_nothing if message is None else v_mailmessage(message)

    def v_receiveall(self, offset=None, limit=None, delete=None):
        if not self._client:
            raise errors.mailserver_closed_connection
        messages = self._client.fetch_all_messages(0 if offset is None else offset.as_integer,
                                                 None if limit is None else limit.as_integer, False if delete is None else delete.as_boolean)
        return array(items=[v_mailmessage(message) for message in messages])	

    def v_countmessages(self):
        if not (self._client and self._client.connected):
            raise errors.mailserver_closed_connection
        return integer(len(self._client))

    def v_delete(self, index):
        if not (self._client and self._client.connected):
            raise errors.mailserver_closed_connection
        self._client.delete(index.as_integer)
        return v_mismatch

    def v_quit(self, force=False):
        if not (self._client and self._client.connected):
            raise errors.mailserver_closed_connection
        self._client.quit()
        return v_mismatch


class SmtpSettings(object):

    def __init__(self):
        self.smtp_server_address = ""
        self.smtp_server_port = 0
        self.smtp_server_user = ""
        self.smtp_server_password = ""
        self.smtp_server_sender = ""
        self.smtp_over_ssl = 0


class v_smtpsettings(generic):

    def __init__(self, smtp_settings=None):
        generic.__init__(self)
        self._value = smtp_settings or SmtpSettings()

    def get_opt(self, name):
        # e.g. SMTP-SERVER-ADDRESS -> smtp_server_address
        attr_name = "_".join(name.lower().split("-"))
        if hasattr(self._value, attr_name):
            return getattr(self._value, attr_name)
        return None

    def v_server(self, **keywords):
        if "let" in keywords:
            self._value.smtp_server_address = keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("server")
        else:
            return string(self._value.smtp_server_address)

    def v_port(self, **keywords):
        if "let" in keywords:
            self._value.smtp_server_port=keywords["let"].as_integer
        elif "set" in keywords:
            raise errors.object_has_no_property("port")
        else:
            return integer(self._value.smtp_server_port)

    def v_user(self, **keywords):
        if "let" in keywords:
            self._value.smtp_server_user = keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("user")
        else:
            return string(self._value.smtp_server_user)

    def v_password(self, **keywords):
        if "let" in keywords:
            self._value.smtp_server_password = keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("password")
        else:
            return string(self._value.smtp_server_password)

    def v_sender(self, **keywords):
        if "let" in keywords:
            self._value.smtp_server_sender = keywords["let"].as_string
        elif "set" in keywords:
            raise errors.object_has_no_property("sender")
        else:
            return string(self._value.smtp_server_sender)

    def v_ssl(self, **keywords):
        if "let" in keywords:
            self._value.smtp_over_ssl = keywords["let"].as_integer
        elif "set" in keywords:
            raise errors.object_has_no_property("ssl")
        else:
            return integer(self._value.smtp_over_ssl)


class v_mailer(generic):

    def v_connect(self, server, port, secure=None):
        from mailing.pop import VDOM_Pop3_client
        client = VDOM_Pop3_client(server.as_string, port.as_integer,
                                secure=False if secure is None else secure.as_boolean)
        return v_mailconnection(client)

    def v_send(self, message):
        return integer(managers.email_manager.send(message.as_specific(v_mailmessage).value))

    def v_send_via(self, message, smtp_settings):
        settings = smtp_settings.as_specific(v_smtpsettings)
        email_manager = VDOM_email_manager(config=settings, daemon=False)
        msg_id = email_manager.send(message.as_specific(v_mailmessage).value)
        if msg_id >= 0:
            email_manager.work()
            ret = email_manager.check(msg_id)
            if ret:
                print (ret)
                msg_id = -1
        else:
            msg_id = -1
        return integer(msg_id)

    def v_receive(self, server, port, login, password, secure=None, index=None, delete=None):
        from mailing.pop import VDOM_Pop3_client
        try:
            client = VDOM_Pop3_client(server.as_string, port.as_integer,
                                    secure=False if secure is None else secure.as_boolean)
        except Exception as e:
            raise mailserver_error(str(e))
        try:
            client.user(login.as_string, password.as_string)
            if not client.connected:
                raise mailserver_closed_connection()		
            message = client.fetch_message(0 if index is None else index.as_integer,
                                         False if delete is None else delete.as_boolean)
        except VDOM_mailserver_invalid_index:
            raise mailserver_no_message_index(index.as_integer)
        except Exception as e:
            raise mailserver_error(str(e))		
        finally:
            client.quit()
        return v_mailmessage(message)

    def v_receiveall(self, server, port, login, password, secure=None, offset=None, limit=None, delete=None):
        from mailing.pop import VDOM_Pop3_client
        try:
            client = VDOM_Pop3_client(server.as_string, port.as_integer,
                                    secure=False if secure is None else secure.as_boolean)
        except Exception as e:
            raise mailserver_error(str(e))		
        try:
            client.user(login.as_string, password.as_string)
            if not client.connected:
                raise mailserver_closed_connection()
            messages=client.fetch_all_messages(0 if offset is None else offset.as_integer,
                                               None if limit is None else limit.as_integer, False if delete is None else delete.as_boolean)
        except Exception as e:
            raise mailserver_error(str(e))		
        finally:
            client.quit()
        return array(items=[v_mailmessage(message) for message in messages])	

    def v_countmessages(self, server, port, login, password, secure=None):
        from mailing.pop import VDOM_Pop3_client
        try:
            client = VDOM_Pop3_client(server.as_string, port.as_integer,
                                    secure=False if secure is None else secure.as_boolean)
        except Exception as e:
            raise mailserver_error(str(e))			
        try:
            client.user(login.as_string, password.as_string)
            if not client.connected:
                raise errors.mailserver_closed_connection()
            count=len(client)
        except Exception as e:
            raise mailserver_error(str(e))		
        finally:
            client.quit()
        return integer(count)

    def v_status(self, msg_id):
        result = managers.email_manager.check(msg_id.as_integer)
        return string(result) if result else v_empty		


class v_server(generic):

    check_regex=re.compile("[0-9A-Z]{8}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{4}-[0-9A-Z]{12}", re.IGNORECASE)

    def __init__(self):
        generic.__init__(self)
        self._mailer = v_mailer()

    def v_application(self, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property("application")
        else:
            return v_vdomapplication(managers.request_manager.current.application())

    def v_getapplication(self):
        return v_vdomapplication(managers.request_manager.current.application())

    def v_createobject(self, type, parent, name=None):
        application = managers.request_manager.current.application()
        type = type.as_string.lower()
        if not self.check_regex.search(type):
            xml_type = managers.xml_manager.get_type_by_name(type)
            type = None if xml_type is None else xml_type.id
        parent = parent.as_string.lower()
        if v_server.check_regex.search(parent):
            parent = application.search_object(parent)
        else:
            objects = application.search_objects_by_name(parent)
            parent = objects[0] if len(objects)==1 else None
        if type is None or parent is None:
            raise errors.invalid_procedure_call(name=u"createobject")
        object_tuple=application.create_object(type, parent)
        obj=application.search_object(object_tuple[1])
        if name is not None:
            obj.set_name(name.as_string)
        return v_vdomobject(obj)

    def v_getobject(self, object_string):
        application = managers.request_manager.current.application()
        object_string = object_string.as_string.lower()
        if self.check_regex.search(object_string):
            obj = application.search_object(object_string)
        else:
            objects = application.search_objects_by_name(object_string)
            obj = objects[0] if objects else None
        return v_vdomobject(obj) if obj else v_nothing

    def v_deleteobject(self, object_string):
        application = managers.request_manager.current.application()
        object_string = object_string.as_string.lower()
        if self.check_regex.search(object_string):
            obj = application.search_object(object_string)
        else:
            objects = application.search_objects_by_name(object_string)
            obj = objects[0] if len(objects) == 1 else None
        if obj is None:
            raise errors.invalid_procedure_call(name=u"deleteobject")
        application.delete_object(obj)
        return v_mismatch

    def v_createresource(self, type, name, data):
        application = managers.request_manager.current.application()
        data, id = data.as_simple, unicode(uuid.uuid4())
        if isinstance(data, binary):
            data = data.as_binary
        elif isinstance(data, string):
            data = data.as_string
            try:
                data = data.encode(default_text_encoding)
            except UnicodeError:
                pass
        else:
            raise errors.invalid_procedure_call("createresource")
        application.create_resource(id, type.as_string, name.as_string, data)
        return string(id)

    def v_getresource(self, resource):
        obj = managers.resource_manager.get_resource(managers.request_manager.current.application(), resource.as_string)
        if obj is None:
            return v_empty
        else:
            data=obj.get_data()
            try:
                return string(data.decode(default_text_encoding))
            except UnicodeError:
                return binary(data)

    def v_deleteresource(self, resource):
        managers.resource_manager.delete_resource(managers.request_manager.current.application(),
                                                  resource.as_string, remove=True)
        return v_mismatch

    def v_htmlencode(self, string2encode):
        return string(unicode(string2encode.as_string.encode("html")))

    def v_urlencode(self, string2encode):
        return string(unicode(string2encode.as_string.encode("url")))

    def v_sendmail(self, sender, recipient, subject, message):
        return integer(managers.email_manager.send(sender.as_string,
                                                           recipient.as_string, subject.as_string, message.as_string))

    def v_mailstatus(self, msg_id):
        ret = managers.email_manager.check(msg_id.as_integer)
        return string(ret) if ret else v_nothing

    def v_mailer(self, **keywords):
        if "let" in keywords or "set" in keywords:
            raise errors.object_has_no_property("mailer")
        else:
            return self._mailer
