"""
NAME: VDOM.utils.mutex<br>
DESCRIPTION: This class implements mutex object for VDOM<br>
DATE: 2005/02/17<br>
AUTHOR: SE Group<br>
VERSION: 0.001<br>
"""

#-------------------------------------------------------------------
# VDOM_mutext allows to realize binary semaphore
#

#from threading import RLock
#from threading import Lock

from builtins import object
from threading import Semaphore

from utils.exception import VDOM_exception

class VDOM_mutex(object):
	""" This class should be used to lock objects """

	def __init__(self):
		""" Constructor """
		self.__mutex = Semaphore(1)
#	self.__mutex = RLock();
#	self.__counter = 0
#	self.__trylock = Lock();

	def lock(self):
		""" Lock object """
		self.__mutex.acquire()
#	self.__counter = self.__counter + 1
#	return self.__counter

	def unlock(self):
		""" Unlock object """
#	self.__trylock.acquire()

#	cntr = self.__counter
#	if cntr:
#	    self.__mutex.release()	
#	    self.__counter = self.__counter - 1
#	    cntr = self.__counter

		self.__mutex.release()

#	return self.__counter


class VDOM_named_mutex_manager(object):
	"""manager of the named mutexes"""

	def __init__(self):
		"""instance creation"""
		self.__map = {}
		self.__count = {}
		self.__mutex = VDOM_mutex()

	def lock(self, name):
		"""lock mutex with specified name"""
		self.__mutex.lock()
		#print("lock*****#####\n%s\n*****#####\n"%str(name))
		if name not in self.__map:
			self.__map[name] = VDOM_mutex()
			self.__count[name] = 1
		else:
			self.__count[name] += 1
		self.__mutex.unlock()
		self.__map[name].lock()

	def unlock(self, name):
		"""unlock mutex with specified name"""
		self.__mutex.lock()
		#print("unlock*****#####\n%s\n*****#####\n"%str(name))
		if name in self.__map:
			self.__map[name].unlock()
			if self.__count[name] > 1:
				self.__count[name] -= 1
			else:
				del(self.__map[name])
				del(self.__count[name])
		self.__mutex.unlock()

	def count(self, name):
		"""get name count"""
		if name in self.__count:
			return self.__count[name]
		return 0


mutex_manager = VDOM_named_mutex_manager()
del VDOM_named_mutex_manager


class VDOM_named_mutex(object):
	"""mutex with name"""

	def __init__(self, name):
		"""constructor"""
		self.__name = name

	def lock(self):
		"""lock mutex"""
		mutex_manager.lock(self.__name)

	def unlock(self):
		"""unlock mutex"""
		mutex_manager.unlock(self.__name)


class VDOM_named_mutex_auto(VDOM_named_mutex):
	"""mutex with name that is locked on creation and unlocked in destructor"""

	def __init__(self, name):
		"""constructor"""
		VDOM_named_mutex.__init__(self, name)
		VDOM_named_mutex.lock(self)

	def __del__(self):
		"""destructor"""
		VDOM_named_mutex.unlock(self)
