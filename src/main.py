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
		try:
			bus_name = dbus.service.BusName('org.stereo3d.shutters', bus=dbus.SessionBus())
			dbus.service.Object.__init__(self, bus_name, '/org/stereo3d/shutters')
			
			self.glasses = nv3d.shutters() # Uploading firmware
		
		except Exception, e:
			print "Error while starting daemon:", e
			sys.exit()
	
	@dbus.service.method('org.stereo3d.shutters')
	def start(self): # parameter rate ?
		try:
			self.glasses.set_rate(120) # Hardcoded for 120Hz display
			print "Setting glasses frame rate ..."
			success = 1
		except:
			print "Rate setting failed !"
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
	DBusGMainLoop(set_as_default=True)
	daemon = DaemonDBUS()
	
	loop = gobject.MainLoop()
	print "Listening ..."
	loop.run()
