import dbus, sys, time

try:
	bus = dbus.SessionBus()
	shutters = bus.get_object('org.stereo3d.shutters', '/org/stereo3d/shutters')
except:
	sys.exit("Can't connect to the daemon !")

start = shutters.get_dbus_method('start', 'org.stereo3d.shutters')
swap = shutters.get_dbus_method('swap', 'org.stereo3d.shutters')
stop = shutters.get_dbus_method('stop', 'org.stereo3d.shutters')

start()

while 1:
	try:
		eye = swap()
		time.sleep(1/120)
		#if eye == 'left' or eye == 'right':
	except:
		break

stop()
