#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time

#import nv3d
import socket

class daemon:
	def __init__(self):
		#self.glasses = nv3d.shutters()
		#self.glasses.set_rate(120)
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind(("", 5000))
		self.socket.listen(5)
	
	def wait(self):
		while 1:
			self.client, address = self.socket.accept()
			print "Connection from ", address
			#self.client.send(data)
			self.synchro()

	def synchro(self):
		while 1:
			data = self.client.recv(512)
			if (data == 'q' or data == 'Q'):
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
					print "ERROR"

if __name__ == "__main__":
	d = daemon()
	d.wait()
