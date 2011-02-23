#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, time

# for Nvidia 3D Vision Glasses
import nv3d

# ctypes
from ctypes import *
from ctypes import util

# DBUS
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

# LOOP
import gobject

class struct_XF86VidModeModeLine(Structure):
    __slots__ = [
        'hdisplay',
        'hsyncstart',
        'hsyncend',
        'htotal',
        'hskew',
        'vdisplay',
        'vsyncstart',
        'vsyncend',
        'vtotal',
        'flags',
        'privsize',
        'private',
    ]
INT32 = c_int   # /usr/include/X11/Xmd.h:135
struct_XF86VidModeModeLine._fields_ = [
    ('hdisplay', c_ushort),
    ('hsyncstart', c_ushort),
    ('hsyncend', c_ushort),
    ('htotal', c_ushort),
    ('hskew', c_ushort),
    ('vdisplay', c_ushort),
    ('vsyncstart', c_ushort),
    ('vsyncend', c_ushort),
    ('vtotal', c_ushort),
    ('flags', c_uint),
    ('privsize', c_int),
    ('private', POINTER(INT32)),
]

class DaemonDBUS(dbus.service.Object):
	def __init__(self):
		try:
			bus_name = dbus.service.BusName('org.stereo3d.shutters', bus=dbus.SessionBus())
			dbus.service.Object.__init__(self, bus_name, '/org/stereo3d/shutters')
			
			self.glasses = nv3d.shutters() # Uploading firmware
		
		except Exception, e:
			print "Error while starting daemon:", e
			sys.exit()
	
	def getRefreshRate(self):
		path = util.find_library('X11')
		if not path:
			raise ImportError('Cannot locate X11 library')
		xlib = cdll.LoadLibrary(path)
		
		path = util.find_library('Xxf86vm')
		if not path:
			raise ImportError('Cannot locate Xxf86vm library')
		Xxf86vm = cdll.LoadLibrary(path)
		
		XF86VidModeModeLine = struct_XF86VidModeModeLine
		
		dpy = xlib.XOpenDisplay(os.environ['DISPLAY'])
		displayNumber = xlib.XDefaultScreen(dpy)
		
		modeline = XF86VidModeModeLine()
		pixelclock = c_int()
		Xxf86vm.XF86VidModeGetModeLine( dpy, displayNumber, pointer(pixelclock), pointer(modeline))
		
		frameRate = pixelclock.value * 1000.0 / modeline.htotal / modeline.vtotal
		return frameRate
	
	@dbus.service.method('org.stereo3d.shutters')
	def start(self): # parameter rate ?
		try:
			refresh_rate = self.getRefreshRate()
			self.glasses.set_rate(refresh_rate)
			print "Setting glasses frame rate ... ("+ refresh_rate +" Hz)"
			success = int(refresh_rate) # Valeur approximative
		except Exception, e:
			print "Rate setting failed"
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
