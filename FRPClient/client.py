import sys
import time
import signal
import curses
import curses.panel
import logging

import ConfigParser

from FRPShared.model import Event,Request
from event import EventSource
from input import InputWindow,MenuInputCommand
from map import MapDialog


class Client(object):
	def __init__(self, user = None):
		self.stdscr = None
		self.logwin = None
		self.location = None
		self.config = ConfigParser.ConfigParser()
		logging.info("Loaded config: %s", self.config.read(['client.cfg']))
		self.user = user or self.config.get('client','user')

		# Event Source - wrapper for inbound ZMQ events and keyboard input
		self.eventsrc = EventSource(self.user)
		pass

	def set_location(self, loc):
		"""Saves the new location into the client's settings, and sets up the 
		location-specific event subscription for the new location"""
		self.location = loc
		self.eventsrc.set_location(loc)

	def setup(self, stdscr):
		# setup curses UI
		self.stdscr = stdscr
		self.panel = curses.panel.new_panel(stdscr)
		self.h, self.w = stdscr.getmaxyx()
		self.setup_logwin()
		self.inputwin = InputWindow(self.config, self.stdscr, self.logline, self.w, 9)

	def setup_logwin(self):
		# TODO: move to separate class/module
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
		"""Prints message to log window"""
		text = msg % args
		self.logwin.scroll()
		self.logwin.addstr(self.logline-1,1,text[:78])
		self.draw_logwin()
		self.logwin.refresh()


	def main(self, stdscr):
		self.setup(stdscr)

		# tells server to set up initial data for this user
		self.send_event('ANNOUNCE')
		# get the ANNOUNCE-response, which contains the initial location
		response = self.eventsrc.recv_obj()
		assert response.rsp == 'ANNOUNCE'
		self.set_location(response.opts['initial_location'])
		
		# Now that the server has told us where we are, send an ENTER notification to 
		# other clients in the same area
		self.send_event('ENTER', old_location = None)

		self.running = True
		while self.running == True:
			# Get the next event from any source
			# This could be a server message for the location or the player, a response to a player request
			# or keyboard input
			evt = self.eventsrc.get_next()

			# process keyboard input first
			# TODO: make this less kludgy
			if self.eventsrc.has_input:
				# inputwin will retrieve the keypress, and return a command line/MenuInputCommand 
				# for LF/Tab keys
				command = self.inputwin.process_key()

				# check for tab-completion request
				if isinstance(command, MenuInputCommand):
					# show tab-complete
					self.show_menu(command)
				elif command is not None:
					# otherwise process the command line (string)
					self.process_input(command)

			# Now get to queue events from the server
			if evt is not None:
				logging.debug("Got evt: (%d) %s", len(evt), evt)
				if evt == 'OK':
					# Client events typically just get an "OK" response
					logging.info("Request acknowledged")
					# TODO: handle response types other than "OK" (there aren't any yet)
				else:
					# if there's a space in, throw away the subscription topic
					if ' ' in evt:
						txt = evt.split(' ',1)[1]
					else:
						txt = evt
					# print response text to the log window, one line at a time
					for line in txt.split('\n'):
						self.log(line)
			# not really sure if we need this anymore
			time.sleep(0.1)


	def process_input(self, command):
		# Any input that doesn't start with '/' is speech
		if not command.startswith('/'):
			self.send_event('SAY', text=command)
			return

		# get the first word as the command name
		if ' ' in command:
			cmd, opt = command.split(' ',1)
		else:
			cmd, opt = command, ''

		# /go and /map have client logic
		if cmd == '/go':
			oldloc = self.location
			self.set_location(opt)
			self.send_event('ENTER',old_location=oldloc)
		elif cmd == '/map':
			# no server command for this yet
			dlg = MapDialog(self.stdscr, 24, 64, 4, 4)
			dlg.run()
			dlg.hide()
		else:
			# all others are sent to the server for processing
			self.send_request(cmd, opt)

	def show_menu(self, menucommand):
		# get the command name from the incomplete request line
		cmd = menucommand.opts[0].split(' ')[0] # get first word
		if cmd == '/go':
			self.inputwin.show_menu(cmd, ['North','South','East','West'])

	def get_options(self):
		# not sure if this is used any more
		cmd = self.buffer.split(' ',1)[0] # get command so far
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
