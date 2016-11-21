#!/bin/python

import hashlib
import random
import socket
import ssl
import string
import threading
import time
import irctargetedsocket

class IRCWorker(irctargetedsocket.IRCTargetedSocket):
	def __init__(self, server, port=6667, proxy=None, proxy_port=None, channels=[],
		     attack_names=[], ignore_names=[], trusted_names=[],
		     ipv6=False, ssl=False, vhost=None, nick=None, password=None):

		irctargetedsocket.IRCTargetedSocket.__init__(self, server, port, proxy,
							     proxy_port, channels, attack_names,
							     ignore_names, trusted_names, ipv6,
							     ssl, vhost, nick, password)

		self.setContext("camila")
		self.sendStatus(vars(self))

	def getParent(self):
		return self.parent

	def setParent(self, parent):
		self.parent = parent	

