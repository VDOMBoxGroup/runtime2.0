from builtins import str
from builtins import range
from builtins import object
from collections import namedtuple
import threading
import time
import email
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.mime.multipart  import MIMEMultipart
from uuid import uuid4
import base64, quopri,re

#MailAttachment = namedtuple("MailAttachment","data, filename, content_type, content_subtype")
MailContentType = namedtuple("MailContentType","type, charset, params")

def mail_to_dict(mail, codecs = ['utf8', 'cp1252', 'latin1' ]):
	result = {}
	try:
		subject = email.Header.decode_header(mail.get('Subject'))
		result["subject"] = subject[0][0].decode(subject[0][1]) if subject[0][1] else decode_strings(subject[0][0], codecs)
	except Exception as ex:
		result["subject"] = ""
		

	try:
		from_email = email.Header.decode_header(mail.get('From'))
		result["from_email"] = from_email[0][0].decode(from_email[0][1]) if from_email[0][1] else decode_strings(from_email[0][0], codecs)
	except Exception as ex:
		result["from_email"] = ""
		

	try:
		to_email = email.Header.decode_header(mail.get('To'))
		result["to_email"] = to_email[0][0].decode(to_email[0][1]) if to_email[0][1] else decode_strings(to_email[0][0], codecs)
	except Exception as ex:
		result["to_email"] = ""
		
	if mail.get('Date'):
		date = mail.get('Date')
		result["date"] = time.strftime("%d %b %Y",email.utils.parsedate(date))
		result["date_in_sec"] = str(time.mktime(email.utils.parsedate(date)))
	else:
		result["date"] = time.strftime("%d %b %Y")
		result["date_in_sec"] = str(time.mktime(time.localtime()))
		
	#try:
	#	mail_type = email.Header.decode_header(mail.get('Content-Type'))
	#	if mail_type and "plain" in mail_type[0][0]:
	#		mail_type = "plain"
	#	else:
	#		mail_type = "html"
	#except Exception, ex:		
	#	mail_type = "html"
		
	if "X-Priority" in mail:
		priority = re.search('\d', mail["X-Priority"])
		if priority:
			result["priority"] = "high" if priority.group(0) == "1" else "normal"		
		
	return result
class MIME_VDOM(MIMENonMultipart):

	def __init__(self, _data, _type, _subtype, _encoder=encoders.encode_base64, **_params):
		MIMENonMultipart.__init__(self, _type, _subtype, **_params)
		self.set_payload(_data)
		_encoder(self)
		
class MailAttachment(object):
	def __init__(self, data=None, filename="", content_type="application", content_subtype="octet-stream", _encoder=encoders.encode_base64, contentid=None,inline_disposition=False, **_params):
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
		#attach = self()
		#if len(t)==4:
			#attach.data, attach.filename, attach.content_type, attach.content_subtype = t
		if isinstance(t, tuple):
			attach = self(*t)
		return attach
	
	def as_mime(self):
		attach = MIME_VDOM(self.data, self.content_type,self.content_subtype,self.encoder,**self.__params)
		if self.filename:
			if self.inline_disposition:
				attach.add_header('content-disposition', 'inline', filename=self.filename)
			else:
				attach.add_header('content-disposition', 'attachment', filename=self.filename)
			attach.add_header('content-location', self.filename)
		if self.content_id:
			attach.add_header('Content-ID', self.content_id)
		return attach

conn = threading.local()

class MailHeader(object):
	def __init__(self, mail_id = "", octets_number = "", client = None):
		self.id = mail_id
		self.size = octets_number
#		self.__client = client		
#		self.__attr = ["from_email", "to_email", "subject", "date"]
#		if self.__client is not None:
#			self.__pop3_config = {"user":client.user,
#			                      "passwd":client.password,
#			                      "host":client.server,
#			                      "port":client.port,
#			                      "secure":client.secure}
		
#	def __getattribute__(self, name):
#		try:
#			return object.__getattribute__(self, name)
#		except:
#			if name in self.__attr:
#				parts = self.__lazyLoad()
#				for item in self.__attr:
#					value = parts[item]
#					setattr(self, item, value)
#				return object.__getattribute__(self, name)
#			else:
#				raise AttributeError
#	
#	def __lazyLoad(self):
#		from .pop import VDOM_Pop3_client
#		if getattr(conn, "current_conn", None) is None:
#			if not self.__client.connected:
#				self.__client = VDOM_Pop3_client(self.__pop3_config["host"], self.__pop3_config["port"], 
#				                                            self.__pop3_config["secure"])
#				self.__client.user(self.__pop3_config["user"], self.__pop3_config["passwd"])
#			if self.__client.connected:
#				conn.current_conn = self.__client.connection
#			else: return None
#								
#		headers = conn.current_conn.top(self.id, 0)[1]
#		mimestring = "\n".join(headers)
#		mail = email.message_from_string(mimestring)
#		return mail_to_dict(mail)
	
class Message(object):
	def __init__(self,**kw):
		self.id = 0
		self.subject 	= None
		self.sender = None #seems not used
		self.from_email = None
		self.reply_to = None
		self.to_email 	= ""
		self.attach	= []
		self.body	= None
		self.date 	= None
		self.nomultipart = False
		self.headers = {}
		self.content_type = "text/html"
		self.content_charset = "utf-8"
		self.content_params = {}
		self.multipart_subtype = 'mixed'
		self.ttl = 50
		self.priority = "normal"
		convertmap = {"id":"id","sender":"sender","from":"from_email", "to":"to_email", "subj":"subject", "msg":"body", "attach": "attach","ttl":"ttl","reply":"reply_to", "headers":"headers", "no_multipart": "nomultipart", "content_type":"content_type", "content_charset":"content_charset", "content_params":"content_params","multipart_subtype":"multipart_subtype"}
		for key,value in kw.items():
			if key in convertmap:
				if key=="attach":
					value = [msg if isinstance(msg,MailAttachment) else MailAttachment.fromtuple(msg) for msg in value]
				if key == "content_type":
					if isinstance(value, tuple):
						if len(value)>1:
							self.content_charset = value[1]
						if len(value)>2 and value[2]:
							self.content_params = value[2]
						value = value[0]						
				setattr(self,convertmap[key],value)
		#Not needed as library do it itself		
		#if isinstance(self.to_email, list) and len(self.to_email)>0:
		#	self.to_email = ", ".join(self.to_email)
				
	def append(self, attachment):
		if self.nomultipart:
			raise Exception("Non Multipart message cannot have attachment")
		if isinstance(attachment,MailAttachment):
			self.attach.append(attachment)
		elif isinstance(attachment, tuple):
			self.attach.append(MailAttachment.fromtuple(attachment))

	
	def as_mime(self):
		#rewrite this code to return MIME object
		
		if self.nomultipart:
			msgbody = self.body
			if isinstance(msgbody, str):
				msgbody = msgbody.encode("utf-8")
			msg = MIMEText(msgbody)
			#if len(self.content_type)>1: #item["content_type"] == (type, charset, params={})
			msg.set_type(self.content_type)
			msg.set_charset(self.content_charset)								
			if self.content_params:
				for key,value in self.content_params.items():
					msg.set_param(key,value)
			#else:
			#	msg.set_type("text/html")
			#	msg.set_charset("utf-8")
		else:
			msg = MIMEMultipart(_subtype=self.multipart_subtype)
			msgbody = self.body
			if  msgbody:
				if isinstance(msgbody, str):
					msgbody = msgbody.encode("utf-8")
				text2 = MIMEText(msgbody)
				text2.set_type("text/html")
				text2.set_charset("utf-8")
				msg.attach(text2)
			attach = self.attach
			for a in attach:
				msg.attach(a.as_mime())
		
		subject = self.subject
		# if isinstance(subject, unicode):
		# 	subject = subject.encode("utf-8")
		msg['Subject'] = subject
		msg['From'] = self.from_email
		msg['To'] = self.to_email
		if self.reply_to:
			msg['Reply-to'] = self.reply_to
		if self.headers:
			for key,value in self.headers.items():
				msg[key] = value
		
		return msg.as_string()
	@classmethod
	def fromstring(self, mimestring, email_id):
		msg = Message()
		msg.id = email_id
		mail = email.message_from_string(mimestring)
		msg.parse_body(mail)
		codecs = [msg.content_charset, 'utf8', 'cp1252', 'latin1' ]
		kw = mail_to_dict(mail, codecs)
		for k,v in kw.items():
			if hasattr(msg, k):
				setattr(msg, k, v)
		
#		try:
#			subject = email.Header.decode_header(mail.get('Subject'))
#			msg.subject		= subject[0][0].decode(subject[0][1]) if subject[0][1] else decode_strings(subject[0][0], codecs)
#		except Exception, ex:
#			msg.subject = ""
			
	
#		try:
#			from_email = email.Header.decode_header(mail.get('From'))
#			msg.from_email	= from_email[0][0].decode(from_email[0][1]) if from_email[0][1] else decode_strings(from_email[0][0], codecs)
#		except Exception, ex:
#			msg.from_email = ""
			
	
#		try:
#			to_email = email.Header.decode_header(mail.get('To'))
#			msg.to_email	= to_email[0][0].decode(to_email[0][1]) if to_email[0][1] else decode_strings(to_email[0][0], codecs)
#		except Exception, ex:
#			msg.to_email = ""
			
#		if mail.get('Date'):
#			date = mail.get('Date')
#			msg.date = time.strftime("%d %b %Y",email.utils.parsedate(date))
#			msg.date_in_sec	= str(time.mktime(email.utils.parsedate(date)))
#		else:
#			msg.date = time.strftime("%d %b %Y")
#			msg.date_in_sec	= str(time.mktime(time.localtime()))
			
		#try:
		#	mail_type = email.Header.decode_header(mail.get('Content-Type'))
		#	if mail_type and "plain" in mail_type[0][0]:
		#		msg.mail_type = "plain"
		#	else:
		#		msg.mail_type = "html"
		#except Exception, ex:		
		#	msg.mail_type = "html"
			
#		if "X-Priority" in mail:
#			priority = re.search('\d', mail["X-Priority"])
#			if priority:
#				msg.priority = "high" if priority.group(0) == "1" else "normal"		
			
		return msg
	
	def parse_body(self,mail):
		body = ""
		#self.content_type = MailContentType("text/html","utf8",{})
		body_charset = "utf8"
		#TODO: check this code for multipart messages with different attachments
		if mail.is_multipart():
			for part in mail.walk():
				if part.get_content_maintype() == "multipart":
					boundary = ""
					double_data = "False"
		
					for p in range(len(part.get_payload())):
						if part.get_boundary() and boundary == part.get_boundary():
							double_data = "True"
						else:
							double_data = "False"
						boundary = part.get_boundary()
						for subpart in part.get_payload(p).walk():
							if ("content-disposition" in subpart and "attachment" in subpart["content-disposition"]):
								oAttach = subpart.get_payload()
								guid = str(uuid4())
		
								#application.storage.write(guid, base64.b64decode(oAttach))
		
								attachment_object = MailAttachment()
								attachment_object.guid = guid
								
								if "Content-Transfer-Encoding" in subpart and subpart["Content-Transfer-Encoding"].lower() == "quoted-printable":
									try:
										attachment_object.data = quopri.decodestring(oAttach)
									except Exception as ex:
										pass								
								else:
									try:
										attachment_object.data= base64.b64decode(oAttach)
									except Exception as ex:
										pass
															
								#attachment_object.data = base64.b64decode(oAttach)
		
								try:
									filename = email.Header.decode_header(subpart.get_filename())
									attachment_object.filename = filename[0][0].decode(filename[0][1]) if filename[0][1] else filename[0][0]
								except:
									attachment_object.filename = subpart.get_filename()
		
								attachment_object.mail_id = ""
								attachment_object.location = "inbox"
								
								self.attach.append(attachment_object)
							else:
								if double_data == "True":
									body = ""
								if "Content-Type" in subpart and "charset" in subpart["Content-Type"]:
									body_charset = subpart["Content-Type"].split('=')[1]
									self.content_charset = body_charset.strip('"')
									body_content_type = subpart["Content-Type"].split(';')[0]
									self.content_type = body_content_type
								if "Content-Transfer-Encoding" in subpart and subpart["Content-Transfer-Encoding"].lower() == "base64":
									try:
										body += base64.b64decode(subpart.get_payload())
									except Exception as ex:
										pass
								elif "Content-Transfer-Encoding" in subpart and subpart["Content-Transfer-Encoding"].lower() == "quoted-printable":
									try:
										body += quopri.decodestring(subpart.get_payload())
									except Exception as ex:
										pass
								else:
									if not isinstance(subpart.get_payload(), list):
										body += subpart.get_payload()
		
		else:
			if "Content-Type" in mail and "charset" in mail["Content-Type"]:
				body_charset = mail["Content-Type"].split('=')[1]
				self.content_charset = body_charset.strip('"')
				body_content_type = mail["Content-Type"].split(';')[0]
				self.content_type = body_content_type				
			if "Content-Transfer-Encoding" in mail and mail["Content-Transfer-Encoding"].lower() == "base64":
				try:
					body += base64.b64decode(mail.get_payload())
				except Exception as ex:
					pass
			elif "Content-Transfer-Encoding" in mail and mail["Content-Transfer-Encoding"].lower() == "quoted-printable":
				try:
					body += quopri.decodestring(mail.get_payload())
				except Exception as ex:
					pass
			else:
				if not isinstance(mail.get_payload(), list):
					body += mail.get_payload()
		self.body = decode_strings(body,[body_charset, 'utf8', 'cp1252'])

def decode_strings(text, codecs_list):
	if type( text ) == str:
		return text

	# if unknown encoding, try decode with latin1
	codecs = codecs_list + [ 'latin1' ]

	result = ''
	for codec in codecs:
		try:
			result = text.decode(codec, 'ignore')
			return result
		except:
			continue

	return result

