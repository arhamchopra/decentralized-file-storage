import socket
def download(filename, IP, port):

	s = socket.socket()             # Create a socket object
	s.connect((IP, port))
	s.send("download " + filename)

	flag_download = 0
	with open(filename, 'wb') as f:
		print ('file created')
		data = s.recv(1024)
		print(data)
		if(data[0] == "1"):
			print('receiving data...')
			flag_download = 1
			data = data[1:]
			f.write(data)
			while True:
				data = s.recv(1024)
				if not data:
					break
		        
		        f.write(data) 				# write data to a file
			print('Successfully downloaded the file')


	f.close()
	s.close()
	print('connection closed')
	return flag_download