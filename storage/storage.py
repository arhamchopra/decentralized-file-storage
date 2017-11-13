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
import config

#  Startup of server
#  Parse Arguments
parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, 
        default=config.HOST, help='IP for the server')
parser.add_argument('--port', type=int, 
        default=config.PORT, help='Port for the server')
parser.add_argument('--server_ip', type=str, 
        default=config.SERVER_IP, help='IP for the server')
parser.add_argument('--server_port', type=int, 
        default=config.SERVER_PORT, help='Port for the server')
parser.add_argument('--total_space', type=int, 
        default=config.TOTAL_SPACE, 
        help='The space provided by the storage client')
parser.add_argument('--max_retries', type=int, 
        default=config.MAX_RETRIES, 
        help='The number of attempts for upload before failing')
parser.add_argument('--open_conn_limit', type=int,
        default=config.OPEN_CONNECTION_LIMIT,
        help='The limit of number of open connections')

args = parser.parse_args()
args_dict = vars(args)


print("Creating socket to inform the server of storage\'s existence")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
	try:
		sock.connect((args_dict["server_ip"], args_dict["server_port"]))
		
		server_request = make_request(
		            entity_type = config.ENTITY_TYPE,
		            type = "add_storage",
		            auth = config.AUTH,
		            storage_space = args_dict["total_space"],
		            used_space = config.USED_SPACE,
		            port_no = args_dict["port"])
		print(server_request)
		print ("send succ")
		sock.send(server_request)

		server_response=read_request(recv_line(sock))
		print(server_response)
		if(server_response['response_code'] == CODE_SUCCESS):
			break

	except Exception as e:
		print e
		break

sock.close()

print("Server successfully acknowledged")
#  Create an open socket for accepting connections
print("Creating Socket for acceptings connections")
open_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
open_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
open_socket.bind((args_dict["host"], args_dict["port"]))
open_socket.listen(args_dict["open_conn_limit"])
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
            target = conn_handler, args=(conn, addr, args_dict))
    handler_thread.start()
   
