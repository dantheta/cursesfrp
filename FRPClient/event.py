
import sys
import zmq
import pickle
import logging

from FRPShared.model import Serializable,Event,Request

class EventSource(object):
	def __init__(self, user):
		self.ctx = zmq.Context()
		self.subscriber = self.ctx.socket(zmq.SUB)
		self.subscriber.connect('tcp://localhost:5555')
		self.subscriber.setsockopt(zmq.SUBSCRIBE, 'player-' + user)
		self.req = self.ctx.socket(zmq.REQ)
		self.req.connect('tcp://localhost:5557')

		self.location = None
		self.setup_poller()

	def setup_poller(self):
		self.poller = zmq.Poller()
		self.poller.register(self.subscriber)
		self.poller.register(self.req, zmq.POLLIN)
		self.poller.register(sys.stdin,zmq.POLLIN)
	
	def set_location(self, loc):
		logging.info("Subscribing: %s", loc)
		if self.location is not None:
			self.subscriber.setsockopt(zmq.UNSUBSCRIBE, self.location)
		self.location = loc
		self.subscriber.setsockopt(zmq.SUBSCRIBE, self.location)

	def get_next(self):
		streams = self.poller.poll(0)
		# prioritize user input?
		self.has_input = False
		if len(streams):
			first = None
			logging.info("Poll response: %s", streams[0])
			for (stream, evtype) in streams:
				if stream == 0:
					logging.debug("User input waiting")
					self.has_input = True
				else:
					if first is None:
						first = stream
			if first is not None:
				return first.recv()
					
	def send(self, obj):
		assert isinstance(obj, Serializable)
		if isinstance(obj, Event):
			self.req.send_pyobj(obj)
		if isinstance(obj, Request):
			self.req.send_pyobj(obj)
		
	def recv(self):
		# receive message (usually response) from REQ
		logging.debug(self.req.recv())

	def recv_obj(self):
		# temporary recv() variant, until all responses have been migrated 
		# to Response objects
		obj = self.req.recv_pyobj()
		logging.debug("Received response: %s", obj.rsp)
		return obj
