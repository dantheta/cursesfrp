
import pickle
import collections

class Serializable(object):
	pass
	

Profile = collections.namedtuple("Profile",
	"m ws bs s t w i a dex   ld int cl wp fel")

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
		
