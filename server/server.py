#  Downloadable Modules
import os
import socket
import argparse
import atexit
import time
from threading import Thread

#  Self-made Modules
import database_utility as db_util
from ping_utility import ping_service
from handlers import conn_handler
import schemas

#  Startup of server
#  Initialize Variables
HOST = '127.0.0.1'
PORT = 10000
ENTITIY_TYPE = "server"
OPEN_CONNECTION_LIMIT = 100

#  File and Storage Schemas in the database
file_info = schemas.file
storage_info = schemas.storage

#  Load/Create Database
DATABASE_PATH = "./database_state.db"
db_handler = None

#  Parse Arguments

#  Create Database
print("Connecting to database ...")
db_handler = db_util.DB_Interface()
db_handler.connect_db()
print("Connection Successful")

#  Start Ping Service
print("Starting Ping service ...")
ping_thread = Thread(target = ping_service,
        args= (db_handler, storage_info["table_name"], "ip"))
ping_thread.daemon = True
ping_thread.start()
print("Ping Started")

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
    handler_thread = Thread(target = conn_handler, args=(conn, addr))
