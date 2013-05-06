
import sys
import getopt
import logging

import FRPClient

logging.basicConfig(
	level = logging.DEBUG,
	filename="client.log",
	format="%(asctime)s\t%(process)d\t%(module)s:%(lineno)d\t%(message)s",
	datefmt="[%Y-%m-%d %H:%M:%S]",
	)

optlist, optargs = getopt.getopt(sys.argv[1:], 'u:')
opts = dict(optlist)

client = FRPClient.Client(user=opts.get('-u'))
client.run()

