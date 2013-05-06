import sys
import time
import signal
import curses
import logging

logging.basicConfig(
	level = logging.DEBUG,
	filename="client.log",
	)

class Client(object):
	def __init__(self):
		self.stdscr = None
		self.logwin = None
		pass

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

	def log(self, msg, *args):
		s = msg % args
		self.logwin.scroll()
		self.logwin.addstr(self.logline-1,1,s[:78])
		self.draw_logwin()
		self.logwin.refresh()

	def main(self, stdscr):
		self.stdscr = stdscr
		self.h, self.w = stdscr.getmaxyx()
		self.setup_logwin()

		for i in range(10):
			self.log("Message %d", i)
			time.sleep(1)

		pass

	def run(self):
		curses.wrapper(self.main)
