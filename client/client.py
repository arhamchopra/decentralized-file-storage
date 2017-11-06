import socket                   # Import socket module
from client_functions import *

server_ip = socket.gethostname()     # should replace local adress with server ip
port = 39000                 	     # Reserve a port for the service.

action = "download"					 #This will be decided by the action the user wants to perform

#File to download
filename = "test.txt"				 #Also will be given by the user

if (action == "download"):

	##################################################################
	#This Part has to be changed
	#Until the server is coded
	#Assume the server has returned it a list of IPs
	#and we have chosen one, '127.0.0.1'
	##################################################################
	storage_ip = socket.gethostname()

	#Get list of Ips from the server
	#loop through list of ips
	#if download(filename,storage_ip,port):
	#	break

	download(filename, storage_ip, port)

