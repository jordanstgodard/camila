#!/bin/python

import user

class Channel(object):
    def __init__(self, channel_name="", modes={}, users=[]):
        self.setName(channel_name)
        self.setModes(modes)
        self.setUsers(users)

    def getName(self):
        return self.channel_name

    def setName(self, channel_name):
        self.channel_name = channel_name

    def getModes(self):
        return self.modes

    def setModes(self, modes):
        self.modes = modes

    def getUsers(self):
        return self.users

    def setUsers(self, users):
        self.users = users
