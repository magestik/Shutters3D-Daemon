#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time

# Nvidia 3D Vision
import nv3d

# DBUS
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

# LOOP
import gobject

class DaemonDBUS(dbus.service.Object):
	def __init__(self):
		bus_name = dbus.service.BusName('org.stereo3d.shutters', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/org/stereo3d/shutters')
	
	@dbus.service.method('org.stereo3d.shutters')
	def start(self):
		try:
			self.glasses = nv3d.shutters()
			self.glasses.set_rate(120)
			print "Initialising glasses ..."
			success = 1
		except:
			print "Initalisation failed !"
			success = 0
		
		return success
	
	@dbus.service.method('org.stereo3d.shutters')
	def swap(self, eye):
		try:
			if eye == 'left':
				self.glasses.set_eye(0)
				success = 1
			elif eye == 'right':
				self.glasses.set_eye(1)
				success = 1
			else:
				success = 0
			#buttons
		except:
			print "Swap Error"
			success = 0
		
		return success
	
	@dbus.service.method('org.stereo3d.shutters')
	def stop(self):
		try:
			self.glasses.__del__()
			print "Releasing glasses ..."
			success = 1
		except:
			print "Stop Error"
			success = 0
		
		return success

if __name__ == "__main__":
	daemon = DaemonDBUS()
	
	loop = gobject.MainLoop()
	print 'Listening'
	loop.run()
