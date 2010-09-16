#!/usr/bin/python
# -*- coding: utf-8 -*-
#Programmed by Kaan AKŞİT

try:
  import sys,os,usb.core,usb.util,time
  from array import array
except ImportError, err:
  print "couldn't load module. %s" % (err)
  sys.exit()

class shutterglass:
  def __init__(self,idv,idp):
    self.NVSTUSB_CLOCK       = 48000000
    self.filename            = 'firmware/nvstusb.fw'
    self.mode3d              = 1
    self.eye_count           = 0
    self.endpoints           = []
    self.interface           = []
    self.idv                 = idv
    self.idp                 = idp
    self.eye                 = 0
    self.cap                 = '\x1b\x5b1;33;32m' + 'ID: '+ hex(self.idv) + ':' + hex(self.idp) + '\x1b[0m'
    self.detect_device()
    self.reset()
    if self.dev is None:
      print self.cap + ' NVIDIA stereo controller \x1b\x5b1;31;40mNOT\x1b[0m found!'
      sys.exit()
    else:
      print self.cap, 'NVIDIA stereo controller found!'
      time.sleep(1)
    if len(self.endpoints) == 0:
      print self.cap, 'NVIDIA stereo controller does \x1b\x5b1;31;40mNOT\x1b[0m have required firmware!'
      self.upload_firmware(self.filepath(self.filename))
      self.release_device()
      self.detect_device()
    return
  def detect_device(self):
    self.dev = usb.core.find(idVendor=self.idv, idProduct=self.idp)
    self.dev.set_configuration()
    self.detect_endpoints()
    return
  def detect_endpoints(self):
    for cfg in self.dev:
      for i in cfg:
        self.interface.append(i.bInterfaceNumber)
        for e in i:
          self.endpoints.append(e.bEndpointAddress)
    return
  def release_device(self):
    self.reset()
    usb.util.release_interface(self.dev,self.interface[0])
    time.sleep(3)
    return
  def filepath(self,filename):
    data_py  = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.normpath(os.path.join(data_py, '..', 'datas'))
    return os.path.join(data_dir, filename)
  def upload_firmware(self,filename):
    firmware = open(filename,'rw')
    print self.cap, 'Started to upload the firmware to NVIDIA stereo controller!'
    lenPos = firmware.read(4)
    while len(lenPos) !=  0:
      length = (ord(lenPos[0])<<8) | ord(lenPos[1])
      pos    = (ord(lenPos[2])<<8) | ord(lenPos[3])
      buf    = firmware.read(length)
      res    = self.dev.ctrl_transfer(0x40, 0xA0, pos, 0x000,buf,0)
      if res < 0:
        print self.cap, 'Firmware of NVIDIA stereo controller \x1b\x5b1;31;40mfailed!\x1b[0m!'
        self.reset()
        return False
      lenPos = firmware.read(4)
    firmware.close()
    print self.cap, 'Firmware of NVIDIA stereo controller is uploaded!'
    return True
  def write(self,data,epn=2):
    self.dev.write(self.endpoints[epn],data)
    #print self.cap, 'NVIDIA stereo controller received the data. \x1b\x5b1;33;32m->\x1b[0m', str(data)
    return True
  def read(self):
    data = self.dev.read(self.endpoints[3],512)
    #print self.cap, 'Data received from NVIDIA stereo controller. \x1b\x5b1;31;40m<-\x1b[0m', str(data)
    return data 
  def reset(self):
    try:
      self.dev.reset()
    except usb.core.USBError:
      pass
    return True
  def NVSTUSB__COUNT(self,us,CLOCK):
    result = (-(us)*(float(CLOCK)/1000000)+1)
    return result
  def set_rate(self,rate=120):
    self.get_keys()
    self.frameTime   = 1000000/rate
    self.activeTime  = 2080
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
    print self.cap, 'New values sent!'
    return True
  def swap_eye(self,r=0):
    self.eye = 1 - self.eye
    self.set_eye(self.eye,r)
    return True
  def set_eye(self,eye=0,r=0):
    if self.mode3d == 1:
      self.eye = eye
      #print self.cap, 'Setting open eye...'
      self.write([0xAA,0xff if eye%2 else 0xfe,0x00,0x00,r>>8&0xff,r>>16&0xff,0xff,0xff],0)
      #print self.cap, 'Left' if eye%2 else 'Right', 'eye is open.'
    if self.eye_count == 16:
      self.get_keys()
      self.eye_count = 0
    self.eye_count += 1
    return True
  def get_keys(self):
    #print self.cap, 'Requesting key status...'
    self.write([0x42, 0x18, 0x03, 0x00])
    readBuf = self.read()
    if len(readBuf) == 7:
      deltaWheel = readBuf[4]
      toggled3D  = readBuf[6] & 0x01
      #print self.cap, 'Delta wheel:',deltaWheel, 'Toggled 3D: ',toggled3D
      self.mode3d = toggled3D ^ self.mode3d
    return True
  def close_device(self):
    cmd1 = [0x02,0x1b,0x01,0x00]
    self.write(cmd1)
    data = self.read()
    cmd0x1b = [0x01,0x1b,0x01,0x00,0x03]
    self.write(cmd0x1b)
    print '\n',self.cap, 'NVIDIA stereo controller is disconnected!'
    #buf = [0xaa,0xFF,0x00,0x00,0x71,0xD9,0xFF,0xFF]
    #self.write(buf,1)
    return True

def main():
  glass = shutterglass(0x0955,0x0007)
  rate  = 65
  glass.set_rate(rate)
  while True:
    try:
      t1 = time.time()
      glass.swap_eye()
      delay =  1./rate - time.time() +  t1
      if delay > 0:
        time.sleep(delay)
    except KeyboardInterrupt:
      glass.close_device()
      sys.exit()
  return

if __name__ == "__main__":
  sys.exit(main())

