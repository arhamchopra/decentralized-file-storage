from common import *
import schemas

ENTITY_TYPE = "server"
AUTH = ""
def conn_handler(conn, addr, db_handler):
    #  Based on the type of connection call different functions
    req_dict = read_request(recv_line(conn))
    print(req_dict)
    
    if req_dict["type"] == "download":
        handle_download(conn, addr, req_dict, db_handler)
    elif req_dict["type"] == "upload":
        pass
    elif req_dict["type"] == "add_storage":
        handle_add_storage(conn, addr, req_dict, db_handler)
    elif req_dict["type"] == "remove_storage":
        pass
    else:
        conn.close()

def handle_download(conn, addr, req_dict, db_handler):
    filename = req_dict["filename"]
    auth = req_dict["auth"]
    query = schemas.file_ip_get_query.format(filename=filename)
    print(query)
    ip_list = db_handler.run_sql("get", query)
    if len(ip_list)==0:
        response = make_request(
                entity_type = ENTITY_TYPE,
                type = "download_ack",
                auth = auth,
                filename = filename,
                response_code = CODE_FAILURE,
                )
        conn.send(response)
        #  File not exist
        return
    print(ip_list)
    ip_list = [ip for ip in ip_list[0][0].split(", ")]
    ip_list_available = []
    for ip in ip_list:
        query = schemas.get_ip_status.format(storage_ip=ip)
        print(query)
        status = db_handler.run_sql("get", query)
        print(status)
        if(len(status)!=0 and status[0][0] != schemas.STORAGE_IP_DOWN):
            ip_list_available.append(ip)
    
    print(ip_list)
    print(ip_list_available)
    if(len(ip_list_available) == 0):
        response = make_request(
                entity_type = ENTITY_TYPE,
                type = "download_ack",
                auth = auth,
                filename = filename,
                response_code = CODE_FAILURE,
                )
        conn.send(response)
        #  File not available right now
        return
    response = make_request(
            entity_type = ENTITY_TYPE,
            type = "download_ack",
            auth = auth,
            filename = filename,
            ip_list = ip_list_available,
            response_code = CODE_SUCCESS,
            )
    conn.send(response)


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
