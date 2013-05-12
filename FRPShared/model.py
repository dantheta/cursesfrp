
import pickle
import collections

# various data model classes, shared between client & server

class Serializable(object):
	pass
	

Profile = collections.namedtuple("Profile",
	"m ws bs s t w i a dex   ld int cl wp fel")

class Event(Serializable):
	def __init__(self, cmd, user, location, **kw):
		self.cmd = cmd
		self.user = user
		self.location = location
		self.opts = kw

class Request(Serializable):
	def __init__(self, req, user, location, *opts):
		self.req = req
		self.user = user
		self.location = location
		self.opts = opts
		
class Response(Serializable):
	def __init__(self, rsp, **kw):
		self.rsp = rsp
		self.opts = kw
		
