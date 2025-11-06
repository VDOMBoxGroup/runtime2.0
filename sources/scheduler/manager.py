from __future__ import absolute_import
from builtins import str
from builtins import object
import managers
from uuid import uuid4
from . import task

class VDOM_scheduler_manager(object):

	def __init__(self):
		self.__task_list = {}

	def restore(self):
		self.__task_list = managers.storage.read_object(VDOM_CONFIG["SCHEDULER-MANAGER-INDEX-STORAGE-RECORD"])

	def fetch(self, task_object):
		concrete_task_list = {}
		for key in self.__task_list:
			if self.__task_list[key][0] is task_object:
				concrete_task_list[key] = self.__task_list[key]

		if concrete_task_list:
			return concrete_task_list
		else:
			return None

	def add_task(self, task_object, interval):
		task_id = str(uuid4())
		self.__task_list[task_id] = (task_object, interval)
		managers.storage.write_object_async(VDOM_CONFIG["SCHEDULER-MANAGER-INDEX-STORAGE-RECORD"],self.__task_list)
		crontab = []
		for key in self.__task_list:
			crontab.append((key, self.__task_list[key][1]))
		self.__built_crontab(crontab)
		return task_id

	def update (self, task_id, task, interval):
		if task_id in self.__task_list:
			self.__task_list[task_id] = (task, interval)
			managers.storage.write_object_async(VDOM_CONFIG["SCHEDULER-MANAGER-INDEX-STORAGE-RECORD"],self.__task_list)	    
			crontab = []
			for key in self.__task_list:
				crontab.append((key, self.__task_list[key][1]))
			self.__built_crontab(crontab)
			return task_id
		else:
			pass

	def dell_task(self, task_id):
		remove_list = []
		for key in self.__task_list:
			if task_id == key:
				remove_list.append(key)

				is_dirty_index = False
				for key in remove_list:
					self.__task_list.pop(key)
					is_dirty_index = True

				if is_dirty_index:
					managers.storage.write_object_async(VDOM_CONFIG["SCHEDULER-MANAGER-INDEX-STORAGE-RECORD"],self.__task_list)
		crontab = []
		for key in self.__task_list:
			crontab.append((key, self.__task_list[key][1]))
		self.__built_crontab(crontab)	

	def on_signal(self, task_id):
		if task_id in self.__task_list:
			task = self.__task_list[task_id][0]
			task.run()
		else:
			pass

	def __built_crontab(self, tasks):
		"""parameters is a list of tuples (task_id, interval)"""
		pass