#!/usr/bin/env python

from distutils.core import setup
import glob

if __name__ == "__main__":
	share_files = glob.glob("src/*")
	setup(  name         = 'shutters3d-syncdaemon',
			version      = '0.1.5',
			description  = 'Stereo Glasses Controller',
			author       = 'Magestik',
			author_email = 'bastien@magestik.fr',
			url          = 'http://magestik.fr/packages/',
			license      = 'GNU GPL 3',
			scripts      = ['scripts/shutters3d-syncdaemon'],
			data_files   = [('/etc/dbus-1/system.d', ['scripts/org.stereo3d.shutters.conf']),
							('/usr/share/shutters3d-syncdaemon', share_files)])
