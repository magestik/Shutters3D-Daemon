#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus, sys, time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class ShuttersGL:
	def __init__(self):	
		self.is_stereo = False # Hardcoded for testing
		self.inverteyes = 1
		self.i_counter = 0
		
		self.refresh_time = float(time.time())
		self.frame = 0
		self.last_frame = 0
		
		try:
			bus = dbus.SystemBus()
			self.shutters = bus.get_object('org.stereo3d.shutters', '/org/stereo3d/shutters')
		except Exception, e:
			raise Exception(e)
	
	def __del__(self):
		pass
		#self.shutters.stop()
	
	def init_glasses(self):
		self.refresh = self.shutters.start()
		if self.refresh == 0:
			sys.exit("Error while starting glasses")

	def init_glut(self):
		glutInit(sys.argv)

		if self.is_stereo:
			glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_STEREO)
		else:
			glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
	
		glutInitWindowSize(512, 512)
		glutCreateWindow("GLUT stereo testing")
		#glutFullScreen()
		
		glutIdleFunc(self.idle)
	
		glutMainLoop()
		
	def idle(self):
		if self.is_stereo:
			glDrawBuffer(GL_BACK_LEFT) # Draw Left Buffer
			self.drawNoImage(0);
			glDrawBuffer(GL_BACK_RIGHT); # Draw right buffer
			self.drawNoImage(1);
			
			# Here code for swapping when quad buffering is supported
		
		else:
			glDrawBuffer(GL_BACK) # Draw either left or right depending on counter
			self.drawNoImage(self.i_counter&1)
		
			if self.inverteyes == 1:
				eye = self.shutters.swap('right')
				self.inverteyes = 0
			else:
				eye = self.shutters.swap('left')
				self.inverteyes = 1
				
			glutSwapBuffers()
			++self.i_counter
		
		self.print_refresh_rate()
		
	def drawNoImage(self, in_i_eye):
		glClearColor(0.0, 0.0, 0.0, 1.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
			
		glBegin(GL_QUADS)
			
		if in_i_eye - self.inverteyes:
			glVertex2f(-1.0, -1.0)
			glVertex2f( 0.0, -1.0)
			glVertex2f( 0.0, 1.0)
			glVertex2f(-1.0, 1.0)
		else:
			glVertex2f( 0.0, -1.0)
			glVertex2f( 1.0, -1.0)
			glVertex2f( 1.0, 1.0)
			glVertex2f( 0.0, 1.0)
			
		glEnd()
	
	def print_refresh_rate(self):
		self.frame = self.frame +1

		if self.frame - self.last_frame >= 600:
			r = (self.frame - self.last_frame) / (float(time.time()) - self.refresh_time)
			self.refresh_time = float(time.time())
			self.last_frame = self.frame
			print "Refresh rate = ", r

			
try:
	area = ShuttersGL()
except Exception, e:
	sys.exit("Can't connect to the daemon: "+ str(e))
else:
	area.init_glasses()
	area.init_glut()
	
area.__del__()
