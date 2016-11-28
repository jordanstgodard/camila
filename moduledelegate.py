#!/bin/python

import importlib
import os

import modules

class ModuleDelegate(object):
	def __init__(self, dir_name="modules"):
		self.modules = []

		for module_file in os.listdir(os.path.dirname("{0}/".format(dir_name))):

			if module_file[-4:] != '.pyc' and '__init__' not in module_file[0:]:
				module_name = "{0}.{1}".format(dir_name, module_file[:-3])
				module = __import__(module_name)
				
				for part in module_name.split(".")[1:]:
					module_attr = getattr(module, part)
					for v in module_attr.__dict__.values():
						if "class" in str(v)[0:6]:
							instance = v()
							self.modules.append(instance)

	def getModules(self):
		return self.modules
