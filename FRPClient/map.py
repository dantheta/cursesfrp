
locations = {
	1: ((1,1), (1,1), [('E',2),('S',3),('W',4)]),
	2: ((4,1), (1,1), [('W',1)]),
	3: ((1,4), (1,1), [('N',1)]),
	4: ((0,1), (1,1), [('E',1)]),
	}

class Grid(object):
	def __init__(self, size):
		self.grid = []
		self.size = size
		for x in range(size):
			self.grid.append( [' '] * size)

for room in locations.itervalues():
	loc = room[0]
	sz = room[1]
	for x in range(sz[0]):	
		for y in range(sz[1]):
			grid[(loc[1]*2) + y][(loc[0]*2)+x] = u"\u2588"
	exits = room[2]

	for direction, room in exits:
		if direction == 'E':
			y = ((sz[1]/2) + loc[1]) * 2
			for x in range((loc[0]+sz[0])*2, (locations[room][0][0]) * 2):
				grid[y][x] = u"\u23E4"
				grid[y][x+1] = u"\u23E4"

#print u"\u23E4"
#print u"\u2028"
#print u"\u007C"

for line in grid:
	print ''.join(line)
