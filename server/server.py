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
import config

#  Startup of server
#  Initialize Variables
HOST = '127.0.0.1'
PORT = 10000
OPEN_CONNECTION_LIMIT = 100

#  File and Storage Schemas in the database
file_info = schemas.file
storage_info = schemas.storage

#  Parse Arguments
parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, 
        default=config.HOST, help='IP for the server')
parser.add_argument('--port', type=int, 
        default=config.PORT, help='Port for the server')
parser.add_argument('--open_conn_limit', type=int,
        default=config.OPEN_CONNECTION_LIMIT,
        help='The limit of number of open connections')

args = parser.parse_args()
args_dict = vars(args)

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
open_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
open_socket.bind((args.host, args.port))
open_socket.listen(args.open_conn_limit)
print("Socket Started")

@atexit.register
def cleanup():
    print("Closing connection to socket")
    open_socket.close()

while True:
    #  Accept connection
    conn, addr = open_socket.accept()
    print("Got a connection from {}".format(addr))
    db_handler_thread = db_util.DB_Interface()
    db_handler_thread.connect_db()
    handler_thread = Thread(
            target = conn_handler, args=(conn, addr, db_handler_thread))
    handler_thread.start()
