
def make_request(entity_type, type, filename, filesize = None, auth, ip = None, ip_list = None , response_code = None):
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
	elif(type == "upload_ack"):
		request['entity_type'] = entity_type
		request['type'] = "upload_ack"
		request['ip'] = ip
		request['response_code'] = response_code
	elif(type == "upload_complete_ack"):
		request['entity_type'] = entity_type
		request['type'] = "upload_complete_ack"
		request['filename'] = filename
		request['response_code'] = response_code
	elif(type == "copy"):
		request['entity_type'] = entity_type
		request['type'] = "copy"
		request['filename'] = filename
		request['auth'] = auth
	else:
		return 0

	return str(request)

def read_request(req):
	return (eval(req))