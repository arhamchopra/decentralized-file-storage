import socket

from common import *
import os

ENTITY_TYPE="client"
#  Add AUTH data here or it wont work
AUTH=""

def handler(arg):
    #  Based on the type of connection call different functions
    if arg["type"] == "download":
        handle_download(arg["auth"], arg["filename"])
        
    elif arg["type"] == "upload":
        pass
    elif arg["type"] == "add_storage":
        pass
    elif arg["type"] == "remove_storage":
        pass
    else:
        conn.close()

def handle_download(auth, filename):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.connect((SERVER_IP,SERVER_PORT))

    server_request=make_request(
            entity_type=ENTITY_TYPE,
            type="download",
            filename=filename,
            auth=AUTH)
    sock.send(server_request)
    server_response=read_request(recv_line(sock))
    if server_response["response_code"] == CODE_FAILURE:
        #  Error Some issue with the server
        return
    id_list=server_response["ip_list"]
    sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    recv_success = 0
    for storage_id in id_list:
        # connect to the server on local computer
        storage_ip = storage_id.split(":")[0]
        storage_port = int(storage_id.split(":")[1])
        try:
            sock.connect((storage_ip, storage_port))
            msg=make_request(
                    entity_type=ENTITY_TYPE,
                    type="download",
                    filename=filename,
                    auth=AUTH) 
            sock.send(msg)
            storage_response=read_request(recv_line(sock))
            if(storage_response["response_code"]!=CODE_SUCCESS):
                continue
            else:
                msg=make_request(
                        entity_type=ENTITY_TYPE,
                        type="download_ack",
                        filename=filename,
                        auth=AUTH,
                        response_code=CODE_SUCCESS) 
                sock.send(msg)


            with open(filename, 'wb') as f:
                filesize=0
                while True:
                    data = sock.recv(RECV_SIZE)
                    # write data to a file
                    f.write(data)
                    filesize+=len(data)
                    if not data :
                        break

            if(storage_response["filesize"]==filesize):
                recv_success=1
                break
            else:
                os.system('rm %s &> /dev/null'%(filename))
                continue
        except:
            continue

    sock.close()
        
    if(recv_success==1):    
        print('Successfully got the file')
    else:
        print('Download error')
            

def handle_upload(conn, addr, db_handler):
    pass

def handle_add_storage(conn, addr, db_handler):
    pass

def handle_remove_storage(conn, addr, db_handler):
    pass
