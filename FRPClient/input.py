
import curses
import logging


class InputWindow(object):
	def __init__(self, config, stdscr, y, width, height):
		self.config = config
		self.stdscr = stdscr
		self.height = height
		self.width = width
		self.y = y
		self.buffer = ''
		self.setup()

	def setup(self):
		self.inputwin = self.stdscr.subwin(9, self.width, self.y,0)
		self.inputpanel = curses.panel.new_panel(self.inputwin)
		self.inputwin.keypad(True)
		self.inputwin.scrollok(True)
		self.inputwin.setscrreg(1,7)
		self.draw()

	def draw(self):
		self.inputwin.box()
		self.inputwin.addch(0,0, curses.ACS_LTEE)
		self.inputwin.addch(0,self.width-1, curses.ACS_RTEE)
		self.inputwin.refresh()
		self.inputwin.move(7, 1)

	def get_input(self):
		self.inputwin.scroll()
		self.draw()
		return self.inputwin.getstr(7,1)

	def get_macro(self, key):
		logging.debug("Looking up macro: %s")
		try:
			return self.config.get('macros', key).replace('<CR>','\n')
		except ConfigParser.NoOptionError:
			return ''

	def process_key(self):
		ch = self.inputwin.getch()
		logging.debug("Got key: %s, %s", type(ch), type(curses.KEY_F8))
		if ch == curses.KEY_F8:
			s = self.get_macro('F8')
			logging.debug("Got macro: %s", s)
			if s:
				if s.endswith('\n'):
					self.buffer = ''
					self.inputwin.scroll()
					self.inputwin.addstr(7,1, s[:-1])
					self.inputwin.refresh()
					return s[:-1]
				else:
					self.inputwin.addstr(7,1+len(self.buffer), s)
					self.buffer += s
					logging.debug("Buffer: %s", self.buffer)
					self.inputwin.refresh()
		elif ch == curses.KEY_BACKSPACE:
			self.inputwin.addch(7, len(self.buffer), ' ')
			self.inputwin.move(7,len(self.buffer))
			self.buffer = self.buffer[:-1]
			self.inputwin.refresh()
		elif ch == 10:
			s = self.buffer
			self.inputwin.scroll()
			self.draw()
			self.buffer = ''
			return s
		elif ch == 9:
			# get options for command so far
			self.get_options()
		elif ch > 256:
			logging.debug("Ignoring key: %s", ch)
		else:
			self.inputwin.addch(7, 1+len(self.buffer), ch)
			self.inputwin.refresh()
			self.buffer += chr(ch)

