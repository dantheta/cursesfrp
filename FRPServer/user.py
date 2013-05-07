import random

from FRPShared.model import Profile

class Users(dict):
	INSTANCE = None

	@classmethod
	def instance(klass):
		if klass.INSTANCE is None:
			klass.INSTANCE = klass()
		return klass.INSTANCE
		

class User(object): 
	def __init__(self, name, profile):
		self.name = name
		self.profile = profile
		self.w = profile.w
		self.searched = False

	def search(self):
		if self.searched:
			return
		self.searched = True
		return (random.randint(0,6), 'Gold')

	@classmethod
	def generate(self, name):
		return User(name, Profile(4,25,25,3,3,5,20,1,20, 20,20,20,20,20)) 
