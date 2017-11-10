#  Downloadable Modules
import os
import socket
import argparse
import atexit
import time
from threading import Thread

#  Self-made Modules
from handlers import conn_handler
from common import *
#  Startup of server
#  Initialize Variables
HOST = '127.0.0.1'
PORT = 18000
ENTITY_TYPE = "storage"
OPEN_CONNECTION_LIMIT = 100
AUTH = ""
AVAILABLE_SPACE = 1000 #Get this from user who is running the storage client
#  Parse Arguments

SERVER_IP = HOST
#  Create a socket to inform the server that this storage client is up
SERVER_PORT = 10000
print("Creating socket to inform the server of storage\'s existence")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while (1):
	try:
		sock.connect((SERVER_IP, SERVER_PORT))
		
		server_request = make_request(
		            entity_type=ENTITY_TYPE,
		            type="add_storage",
		            auth=AUTH,
		            storage_space = AVAILABLE_SPACE,
		            port_no = PORT)
		print(server_request)
		print ("send succ")
		sock.send(server_request)

		server_response=read_request(recv_line(sock))
		print(server_response)
		if(server_response['response_code'] == CODE_SUCCESS):
			break

	except Exception as e:
		print e

sock.close()

print("Server successfully acknowledged")
#  Create an open socket for accepting connections
print("Creating Socket for acceptings connections")
open_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
open_socket.bind((HOST, PORT))
open_socket.listen(OPEN_CONNECTION_LIMIT)
print("Socket Started")

@atexit.register
def cleanup():
    print("Closing connection to socket")
    open_socket.close()

while True:
    #  Accept connection
    conn, addr = open_socket.accept()
    print("Got a connection from {}".format(addr))
    handler_thread = Thread(
            target = conn_handler, args=(conn, addr))
    handler_thread.start()
