import sys
import time
import signal
import curses
import curses.panel
import logging

import ConfigParser

from FRPShared.model import Event,Request
from event import EventSource
from menu import Menu
from input import InputWindow


class Client(object):
	def __init__(self, user = None):
		self.stdscr = None
		self.logwin = None
		self.location = None
		self.config = ConfigParser.ConfigParser()
		logging.info("Loaded config: %s", self.config.read(['client.cfg']))
		self.user = user or self.config.get('client','user')
		self.eventsrc = EventSource(self.user)
		pass

	def set_location(self, loc):
		self.location = loc
		self.eventsrc.set_location(loc)

	def setup(self, stdscr):
		self.stdscr = stdscr
		self.panel = curses.panel.new_panel(stdscr)
		self.h, self.w = stdscr.getmaxyx()
		self.setup_logwin()
		self.inputwin = InputWindow(self.config, self.stdscr, self.logline, self.w, 9)

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

	def log(self, msg, *args):
		text = msg % args
		self.logwin.scroll()
		self.logwin.addstr(self.logline-1,1,text[:78])
		self.draw_logwin()
		self.logwin.refresh()


	def main(self, stdscr):
		self.setup(stdscr)

		self.send_event('ANNOUNCE')
		response = self.eventsrc.recv_obj()
		assert response.rsp == 'ANNOUNCE'
		self.set_location(response.opts['initial_location'])

		self.send_event('ENTER', old_location = None)
		self.running = True
		while self.running == True:
			evt = self.eventsrc.get_next()
			if self.eventsrc.has_input:
				command = self.inputwin.process_key()
				if command is not None:
					self.process_input(command)
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


	def process_input(self, command):
		if not command.startswith('/'):
			self.send_event('SAY', text=command)
			return

		if ' ' in command:
			cmd, opt = command.split(' ',1)
		else:
			cmd, opt = command, ''

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
