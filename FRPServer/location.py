
import random
import logging

places = ['room','corridor','cavern','cave']
place_attr = ['light','dark','damp','dry','dusty','dimly-lit']

from language import *

from user import Users,User

directions = {
	'N': 'north',
	'E': 'east',
	'W': 'west',
	'S': 'south',
	}

def make_place_desc():
	return "You are in a {attr} {place}.".format(
				attr = random.sample(place_attr,1)[0],
				place = random.sample(places,1)[0],
				)

class Locations(object):
	def __init__(self):
		self.data = {}
		self.seq = 1

	def fill(self, name):
		logging.debug("Creating location: %s", name)
		self.data[name] = Location.generate(name)

	def __getitem__(self, index):
		if index not in self.data:
			self.fill(index)
		return self.data[index]

	def __setitem__(self, index, value):
		self.data[index] = value

class Location(object):
	def __init__(self, loc, desc, exits = None):
		self.loc = loc
		self.desc = desc
		self.users = set()
		self.searched = False
		self.exits = exits or {'N','E','W','S'}
		self.enemies = []
		self.dead = []
		self.objects = []

	def search(self):
		if self.searched:
			return
		self.searched = True
		return (random.randint(0,6), 'Gold')

	@classmethod
	def generate(klass, name = None):
		loc = klass(name, make_place_desc(), 
			set(random.sample(['N','E','W','S'], random.randint(1,3)))
			)

		if random.randint(0,10) > 1:
			orc = User.generate(name + 'orc')
			loc.enemies.append(orc)
			Users.instance()[orc.name] = orc

		return loc
		
	def describe(self, user):
		reply = self.desc + "\n"
		if len(self.users) > 1:
			reply += "There are {0} other people here: {1}\n".format(
				len(self.users) - 1,
				nl_join([ x for x in self.users if x != user])
				)
		if len(self.exits) :
			reply += "There {0} to the {1}.\n".format(
				to_be_plural("exit", len(self.exits)>1),
				nl_join([directions[x] for x in self.exits])
				)
		if len(self.enemies):
			reply += "Enemies present: {0} {1}".format(
				len(self.enemies),
				pluralize(self.enemies[0].name) if len(self.enemies) > 1 else self.enemies[0].name
				)
		if len(self.dead):
			reply += "Dead enemies present: {0} {1}".format(
				len(self.dead),
				pluralize(self.dead[0].name) if len(self.dead) > 1 else self.dead[0].name
				)
		return reply
