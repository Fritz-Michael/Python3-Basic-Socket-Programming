import socket
from threading import Thread
from ast import literal_eval

clients = {}
addresses = {}
host = '127.0.0.1'
port = 5678
active = []
addr = (host, port)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(addr)

def broadcast(msg, prefix=""):  # prefix is for name identification.
	"""Broadcasts a message to all the clients."""
	for sock in clients:
		sock.send(bytes(prefix, "utf8")+msg)

def private_message(address,message):
	message = '<private>' + message
	receiver = list(filter(lambda x: address in str(x), clients))[0]
	receiver.send(bytes(message,'utf-8'))

def accept_incoming_connections():
	"""Sets up handling for incoming clients."""
	while True:
		client, client_address = server.accept()
		print(str(client_address[0]) + ":" + str(client_address[1]) + " has connected.")
		addresses[client] = client_address
		Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
	"""Handles a single client connection."""
	name = client.recv(2048).decode("utf8")
	welcome = 'Welcome %s! Enter {quit} to exit.' % name
	try:
		client.send(bytes(welcome, "utf8"))
		msg = "%s: has joined the chat!" % name
		broadcast(bytes(msg, "utf8"))
		clients[client] = name
		temp_client = {'Address':addresses[client],'Name':clients[client]}
		active.append(temp_client)
		broadcast(bytes(str(active),'utf-8'))
		while True:
			msg = client.recv(2048)
			if '(' in msg.decode('utf-8') and ')' in msg.decode('utf-8'):
				temp = msg.decode('utf-8').split(')')
				address = temp[0] + ')'
				private_message(address,temp[1])
			elif msg != bytes("{quit}", "utf8"):
				broadcast(msg, "<global>" + name + ": ")
				print(client)
			else:
				#client.send(bytes("{quit}", "utf8"))
				client.close()
				active.remove({'Address':addresses[client],'Name':clients[client]})
				del clients[client]
				broadcast(bytes("%s has left the chat." % name, "utf8"))
				broadcast(bytes(str(active),'utf-8'))
				break
	except Exception as e:
		print(e)

if __name__ == "__main__":
	server.listen(5)  # Listens for 5 connections at max.
	print("Waiting for connection...")
	accept_clients_thread = Thread(target=accept_incoming_connections)
	accept_clients_thread.start()  # Starts the infinite loop.
	accept_clients_thread.join()
	server.close()

