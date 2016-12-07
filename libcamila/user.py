#!/bin/python

class User(object):
    def __init__(self, nickname=None, password=None, realname=None, username=None):
        self.setNickname(nickname)
        self.setPassword(password)
        self.setRealname(realname)
        self.setUsername(username)

    def getNickname(self):
        return self.nickname

    def setNickname(self, nickname):
        self.nickname = nickname

    def getPassword(self):
        return self.password

    def setPassword(self, password):
        self.password = password

    def getRealname(self):
        return self.realname

    def setRealname(self, realname):
        self.realname = realname

    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username
