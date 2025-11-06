
# import sys
from builtins import range
from builtins import object
import os
import shutil
import re
import types

from utils.exception import *

# check if path exists
# read file
# write file
# rm file
# create dir
# rm dir
# list dir
# rename
# search file
# copy file
# copy dir
# check if path is directory
# get file size
# get file/dir creation time (doesn't work under Win32)
# get file/dir last modification time


class VDOM_share(object):
    """interface to shared files"""

    def __init__(self):
        self.__path = VDOM_CONFIG["SHARE-DIRECTORY"]

    def exists(self, name):
        """checks if path exists"""
        return os.path.exists(os.path.join(self.__path, name))

    def read(self, name, size=-1, binary=True):
        """read file, return None on error"""
        mode = "rb"
        if not binary:
            mode = "rt"
        f = None
        try:
            f = open(os.path.join(self.__path, name), mode)
            data = f.read(size)
            f.close()
            return data
        except:
            if f:
                f.close()
            return None

    def get_handler(self, name, size=-1, binary=True):
        """read file, return None on error"""
        mode = "rb"
        if not binary:
            mode = "rt"
        f = None
        try:
            f = open(os.path.join(self.__path, name), mode)
            return f
        except:
            if f:
                f.close()
            return None

    def write(self, name, data, binary=True, append=False):
        """write file, return True on success and False on error"""
        mode = "w"
        if append:
            mode = "a"
        if binary:
            mode += "b"
        else:
            mode += "t"
        f = None
        try:
            f = open(os.path.join(self.__path, name), mode)
            if type(data) == types.FileType or hasattr(data, "read"):
                shutil.copyfileobj(data, f)
            else:
                f.write(data)
            f.close()
            return True
        except:
            if f:
                f.close()
            return False
    def from_tempfile(self, name, tempfile_obj):
        try:
            shutil.copy(tempfile_obj.name, os.path.join(self.__path, name))
            return True
        except:
            return False
    def mkdir(self, name):
        """create directory, can create intermediate directories, return True on success and False on error"""
        try:
            os.makedirs(os.path.join(self.__path, name))
            return True
        except:
            return False

    def rmdir(self, name):
        """remove directory with it's content recursively, return True on success and False on error"""
        try:
            shutil.rmtree(os.path.join(self.__path, name))
            return True
        except:
            return False

    def rmfile(self, name):
        """remove file, return True on success and False on error"""
        try:
            os.remove(os.path.join(self.__path, name))
            return True
        except:
            return False

    def listdir(self, name="", sort=True):
        """list directory, return None on error"""
        try:
            x = os.listdir(os.path.join(self.__path, name))
            if not sort:
                return x
            x1 = []
            x2 = []
            for item in x:
                if self.isdir(os.path.join(name, item)):
                    x1.append(item)
                else:
                    x2.append(item)
            return x1 + x2
        except:
            return None

    def rename(self, oldname, newname):
        """rename file or directory, return True on success and False on error"""
        try:
            os.rename(os.path.join(self.__path, oldname), os.path.join(self.__path, newname))
            return True
        except:
            return False

    def search(self, regexp="", start_dir="", recursive=False):
        """search files, return list of paths, on error return None"""
        r = None
        try:
            r = os.walk(os.path.join(self.__path, start_dir))
        except:
            return None
        if not recursive:
            for item in r:
                (l1, l2) = self.__filter(item[2], regexp)
                return l1
            return None
        else:
            l1 = []
            l2 = []
            n = len(os.path.join(self.__path, start_dir)) + 1
            for item in r:
                for fname in item[2]:
                    l1.append(fname)
                    x = os.path.join(item[0], fname)
                    l2.append(x[n - 1:])
            (l1, l2) = self.__filter(l1, regexp, l2)
            return l2

    def __filter(self, l1, regexp, l2=None):
        o1 = []
        o2 = []
        rexp = re.compile(regexp, re.IGNORECASE)
        for idx in range(len(l1)):
            if rexp.match(l1[idx]):
                o1.append(l1[idx])
                if l2:
                    o2.append(l2[idx])
        return (o1, o2)

    def copyfile(self, source, dest):
        """copy file, return True on success and False on error"""
        try:
            shutil.copy(os.path.join(self.__path, source), os.path.join(self.__path, dest))
            return True
        except:
            return False

    def copydir(self, source, dest):
        """copy directory, return True on success and False on error"""
        try:
            shutil.copytree(os.path.join(self.__path, source), os.path.join(self.__path, dest))
            return True
        except:
            return False

    def isdir(self, path=""):
        """check if path is a directory, return None on error"""
        try:
            return os.path.isdir(os.path.join(self.__path, path))
        except:
            return None

    def size(self, path=""):
        """get file size, return None on error"""
        try:
            k = os.stat(os.path.join(self.__path, path))
            return k.st_size
        except:
            return None

    def ctime(self, path=""):
        """get file/dir creation time, return None on error"""
        try:
            k = os.stat(os.path.join(self.__path, path))
            return k.st_birthtime  # not available under Win32
        except:
            return None

    def mtime(self, path=""):
        """get file/dir last modification time, return None on error"""
        try:
            k = os.stat(os.path.join(self.__path, path))
            return k.st_mtime
        except:
            return None
