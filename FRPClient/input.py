
import curses
import logging

from menu import Menu

class InputCommand(object):
	def __init__(self, *opts):
		self.opts = opts

class MenuInputCommand(InputCommand):pass

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
		self.win = self.stdscr.subwin(9, self.width, self.y,0)
		self.inputpanel = curses.panel.new_panel(self.win)
		self.win.keypad(True)
		self.win.scrollok(True)
		self.win.setscrreg(1,7)
		self.draw()

	def draw(self):
		self.win.box()
		self.win.addch(0,0, curses.ACS_LTEE)
		self.win.addch(0,self.width-1, curses.ACS_RTEE)
		self.win.refresh()
		self.win.move(7, 1)

	def get_input(self):
		""" Old synchronous line input"""
		self.win.scroll()
		self.draw()
		return self.win.getstr(7,1)

	def show_menu(self, command, options):
		"""Shows the tab-completion menu"""
		menu = Menu(self.win, options )
		option = menu.run()
		menu.hide()
		if option is not None:
			self.set_buffer(command + ' ' + option)

	def set_buffer(self, text):
		"""Allows text to be pasted into the input buffer and displayed onscreen as an 
		incomplete command"""
		self.buffer = text
		self.win.move(7,1)
		self.win.clrtoeol()
		self.win.addstr(7, 1, self.buffer)
		self.draw()
		

	def get_macro(self, key):
		""" Get the full command line for a given macro key """
		logging.debug("Looking up macro: %s")
		try:
			#<CR> is the magic string for line-feed in the ini-file
			return self.config.get('macros', key).replace('<CR>','\n')
		except ConfigParser.NoOptionError:
			return ''

	def process_key(self):
		"""Handles a single keypress by appending it to the buffer.  
		Characters are displayed on the screen.  If the last character is LF, then the full 
		command line is returned to the caller for processing, otherwise None.
		If a tab-character is supplied, then the special return value MenuInputCommand is returned, 
		telling the command processor to invoke the tab-completion menu"""

		#TODO: wrap command lines in an InputCommand class so that we're not mixing return types
		# just for the hell of it.

		# handle a single key of input
		ch = self.win.getch()
		logging.debug("Got key: %s, %s", type(ch), type(curses.KEY_F8))
		if ch == curses.KEY_F8:
			# at the moment F8 is the only macro key
			s = self.get_macro('F8')
			logging.debug("Got macro: %s", s)
			if s:
				if s.endswith('\n'):
					# if the macro command ends with \n, then it's a complete command and we should
					# give that command back to the caller
					self.buffer = ''
					self.win.scroll()
					self.win.addstr(7,1, s[:-1])
					self.win.refresh()
					return s[:-1]
				else:
					# otherwise, append the character
					self.win.addstr(7,1+len(self.buffer), s)
					self.buffer += s
					logging.debug("Buffer: %s", self.buffer)
					self.win.refresh()
		elif ch == curses.KEY_BACKSPACE:
			# backspace removes the last character from the screen and the buffer
			if len(self.buffer):
				self.win.addch(7, len(self.buffer), ' ')
				self.win.move(7,len(self.buffer))
				self.buffer = self.buffer[:-1]
				self.win.refresh()
		elif ch == 10:
			# linefeed ends the command, and returns it to the caller
			s = self.buffer
			self.win.scroll()
			self.draw()
			self.buffer = ''
			return s
		elif ch == 9:
			# send back a request for the tab-completion menu.  The command so far
			# is supplied so that the command processor knows which set of options
			# to supply
			return MenuInputCommand(self.buffer)
		elif ch > 256:
			# ignore keys that would crash the program
			logging.debug("Ignoring key: %s", ch)
		else:
			# otherwise, just append the input to the buffer
			self.win.addch(7, 1+len(self.buffer), ch)
			self.win.refresh()
			self.buffer += chr(ch)

