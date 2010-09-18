#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time
import pynotify
import wx

#import nv3d
import socket

from threading import Thread
import gobject
gobject.threads_init() # For prevent GTK freeze

class daemon(Thread):
	def __init__(self,i): # Prepare the socket in a separated Thread
		Thread.__init__(self)
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind(('', 5000))
		self.socket.listen(5)

		self.gui = i
		self.status = -1 # for the Thread
	
	def run(self): # Is called when we start the Thread
		while 1:
			self.client, address = self.socket.accept() # Wait here
			print "Connection from ", address
			self.synchro()

	def synchro(self): # Listen the client for controlling glasses
		#self.glasses = nv3d.shutters()
		#self.glasses.set_rate(120)
		self.gui.notify("3D signal detected")
		
		#self.client.send(data) # to send some informations to the client (maybe key status)
		while 1:
			data = self.client.recv(512)
			if (data == 'q' or data == 'Q'):
				self.gui.notify("3D signal terminated")
				self.client.close()
				break;
			else:
				if(data == 'l' or data == 'L'):
					#self.glasses.set_eye(0)
					i=1
				elif(data == 'r' or data == 'R'):
					#self.glasses.set_eye(1)
					i=1
				else:
					self.gui.notify("Error : client has been killed ?")
					self.client.close()
					break;

		#self.glasses.__del__() # Stop glasses and release interface

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
	
	i = interface(None)
	i.Show(False)
	
	d = daemon(i)
	d.start()
	
	app.MainLoop()
