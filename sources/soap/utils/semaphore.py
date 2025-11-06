
from builtins import object
from threading import BoundedSemaphore as sem
#import inspect

class VDOM_semaphore(object):

	def __init__(self, counter=1):
		self.__semaphore = sem(counter)

	def lock(self):
		#s = inspect.stack()
		#for frame in s[1:8]:
			#print( str(frame[3])+" "+str((frame[4] or [""])[0]).strip())
		ret = self.__semaphore.acquire()
		

	def unlock(self):
		self.__semaphore.release()	
