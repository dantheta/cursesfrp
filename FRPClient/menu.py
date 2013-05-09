
import time
import curses
import logging
import curses.panel


class Menu(object):
	def __init__(self, parent, options):
		self.options = options
		self.parent = parent
		self.sel = 0
		self.setup()

	def setup(self):
		self.win = self.parent.subwin(10,20,5,5)
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

	def hide(self):
		logging.debug("Hiding menu")
		del self.win
		del self.panel
		curses.panel.update_panels()
		curses.doupdate()
	

def test(stdscr):
	m = Menu(stdscr, ['One','Two','Three','Four'])
	m.run()

if __name__ == '__main__':
	logging.basicConfig(
		level = logging.DEBUG,
		filename='menu.test.log'
		)
	curses.wrapper(test)

