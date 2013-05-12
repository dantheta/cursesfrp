
import curses
import itertools
import collections

from dialog import Dialog

Location = collections.namedtuple("Location", "pos size exits")

locations = {
	1: Location((2,2), (1,1), [('E',2),('S',3),('W',4)]),
	2: Location((6,2), (3,4), [('W',1)]),
	3: Location((2,6), (4,1), [('N',1)]),
	4: Location((0,2), (1,1), [('E',1)]),
	}

class Grid(object):
	SCALE = 2
	TR = u"\u2510"
	TL = u"\u250c"
	BL = u"\u2514"
	BR = u"\u2518"
	H = u"\u2500"
	V = u"\u2502"
	CHARS = [ TL, BL, TR, BR ]

	def __init__(self, size):
		self.grid = []
		self.size = size
		for x in range(size):
			self.grid.append( [' '] * size)

	def scale(self, x):
		return x * self.SCALE

	def add_room(self, room):
		loc = room.pos
		size = room.size
		scale = self.scale

		#for x in range((loc[0])*self.SCALE, (loc[0]+sz[0])*self.SCALE):	
		#	for y in range((loc[1])*self.SCALE, (loc[1]+sz[1])*self.SCALE):	
		#		self.grid[y][x] = u"\u2588"

		for ch, (x, y) in zip(self.CHARS, itertools.product(
			(scale(loc[0]), scale(loc[0]+size[0])-1),
			(scale(loc[1]), scale(loc[1]+size[1])-1),
			)):
			self.grid[y][x] = ch

		for x in range(scale(loc[0])+1, scale(loc[0]+size[0])-1):
			for y in scale(loc[1]), scale(loc[1]+size[1])-1:
				self.grid[y][x] = self.H
		for y in range(scale(loc[1])+1, scale(loc[1]+size[1])-1):
			for x in scale(loc[0]), scale(loc[0]+size[0])-1:
				self.grid[y][x] = self.V
			



	def add_exit(self, _from, _dir, _to):
		if _dir == 'E':
			y = ((_from.size[1]/2) + _from.pos[1]) * self.SCALE
			for x in range((_from.pos[0]+_from.size[0])*self.SCALE, _to.pos[0] * self.SCALE):
				self.grid[y][x] = u"\u23E4"
		if _dir == 'S':
			x =  ((_from.size[0]/2) + _from.pos[0]) * self.SCALE
			for y in range((_from.pos[1]+_from.size[1])*self.SCALE, _to.pos[1] * self.SCALE):
				self.grid[y][x] = u"\u007C"
		
	def draw_ascii(self):
		for line in self.grid:
			print ''.join(line)

class MapDialog(Dialog):
	SCALE = 2


	def __init__(self, *args):
		Dialog.__init__(self, *args)
		self.locations = locations
		self.setup()

	def setup(self):
		self.win = self.parent.subwin(self.height, self.width, self.top, self.left)
		self.panel = curses.panel.new_panel(self.win)
		self.save_background()
		curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)
		self.win.bkgd(' ', curses.color_pair(3))
		self.setup_chars()

	def setup_chars(self):
		self.H = curses.ACS_HLINE
		self.V = curses.ACS_VLINE

		self.TR = curses.ACS_URCORNER
		self.TL = curses.ACS_ULCORNER
		self.BR = curses.ACS_LRCORNER
		self.BL = curses.ACS_LLCORNER
		self.CHARS = [ self.TL, self.BL, self.TR, self.BR ]

	def run(self):
		self.draw()
		self.win.getch()

	def draw(self):
		self.draw_locations()
		self.win.box()
		self.win.refresh()

	def draw_locations(self):
		for room in self.locations.itervalues():
			self.add_room(room)

	def scale(self, x):
		return x * self.SCALE

	def add_room(self, room):
		loc = room.pos
		size = room.size
		scale = self.scale

		for ch, (x, y) in zip(self.CHARS, itertools.product(
			(scale(loc[0]), scale(loc[0]+size[0])-1),
			(scale(loc[1]), scale(loc[1]+size[1])-1),
			)):
			self.win.addch(y+1, x+1, ch)

		for x in range(scale(loc[0])+1, scale(loc[0]+size[0])-1):
			for y in scale(loc[1]), scale(loc[1]+size[1])-1:
				self.win.addch(y+1, x+1, self.H)

		for y in range(scale(loc[1])+1, scale(loc[1]+size[1])-1):
			for x in scale(loc[0]), scale(loc[0]+size[0])-1:
				self.win.addch(y+1, x+1, self.V)

		for (_dir, _to) in room.exits:
			self.add_exit(room, _dir, locations[_to])
			
	def add_exit(self, _from, _dir, _to):
		if _dir == 'E':
			y = ((_from.size[1]/2) + _from.pos[1]) * self.SCALE
			for x in range((_from.pos[0]+_from.size[0])*self.SCALE, _to.pos[0] * self.SCALE):
				self.win.addch(y+1,x+1,self.H)

		if _dir == 'S':
			x =  ((_from.size[0]/2) + _from.pos[0]) * self.SCALE
			for y in range((_from.pos[1]+_from.size[1])*self.SCALE, _to.pos[1] * self.SCALE):
				self.win.addch(y+1,x+1,self.V)
		

if __name__ == '__main__':
	grid = Grid(20)
	for room in locations.itervalues():
		grid.add_room(room)
		for (_dir, _to) in room.exits:
			grid.add_exit(room, _dir, locations[_to])

	grid.draw_ascii()
