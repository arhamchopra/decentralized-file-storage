#  Downloadable Modules
import os
import socket
import argparse
import atexit
import time
from threading import Thread

#  Self-made Modules
from handlers import conn_handler

#  Startup of server
#  Initialize Variables
HOST = '127.0.0.1'
PORT = 12345
ENTITIY_TYPE = "storage"
OPEN_CONNECTION_LIMIT = 100

#  Parse Arguments

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
   