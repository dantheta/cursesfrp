
import sys
import zmq
import pickle
import random
import logging
import collections

from FRPShared.model import Event,Request,Profile
from FRPServer.fight import Fight
from FRPServer.location import Locations
from FRPServer.user import Users,User

logging.basicConfig(
	level = logging.DEBUG,
	format="%(asctime)s\t%(process)d\t%(module)s:%(lineno)d\t%(message)s",
	datefmt="[%Y-%m-%d %H:%M:%S]",
)

ctx = zmq.Context()
sock = ctx.socket(zmq.PUB)
sock3 = ctx.socket(zmq.REP)

places = Locations()
users = Users.instance()

def process_request(req):
	if req.req == '/look':
		loc = places[req.location]
		reply = loc.describe(req.user)
		sock3.send("/look " + reply)
	elif req.req == '/loot':
		loc = places[req.location]
		for dead in loc.dead:
			found = dead.search()
			if found is not None:
				sock3.send("/loot You found {0} {1}.".format(found[0], found[1]))
				break
		else:
			sock3.send("/loot You found nothing.")
				
	elif req.req == '/search':
		loc = places[req.location]
		found = loc.search()
		if found is None:
			sock3.send("/search You found nothing.")
		else:
			sock3.send("/search You found {0} {1}.".format(found[0], found[1]))
	elif req.req == '/attack':
		# assume we're attacking the first enemy
		loc = places[req.location]
		user = users[req.user]
		if len(loc.enemies) == 0:
			sock3.send('/attack No enemies to attack')
		else:
			enemy = loc.enemies[0]
			fight = Fight(user, enemy, sock, ['player-' + user.name])
			winner = fight.fight()
			if winner != enemy:
				loc.enemies.remove(enemy)
				loc.dead.append(enemy)
			sock3.send('/attack {0} wins'.format(winner.name))
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
				places[evt.kw['old_location']].users.discard(evt.user)
		except ValueError: pass
		places[evt.location].users.update([evt.user])
		sock.send("{o.location} [{o.user}] arrives.".format(o=evt))
		sock3.send("OK")
	elif evt.cmd == "ANNOUNCE":
		logging.info("Generating user record: %s", evt.user)
		users[evt.user] = User.generate(evt.user)
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
							
