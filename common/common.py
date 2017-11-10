
RECV_SIZE = 1024
SEND_SIZE = 1024
def recv_line(conn):
    data = ""
    data += conn.recv(RECV_SIZE).decode("utf-8")
    return data

def make_request(entity_type, type, filename = None, auth = None, filesize = None, ip = None, ip_list = None , response_code = None, storage_space = None, port_no = None):
	request = {}
	#download : client -> server
	if(type == "download"):
		request['entity_type'] = entity_type
		request['type'] = "download"
		request['filename'] = filename
		request['ip'] = ip
		request['auth'] = auth
	#upload : client -> servers
	elif(type == "upload"):
		request['entity_type'] = entity_type
		request['type'] = "upload"
		request['filename'] = filename
		request['filesize'] = filesize
		request['ip'] = ip
		request['auth'] = auth
	#download_ack : server -> client
	elif(type == "download_ack"):
		request['entity_type'] = entity_type
		request['type'] = "download_ack"
		request['ip_list'] = ip_list
		request['response_code'] = response_code
		request['filename'] = filename
		request['filesize'] = filesize
		request['auth'] = auth
	#upload_ack : server -> client
	elif(type == "upload_ack"):
		request['entity_type'] = entity_type
		request['type'] = "upload_ack"
		request['ip'] = ip
		request['response_code'] = response_code
		request['filesize'] = filesize
		request['auth'] = auth
	#upload_complete_ack : storage_client -> client
	elif(type == "upload_complete_ack"):
		request['entity_type'] = entity_type
		request['type'] = "upload_complete_ack"
		request['filename'] = filename
		request['response_code'] = response_code
		request['filesize'] = filesize
		request['auth'] = auth
	#copy : server -> storage_client
	elif(type == "copy"):
		request['entity_type'] = entity_type
		request['type'] = "copy"
		request['filename'] = filename
		request['filesize'] = filesize
		request['ip'] = ip 
		request['auth'] = auth
	#add_storage : storage_client -> server
	elif(type == "add_storage"):
		request['entity_type'] = entity_type
		request['type'] = "add_storage"
		request['auth'] = auth
		request['storage_space'] = storage_space
		request['port'] = port_no
	#storage_added_ack : server -> storage_client
	elif(type == "storage_added_ack"):
		request['entity_type'] = entity_type
		request['type'] = "storage_added_ack"
		request['response_code'] = response_code
		request['auth'] = auth

	else:
		return 0

	return str(request)


def read_request(req):
	return (eval(req))


#  Error Codes
CODE_SUCCESS = 300
CODE_FAILURE = 400

