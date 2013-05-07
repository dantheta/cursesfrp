
import sys
import zmq
import logging
import pickle

class Serializable(object):
	def dump(self):
		return pickle.dumps(self)
	

class Event(Serializable):
	def __init__(self, cmd, user, location, **kw):
		self.cmd = cmd
		self.user = user
		self.location = location
		self.kw = kw

class Request(Serializable):
	def __init__(self, req, user, location, *opts):
		self.req = req
		self.user = user
		self.location = location
		self.opts = opts
		
class Response(Serializable):
	def __init__(self, rsp, *opts):
		self.rsp = rsp
		self.opts = opts
		

class EventSource(object):
	def __init__(self):
		self.ctx = zmq.Context()
		self.subscriber = self.ctx.socket(zmq.SUB)
		self.subscriber.connect('tcp://localhost:5555')
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

	def poll(self, timeout=250):
		streams = self.poller.poll(timeout)
		if len(streams):
			return True
		return False

	def get_next(self):
		streams = self.poller.poll(0)
		# prioritize user input?
		self.has_input = False
		if len(streams):
			first = None
			logging.info("Poll response: %s", streams[0])
			for (stream, evtype) in streams:
				if isinstance(stream, int):
					logging.debug("User input waiting")
					self.has_input = True
				else:
					first = stream
			if first is not None:
				return first.recv()
					
	def send(self, obj):
		assert isinstance(obj, Serializable)
		if isinstance(obj, Event):
			self.req.send(obj.dump())
		if isinstance(obj, Request):
			self.req.send(obj.dump())
		

