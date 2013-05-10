
import logging

from user import User
from FRPShared.model import Response

class EventProcessor(object):
	def __init__(self, server):
		self.places = server.places
		self.users = server.users
		self.event_pub = server.event_pub

	def process(self, evt, replysock):
		cmd = evt.cmd.lower()
		if not hasattr(self, cmd):
			replysock.send('UNKNOWN')
			return
		func = getattr(self, cmd)
		func(evt, replysock)

	def say(self, evt, replysock):
		self.event_pub.send("{o.location} [{o.user}] {text}".format(o = evt, text = evt.opts['text']) )
		replysock.send("OK")

	def enter(self, evt, replysock):
		logging.info("Got new location for %s: %s", evt.user, evt.location)
		try:
			if evt.opts.get('old_location'):
				self.places[evt.opts['old_location']].users.discard(evt.user)
		except ValueError: pass
		self.places[evt.location].users.update([evt.user])
		self.event_pub.send("{o.location} [{o.user}] arrives.".format(o=evt))
		replysock.send("OK")

	def announce(self, evt, replysock):
		logging.info("Generating user record: %s", evt.user)
		self.users[evt.user] = User.generate(evt.user)
		replysock.send_pyobj(Response('ANNOUNCE',initial_location='location-1'))
