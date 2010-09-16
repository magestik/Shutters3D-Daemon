import urllib, os, sys, shutil

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
if not os.path.exists(dest):
	os.mkdir(dest)
os.rename(temp+'/nvstusb.fw', dest+'/nvstusb.fw')

# Clearing our work directory
print "\nDeleting all files ..."
os.remove(path) # EXE
os.remove(temp+"nvstusb.sys")
os.remove(temp+"nvstusb.bin")
os.rmdir(temp)

