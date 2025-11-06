
from builtins import str
from builtins import range
from builtins import object
import string, random, math, time, os
from hashlib import md5
from uuid import uuid1
import managers


class VDOM_id(object):
    """id generation class"""
    def hexstr(self, s):
        """convert byte array to hex string"""
        h = string.hexdigits
        r = ""
        for c in s:
            i = ord(c)
            r = r + h[(i >> 4) & 0xF] + h[i & 0xF]
        return r

    def new(self):
        """generate new id"""
        md5obj = md5(str(time.time() + random.random() + math.sin(random.random())))
        return self.hexstr(md5obj.digest())

    def random_string(self, length):
        """generate random string of the specified length"""
        h = string.hexdigits
        r = ""
        for i in range(length):
            a = random.randint(0, 255)
            r = r + h[a & 0xF]
        return r


def vdomid():
    """generate new id"""
    return md5((str(time.time()) + str(math.sin(random.random()))).encode() + _urandom() ).hexdigest()
    # return md5(b''.join([str(time.time()),_urandom(),str(math.sin(random.random()))])).hexdigest()
    # return md5("%s%s" %(uuid1().bytes, math.sin(random.random()))).hexdigest()

def hexstr(s):
    """convert byte array to hex string"""
    h = string.hexdigits
    r = ""
    for c in s:
        i = ord(c)
        r = r + h[(i >> 4) & 0xF] + h[i & 0xF]
    return r


def _urandom():
    if hasattr(os, 'urandom'):
        return os.urandom(30)
    return str(random()).encode('ascii')


def generate_key(salt=None):
    if salt is None:
        salt = repr(salt).encode('ascii')
    return sha1(b''.join([
        salt,
        str(time.time()).encode('ascii'),
        _urandom()
        ])).hexdigest()

def guid2mod(guid):
    """transform guid to module name"""
    return "module_" + "_".join(guid.split("-"))

#def id2res(owner_id, res_id, res_type):
#	"""transform owner id and resource id to resource name"""
#	return "res_" + owner_id + "_" + res_id + "." + res_type

def id2link(res_id):
    """transform resource id to resource URL"""
    return "/%s.res"%res_id

def id2link1(res_id):
    """transform resource id to resource URL"""
    o = managers.resource_manager.get_resource(None, res_id)
    if not o:
        return ""
    return "".join(["/", res_id, ".", o.res_format])

#def id2tempres(owner_id, tempres_id, res_type):
    #"""transform owner id and temporary resource id to temporary resource name"""
    #return "temp_" + owner_id + "_" + tempres_id + "." + res_type

def is_valid_identifier(value):
    if value == "": return False
    first = value[0]
    if not ('_' == first or first.isalpha()):
        return False
    last = value[1:]
    for i in last:
        if not ('_' == i or i.isalnum()):
            return False
    return True
