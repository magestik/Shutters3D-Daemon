#!/usr/bin/env python

from distutils.core import setup
import glob

if __name__ == "__main__":
	data_files = glob.glob("src/*")
	setup(  name         = 'tuxstereoviewer',
			version      = '0.2.3',
			description  = 'Stereo Images Viewer',
			author       = 'Magestik',
			author_email = 'bastien@magestik.fr',
			url          = 'http://magestik.fr/packages/',
			license      = 'GNU GPL 3',
			scripts      = ['datas/tuxstereoviewer'],
			data_files=[('/usr/share/applications', ['datas/tuxstereoviewer.desktop']),
						('/usr/share/pixmaps', ['datas/tuxstereoviewer.png']),
						('/usr/share/tuxstereoviewer', data_files)] )
