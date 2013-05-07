
import random
import logging

from FRPShared.model import *

def d(s, x=0):
	return random.randint(1, s) + x

class Killed(Exception): pass

class Fight(object):
	def __init__(self, p1, p2, status = None, players = []):
		self.p1, self.p2 = p1, p2
		self.status = status
		self.players = players

	def log(self, msg, *args):
		logging.info(msg, *args)
		if self.status:
			for p in self.players:
				self.status.send(p + " " + (msg % args))
		
	def fight(self, p1bonus={}, p2bonus={}):
		if self.p1.profile.i + p1bonus.get('i',0) <= self.p2.profile.i + p2bonus.get('i',0):
			a1, a2 = self.p1, self.p2
		else:
			a1, a2 = self.p2, self.p1
		self.log("%s attacks first (%d v. %d)", a1.name, a1.profile.i, a2.profile.i)

		try:
			while True:
				a1dmg = self.attack(a1, a2)
				a2dmg = self.attack(a2, a1)
				if a1dmg >= a2dmg:
					self.log("%s: wins the round", a1.name)
		except Killed,v:
			return v.args[1] # return winner

	def attack(self, atk, dfn):
		roll = d(100)
		self.log("%s: attack roll: %d", atk.name, roll)
		if roll > atk.profile.ws:
			self.log("%s: misses", atk.name)
			return

		dmg = d(6) + atk.profile.s - dfn.profile.t
		self.log("%s: damage roll: %d", atk.name, dmg)
		dfn.w -= dmg
		self.log("%s: wounds remain %d", dfn.name, dfn.w)
		if dfn.w <= 0:
			self.log("%s: dead.", dfn.name)
			raise Killed(dfn,atk)
		return dmg
	
	def hitloc(self, roll):
		key = (roll % 10) * 10 + ((roll%100) / 10)
		if roll == 100:
			return 'left_arm'
		if key <= 15:
			return 'head'
		if key <= 35:
			return 'right_arm'
		if key <= 55:
			return 'left_arm'
		if key <= 80:
			return 'body'
		if key <= 90:
			return 'right_leg'
		if key <= 99:
			return 'left_arm'


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	from user import User

	p1 = User("P1",Profile(4,25,25,3,3,5,20,1,20, 20,20,20,20,20))
	p2 = User("P2",Profile(4,25,25,3,3,5,20,1,20, 20,20,20,20,20))

	f = Fight(p1,p2)
	f.fight()
	 
