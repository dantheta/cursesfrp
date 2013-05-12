
import curses
import logging
import itertools

class Dialog(object):
	def __init__(self, parent, height, width, top, left):
		self.parent = parent 
		self.height = height
		self.width = width
		self.top = top
		self.left = left

	def save_background(self):
		background = []
		for (y, x) in itertools.product(
			range(self.top,self.top+self.height), 
			range(self.left, self.left + self.width)
			):
			background.append(self.parent.inch(y,x))
		self._background = background

	def restore_background(self):
		for ch, (y, x) in zip(self._background, 
			itertools.product(
				range(self.top,self.top+self.height), 
				range(self.left, self.left + self.width)
			)):
			self.parent.addch(y,x,ch)

	def hide(self):
		del self.win
		del self.panel
		curses.panel.update_panels()
		curses.doupdate()
		self.restore_background()
		self.parent.refresh()

		
		
