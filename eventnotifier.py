#!/bin/python

class EventNotifier(object):

	def __init__(self):
		# subscriber -> events
		self.subscriberDict = {}

		self.eventCodes = {
			0 : "ADD_ATTACK_NAMES",
			1 : "REMOVE_ATTACK_NAMES",
			2 : "LIST_ATTACK_NAMES",
			3 : "ADD_IGNORE_NAMES",
			4 : "REMOVE_IGNORE_NAMES",
			5 : "LIST_IGNORE_NAMES",
			6 : "ADD_TRUSTED_NAMES", 
			7 : "REMOVE_TRUSTED_NAMES",
			8 : "LIST_TRUSTED_NAMES",
			9 : "ADD_ATTACK_CHANNELS",
			10 : "REMOVE_ATTACK_CHANNELS",
			11 : "LIST_ATTACK_CHANNELS",
			12 : "KILL_WORKERS",
			13 : "START_ATTACK",
			14 : "STOPATTACK"
		}


	def publish(self, event, target, data):
		# Iterate through each event for each subscriber
		subscribers = self.subscriberDict.keys()
		for s in subscribers:
			for e in self.subscriberDict[s]:
				if e == event:
					s.inform(event, target, data)
					break


	def subscribe(self, subscriber, events=None):
		# if nothing passed in, let's just subscribe to all events
		if events == None or events == []:
			events = self.eventCodes.keys()

		if subscriber not in self.subscriberDict.keys():
			self.subscriberDict[subscriber] = events
		else:
			for e in events:
				if e not in self.subscriberDict[subscriber]:
					self.subscriberDict[subscriber].append(e)


	def unsubscribe(self, subscriber):
		self.subscriberDict[subscriber] = None
			
