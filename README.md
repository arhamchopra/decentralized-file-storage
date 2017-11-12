# Decentralized Storage Network #
*This is a course project of CS425A : Computer Networks*

## Requirements
* Python
     + Libraries : MySQLdb, argparse, socket, atexit, os, random, time, threading, subprocess
* MySQL
* nmap

## Types of devices on the network ##
* Central Server 
+ Storage Server, essentially some clients themselves
- Client

## Description
A decentralized network would consist of two layers of communication. First layer consists of the group of manager nodes serving the network. It usually is dynamically allocated and not static for security reasons. The second layer consists of each of these manager nodes interacting with client nodes connected to them and serving their queries. Because the duration for this project was short, we implement only the second layer of such a network. Once this layer is in place, we could build the first layer on top of it.

## Functionalities

####Upload
To upload a client's file to one of the storage client; The server provides an IP address to the client upon receiving a request for an upload. The client uploads the file to the machine with the particular IP. Then the server takes over and makes copies of the files to allow for storage client crashes, by using the **copy** protocol.

####Download
To download a client's file from a storage; The client sends a download request to the server which provides it with a list of IPs of machines which have the particular file. The client requests the storage client(selected from the list) for the file. The client iterates over the received list of IPs until it receives the file it wants to download.

####Copy
To copy a file to multiple storage clients, to ensure the file remains available for download even when a storage client goes down; After a client finishes an upload to a storage client, the server requests the storage client to copy the file to another storage client. This is done multiple times by the server to copy the file to several nodes.