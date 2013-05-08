
import sys
import zmq
import pickle
import random
import logging
import collections

from FRPShared.model import Event,Request,Profile

from FRPServer.location import Locations
from FRPServer.user import Users,User
from FRPServer.request import RequestProcessor
from FRPServer.event import EventProcessor

logging.basicConfig(
	level = logging.DEBUG,
	format="%(asctime)s\t%(process)d\t%(module)s:%(lineno)d\t%(message)s",
	datefmt="[%Y-%m-%d %H:%M:%S]",
)

ctx = zmq.Context()

class Server(object):
	def __init__(self):
		self.event_pub = ctx.socket(zmq.PUB)
		self.request_sock = ctx.socket(zmq.REP)

		self.places = Locations()
		self.users = Users.instance()

		self.request_processor = RequestProcessor(self)
		self.event_processor = EventProcessor(self)

	def run(self):

		self.event_pub.bind('tcp://*:5555')
		self.request_sock.bind('tcp://*:5557')

		poller = zmq.Poller()
		poller.register(self.request_sock,zmq.POLLIN)
		poller.register(sys.stdin,zmq.POLLIN)

		while True:
			for (stream, evt) in poller.poll(None):
				if stream == 0:
					msg = raw_input()
					self.event_pub.send(msg)
				else:
					obj = stream.recv_pyobj()
					logging.info("Received object: %s", repr(obj))
					if isinstance(obj, Event):
						logging.info("Received event: %s; %s; %s", obj.cmd, obj.user, obj.location)
						self.event_processor.process(obj, stream)
					elif isinstance(obj, Request):
						logging.info("Received request: %s; %s; %s", obj.req, obj.user, obj.location)
						self.request_processor.process(obj, stream)
							
if __name__ == '__main__':
	server = Server()
	server.run()
