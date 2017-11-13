import os
import socket

from common import *

ENTITY_TYPE="client"
MAIDSAFE_FILEPATH = "./maidsafe/"
MAX_RETRIES = 10

def handler(args):
    #  Based on the command of connection call different functions
    if "dirpath" in args.keys():
        MAIDSAFE_FILEPATH = args["dirpath"]
    if "max_retries" in args.keys():
        MAX_RETRIES = args["max_retries"]

    if args["command"] == "download":
        handle_download(args["auth"], args["filename"])
    elif args["command"] == "upload":
        handle_upload(args["auth"], args["filename"])
    elif args["command"] == "list":
        handle_list()
    else:
        print("Invalid usage, check with instructions")

def handle_download(auth, filename):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.connect((SERVER_IP,SERVER_PORT))

    server_request=make_request(
            entity_type =ENTITY_TYPE,
            type ="download",
            filename=filename,
            auth=auth
            )
    sock.send(server_request)
    server_response=read_request(recv_line(sock))
    if server_response["response_code"] == CODE_FAILURE:
        #  Error Some issue with the server
        return
    id_list=server_response["ip_list"]
    sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # id_list=["127.0.0.1:12345"]
    
    recv_success = 0
    for storage_id in id_list:
        # connect to the server on local computer
        storage_ip = storage_id.split(":")[0]
        storage_port = int(storage_id.split(":")[1])
        try:
            sock.connect((storage_ip, storage_port))

            msg=make_request(
                    entity_type =ENTITY_TYPE,
                    type ="download",
                    filename=filename,
                    auth=auth
                    ) 
            sock.send(msg)
            storage_response=read_request(recv_line(sock))
            if(storage_response["response_code"]!=CODE_SUCCESS):
                continue
            else:
                msg=make_request(
                        entity_type =ENTITY_TYPE,
                        type ="download_ack",
                        filename=filename,
                        auth=auth,
                        response_code=CODE_SUCCESS
                        )
                sock.send(msg)

            with open(filename, "wb") as f:
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
                os.system("rm %s &> /dev/null"%(filename))
                continue
        except:
            continue

    sock.close()
        
    if(recv_success==1):    
        print("Successfully got the file")
    else:
        print("Download error")

def _upload_helper(server_response_code, storage_id, auth, filename, filepath):
    if server_response_code == CODE_FAILURE:
        print("Server Error")
        return False

    filesize = os.path.getsize(filepath)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         

    send_success = 0
    # connect to the server on local computer
    storage_ip = storage_id.split(":")[0]
    storage_port = int(storage_id.split(":")[1])
    print(storage_ip)
    print(storage_port)

    sock.connect((storage_ip, storage_port))
    msg = make_request(
        entity_type = ENTITY_TYPE,
        type ="upload",
        filename = filename,
        filesize = filesize,
        auth = auth
        ) 
    sock.send(msg)
    storage_response = read_request(recv_line(sock))

    if(storage_response["response_code"]!=CODE_SUCCESS):
        return False

    with open(filepath, "rb") as f:
        print ("file opened")
        while True:
            data=f.read(SEND_SIZE)
            if len(data)==0 :
                send_success=1
                break
            sock.send(data)
            #print("data=%s"%(data))
            # write data to a file
    upload_status = False
    if(send_success == 1):
        storage_response_ack = read_request(recv_line(sock))
        if(storage_response_ack["response_code"]==CODE_SUCCESS):
            print("Successfully sent the file")
            upload_status = True
        else:
            print("Upload not successful")
    else:
        print("Upload error")
    
    sock.close()
    return upload_status

def handle_upload(auth, filename):
    print("IIS CALLSEDJK:w")
    file_exists = os.path.isfile(filename)
    if not file_exists:
        print("File doesn't exist")
        return

    filesize = os.path.getsize(filename)
    is_retry = False
    resp_code = -1
    storage_ip = -1

    retries = 0
    while retries<MAX_RETRIES:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
        sock.connect(( SERVER_IP, SERVER_PORT ))

        if is_retry:
            server_request=make_request(
                entity_type = ENTITY_TYPE,
                type ="upload",
                filename=filename,
                filesize=filesize,
                auth=auth,
                response_code = resp_code,
                ip = storage_ip,
                )
        else:
            server_request=make_request(
                entity_type = ENTITY_TYPE,
                type ="upload",
                filename=filename,
                filesize=filesize,
                auth=auth,
                )
        print(server_request)
        sock.send(server_request)

        server_response = read_request(recv_line(sock))
        sock.close()
        print(server_response)
        storage_id = server_response["ip"]
        resp_code = server_response["response_code"]
        upload_success = _upload_helper(resp_code, storage_id, 
                                        auth, filename, filename)

        if upload_success:
            maidsafe_path = os.path.join(MAIDSAFE_FILEPATH, filename)
            open(maidsafe_path, "a").close()
            break;
        else:
            retries += 1

def handle_upload_temp(auth, filename):
    file_exists=os.path.isfile(filename)
    if not file_exists:
        print("File doesn't exist")
        return

    filesize = os.path.getsize(filename)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
    sock.connect(( SERVER_IP, SERVER_PORT ))

    server_request=make_request(
        entity_type =ENTITY_TYPE,
        type ="upload",
        filename=filename,
        filesize=filesize,
        auth=auth,
        )
    print(server_request)
    sock.send(server_request)

    server_response=read_request(recv_line(sock))
    print(server_response)

    if (server_response["response_code"]==CODE_FAILURE):
        print("Server Error")
        sock.close()
        return

    storage_id=server_response["ip"]

    sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         

    # storage_id="127.0.0.1:12345"

    send_success=0
    # connect to the server on local computer
    storage_ip=storage_id.split(":")[0]
    storage_port=int(storage_id.split(":")[1])
    print(storage_ip)
    print(storage_port)

    sock.connect((storage_ip, storage_port))
    msg=make_request(entity_type =ENTITY_TYPE,
        type ="upload",
        filename=filename,
        filesize=filesize,
        auth=auth
        ) 
    sock.send(msg)
    storage_response=read_request(recv_line(sock))
    if(storage_response["response_code"]!=CODE_SUCCESS):
        pass        

    else:
        with open(filename, "rb") as f:
            print ("file opened")
            while True:
                data=f.read(SEND_SIZE)
                if len(data)==0 :
                    send_success=1
                    break
                sock.send(data)
                #print("data=%s"%(data))
                # write data to a file
    if(send_success == 1):
            storage_response_ack = read_request(recv_line(sock))
            if(storage_response_ack["response_code"]==CODE_SUCCESS):
                print("Successfully sent the file")
                maidsafe_path = os.path.join(MAIDSAFE_FILEPATH, filename)
                open(maidsafe_path, "a").close()
            else:
                print("Upload not successful")
    elif(send_success==0):
        print("Upload error")

    sock.close()

def handle_list():
    file_list = os.listdir(MAIDSAFE_FILEPATH)
    for file in file_list:
        print(file)
