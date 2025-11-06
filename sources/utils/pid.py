""" VDOM_server_pid is used to write pid file for server to stop it later """

from builtins import object
import os

class VDOM_server_pid(object):
	"""server pid class"""

	def __init__(self, pidfile, write=True, remove=False):
		"""constructor, read or write pid from/to pidfile"""
		self.__pidfile = pidfile
		self.__remove = remove
		self.__pid = os.getpid()
		try:
			if write:
				file = open(self.__pidfile, "w")
				file.write("%s" % self.__pid)
			else:
				file = open(self.__pidfile, "r")
				self.__pid = int(file.read())
			file.close()
		except: pass

	def getpid(self):
		"""return stored pid"""
		return self.__pid

	def __del__(self):
		"""destructor, remove pidfile if requested"""
		if self.__remove:
			try: os.remove(self.__pidfile)
			except: pass
