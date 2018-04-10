import socket
from threading import Thread 
import tkinter
from tkinter import *
from tkinter import filedialog
from ast import literal_eval

class GroupChat(tkinter.Tk):
	def __init__(self, socket, username, name,*args,**kwargs):
		tkinter.Tk.__init__(self,*args,**kwargs)

		self.my_msg = tkinter.StringVar() 
		self.username = username
		self.group_name = name
		self.my_msg.set("")
		self.client_socket = socket

		self.title(name + 'Chat room')
		self.geometry('400x400')

		self.messages_frame = tkinter.Frame(self)
		self.active_clients_frame = tkinter.Frame(self)
		self.top_frame = tkinter.Frame(self)
		self.bottom_frame = tkinter.Frame(self)

		self.scrollbar = tkinter.Scrollbar(self.messages_frame)
		self.msg_list = tkinter.Listbox(self.messages_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)

		self.scrollbar.grid(row=4,column=1,rowspan=3,sticky=tkinter.N+tkinter.S)
		self.msg_list.grid(row=4,column=0,rowspan=3)

		self.entry_field = tkinter.Entry(self.bottom_frame, textvariable=self.my_msg)
		self.send_button = tkinter.Button(self.bottom_frame, text="Send", command=self.send)
		self.entry_field.bind("<Return>", self.send)

		self.send_button.grid(row=7,column=0)
		self.entry_field.grid(row=6,column=0)

		self.top_frame.grid(row=0,column=0)
		self.messages_frame.grid(row=1,column=0)
		self.active_clients_frame.grid(row=1,column=1)
		self.bottom_frame.grid(row=2,column=0)

		#self.initialize_sockets()
		self.start_thread()

	def initialize_sockets(self):
		self.host = '127.0.0.1'
		self.port = 5678

		self.buffer = 1024
		self.address = (self.host, self.port)

		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect(self.address)

	def send(self):
		msg = '#group_text ' + '\n'
		msg +=  self.entry_field.get() + '\n'
		msg += '#sender ' + self.username + '\n'
		msg += '#name ' + self.group_name

		self.my_msg.set("")  # Clears input field.
		self.client_socket.send(bytes(msg, "utf8"))

	def receive(self):
		while True:
			msg = self.client_socket.recv(1024).decode('utf-8')
			if '#group' in msg:
				msg = msg.split(' ')
				del msg[0]
				msg = ''.join(msg)
				self.msg_list.insert(tkinter.END, msg)

	def start_thread(self):
		receive_thread = Thread(target=self.receive)
		receive_thread.start()




class DialogEntry(tkinter.Tk):
	def __init__(self, members, socket, username,*args,**kwargs):
		tkinter.Tk.__init__(self,*args,**kwargs)

		#init ui
		self.group_name = tkinter.StringVar()
		self.group_password = tkinter.StringVar()
		self.roles = tkinter.StringVar()
		self.roles.set('None')
		self.group_members = members
		self.client_socket = socket
		self.username = username

		self.group_name_label = tkinter.Label(self,text="Group Name:")
		self.group_name_field = tkinter.Entry(self, textvariable=self.group_name)

		self.group_password_label = tkinter.Label(self,text="Group Password:")
		self.group_password_field = tkinter.Entry(self, textvariable=self.group_password)

		self.members = tkinter.Listbox(self,selectmode=tkinter.MULTIPLE,width=50)
		for member in self.group_members:
			self.members.insert(tkinter.END,member)

		self.create_group_button = tkinter.Button(self,text="Create Group",command=self.create_group)

		#grid
		self.group_name_label.grid(row=0,column=0)
		self.group_name_field.grid(row=0,column=1)

		self.group_password_label.grid(row=1,column=0)
		self.group_password_field.grid(row=1,column=1)

		self.members.grid(row=2,column=0,columnspan=2)

		self.create_group_button.grid(row=3,column=0,columnspan=2)

	def create_group(self):
		msg = '#group_name ' + self.group_name_field.get() + '\n'
		msg += '#group_password ' + self.group_password_field.get() + '\n'
		msg += '#group_members '
		for member in self.members.curselection():
			msg += str(self.group_members[member]) + ' '
		self.client_socket.send(bytes(msg,'utf-8'))
		self.destroy()



class DialogJoin(tkinter.Tk):
	def __init__(self, socket, username,*args,**kwargs):
		tkinter.Tk.__init__(self,*args,**kwargs)

		#init ui
		self.group_name = tkinter.StringVar()
		self.group_password = tkinter.StringVar()
		self.client_socket = socket
		self.username = username

		self.group_name_label = tkinter.Label(self,text="Group Name:")
		self.group_name_field = tkinter.Entry(self, textvariable=self.group_name)

		self.group_password_label = tkinter.Label(self,text="Group Password:")
		self.group_password_field = tkinter.Entry(self, textvariable=self.group_password)

		self.join_group_button = tkinter.Button(self,text="Join Group",command=self.join_group)

		#grid
		self.group_name_label.grid(row=0,column=0)
		self.group_name_field.grid(row=0,column=1)

		self.group_password_label.grid(row=1,column=0)
		self.group_password_field.grid(row=1,column=1)

		self.join_group_button.grid(row=3,column=0,columnspan=2)

	def join_group(self):
		msg = '#join_name ' + self.group_name_field.get() + '\n'
		msg += '#join_password ' + self.group_password_field.get() + '\n'
		msg += '#join_user ' + self.username
		self.client_socket.send(bytes(msg,'utf-8'))
		self.destroy()




class Chatme(tkinter.Tk):
    
	def __init__(self,*args,**kwargs):
		tkinter.Tk.__init__(self,*args,**kwargs)

		self.active_clients = []
		self.active_clients.insert(0,'global')
		self.my_msg = tkinter.StringVar() 
		self.username = tkinter.StringVar()
		self.private_message = tkinter.StringVar()
		self.message = tkinter.StringVar()
		self.message.set('global')
		self.my_msg.set("")


		self.title("Chatme")
		self.geometry('400x400')

		self.messages_frame = tkinter.Frame(self)
		self.active_clients_frame = tkinter.Frame(self)
		self.top_frame = tkinter.Frame(self)
		self.bottom_frame = tkinter.Frame(self)

		self.scrollbar = tkinter.Scrollbar(self.messages_frame)

		self.username_label = tkinter.Label(self.top_frame,text='Username:')
		self.username_field = tkinter.Entry(self.top_frame, textvariable=self.username)
		self.username_field.bind("<Return>", self.set_username)
		self.username_button = tkinter.Button(self.top_frame,text='Set',command=self.set_username)
		self.roles = tkinter.OptionMenu(self.messages_frame,self.message,*self.active_clients)
		self.msg_list = tkinter.Listbox(self.messages_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)

		self.username_label.grid(row=0,column=0)
		self.username_field.grid(row=1,column=0)
		self.username_button.grid(row=2,column=0)
		self.roles.grid(row=3,column=0,columnspan=2,sticky=tkinter.W+tkinter.E)
		self.scrollbar.grid(row=4,column=1,rowspan=3,sticky=tkinter.N+tkinter.S)
		self.msg_list.grid(row=4,column=0,rowspan=3)

		self.entry_field = tkinter.Entry(self.bottom_frame, textvariable=self.my_msg)
		self.send_button = tkinter.Button(self.bottom_frame, text="Send", command=self.send)
		self.send_button.configure(state='disabled')
		self.entry_field.bind("<Return>", self.send)
		self.send_file_button = tkinter.Button(self.bottom_frame, text="Send File", command=self.send_file)

		self.send_button.grid(row=7,column=0)
		self.send_file_button.grid(row=7,column=1)
		self.entry_field.grid(row=6,column=0)

		self.top_frame.grid(row=0,column=0)
		self.messages_frame.grid(row=1,column=0)
		self.active_clients_frame.grid(row=1,column=1)
		self.bottom_frame.grid(row=2,column=0)

		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.initialize_sockets()
		self.start_thread()


	def initialize_sockets(self):
		self.host = '127.0.0.1'
		self.port = 5678

		self.buffer = 1024
		self.address = (self.host, self.port)

		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect(self.address)

	def receive(self):
		"""Handles receiving of messages."""
		while True:
			try:
				try:
					msg = self.client_socket.recv(self.buffer).decode('utf-8')
					if '#create_group' in msg:
						msg = msg.split(' ')
						group_name = msg[1]
						self.group_chat = GroupChat(self.client_socket,self.username.get(),group_name)
						self.group_chat.mainloop()
					elif '#group' in msg:
						pass
					elif '[' not in msg:
						self.msg_list.insert(tkinter.END, msg)
					else:
						self.active_clients = literal_eval(msg)
						self.active_clients.insert(0,'global')
						self.roles['menu'].delete(0,tkinter.END)
						self.message.set('global')
						for client in self.active_clients:
							self.roles['menu'].add_command(label=client,command=tkinter._setit(self.message,client))
				except Exception as e:
					with open('received_file', 'wb') as f:
						while True:
							data = self.client_socket.recv(2048)
							print('data=%s', (data))
							if not data:
								break
							f.write(data)
			except OSError:  # Possibly client has left the chat.
				break


	def send(self,event=None):  # event is passed by binders.
		"""Handles sending of messages."""
		msg = self.my_msg.get()
		self.my_msg.set("")  # Clears input field.
		if msg == "{quit}":
			self.client_socket.send(bytes(msg, "utf8"))
			self.client_socket.close()
			self.quit()
		elif self.message.get() == 'global':
			print('global chat')
			self.client_socket.send(bytes(msg, "utf8"))
		else:
			msg = str(literal_eval(self.message.get())['Address']) + ' From ' + self.username.get() + ': ' + msg
			self.client_socket.send(bytes(msg, "utf8"))


	def send_file(self):
		self.filename = filedialog.askopenfilename()
		temp = open(self.filename,'rb')
		self.client_socket.sendfile(temp)

	def set_username(self,event=None):
		username = self.username.get()
		self.client_socket.send(bytes(username,'utf-8'))
		self.username_button.configure(state='disabled')
		self.username_field.configure(state='disabled')
		self.send_button.configure(state='normal')
		self.username_field.grid_forget()
		self.username_label.grid_forget()
		self.username_button.grid_forget()
		self.create_group_button = tkinter.Button(self.top_frame,text="Create Group",command=self.create_group)
		self.create_group_button.grid(row=1,column=0)
		self.join_group_button = tkinter.Button(self.top_frame,text="Join Group",command=self.join_group)
		self.join_group_button.grid(row=1,column=1)

	def on_closing(self,event=None):
		"""This function is to be called when the window is closed."""
		self.my_msg.set("{quit}")
		self.send()

	def start_thread(self):
		receive_thread = Thread(target=self.receive)
		receive_thread.start()

	def create_group(self):
		self.group_dialog = DialogEntry(self.active_clients,self.client_socket,self.username.get())
		self.group_dialog.mainloop()


	def join_group(self):
		self.join_dialog = DialogJoin(self.client_socket,self.username.get())
		self.join_dialog.mainloop()



if __name__ == '__main__':
	GUI = Chatme()
	GUI.mainloop() 
