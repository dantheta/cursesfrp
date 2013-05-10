
import logging

from fight import Fight

class RequestProcessor(object):
	def __init__(self, server):
		self.places = server.places
		self.users = server.users
		self.event_pub = server.event_pub
		pass

	def process(self, req, replysock):
		verb = req.req[1:]
		logging.info("Received verb: %s", verb)
		if not hasattr(self, verb):
			logging.info("Unknown command: %s", verb)
			replysock.send(req + ' Unknown Command')
			return
		func = getattr(self, verb)
		logging.debug("Got function: %s", func)
		try:
			func(req, replysock)
		except Exception,v:
			logging.error("Error: %s", str(v))
			replysock.send(verb + ' ERR')
		
	def look(self, req, replysock):
		loc = self.places[req.location]
		reply = loc.describe(req.user)
		replysock.send("/look " + reply)
	
	def loot(self, req, replysock):
		loc = self.places[req.location]
		for dead in loc.dead:
			found = dead.search()
			if found is not None:
				replysock.send("/loot You found {0} {1}.".format(found[0], found[1]))
				break
		else:
			replysock.send("/loot You found nothing.")
				
	def search(self, req, replysock):
		loc = self.places[req.location]
		found = loc.search()
		if found is None:
			replysock.send("/search You found nothing.")
		else:
			replysock.send("/search You found {0} {1}.".format(found[0], found[1]))

	def attack(self, req, replysock):
		# assume we're attacking the first enemy
		loc = self.places[req.location]
		user = self.users[req.user]
		if len(loc.enemies) == 0:
			replysock.send('/attack No enemies to attack')
		else:
			enemy = loc.enemies[0]
			fight = Fight(user, enemy, self.event_pub, ['player-' + user.name])
			winner = fight.fight()
			if winner != enemy:
				loc.enemies.remove(enemy)
				loc.dead.append(enemy)
			replysock.send('/attack {0} wins'.format(winner.name))

		
