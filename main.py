#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time

# Nvidia 3D Vision
#import nv3d

# DBUS
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

# GUI
import pynotify
import wx

class DaemonDBUS(dbus.service.Object):
	def __init__(self):
		bus_name = dbus.service.BusName('org.stereo3d.shutters', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/org/stereo3d/shutters')
	
	@dbus.service.method('org.stereo3d.shutters')
	def start(self):
		GUI.notify("3D signal detected")
		self.glasses = nv3d.shutters()
		self.glasses.set_rate(120)
		print "Initialising glasses ..."
		return "OK"
	
	@dbus.service.method('org.stereo3d.shutters')
	def swap(self):
		if self.glasses.eye == 1:
			self.glasses.set_eye(0)
			return "left"
		else:
			self.glasses.set_eye(1)
			return "right"

	@dbus.service.method('org.stereo3d.shutters')
	def stop(self):
		GUI.notify("3D signal terminated")
		self.glasses.__del__()
		print "Releasing glasses ..."
		return "OK"

class interface(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, style=wx.FRAME_NO_TASKBAR | wx.NO_FULL_REPAINT_ON_RESIZE)
		pynotify.init("Shutters3D Daemon")		
		
		self.tbicon = wx.TaskBarIcon()
		icon = wx.Icon('3D.ico', wx.BITMAP_TYPE_ICO)
		self.tbicon.SetIcon(icon, '')
		
		self.Show(True)

   	def notify(self, msg):
		msg = pynotify.Notification("Nvidia 3D Vision", msg, "3D.png")
		msg.show()

if __name__ == "__main__":
	app = wx.App(False)
	
	GUI = interface(None)
	GUI.Show(False)
	
	DBusGMainLoop(set_as_default=True)
	daemon = DaemonDBUS()

	app.MainLoop()
