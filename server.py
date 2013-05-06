
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
sock2 = ctx.socket(zmq.PULL)
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
		sock3.send("/look " + place_desc[req.location])
	else:
		sock3.send("Unknown request")

def process_event(evt):
	if evt.cmd == 'SAY':
		sock.send("{o.location} [{o.user}] {text}".format(o = evt, text = evt.kw['text']) )
	if evt.cmd == 'ENTER':
		logging.info("Got new location for %s: %s", evt.user, evt.location)
		try:
			location_users[evt.kw['old_location']].remove(evt.user)
		except ValueError: pass
		location_users[evt.location].append(evt.user)

if __name__ == '__main__':
	sock.bind('tcp://*:5555')
	sock2.bind('tcp://*:5556')
	sock3.bind('tcp://*:5557')

	poller = zmq.Poller()
	poller.register(sock2,zmq.POLLIN)
	poller.register(sock3,zmq.POLLIN)
	poller.register(sys.stdin,zmq.POLLIN)

	while True:
		for (stream, evt) in poller.poll(None):
			if stream == 0:
				msg = raw_input()
				sock.send(msg)
			else:
				msg = stream.recv()
				if stream == sock2:
					evt = pickle.loads(msg)
					logging.info("Received event: %s; %s; %s", evt.cmd, evt.user, evt.location)
					process_event(evt)

				if stream == sock3:
					req = pickle.loads(msg)
					logging.info("Received request: %s; %s; %s", req.req, req.user, req.location)
					process_request(req)
							
