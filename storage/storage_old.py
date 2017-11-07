import socket 

s = socket.socket() 
host = socket.gethostname()     # Get local machine name
port = 39000
s.bind((host, port))            # Bind to the port
s.listen(5)                     # Now wait for client connection
print 'Storage client is listening'
#serverip

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print 'Got connection from', addr
    data = conn.recv(1024)
    print('data=%s', repr(data))
    if (data.split(' ')[0]== "download"): 
    	try:
			filename = data.split(' ')[1]
			f = open(filename,'rb')
			l = f.read(1024)
			conn.send("1")
			while (l):
				conn.send(l)
				l = f.read(1024)
			f.close()

			print('Done sending')
			conn.close()
    	except :
    		conn.send("0")
    		print('No such file exists')

    #send the server a message informing about this download