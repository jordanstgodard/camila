#!/bin/python

import Queue

class AttackModule(object):
	def __init__(self, data=None):
		self.setModuleName("attack")
		self.setData(data)
		self.setNode(None)
		self.setQueue(None)

	def start(self, queue):
		self.setQueue(queue)

	def stop(self):
		self.getQueue().task_done()

	def isRunning(self):
		return not self.getQueue().empty()

	def getQueue(self):
		return self.queue

	def setQueue(self, queue):
		self.queue = queue

	def getData(self):
		return self.data

	def setData(self, data):
		self.data = data

	def getModuleName(self):
		return self.module_name

	def setModuleName(self, module_name):
		self.module_name = module_name

	def getNode(self):
		return self.node

	def setNode(self, node):
		self.node = node
