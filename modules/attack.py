#!/bin/python

class AttackModule(object):
	def __init__(self, data=None):
		self.setModuleName("attack")
		self.setData(data)
		self.setRunning(False)

	def start(self):
		self.setRunning(True)

	def stop(self):
		self.setRunning(False)

	def isRunning(self):
		return self.is_running

	def setRunning(self, is_running):
		self.is_running = is_running

	def getData(self):
		return self.data

	def setData(self, data):
		self.data = data

	def getModuleName(self):
		return self.module_name

	def setModuleName(self, module_name):
		self.module_name = module_name
