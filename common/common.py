
RECV_SIZE = 1024
SEND_SIZE = 1024
SERVER_IP = "127.0.0.1"
SERVER_PORT = 10000
def recv_line(conn):
    data = ""
    data += conn.recv(RECV_SIZE)
    #  data += conn.recv(RECV_SIZE).decode("utf-8")
    return data

def make_request(entity_type, type, filename, auth, filesize = None, ip = None, ip_list = None , response_code = None):
	request = {}
	if(type == "download"):
		request['entity_type'] = entity_type
		request['type'] = "download"
		request['filename'] = filename
		request['ip'] = ip
		request['auth'] = auth
	elif(type == "upload"):
		request['entity_type'] = entity_type
		request['type'] = "upload"
		request['filename'] = filename
		request['filesize'] = filesize
		request['ip'] = ip
		request['auth'] = auth
	elif(type == "download_ack"):
		request['entity_type'] = entity_type
		request['type'] = "download_ack"
		request['ip_list'] = ip_list
		request['response_code'] = response_code
		request['filename'] = filename
		request['filesize'] = filesize
		request['auth'] = auth
	elif(type == "upload_ack"):
		request['entity_type'] = entity_type
		request['type'] = "upload_ack"
		request['ip'] = ip
		request['response_code'] = response_code
		request['filesize'] = filesize
		request['auth'] = auth
	elif(type == "upload_complete_ack"):
		request['entity_type'] = entity_type
		request['type'] = "upload_complete_ack"
		request['filename'] = filename
		request['response_code'] = response_code
		request['filesize'] = filesize
		request['auth'] = auth
	elif(type == "copy"):
		request['entity_type'] = entity_type
		request['type'] = "copy"
		request['filename'] = filename
		request['auth'] = auth
		request['filesize'] = filesize
		request['auth'] = auth
	else:
		return 0

	return str(request)


def read_request(req):
	return (eval(req))


#  Error Codes
CODE_SUCCESS = 300
CODE_FAILURE = 400

