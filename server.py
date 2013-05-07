
import sys
import zmq
import pickle
import random
import logging
import collections

from FRPClient.event import Event,Request

logging.basicConfig(
	level = logging.DEBUG,
	format="%(asctime)s\t%(process)d\t%(module)s:%(lineno)d\t%(message)s",
	datefmt="[%Y-%m-%d %H:%M:%S]",
)

ctx = zmq.Context()
sock = ctx.socket(zmq.PUB)
sock3 = ctx.socket(zmq.REP)

places = ['room','corridor','cavern','cave']
place_attr = ['light','dark','damp','dry']

place_desc = {}

location_users = collections.defaultdict(list)

def make_place_desc():
	return "You are in a {attr} {place}.".format(
				attr = random.sample(place_attr,1)[0],
				place = random.sample(places,1)[0],
				)

def process_request(req):
	if req.req == '/look':
		if req.location not in place_desc:
			place_desc[req.location] = make_place_desc()
		reply = place_desc[req.location]
		if len(location_users[req.location]) > 1:
			reply += "  There are {0} other people here: {1}".format(
				len(location_users[req.location]) - 1,
				','.join([ x for x in location_users[req.location] if x != req.user])
				)
		sock3.send("/look " + reply)
	else:
		sock3.send("Unknown request")

def process_event(evt):
	if evt.cmd == 'SAY':
		sock.send("{o.location} [{o.user}] {text}".format(o = evt, text = evt.kw['text']) )
		sock3.send("OK")
	elif evt.cmd == 'ENTER':
		logging.info("Got new location for %s: %s", evt.user, evt.location)
		try:
			if evt.kw.get('old_location'):
				location_users[evt.kw['old_location']].remove(evt.user)
		except ValueError: pass
		location_users[evt.location].append(evt.user)
		sock.send("{o.location} [{o.user}] arrives.".format(o=evt))
		sock3.send("OK")
	else:
		sock3.send("UNKNOWN")

if __name__ == '__main__':
	sock.bind('tcp://*:5555')
	sock3.bind('tcp://*:5557')

	poller = zmq.Poller()
	poller.register(sock3,zmq.POLLIN)
	poller.register(sys.stdin,zmq.POLLIN)

	while True:
		for (stream, evt) in poller.poll(None):
			if stream == 0:
				msg = raw_input()
				sock.send(msg)
			else:
				msg = stream.recv()
				evt = pickle.loads(msg)
				if isinstance(evt, Event):
					logging.info("Received event: %s; %s; %s", evt.cmd, evt.user, evt.location)
					process_event(evt)
				elif isinstance(evt, Request):
					req = pickle.loads(msg)
					logging.info("Received request: %s; %s; %s", req.req, req.user, req.location)
					process_request(req)
							
