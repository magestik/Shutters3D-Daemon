#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
	import sys, os, time
	import usb.core, usb.util
	import urllib
	from array import array
except ImportError, err:
	print "couldn't load module. %s" % (err)
	sys.exit()

class shutters:
	def __init__(self):
		self.firm_dir	= os.path.expanduser("~") + '/.nvidia3D/'
		self.firm_name 	= 'nvstusb.fw'
		
		self.NVSTUSB_CLOCK = 48000000
		
		self.mode3d = 1
		self.eye_count = 0
		self.endpoints = []
		self.interface = []
		self.detect_device()
		self.reset()
		
		if self.dev is None:
			print 'NVIDIA stereo controller NOT found!'
			sys.exit()
		else:
			print 'NVIDIA stereo controller found!'
			time.sleep(1)
		
		if len(self.endpoints) == 0:
			print 'NVIDIA stereo controller does NOT have required firmware!'
			if not os.path.exists(self.firm_dir+self.firm_name):
				self.download_firmware()
			self.upload_firmware()
			self.release_device()
			time.sleep(1)
			self.detect_device()
		
		self.get_keys() # Get Keys at the beginning ... Why ?
		return
	
	def __del__(self):
		self.close_device()
		self.release_device()

	#
	# USB functions
	#
	def detect_device(self): # Looking for the device
		self.dev = usb.core.find(idVendor=0x0955, idProduct=0x0007)
		self.dev.set_configuration()
		self.detect_endpoints()
		return
	
	def detect_endpoints(self): # Detecting all (actually 4) endpoints
		for cfg in self.dev:
			for i in cfg:
				self.interface.append(i.bInterfaceNumber)
				for e in i:
					self.endpoints.append(e.bEndpointAddress)
		return
	
	def write(self,data,epn=2): # Write to an endpoint
		self.dev.write(self.endpoints[epn],data)
		return True
	
	def read(self): # Read from an endpoint
		data = self.dev.read(self.endpoints[3],512)
		return data
	
	def release_device(self): # Release USB interface
		self.reset()
		usb.util.release_interface(self.dev,self.interface[0])
		time.sleep(3)
		return
		
	def reset(self): # Reset USB
		try:
			self.dev.reset()
		except usb.core.USBError:
			pass
		return True
	
	#
	# Glasses control functions
	#
	def NVSTUSB__COUNT(self,us,CLOCK):
		result = (-(us)*(float(CLOCK)/1000000)+1)
		return result
	
	def set_rate(self,rate=120): # Set refresh rate	
		self.frameTime = 1000000/rate
		self.activeTime = 2080
		w = int(self.NVSTUSB__COUNT(4568.50,self.NVSTUSB_CLOCK/4))
		x = int(self.NVSTUSB__COUNT(4774.50,self.NVSTUSB_CLOCK/12))
		y = int(self.NVSTUSB__COUNT(self.activeTime,self.NVSTUSB_CLOCK/12))
		z = int(self.NVSTUSB__COUNT(self.frameTime,self.NVSTUSB_CLOCK/4))
		
		self.cmdTimings = [0x01,0x00,0x18,0x00,w&0xFF,w>>8&0xFF,w>>16&0xFF,w>>24&0xFF,x&0xFF,x>>8&0xFF,x>>16&0xFF,x>>24&0xFF,y&0xFF,y>>8&0xFF,y>>16&0xFF,y>>24&0xFF,0x30,0x28,0x24,0x22,0x0a,0x08,0x05,0x04,z&0xFF,z>>8&0xFF,z>>16&0xFF,z>>24&0xFF]
		#self.cmdTimings = [0x01,0x00,0x18,0x00,0xE1,0x29,0xFF,0xFF,0x68,0xB5,0xFF,0xFF,0x81,0xDF,0xFF,0xFF,0x30,0x28,0x24,0x22,0x00,0x08,0x05,0x04,0x61,0x79,0xF9,0xFF]
		
		self.write(self.cmdTimings)
		self.write([0x01,0x1c,0x02,0x00,0x02,0x00])
		self.write([0x01,0x1e,0x02,0x00,rate*2,(rate*2)>>8&256])
		self.write([0x01,0x1b,0x01,0x00,0x07])
		self.write([0x40,0x18,0x03,0x00])
		print 'New rate sent!'
		return True
	
	def set_eye(self, eye=0, r=0): # Swap eyes
		if self.mode3d == 1:
			self.write([0xAA,0xff if eye%2 else 0xfe,0x00,0x00,r>>8&0xff,r>>16&0xff,0xff,0xff],0)
		
		if self.eye_count == 16:
			self.get_keys()
			self.eye_count = 0
		
		self.eye_count += 1
		return True
	
	def get_keys(self): # Get keys status
		self.write([0x42, 0x18, 0x03, 0x00])
		readBuf = self.read()
		if len(readBuf) == 7:
			deltaWheel = readBuf[4]
			toggled3D = readBuf[6] & 0x01
			#print self.cap, 'Delta wheel:',deltaWheel, 'Toggled 3D: ',toggled3D
			self.mode3d = toggled3D ^ self.mode3d
		return True
	
	def close_device(self): # Shutdown glasses
		cmd1 = [0x02,0x1b,0x01,0x00]
		self.write(cmd1)
		data = self.read()
		cmd0x1b = [0x01,0x1b,0x01,0x00,0x03]
		self.write(cmd0x1b)
		print 'NVIDIA stereo controller is disconnected!'
		#buf = [0xaa,0xFF,0x00,0x00,0x71,0xD9,0xFF,0xFF]
		#self.write(buf,1)
		return True
	
	#
	# Firmware functions
	#
	def upload_firmware(self): # Upload firmware to usb
		filename = self.firm_dir+self.firm_name
		firmware = open(filename,'rw')
		print 'Started to upload the firmware to NVIDIA stereo controller!'
		lenPos = firmware.read(4)
		while len(lenPos) != 0:
			length = (ord(lenPos[0])<<8) | ord(lenPos[1])
			pos = (ord(lenPos[2])<<8) | ord(lenPos[3])
			buf = firmware.read(length)
			res = self.dev.ctrl_transfer(0x40, 0xA0, pos, 0x000,buf,0)
			if res < 0:
				print 'Firmware of NVIDIA stereo controller failed!'
				self.reset()
				return False
			lenPos = firmware.read(4)
		firmware.close()
		print 'Firmware of NVIDIA stereo controller is uploaded!'
		return True
			
	def download_firmware(self): # Download and extract firmware from nvidia.com
		print "Starting firmware upgrade ..."
		dest	= os.path.expanduser("~") + '/.nvidia3D/' # Where the firmware has to be
		temp 	= '/tmp/nvidia3D/' # Work directory
		name 	= 'NVIDIA_3D_Vision_v258.96_driver.exe'
		path	= temp + name
		
		# Creating and going to our work directory
		if not os.path.exists(temp):
			os.mkdir(temp)
		
		os.chdir(temp)
		
		# Downloading the windows executable
		if not os.path.exists(path):
			print "\nDownloading "+ name +" ..."
			urllib.urlretrieve('http://fr.download.nvidia.com/Windows/3d_vision_stereo/'+ name, path)
		else:
			print "\n"+ name+" is already downloaded !"
		
		# Extraction the sys file from the exe
		print "Extracting nvstusb.sys ...\n"
		os.system("cabextract -F nvstusb.sys "+path)
		
		# Extracting the fw file from the sys
		print "\nExtracting nvstusb.fw ..."
		os.system(sys.path[0]+"/extractfw nvstusb.sys") # you need to compile extractfw
		
		# Moving the firmware where it has to be
		if not os.path.exists(self.firm_dir):
			os.mkdir(self.firm_dir)
			
		os.rename(temp+'/nvstusb.fw', self.firm_dir+self.firm_name)
		
		# Clearing our work directory
		print "\nDeleting all files ..."
		os.remove(path) # EXE
		os.remove(temp+"nvstusb.sys")
		os.remove(temp+"nvstusb.bin")
		os.rmdir(temp)
