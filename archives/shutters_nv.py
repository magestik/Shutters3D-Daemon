#!/usr/bin/env python
import usb
import sys
from time import sleep
import time

# ! MUST BE ROOT ! #

class Nvidia:
	"Abstract class for Nvidia 3D Vision controll"
	
	def __init__(self):
		self.eye			= 'left'
		
		self.cmd = {}
		self.cmd['WRITE']	= 0x01
		self.cmd['READ'] 	= 0x02
		self.cmd['CLEAR']	= 0x40
		self.cmd['SET_EYE']	= 0xAA
		
		self.cmd['CLOCK']	 = 48000000
		self.cmd['T0_CLOCK'] = self.cmd['CLOCK'] / 12
		self.cmd['T2_CLOCK'] = self.cmd['CLOCK'] / 4

		try:
			self.handle = self.getDevice()
		except:
			print "Can't initialise Nvidia 3D Vision"
			sys.exit()
		
		try:
			self.handle.setConfiguration(1) 
			self.handle.claimInterface(0) 
		except:
			print "Error during initialisation"
		
	def __del__(self):
		try:
			print "TRY TO STOP"
			self.stopDevice()
			self.handle.releaseInterface()
			del self.handle
		except: # n'existe pas
			print "ERROR WHILE STOPING"

	#
	# Functions for Writing/Reading in USB
	#
	
	# 4 endpoints
	# 0x01 (1 | 0x00) => Write
	# 0x81 (? | 0x??) => ???
	# 0x02 (2 | 0x00) => Write
	# 0x84 (4 | 0x80) => Read
	
	def write(self, endpoint, data, size = 0):
		try:
			LIBUSB_ENDPOINT_OUT = 0x00
			self.handle.bulkWrite(endpoint | LIBUSB_ENDPOINT_OUT, data, 1000)
		except usb.USBError as e:
			if e.args != ('No error',): # http://bugs.debian.org/476796
				raise e
	
	def read(self, endpoint, size):
		try:
			LIBUSB_ENDPOINT_IN = 0x80
			return self.handle.bulkRead(endpoint | LIBUSB_ENDPOINT_IN, size, 1000)
		except usb.USBError as e:
			if e.args != ('No error',): # http://bugs.debian.org/476796
				raise e

	#
	# Functions for initialising the Controller
	#
	def getDevice(self): # Make the link with the controller
		dev = self.findDevice(0x0007, 0x0955)
		if dev is None:
			raise ValueError('Nvidia 3D Vision not detected')
		
		ep = self.checkDevice(dev)
		if ep == 0:
			self.loadFirmware()
		
		return dev.open()
	
	def findDevice(self, idProduct, idVendor): # Find the controller
		busses	= usb.busses() # List of all USB devices
		for bus in busses: # Search for Nvidia 3D Vision
			for dev in bus.devices:
				if dev.idProduct == idProduct and dev.idVendor == idVendor:
					return dev
	
	def checkDevice(self, dev): # Get Endpoints
		configs 		= dev.configurations[0]
		interface 		= configs.interfaces[0][0]
		self.endpoints 	= []
		self.pipes 		= []
		count 			= 0
		for endpoint in interface.endpoints:
			count = count + 1
			self.endpoints.append(endpoint)
			self.pipes.append(endpoint.address)
		return count
			
	#
	# Functions for controlling the Dongle
	#
	def setRefreshRate(self, rate = 120): # refresh variables and initialize usb device
		self.rate 		= rate
		self.frameTime	= 1000000 / self.rate
		self.activeTime	= 2080
		
		# First command
		# 01 00 18 00   E1 29 FF FF   68 B5 FF FF   81 DF FF FF   30 28 24 22   0A 08 05 04   61 79 F9 FF
		brutTimings = [ self.cmd['WRITE'], 0x00, 0x18, 0x00, 0xE1, 0x29, 0xFF, 0xFF, 0x68, 0xB5, 0xFF, 0xFF, 0x81, 0xDF, 0xFF, 0xFF, 0x30, 0x28, 0x24, 0x22, 0x0, 0x08, 0x05, 0x04, 0x61, 0x79, 0xF9, 0xFF]		
		self.write(2, brutTimings) # OK
		
		# Second command
		# 01 1C 02 00 02 00
		cmd0x1c = [ self.cmd['WRITE'], 0x1c, 0x02, 0x00, 0x02, 0x00 ] 
		self.write(2, cmd0x1c) # OK
		
		# Third command
		# 01 1E 02 00 F0 00
		timeout = self.rate * 2
		cmdTimeout = [ self.cmd['WRITE'], 0x1e, 0x02, 0x00, timeout, timeout>>8 ] 
		self.write(2, cmdTimeout) # OK
		
		# Fourth command
		# 01 1B 01 00 07
		cmd0x1b = [ self.cmd['WRITE'], 0x1b, 0x01, 0x00, 0x07 ] 
		self.write(2, cmd0x1b) # OK
		
		# Fifth command
		# 01 1B 01 00 07
		clear = [self.cmd['CLEAR'], 0x18, 0x03, 0x00] 
		self.write(2, clear) # OK
		
	def setEye(self, first = 0, r = 0): # Swap Eyes
		if first == 0:
			eye = 0xFE
		else:
			eye = 0xFF
		
		parameter = {} # All possibilities
		parameter['C0'] = { 0x0D, 0x4E, 0x8F, 0xD0 }
		parameter['C1'] = { 0x11, 0x52, 0x93, 0xD4 }
		parameter['C2'] = { 0x15, 0x56, 0x97, 0xD8 }
		parameter['C3'] = { 0x19, 0x5A, 0x9B, 0xDC }
		parameter['C4'] = { 0x1D, 0x5E, 0x9F, 0xE1 }
		parameter['C5'] = { 0x21, 0x63, 0xA4, 0xE5 }
		parameter['C6'] = { 0x25, 0x67, 0xA8, 0xE9 }
		
		a = 0x4E
		b = 0xC0
		
		# AA FF 00 00 .. .. FF FF
		# AA FE 00 00 .. .. FF FF
		buf = [ self.cmd['SET_EYE'], eye, 0x00, 0x00, a, b, 0xFF, 0xFF ]
		self.write(1, buf) # => PROBLEM HERE (r is probably important) !
	
	# Magestik add
	def stopDevice(self): # Tell the device we want to stop (?)
		cmd1 = [ self.cmd['READ'], 0x1b, 0x01, 0x00 ]
		self.write(2, cmd1) # OK
		
		data = self.read(4, 5) # 1b 01 00 04 07 => OK
		
		cmd0x1b = [ self.cmd['WRITE'], 0x1b, 0x01, 0x00, 0x03 ]
		self.write(2, cmd0x1b) # OK
		
		buf = [ self.cmd['SET_EYE'], 0xFF, 0x00, 0x00, 0x71, 0xD9, 0xFF, 0xFF ]
		self.write(1, buf)	# OK
	
	def eventKeys(self): # Ask for key which have been pressed	
		# Time beetween calling this functions in the usblog
		# 0.300 / 0.845 / 0.498 / 0.132 / 0.099 / 0.131 / 0.132 / 0.099 / 0.132 / 0.1 / 0.132 / 0.132 / 0.131 / 0.132 / 0.242
		# When constant it's about every 16 eye swap (at 120 Hz)
		
		# 42 18 03 00
		cmd1 = [self.cmd['READ'] | self.cmd['CLEAR'], 0x18, 0x03, 0x00]
		self.write(2, cmd1) # OK
		
		data = self.read(4, 4+cmd1[2]) # OK but sometimes an error happens
		
		try:
			key 	= {}
		
			key[1] 	= int(data[4]) 	# Scroll 
			# PRINT => vers le bas = {1: 255, 2: 0, 3: 0} ou vers le haut = {1: 1, 2: 0, 3: 0}
		
			key[2]	= int(data[5]) # Scroll + button 
			# PRINT => vers le bas =  {1: 0, 2: 255, 3: 0} ou vers le haut = {1: 0, 2: 1, 3: 0}
		
			key[3]	= int(data[6] & 0x01) # Button
			# PRINT => {1: 0, 2: 0, 3: 1}

			if key[1] > 0:
				print key
		except:
			print "Key event Error"
		
if __name__ == "__main__":
	nv = Nvidia()

	nv.eventKeys() # Yeah we ask for keys here ... like in the usblog (I think it's for the "clear" command)
	
	nv.setRefreshRate()

	eye = 0
	key = 0
	while True:
		t1 = time.time()
		
		nv.setEye(eye)
		eye = 1 - eye
		
		if key == 16:
			nv.eventKeys()
			key = 0
		else:
			key = key + 1
		
		t2 = time.time()
		
		sleep((1.0 / nv.rate) - (t2-t1))

