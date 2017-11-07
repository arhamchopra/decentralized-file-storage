from common import *

def conn_handler(conn, addr, db_handler):
    #  Based on the type of connection call different functions
    request = recv_line()
    req_dict = parse(request)
    
    if req_dict["type"] == "download":
        pass
    elif req_dict["type"] == "upload":
        pass
    elif req_dict["type"] == "add_storage":
        pass
    elif req_dict["type"] == "remove_storage":
        pass
    else:
        conn.close()

def handle_download(conn, addr, db_handler):
    pass

def handle_upload(conn, addr, db_handler):
    pass

def handle_add_storage(conn, addr, db_handler):
    pass

def handle_remove_storage(conn, addr, db_handler):
    pass
