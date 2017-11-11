# Distributed storage network #
*This is a course project of CS425A : Computer Networks*

##Requirements
* Python
 + argparse
 + MySQLdb
* MySQL

## Types of devices on the network ##
* Central Server 
+ Storage Client
- Client

## Description
The distributed storage is a Peer-to-peer application. 
Storage clients provide a certain amount of storage to the network. 
The clients (who could also be storage clients) can use the storage provided. 
The server monitors the logistics of the network and provides some guarantees on the availability of files even when some storage clients go down.

## Functionalities

####Upload
To upload a client's file to one of the storage client's storage.
The server provides an IP address to the client upon receiving a request for an upload.
The client uploads the file to the machine with the particular IP.
Then the server takes over and makes copies of the files to allow for storage client crashes by using the **copy** protocol.

####Download
To download a client's file from a storage.
The client sends a download request to the server which provides it with a list of IPs of machines which have the particular file.
The client requests the storage client(selected from the list) for the file.

####Copy
To copy a file to multiple storage clients to ensure the file remains available for download even when a storage client goes down.
Server requests the storage client to copy the file right after an upload to it, to copy the file to another storage client.
This is done multiple times by the server.