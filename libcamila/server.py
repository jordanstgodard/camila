#!/bin/python

class Server(object):
    def __init__(self, address, port=6667, proxy=None, proxy_port=None,
                 ipv6=False, ssl=False, vhost=None):
        self.setAddress(address)
        self.setPort(port)
        self.setProxy(proxy)
        self.setProxyPort(proxy_port)
        self.setIPv6(ipv6)
        self.setSSL(ssl)
        self.setVHost(vhost)

    def getAddress(self):
        return self.server_address

    def setAddress(self, server_address):
        self.server_address = server_address

    def isIPv6(self):
        return self.ipv6

    def setIPv6(self, ipv6):
        self.ipv6 = ipv6

    def getPort(self):
        return self.port

    def setPort(self, port):
        self.port = port

    def getProxy(self):
        return self.proxy

    def setProxy(self, proxy):
        self.proxy = proxy

    def getProxyPort(self):
        return self.proxy_port

    def setProxyPort(self, proxy_port):
        self.proxy_port = proxy_port

    def isSSL(self):
        return self.ssl

    def setSSL(self, ssl):
        self.ssl = ssl

    def getVHost(self):
        return self.vhost

    def setVHost(self, vhost):
        self.vhost = vhost
