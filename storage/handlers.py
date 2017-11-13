import os
import subprocess
import socket

from common import *
import config

ENTITY_TYPE = config.ENTITY_TYPE
TOTAL_SPACE = config.TOTAL_SPACE
HOST = config.HOST
PORT = config.PORT
MAX_RETRIES = config.MAX_RETRIES

def conn_handler(conn, addr, args):
    if "host" in args:
        HOST = args["host"]
    if "port" in args:
        PORT = args["port"]
    if "total_space" in args:
        TOTAL_SPACE = args["total_space"]
    if "max_retries" in args:
        MAX_RETRIES = args["max_retries"]
    #  Based on the type of connection call different functions
    req_dict = read_request(recv_line(conn))
    
    if req_dict["type"] == "download":
        handle_download(conn, addr, req_dict)
    elif req_dict["type"] == "upload":
        handle_upload(conn, addr, req_dict)
    elif req_dict["type"] == "copy":
        handle_copy(conn, addr, req_dict)
    conn.close()

def handle_download(conn, addr, req_dict):
    auth = req_dict["auth"]
    filename = req_dict["filename"]
    filepath = os.path.join(auth, filename)
    file_exists = os.path.isfile(filepath)
    print(file_exists)
    if not file_exists:
        msg=make_request(
                entity_type=ENTITY_TYPE,
                type="download_ack",
                filename=filename,
                auth=auth,
                response_code=CODE_FAILURE) 
        conn.send(msg)
        return

    filesize = os.path.getsize(filepath)

    msg=make_request(
            entity_type=ENTITY_TYPE,
            type="download_ack",
            filename=filename,
            filesize=filesize,
            auth=auth,
            response_code=CODE_SUCCESS) 
    conn.send(msg)

    client_ack = read_request(recv_line(conn))
    if client_ack["response_code"] != CODE_SUCCESS:
        return

    with open(filepath,'rb') as f:
        while True:
            data = f.read(SEND_SIZE)
            if not data:
                break
            conn.send(data)

def handle_upload(conn, addr, req_dict):
    auth = req_dict["auth"]
    filename = req_dict["filename"]
    filepath = os.path.join(auth, filename)
    filesize = int(req_dict["filesize"])
    auth_exists = os.path.isdir(auth)
    if not auth_exists:
        os.mkdir(auth)
        #os.chmod(auth)
        #3164 in octal is 500 in decimal
    raw_out=subprocess.Popen(["du","-bs"], stdout=subprocess.PIPE)
    out=str(raw_out.stdout.read())
    used_space=int(out.split("\t")[0])
    print(used_space)
    if(filesize + used_space > TOTAL_SPACE):
        msg=make_request(
                entity_type=ENTITY_TYPE,
                type="upload_ack",
                filename=filename,
                auth=auth,
                response_code=CODE_FAILURE) 
        conn.send(msg)
        conn.close()
        return

    msg=make_request(
            entity_type=ENTITY_TYPE,
            type="upload_ack",
            filename=filename,
            filesize=filesize,
            auth=auth,
            response_code=CODE_SUCCESS) 
    conn.send(msg)
    fsize=0
    with open(filepath,'wb') as f:
        while True:
            data = conn.recv(RECV_SIZE)
            f.write(data)
            fsize+=len(data)
            if len(data)<RECV_SIZE:
                break       

    if(filesize==fsize):
        msg = make_request(
                entity_type=ENTITY_TYPE,
                type="upload_complete_ack",
                filename=filename,
                filesize=filesize,
                auth=auth,
                response_code=CODE_SUCCESS) 
        conn.send(msg)
        msg2 = make_request(
                entity_type=ENTITY_TYPE,
                type="upload_complete_ack",
                filename=filename,
                filesize=filesize,
                auth=auth,
                ip = "{}:{}".format(HOST, PORT),
                response_code=CODE_SUCCESS) 
        # Create a socket to send the upload complete ack to the server
        print("Request to server")
        print(msg2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        sock.connect(( SERVER_IP, SERVER_PORT ))
        sock.send(msg2)
        sock.close()
    else:
        os.system('rm %s 2>&1 >/dev/null'%(filepath))
        msg=make_request(
                entity_type=ENTITY_TYPE,
                type="upload_complete_ack",
                filename=filename,
                filesize=filesize,
                auth=auth,
                response_code=CODE_FAILURE) 
        conn.send(msg)
    conn.close()

def _copy_helper(req_dict):

    # Auth is the auth of the owner of the file
    auth = req_dict["auth"]
    filename = req_dict["filename"]
    filesize = req_dict["filesize"]
    storage_id = req_dict["ip"]
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
    filepath = auth+"/"+filename
    if(storage_response["response_code"] != CODE_SUCCESS):
        return False

    with open(filepath, "rb") as f:
        print ("file opened")
        while True:
            data = f.read(SEND_SIZE)
            if len(data) == 0 :
                send_success = 1
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

def _storage_upload_helper(server_response, auth, filename, filepath, filesize):

    if (server_response["response_code"]==CODE_FAILURE):
        print("Server Error")
        sock.close()
        return False

    storage_id = server_response["ip"]

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

def handle_copy(conn, addr, req_dict):

    conn.close()
    copy_success = False
    copy_success = _copy_helper(req_dict)
    
    if (copy_success != True):
        copy_flag = 0
        # Auth is the auth of the owner of the file
        auth = req_dict["auth"]
        filename = req_dict["filename"]
        filesize = req_dict["filesize"]

        retries = 0
        while retries<MAX_RETRIES:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
            sock.connect(( SERVER_IP, SERVER_PORT ))

            server_request=make_request(
                entity_type = ENTITY_TYPE,
                type ="upload",
                filename=filename,
                filesize=filesize,
                auth=auth,
                )
            print(server_request)
            sock.send(server_request)

            server_res = read_request(recv_line(sock))
            sock.close()
            print(server_res)
            filepath = auth + "/" + filename
            upload_success = _storage_upload_helper(server_res, auth, filename, filepath, filesize)

            if upload_success:
                copy_flag = 1
                break
            else:
                retries += 1

        if copy_flag:
            print ("Copy of "+filename +" is successful")
        else:
            print ("Copy of "+filename +" failed")
    else:
        print ("Copy of "+req_dict["filename"] +" successful")
