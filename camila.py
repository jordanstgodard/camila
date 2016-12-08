#!/bin/python

import argparse
import random
import threading
import time
import ircnode
import eventnotifier

from libcamila import channel, server, user

'''
******************************************************************************************
*       ######       #            #         #       #########  #               #         *
*      #            # #          # #       # #          #      #              # #        *
*     #            #   #        #   #     #   #         #      #             #   #       *
*     #           #######      #     #   #     #        #      #            #######      *
*      #         #       #    #       # #       #       #      #           #       #     *
*       ######  #         #  #         #         #  #########  #########  #         #    *
******************************************************************************************
'''

debug = True

def camila(message):
	print '[camila] # {0}'.format(message)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--attack-names', type=str, nargs='+', help="name list to attack. Overrides retrieving names!")
	parser.add_argument('-c', '--attack-channels', type=str, nargs='+', help="channels to attack")
	parser.add_argument('-i', '--ignore-names', type=str, nargs='+', help="name list to ignore attacking")
	parser.add_argument('-p', '--proxies', type=str, nargs='+', help="proxy list")
	parser.add_argument('-s', '--server', type=str, help="IRC server to connect to as SERVER:PORT")
	parser.add_argument('-t', '--threads', type=int, help="number of threads (defaults to 1)")
	parser.add_argument('-T', '--trusted-names', type=str, nargs='+', help="Names to trust to send commands")
	parser.add_argument('-v', '--vhost', type=str, help="custom vhost")
	parser.add_argument('--ipv6', help="use IPv6 (defaults to false)")
	parser.add_argument('--password', help="nickserv password")
	parser.add_argument('--ssl', help="use SSL (defaults to false)")

	args = parser.parse_args()

	if args.attack_channels == None:
		args.attack_channels = []

	if args.attack_names == None:
		args.attack_names = []

	if args.ignore_names == None:
		args.ignore_names = []

	if args.proxies == None:
		args.proxies = []

	if args.ipv6 == None:
		args.ipv6 = False

	if args.ssl == None:
		args.ssl = False

	if args.threads == None:
		args.threads = 1


	args.port = int(args.server.split(':')[-1])
	args.server = args.server.split(':')[0]

	threads = []

	proxy = None
	proxy_port = None

	if args.proxies != []:
		choice = random.choice(args.proxies)
		proxy = choice.split(':')[0]
		proxy_port = int(choice.split(':')[-1])

	s = server.Server(args.server, args.port, proxy, proxy_port,
					  args.ipv6, args.ssl, args.vhost)
	u = user.User("camila")

	master = ircnode.IRCNode(s, u, args.threads, args.attack_channels,
							 args.attack_names, args.ignore_names,
							 args.trusted_names)
	args.ignore_names.append(master.getUser().getNickname())
	notifier = master.getNotifier()

	threads.append(master)

	for i in range(args.threads):
		if args.proxies != []:
			choice = random.choice(args.proxies)
			proxy = choice.split(':')[0]
			proxy_port = int(choice.split(':')[-1])

			s.setProxy(proxy)
			s.setProxyPort(proxy_port)

		w = ircnode.IRCNode(s, user.User(), args.threads, args.attack_channels,
							args.attack_names, args.ignore_names, args.trusted_names)
		threads.append(w)
		args.ignore_names.append(w.getUser().getNickname())
	try:

		for t in threads:
			t.setNodes(threads)
			t.setIgnoreNames(args.ignore_names)

			t.setNotifier(notifier)
			t.getNotifier().subscribe(t)

			t.setDaemon(True)
			t.start()

		while threading.active_count() > args.threads:
			time.sleep(1)
		pass
	except KeyboardInterrupt:
		master.quit()

		for t in threads:
			t.kill_received = True

if __name__ == "__main__":
	main()
