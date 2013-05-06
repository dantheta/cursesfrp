import sys
import time
import signal
import curses
import logging

from event import EventSource,Event,Request


class Client(object):
	def __init__(self, user = None):
		self.stdscr = None
		self.logwin = None
		self.eventsrc = EventSource()
		self.set_location('location-1')
		self.user = user or 'Dantheta'
		pass

	def set_location(self, loc):
		self.location = loc
		self.eventsrc.set_location(loc)

	def setup(self, stdscr):
		self.stdscr = stdscr
		curses.echo()
		self.h, self.w = stdscr.getmaxyx()
		self.setup_logwin()
		self.setup_inputwin()

	def setup_logwin(self):
		self.logline = self.h-9
		dims = self.logline+1, self.w, 0, 0
		logging.info("Dims: %s", dims)
		self.logwin = self.stdscr.subwin(*dims)
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
		self.inputwin.scrollok(True)
		self.inputwin.setscrreg(1,7)
		self.draw_inputwin()

	def draw_inputwin(self):
		self.inputwin.box()
		self.inputwin.addch(0,0, curses.ACS_LTEE)
		self.inputwin.addch(0,self.w-1, curses.ACS_RTEE)
		self.inputwin.refresh()

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

		while True:
			evt = self.eventsrc.get_next()
			if self.eventsrc.has_input:
				s = self.get_input()
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
			if evt is not None:
				logging.debug("Got evt: %s", evt)
				self.log(evt.split(' ',1)[1])
			time.sleep(0.1)

	def send_event(self, cmd, **kw):
		evt = Event(cmd, self.user, self.location, **kw)
		self.eventsrc.send(evt)
		
	def send_request(self, cmd, opt):
		rq = Request(cmd, self.user, self.location, opt)
		self.eventsrc.send(rq)

	def run(self):
		curses.wrapper(self.main)
