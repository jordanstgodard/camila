#!/bin/python

import hashlib
import random
import socket
import socks
import ssl
import string
import threading
import time

from libcamila import channel, server, user

class IRCSocket(object):
	'''
	IRCSocket is a generic IRC socket connection class that does provide
	compliant RFC 1459 / RFC 2812 event handling.

	All classes should inherit this class and override event-driven functionality
	specificically for it's own needs.

	RFC 1459 Constants
	https://tools.ietf.org/html/rfc1459#section-4.6

	RFC 2812 Constants
	https://tools.ietf.org/html/rfc2812
	'''

	codes = {
		"001" : "RPL_WELCOME",
		"002" : "RPL_YOURHOST",
		"003" : "RPL_CREATED",
		"004" : "RPL_MYINFO",
		"005" : "RPL_BOUNCE",
		"200" : "RPL_TRACELINK",
		"201" : "RPL_TRACECONNECTING",
		"202" : "RPL_TRACEHANDSHAKE",
		"203" : "RPL_TRACEUNKNOWN",
		"204" : "RPL_TRACEOPERATOR",
		"205" : "RPL_TRACEUSER",
		"206" : "RPL_TRACESERVER",
		"208" : "RPL_TRACENEWTYPE",
		"211" : "RPL_STATSLINKINFO",
		"212" : "RPL_STATSCOMMANDS",
		"213" : "RPL_STATSCLINE",
		"214" : "RPL_STATUSNLINE",
		"215" : "RPL_STATSILINE",
		"216" : "RPL_STATSKLINE",
		"218" : "RPL_STATSYLINE",
		"219" : "RPL_ENDOFSTATS",
		"221" : "RPL_UMODEIS",
		"241" : "RPL_STATSLLINE",
		"242" : "RPL_STATSUPTIME",
		"243" : "RPL_STATSOLINE",
		"244" : "RPL_STATSHLINE",
		"251" : "RPL_LUSERCLIENT",
		"252" : "RPL_LUSEROP",
		"253" : "RPL_LUSERUNKNOWN",
		"254" : "RPL_LUSERCHANNELS",
		"255" : "RPL_LUSERME",
		"256" : "RPL_ADMINME",
		"257" : "RPL_ADMINLOC1",
		"258" : "RPL_ADMINLOC2",
		"259" : "RPL_ADMINEMAIL",
		"261" : "RPL_TRACELOG",
		"300" : "RPL_NONE",
		"301" : "RPL_AWAY",
		"302" : "RPL_USERHOST",
		"303" : "RPL_ISON",
		"305" : "RPL_UNAWAY",
		"306" : "RPL_NOWAWAY",
		"311" : "RPL_WHOISUSER",
		"312" : "RPL_WHOISSERVER",
		"313" : "RPL_WHOISOPERATOR",
		"314" : "RPL_WHOWASUSER",
		"315" : "RPL_ENDOFWHO",
		"317" : "RPL_WHOISIDLE",
		"318" : "RPL_ENDOFWHOIS",
		"319" : "RPL_WHOISCHANNELS",
		"321" : "RPL_LISTSTART",
		"322" : "RPL_LIST",
		"323" : "RPL_LISTEND",
		"324" : "RPL_CHANNELMODEIS",
		"331" : "RPL_NOTOPIC",
		"332" : "RPL_TOPIC",
		"341" : "RPL_INVITING",
		"342" : "RPL_SUMMONING",
		"351" : "RPL_VERSION",
		"352" : "RPL_WHOREPLY",
		"353" : "RPL_NAMREPLY",
		"364" : "RPL_LINKS",
		"365" : "RPL_ENDOFLINKS",
		"366" : "RPL_ENDOFNAMES",
		"367" : "RPL_BANLIST",
		"368" : "RPL_ENDOFBANLIST",
		"369" : "RPL_ENDOFWHOWAS",
		"371" : "RPL_INFO",
		"372" : "RPL_MOTD",
		"374" : "RPL_ENDOFINFO",
		"375" : "RPL_MOTDSTART",
		"376" : "RPL_ENDOFMOTD",
		"381" : "RPL_YOUREOPER",
		"382" : "RPL_REHASHING",
		"391" : "RPL_TIME",
		"392" : "RPL_USERSSTART",
		"393" : "RPL_USERS",
		"394" : "RPL_ENDOFUSERS",
		"395" : "RPL_NOUSERS",
		"401" : "ERR_NOSUCHNICK",
		"402" : "ERR_NOSUCHSERVER",
		"403" : "ERR_NOSUCHCHANNEL",
		"404" : "ERR_CANNOTSENDTOCHAN",
		"405" : "ERR_TOOMANYCHANNELS",
		"406" : "ERR_WASNOSUCHNICK",
		"407" : "ERR_TOOMANYTARGETS",
		"409" : "ERR_NOORIGIN",
		"411" : "ERR_NORECIPIENT",
		"412" : "ERR_NOTEXTTOSEND",
		"413" : "ERR_NOTOPLEVEL",
		"414" : "ERR_WILDTOPLEVEL",
		"421" : "ERR_UNKNOWNCOMMAND",
		"422" : "ERR_NOMOTD",
		"423" : "ERR_NOADMININFO",
		"424" : "ERR_FILEERROR",
		"431" : "ERR_NONICKNAMEGIVEN",
		"432" : "ERR_ERRONEUSNICKNAME",
		"433" : "ERR_NICKNAMEINUSE",
		"436" : "ERR_NICKCOLLISION",
		"437" : "ERR_UNAVAILRESOURCE",
		"441" : "ERR_USERNOTINCHANNEL",
		"442" : "ERR_NOTONCHANNEL",
		"444" : "ERR_NOLOGIN",
		"445" : "ERR_SUMMONDISABLED",
		"446" : "ERR_USERDISABLED",
		"451" : "ERR_NOTREGISTERED",
		"461" : "ERR_NEEDMOREPARAMS",
		"462" : "ERR_ALREADYREGISTERED",
		"463" : "ERR_NOPERMFORHOST",
		"464" : "ERR_PASSWDMISMATCH",
		"465" : "ERR_YOUREBANNEDCREEP",
		"467" : "ERR_KEYSET",
		"471" : "ERR_CHANNELISFULL",
		"472" : "ERR_UNKNOWNMODE",
		"473" : "ERR_INVITEONLYCHAN",
		"474" : "ERR_BANNEDFROMCHAN",
		"475" : "ERR_BADCHANNELKEY",
		"481" : "ERR_NOPRIVILEGES",
		"482" : "ERR_CHANOPRIVSNEEDED",
		"483" : "ERR_CANTKILLSERVER",
		"491" : "ERR_NOOPERHOST",
		"501" : "ERR_UMODEUNKNOWNFLAG",
		"502" : "ERR_USERSDONTMATCH"
	}

	def __init__(self, server, user, channels=[]):
		'''
		Generic IRC Socket object
		'''

		# Server connection settings
		self.setServer(server)

		self.setSocket(None)

		self.setUser(user)
		u = self.getUser()
		nickname = u.getNickname() if u.getNickname() != None else self.getHash(4, 15)
		u.setNickname(nickname)
		u.setRealname(nickname)
		u.setUsername(nickname)

		channel_obj = []
		for c in channels:
			channel_obj.append(channel.Channel(c))
		self.setChannels(channel_obj)

		self.setConnected(False)
		self.setContext("ircsocket")

	def connect(self):
		'''
		Creates a socket connection and listener to the server.
		Attempts to reconnect if the connection is unsuccessful.
		'''

		s = self.getServer()
		u = self.getUser()
		try:
			self.createSocket()
			self.socket.connect((s.getAddress(), s.getPort()))

			self.raw('USER {0} 0 * :{1}'.format(u.getUsername(), u.getRealname()))
			self.nick(u.getNickname())
			if u.getPassword():
				self.raw('PASS {0}'.format(u.getPassword()))
		except socket.error as e:
			print 'Failed to connect to {0}:{1}. {2}'.format(s.getAddress(), s.getPort(), e)
			self.reconnect()
		else:
			self.connected = True
			self.listen()

	def ctcp(self, target, data):
		self.sendMessage(target, '\001{0}\001'.format(data))

	def event(self, line):
		s = self.getServer()
		u = self.getUser()

		args = line.split()

		if args[0] == 'PING':
			self.raw('PONG {0}'.format(args[1][1:]))

		# Exception and code handling
		c = self.getCodes()
		if args[1] in c:
			reply = c[args[1]]
			m = "{0} ({1}) received.".format(s, args[1])

			# Server connected
			if reply in ("RPL_WELCOME", "RPL_YOURHOST", "RPL_CREATED"):
				n = "Connected to {0}:{1}".format(s.getAddress(), s.getPort())
				if s.getProxy():
					n = "{0} using proxy {1}:{2}".format(n, s.getProxy(), s.getProxyPort())
				self.sendStatus("{0} {1}".format(m, n))

				for channel in self.getChannels():
					self.join(channel.getName())

			# Server unavailable exceptions
			elif reply in ("ERR_NOSUCHSERVER", "ERR_YOUREBANNEDCREEP",
				   "ERR_YOUWILLBEBANNED"):
				self.quit()

			# Channel unavailable exceptions
			elif reply in ("ERR_UNAVAILARESOURCE", "ERR_NOSUCHCHANNEL",
				   "ERR_CHANNELISFULL", "ERR_INVITEONLYCHAN",
				   "ERR_BANNEDFROMCHAN", "ERR_BADCHANNELKEY"):
				self.sendStatus(m)

				chan = args[3]
				for channel in self.getChannels():
					if channel.getName().lower() == chan.lower():
						n = "Removing {0} from channels list".format(chan)
						self.sendStatus(n)
						self.getChannels().remove(channel)

			# Nickname unavailable exceptions
			elif reply in ("ERR_NONICKNAMEGIVEN", "ERR_ERRONEUSNICKNAME",
				   "ERR_NICKNAMEINUSE", "ERR_NICKCOLLISION"):
				self.sendStatus(m)
				u.setNickname(self.getHash(4, 15))
				self.nick(u.getNickname())

			elif reply == "RPL_NAMREPLY":
				chan = args[4]
				names = line.split(chan + ' :')[1].split()

				for c in self.getChannels():
					if c.getName() == chan:
						for name in names:
							if name[:1] in '~!@%&+:':
								name = name.replace(name[0], "")
							if name not in c.getUsers():
								c.getUsers().append(user.User(name))

		# KICK auto join
		elif args[1] == "KICK":
			chan = args[2]
			self.join(chan)

		# INVITE auto join
		elif args[1] == "INVITE":
			inv_nick = args[2]
			chan = args[3]
			self.join(chan)

	def identify(self, nick, password):
		self.sendMessage('nickserv', 'identify {0} {1}'.format(nick, password))

	def invite(self, nick, channel):
		self.raw('INVITE {0} {1}'.format(nick, channel))

	def join(self, channel, key=None):
		if key:
			self.raw('JOIN {0} {1}'.format(channel, key))
		else:
			self.raw('JOIN ' + channel)

	def kick(self, nick, channel, message=None):
		if message:
			self.raw('KICK {0} {1} :{2}'.format(nick, channel, message))
		else:
			self.raw('KICK {0} {1}'.format(nick, channel))

	def listen(self):
		s = self.getServer()

		while self.connected:
			try:
				data = self.socket.recv(1024)
				lines = data.split('\r\n')

				for line in lines:
					if line != "":
						self.sendStatus(line)

					if line.startswith('ERROR :Closing Link:'):
						raise Exception('Connection to {0}:{1} closed'.format(s.getAddress(), s.getPort()))
					elif len(line.split()) >= 2:
						self.event(line)
			except Exception as e:
				print e
		self.quit()

	def mode(self, target, mode):
		self.raw('MODE {0} {1}'.format(target, mode))

	def names(self, channel):
		self.raw('NAMES {0}'.format(channel))

	def nick(self, nick):
		self.raw('NICK {0}'.format(nick))

	def notice(self, target, message):
		self.raw('NOTICE {0} :{1}'.format(target, message))

	def oper(self, nick, password):
		self.raw('OPER {0} {1}'.format(nick, password))

	def part(self, channel, message=None):
		if message:
			self.raw('PART {0} {1}'.format(channel, message))
		else:
			self.raw('PART {0}'.format(channel))

	def quit(self, message=None):
		if message:
			self.raw('QUIT :{0}'.format(message))
		else:
			self.raw('QUIT')

		self.setConnected(False)

	def raw(self, message):
		self.getSocket().send(bytes('{0}\r\n'.format(message)))

	def reconnect(self, delay=10):
		if self.socket != None:
			self.socket.close()
			time.sleep(delay)
			self.connect()

	def register(self, nick, email):
		self.sendMessage('nickserv', 'register {0} {1}'.format(nick, email))

	def sendMessage(self, target, message):
		self.raw('PRIVMSG {0} :{1}'.format(target, message))

	def topic(self, channel, message):
		self.raw('TOPIC {0} :{1}'.format(channel, message))

	def whois(self, target):
		self.raw('WHOIS {0}'.format(target))

	'''
	Getters and setters
	'''
	def getHash(self, min=1, max=32):
		if min <= 0: min = 1
		if max <= 0: max = 32

		charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890'
		l = random.randint(min, max)
		r = "".join(random.choice(charset) for i in range(10))
		h = hashlib.md5()
		h.update(r)

		return "{0}".format(h.hexdigest()[0:l])

	def getChannels(self):
		return self.channels

	def setChannels(self, channels):
		self.channels = channels

	def getCodes(self):
		return self.codes

	def isConnected(self):
		return self.connected

	def setConnected(self, connected):
		self.connected = connected

	def getContext(self):
		return self.context

	def setContext(self, context):
		self.context = context

	def getServer(self):
		return self.server

	def setServer(self, server):
		self.server = server

	def createSocket(self, conn_timeout=121):
		s = self.getServer()

		if s.isIPv6():
			self.setSocket(socks.socksocket(socket.AF_INET6, socket.SOCK_STREAM))
		else:
			self.setSocket(socks.socksocket(socket.AF_INET, socket.SOCK_STREAM))

		self.getSocket().setblocking(0)
		self.getSocket().settimeout(conn_timeout)

		if s.getVHost():
			self.getSocket().bind((s.getVHost(), 0))

		if s.getProxy():
			self.getSocket().setproxy(socks.PROXY_TYPE_SOCKS5, s.getProxy(), s.getProxyPort())

		if s.isSSL():
			self.setSocket(ssl.wrap_socket(self.getSocket()))

	def getSocket(self):
		return self.socket

	def setSocket(self, socket):
		self.socket = socket

	def sendStatus(self, message):
		t = time.strftime('[%I:%M:%S]')
		print '{0} | [{1}@{2}] - {3}'.format(t, self.getUser().getNickname(), self.getContext(), message)

	def getUser(self):
		return self.user

	def setUser(self, user):
		self.user = user
