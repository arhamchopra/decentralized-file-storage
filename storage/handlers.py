from common import *
import os
import subprocess

ENTITY_TYPE = "storage"
TOTAL_SPACE = 1200000
def conn_handler(conn, addr):
    #  Based on the type of connection call different functions
    req_dict = read_request(recv_line(conn))
    
    if req_dict["type"] == "download":
        handle_download(conn, addr, req_dict)
    elif req_dict["type"] == "upload":
        handle_upload(conn, addr, req_dict)
    elif req_dict["type"] == "add_storage":
        pass
    elif req_dict["type"] == "remove_storage":
        pass
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
        msg=make_request(
                entity_type=ENTITY_TYPE,
                type="upload_complete_ack",
                filename=filename,
                filesize=filesize,
                auth=auth,
                response_code=CODE_SUCCESS) 
        conn.send(msg)
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
