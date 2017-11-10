from common import *
import os

ENTITY_TYPE = "storage"
def conn_handler(conn, addr):
    #  Based on the type of connection call different functions
    req_dict = read_request(recv_line(conn))
    
    if req_dict["type"] == "download":
        handle_download(conn, addr, req_dict)
    elif req_dict["type"] == "upload":
        pass
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

def handle_upload(conn, addr, db_handler):
    pass

def handle_add_storage(conn, addr, db_handler):
    pass

def handle_remove_storage(conn, addr, db_handler):
    pass
