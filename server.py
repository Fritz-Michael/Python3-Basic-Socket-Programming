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
groups = []

def join_group(msg):
	msg = msg.decode('utf-8')
	info = msg.split('\n')
	group_name = info[0].split(' ')[1]
	group_password = info[1].split(' ')[1]
	group_user = info[2].split(' ')[1]
	is_found = False
	is_approve = False
	for ctr, val in enumerate(groups):
		if val['Name'] == group_name:
			is_found = True
			grp = ctr
			break

	for addr in active:
		if addr['Name'] == group_user:
			print('found address!')
			group_user = addr['Address']

	if is_found:
		print('group found!')
		if groups[ctr]['Password'] == group_password:
			print('correct password!')
			for sock in clients:
				print(sock)
				if str(group_user) in str(sock):
					print('approves!')
					groups[ctr]['Members'].append(sock)
					msg = '#create_group ' + group_name
					sock.send(bytes(msg,'utf-8'))
					is_approve = True
					break

	if not is_approve:
		for sock in clients:
			if str(group_user) in str(sock):
				msg = '<private> Unable to join group'
				sock.send(bytes(msg,'utf-8'))
				is_approve = True
				break

def message_group(msg):
	info = msg.split('\n')
	print(info)
	msg = '#group '
	sender = info[2].split(' ')[1]
	msg += sender + ':  ' + info[1]
	group_name = info[3].split(' ')[1]
	group = list(filter(lambda x: x['Name'] == group_name,groups))[0]

	for member in group['Members']:
		member.send(bytes(msg,'utf-8'))


def create_group(msg):
	members = []
	is_found = False
	group_info = msg.split('\n')
	group_name = group_info[0].split(' ')[1]
	group_password = group_info[1].split(' ')[1]
	group_members = group_info[2].split('/')
	print(group_info[2])
	print(group_members)
	group_members = [x for x in group_members]
	del group_members[0]
	del group_members[-1]
	group_members = [literal_eval(x) for x in group_members]

	for member in group_members:
		for sock in clients:
			print(sock)
			if str(member['Address']) in str(sock):
				members.append(sock)
				print(member)

	members = list(set(members))
	print(members)
	msg = '#create_group ' + group_name
	for member in members:
		member.send(bytes(msg,'utf-8'))
	groups.append({'Name':group_name,'Password':group_password,'Members':members})

def broadcast(msg, prefix=""):  # prefix is for name identification.
	"""Broadcasts a message to all the clients."""
	for sock in clients:
		sock.send(bytes(prefix, "utf8")+msg)

def broadcast_file(msg):
	for sock in clients:
		sock.send(msg)

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
			msg = client.recv(1024)
			if '#join_name' in msg.decode('utf-8'):
				join_group(msg)
			elif '#group_text' in msg.decode('utf-8'):
				message_group(msg.decode())
			elif '#group_name' in msg.decode('utf-8'):
				create_group(msg.decode('utf-8'))
			elif '(' in msg.decode('utf-8') and ')' in msg.decode('utf-8'):
				temp = msg.decode('utf-8').split(')')
				address = temp[0] + ')'
				private_message(address,temp[1])
			elif msg != bytes("{quit}", "utf8"):
				broadcast(msg, "<global>" + name + ": ")
				print(client)
				#client.close()
			elif msg.decode('utf-8') == '{quit}':
				#client.send(bytes("{quit}", "utf8"))
				active.remove({'Address':addresses[client],'Name':clients[client]})
				del clients[client]
				broadcast(bytes("%s has left the chat." % name, "utf8"))
				broadcast(bytes(str(active),'utf-8'))
				break
			else:
				print('hello')
				broadcast_file(msg)
	except Exception as e:
		print(e)

if __name__ == "__main__":
	server.listen(5)  # Listens for 5 connections at max.
	print("Waiting for connection...")
	accept_clients_thread = Thread(target=accept_incoming_connections)
	accept_clients_thread.start()  # Starts the infinite loop.
	accept_clients_thread.join()
	server.close()

