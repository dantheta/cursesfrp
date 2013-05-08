import sys
import time
import signal
import curses
import curses.panel
import logging

from FRPShared.model import Event,Request
from event import EventSource
from menu import Menu


class Client(object):
	def __init__(self, user = None):
		self.stdscr = None
		self.logwin = None
		self.location = ''
		self.user = user or 'Dantheta'
		self.eventsrc = EventSource(self.user)
		self.set_location('location-1')
		self.buffer = ''
		pass

	def set_location(self, loc):
		self.location = loc
		self.eventsrc.set_location(loc)

	def setup(self, stdscr):
		self.stdscr = stdscr
		self.panel = curses.panel.new_panel(stdscr)
		self.h, self.w = stdscr.getmaxyx()
		self.setup_logwin()
		self.setup_inputwin()

	def setup_logwin(self):
		self.logline = self.h-9
		dims = self.logline+1, self.w, 0, 0
		logging.info("Dims: %s", dims)
		self.logwin = self.stdscr.subwin(*dims)
		self.logpanel = curses.panel.new_panel(self.logwin)
		self.logwin.scrollok(True)
		self.logwin.setscrreg(1,self.logline-1)
		self.draw_logwin()

	def draw_logwin(self):
		self.logwin.box()
		self.logwin.addch(self.logline,0,curses.ACS_LTEE)
		self.logwin.addch(self.logline,self.w-1,curses.ACS_RTEE)
		self.logwin.refresh()

	def setup_inputwin(self):
		self.inputwin = self.stdscr.subwin(9, self.w, self.logline,0)
		self.inputpanel = curses.panel.new_panel(self.inputwin)
		self.inputwin.scrollok(True)
		self.inputwin.setscrreg(1,7)
		self.draw_inputwin()

	def draw_inputwin(self):
		self.inputwin.box()
		self.inputwin.addch(0,0, curses.ACS_LTEE)
		self.inputwin.addch(0,self.w-1, curses.ACS_RTEE)
		self.inputwin.refresh()
		self.inputwin.move(7, 1)

	def log(self, msg, *args):
		s = msg % args
		self.logwin.scroll()
		self.logwin.addstr(self.logline-1,1,s[:78])
		self.draw_logwin()
		self.logwin.refresh()

	def kbhit(self):
		self.inputwin.nodelay(True)
		ch = self.inputwin.getch()
		if ch != -1:
			self.inputwin.ungetch(ch)
		self.inputwin.nodelay(False)
		return ch != -1

	def get_input(self):
		self.inputwin.scroll()
		self.draw_inputwin()
		return self.inputwin.getstr(7,1)

	def main(self, stdscr):
		self.setup(stdscr)

		self.send_event('ANNOUNCE')
		self.eventsrc.recv()
		self.send_event('ENTER', old_location = None)
		while True:
			evt = self.eventsrc.get_next()
			if self.eventsrc.has_input:
				s = self.process_key()
				if s is not None:
					self.process_input(s)
			if evt is not None:
				logging.debug("Got evt: (%d) %s", len(evt), evt)
				if evt == 'OK':
					logging.info("Request acknowledged")
				else:
					if ' ' in evt:
						txt = evt.split(' ',1)[1] # throw away topic
					else:
						txt = evt
					for line in txt.split('\n'):
						self.log(line)
			time.sleep(0.1)

	def process_key(self):
		ch = self.inputwin.getch()
		if ch == 10:
			s = self.buffer
			self.inputwin.scroll()
			self.draw_inputwin()
			self.buffer = ''
			return s
		elif ch == 9:
			# get options for command so far
			self.get_options()
		else:
			self.inputwin.addch(7, 1+len(self.buffer), ch)
			self.inputwin.refresh()
			self.buffer += chr(ch)

	def process_input(self, s):
		if not s.startswith('/'):
			self.send_event('SAY', text=s)
		else:
			if ' ' in s:
				cmd, opt = s.split(' ',1)
			else:
				cmd, opt = s, ''

			if cmd == '/go':
				oldloc = self.location
				self.set_location(opt)
				self.send_event('ENTER',old_location=oldloc)
			else:
				self.send_request(cmd, opt)

	def get_options(self):
		cmd = self.buffer.split(' ',1)[0] # get command so far
		menu = Menu(self.logwin, ['North','South','East','West'])
		option = menu.run()
		if option is not None:
			self.inputwin.addstr(7,1+len(self.buffer), ' ' + option)
			self.buffer += ' ' + option
			menu.hide()
			self.logwin.refresh()

			self.inputwin.scroll()
			self.draw_inputwin()
			self.process_input(self.buffer)
		else:
			menu.hide()
			self.logwin.refresh()

	def send_event(self, cmd, **kw):
		evt = Event(cmd, self.user, self.location, **kw)
		self.eventsrc.send(evt)
		
	def send_request(self, cmd, opt):
		rq = Request(cmd, self.user, self.location, opt)
		self.eventsrc.send(rq)

	def run(self):
		curses.wrapper(self.main)
