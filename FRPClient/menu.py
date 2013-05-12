
import time
import curses
import logging
import curses.panel

from dialog import Dialog

class Menu(Dialog):
	def __init__(self, parent, options):
		Dialog.__init__(self, parent, 6, 20, 1, 15)
		self.options = options
		self.sel = 0
		self.setup()

	def setup(self):
		logging.debug("Parent : %s", self.parent)
		logging.debug("Parent size: %s", self.parent.getmaxyx())
		self.save_background()
		self.win = self.parent.derwin(6,20,1,15)
		self.panel = curses.panel.new_panel(self.win)
		self.win.keypad(True)
		curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)


	def draw(self):
		self.win.box()
		self.win.bkgd(' ', curses.color_pair(2))
		for n, opt in enumerate(self.options):
			self.win.addstr(n+1, 2, opt)
			if self.sel == n:
				self.win.addch(n+1, 1, curses.ACS_RARROW)
				self.win.addch(n+1, 18, curses.ACS_LARROW)
			else:
				self.win.addch(n+1, 1 , ' ')
				self.win.addch(n+1, 18, ' ')
		self.win.refresh()

	def up(self):
		if self.sel > 0:
			self.sel -= 1
		self.draw()

	def down(self):
		if self.sel < len(self.options)-1:
			self.sel += 1
		self.draw()

	def run(self):
		self.draw()
		while True:
			ch = self.win.getch()
			logging.info("Got key: %s", ch)
			if ch == curses.KEY_DOWN:
				self.down()
			elif ch == curses.KEY_UP:
				self.up()
			if ch == 10: # enter
				logging.info("Selected: %s", self.options[self.sel])
				return self.options[self.sel]
			if ch == 27: # escape
				logging.info("Cancel")
				return None

	

def test(stdscr):
	m = Menu(stdscr, ['One','Two','Three','Four'])
	m.run()

if __name__ == '__main__':
	logging.basicConfig(
		level = logging.DEBUG,
		filename='menu.test.log'
		)
	curses.wrapper(test)

