# TCP client example
import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 5000))

while 1:
	data = raw_input ( "SEND (TYPE q or Q to Quit):" )
	if (data <> 'Q' and data <> 'q'):
		client_socket.send(data)
	else:
		client_socket.send(data)
		client_socket.close()
		break;
