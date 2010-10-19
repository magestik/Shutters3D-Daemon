#######################
 
# consumeservice.py
# consumes a method in a service on the dbus
 
import dbus
 
bus = dbus.SessionBus()
helloservice = bus.get_object('org.stereo3d.shutters', '/org/stereo3d/shutters')
start = helloservice.get_dbus_method('start', 'org.stereo3d.shutters')
swap = helloservice.get_dbus_method('swap', 'org.stereo3d.shutters')
#hello = helloservice.get_dbus_method('swap', 'org.stereo3d.shutters')

print start()
print swap()
