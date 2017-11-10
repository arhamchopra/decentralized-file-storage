from common import *
import schemas

ENTITY_TYPE = "server"
AUTH = ""
def conn_handler(conn, addr, db_handler):
    #  Based on the type of connection call different functions
    req_dict = read_request(recv_line(conn))
    print(req_dict)
    
    if req_dict["type"] == "download":
        pass
    elif req_dict["type"] == "upload":
        pass
    elif req_dict["type"] == "add_storage":
        handle_add_storage(conn, addr, req_dict, db_handler)
    elif req_dict["type"] == "remove_storage":
        pass
    else:
        conn.close()

def handle_download(conn, addr, db_handler):
    pass

def handle_upload(conn, addr, db_handler):
    pass

def handle_add_storage(conn, addr, req_dict, db_handler):
    storage_space_available = req_dict['storage_space']
    port_no = req_dict['port']
    query = schemas.storage_insertion_query.format(storage_ip = addr[0]+':'+str(port_no),storage_space = storage_space_available, used_space = 0,status = 1,file_lock = "")
    if(db_handler.run_sql("insert", query) != 0):
        response = make_request(
                    entity_type = ENTITY_TYPE,
                    type = "storage_added_ack",
                    auth = AUTH,
                    response_code = CODE_SUCCESS,
                    )
    else:
        response = make_request(
                    entity_type = ENTITY_TYPE,
                    type = "storage_added_ack",
                    auth = AUTH,
                    response_code = CODE_FAILURE,
                    )
    
    conn.send(response)
    print("Database entry of", addr[0] +':'+ str(port_no), "made")
    return

def handle_remove_storage(conn, addr, db_handler):
    pass
