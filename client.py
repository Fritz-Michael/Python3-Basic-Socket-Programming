import socket
from threading import Thread 
import tkinter
from tkinter import filedialog
from ast import literal_eval

class Chatme(tkinter.Tk):
    
    def __init__(self,*args,**kwargs):
        tkinter.Tk.__init__(self,*args,**kwargs)
        self.title("Chatme")
        self.geometry('400x400')
        self.active_clients = []
        self.active_clients.insert(0,'global')
        self.messages_frame = tkinter.Frame(self)
        self.active_clients_frame = tkinter.Frame(self)
        self.top_frame = tkinter.Frame(self)
        self.bottom_frame = tkinter.Frame(self)
        self.my_msg = tkinter.StringVar() 
        self.username = tkinter.StringVar()
        self.private_message = tkinter.StringVar()
        self.message = tkinter.StringVar()
        self.message.set('global')
        self.my_msg.set("")
        self.scrollbar = tkinter.Scrollbar(self.messages_frame)
        # Following will contain the messages.
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
        self.send_file_button.grid(row=8,column=0)
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
                    if '[' not in msg:
                        self.msg_list.insert(tkinter.END, msg)
                    else:
                        self.active_clients = literal_eval(msg)
                        self.active_clients.insert(0,'global')
                        self.roles['menu'].delete(0,tkinter.END)
                        self.message.set('global')
                        for client in self.active_clients:
                            self.roles['menu'].add_command(label=client,command=tkinter._setit(self.message,client))
                except:
                    with open('received_file', 'wb') as f:
                        while True:
                            print('receiving data...')
                            data = self.client_socket.recv(1024)
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

    def on_closing(self,event=None):
        """This function is to be called when the window is closed."""
        self.my_msg.set("{quit}")
        self.send()

    def start_thread(self):
        receive_thread = Thread(target=self.receive)
        receive_thread.start()

#----Now comes the sockets part----

if __name__ == '__main__':
    GUI = Chatme()
    GUI.mainloop() 

















# if __name__ == '__main__':
#     host = '127.0.0.1'
#     port = 5678
#     server = (host, port)

#     mySocket = socket.socket()
#     mySocket.connect((host,port))
#     data = mySocket.recv(1024).decode()
#     print(data)
#     username = input("Enter username: ")
#     message = input(username + " -> ")
#     message = username + ": " + message
#     while message != 'q':
#         mySocket.sendto(message.encode(),host)
#         # data = mySocket.recv(1024).decode()
#         # print ('Received from server: ' + data)
#         message = input(username + " -> ")
#         message = username + ": " + message
     
#     mySocket.close()