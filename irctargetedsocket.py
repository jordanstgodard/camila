#!/bin/python

import hashlib
import random
import socket
import ssl
import string
import sys
import threading
import time

import ircsocket
import modules
import moduledelegate

class IRCTargetedSocket(ircsocket.IRCSocket, threading.Thread):
	'''
	IRCTargetedSocket is a threaded IRC socket with additional behavior keeping track of
	names to attack, ignore, and trust. When an object of this class is started, the run()
	interface method is automatically invoked and creates a connection to the server.
	Threaded objects of this class should avoid directly calling connect()

	Additionally, it contains an eventnotifier.EventNotifier object to publish messages
	to a event system for other subscribing objects.

	All attacking classes should inherit this functionality.
	'''

	def __init__(self, server, port=6667, proxy=None, proxy_port=None, channels=[],
		     attack_names=[], ignore_names=[], trusted_names=[],
		     ipv6=False, ssl=False, vhost=None, nick=None, password=None):
		
		ircsocket.IRCSocket.__init__(self, server, port, proxy, proxy_port,
					     channels, ipv6, ssl, vhost, nick, password)

		threading.Thread.__init__(self)

		self.setNodes([])
		
		self.setAttackNames(attack_names)
		self.setIgnoreNames(ignore_names)
		self.setTrustedNames(trusted_names)

		# Initial list of attack names passed in
		# attack_name_override flag is set to True
		# to allow strict attacking of only those nicks
		if self.getAttackNames() != []:
			self.setAttackNameOverride(True)
		else:
			self.setAttackNameOverride(False)

		self.setContext("irctargetedsocket")

		self.setNotifier(None)

		modDelegate = moduledelegate.ModuleDelegate()
		self.setModules(modDelegate.getModules())

		# Dictionary of Module -> Thread		
		self.setAttackQueue({})
	
	def run(self):
		self.connect()

	def event(self, line):
		super(IRCTargetedSocket, self).event(line)
	
		args = line.split()
		c = self.getCodes()

		if args[1] in c:
			s = c[args[1]]
			m = "{0} ({1}) received.".format(s, args[1]) 
	
			# Nicks replied back from channel join or /NAMES
			if s == "RPL_NAMREPLY":
				chan = args[4]
				names = line.split(chan + ' :')[1].split()
				
				for name in names:
					if name[:1] in '~!@%&+:':
						name = name[1:]

					if name != self.getNickname() and name not in self.getIgnoreNames() and name not in self.getAttackNames() and name not in self.getNodeNames():
						self.getAttackNames().append(name)

			# Nickname not found on server
			elif s in ("ERR_NOSUCHNICK", "ERR_WASNOSUCHNICK"):
				self.sendStatus(m)

				name = args[3]
				if name[:1] in '~!@%&+:':
					name = name[1:]

				self.getAttackNames().remove(name)

		elif args[1] == "PRIVMSG":
			target = args[0].split('!')[0][1:]
			message = "".join(str(s) + " " for s in args[3:]).split(':')[1].rstrip()

			if "#" == args[2][0]:
				pass
			else:
				self.processCommand(target, message)

	def inform(self, event, target, data):
		self.sendStatus("event={0}, target={1}, data={2} informed".format(event, target, data))
		'''
		exe = None
		for m in self.getModules():
			if event.lower() == m.getModuleName().lower():
				self.sendStatus("Module {0} invoked")
				exe = m
				break

		if exe != None:
			exe.run()
		'''

		if event == 0: #ADD_ATTACK_NAMES
			self.listAppend(data, self.getAttackNames())

		elif event == 1: #REMOVE_ATTACK_NAMES
			self.listRemove(data, self.getAttackNames())

		elif event == 2: #LIST_ATTACK_NAMES
			self.listNames(target, "attack_names", self.getAttackNames())

		elif event == 3: #ADD_IGNORE_NAMES
			self.listAppend(data, self.getIgnoreNames())

		elif event == 4: #REMOVE_IGNORE_NAMES
			self.listRemove(data, self.getIgnoreNames())

		elif event == 5: #LIST_IGNORE_NAMES
			self.listNames(target, "ignore_names", self.getIgnoreNames())

		elif event == 6: #ADD_TRUSTED_NAMES
			self.listAppend(data, self.getTrustedNames())

		elif event == 7: #REMOVE_TRUSTED_NAMES
			self.listRemove(data, self.getTrustedNames())

		elif event == 8: #LIST_TRUSTED_NAMES
			self.listNames(target, "trusted_names", self.getTrustedNames())

		elif event == 9: #ADD_ATTACK_CHANNELS
			self.listAppend(data, self.getChannels())
			
			for channel in data:
				self.join(channel)

		elif event == 10: #REMOVE_ATTACK_CHANNELS
			self.listRemove(data, self.getChannels())

			for channel in data:
				self.part(channel)

		elif event == 11: #LIST_ATTACK_CHANNELS
			self.listNames(target, "channels", self.getChannels())

		elif event == 13: #START_ATTACK
			attackData = {
				"node" : self,
				"target" : target,
				"data" : data
			}

			queue = self.getAttackQueue()
			for attack in queue.keys():
				if not attack.isRunning():
					attack.setData(attackData)
				
					queue[attack].start()

		elif event == 14: #STOP_ATTACK
			queue = self.getAttackQueue()
			for attack in queue.keys():
				self.sendStatus("STOPPING. attack={0}".format(attack))

				if attack.isRunning():
					attack.stop()

					queue[attack].kill_received = True

					# Create a new thread since threads are only started once
					t = threading.Thread(target=attack.start)
					t.setDaemon(True)
					queue[attack] = t

		elif event == 15: #ADD_ATTACK_QUEUE
			for d in data:
				for m in self.getModules():
					if m.getModuleName().lower() == d.lower():
						t = threading.Thread(target=m.start)
						t.setDaemon(True)
						self.getAttackQueue()[m] = t

		elif event == 16: #REMOVE_ATTACK_QUEUE
			for d in data:
				for m in self.getModules():
					if m.getModuleName().lower()  == d.lower():
						self.getAttackQueue()[m] = None

	def processCommand(self, target, message):
		pass

	def listAppend(self, values, l):
		for value in values:
			if value not in l:
				l.append(value)

	def listRemove(self, values, l):
		for value in values:
			if value in l:
				l.remove(value)

	def listNames(self, target, listname, names):
		t = time.strftime('[%I:%M:%S]')
		m = '{0} | [{1}@{2}] - {3}={4}'

		i = 0
		l = []
		for name in names:
			l.append(name)
			i = i + 1
		
			if i % 16 == 0:
				self.sendMessage(target, m.format(t, self.getNickname(), self.getContext(), listname, l))
				self.sendStatus(m.format(t, self.getNickname(), self.getContext(), listname, l))
				l[:] = []

		if l != []:
			self.sendMessage(target, m.format(t, self.getNickname(), self.getContext(), listname, l))
			self.sendStatus(m.format(t, self.getNickname(), self.getContext(), listname, l))

		if names == None or names == []:
			self.sendMessage(target, m.format(t, self.getNickname(), self.getContext(), listname, names))
			self.sendStatus(m.format(t, self.getNickname(), self.getContext(), listname, names))

	def getCommands(self):
		return self.commands

	def setCommands(self, commands):
		self.commands = commands

	def getAttackNameOverride(self):
		return self.attack_name_override

	def setAttackNameOverride(self, attack_name_override):
		self.attack_name_override = attack_name_override

	def getAttackNames(self):
		return self.attack_names

	def setAttackNames(self, attack_names):
		self.attack_names = attack_names

	def getAttackQueue(self):
		return self.attack_queue

	def setAttackQueue(self, attack_queue):
		self.attack_queue = attack_queue

	def getTrustedNames(self):
		return self.trusted_names

	def setTrustedNames(self, trusted_names):
		self.trusted_names = trusted_names

	def getIgnoreNames(self):
		return self.ignore_names

	def setIgnoreNames(self, ignore_names):
		self.ignore_names = ignore_names

	def getModules(self):
		return self.modules

	def setModules(self, modules):
		self.modules = modules

	def getNodes(self):
		return self.nodes

	def setNodes(self, nodes):
		self.nodes = nodes

	def getNodeNames(self):
		names = []
		for n in self.getNodes():
			names.append(n.getNickname())
		return names

	def getNotifier(self):
		return self.notifier

	def setNotifier(self, notifier):
		self.notifier = notifier
