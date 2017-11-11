import random

from common import *
import schemas

ENTITY_TYPE = "server"
AUTH = ""
MAX_RETRIES = 10
def conn_handler(conn, addr, db_handler):
    #  Based on the type of connection call different functions
    req_dict = read_request(recv_line(conn))
    print(req_dict)
    
    if req_dict["type"] == "download":
        handle_download(conn, addr, req_dict, db_handler)
    elif req_dict["type"] == "upload":
        handle_upload(conn, addr, req_dict, db_handler)
    elif req_dict["type"] == "add_storage":
        handle_add_storage(conn, addr, req_dict, db_handler)
    elif req_dict["type"] == "remove_storage":
        pass
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


def handle_upload(conn, addr, req_dict, db_handler):
    auth = req_dict["auth"]
    filename = req_dict["filename"]
    filesize = req_dict["filesize"]
    if "response_code" in req_dict.keys() and \
        req_dict["response_code"] == CODE_FAILURE:
        query = schemas.lock_remove_query.format(
                old_filename=filename,
                old_status = schemas.STORAGE_IP_LOCKED,
                )
        rows_affected = db_handler.run_sql("update", query)
    retries = 0
    while retries<MAX_RETRIES:
        query = schemas.get_ip_suff_storage.format(filesize=filesize)
        print(query)
        id_list = db_handler.run_sql("get", query)
        print("The result is")
        print(id_list)
        if len(id_list) == 0:
            retries += 1
            continue

        locked = False
        lock_attempts = 0
        while(not locked and lock_attempts<len(id_list)):
            lock_attempts+=1
            id = random.choice(id_list)
            id = id[0]
            #  Check if not already locked and try to lock
            #  If successful in locking
            query = schemas.lock_add_query.format(
                    new_filelock = filename,
                    new_status = schemas.STORAGE_IP_LOCKED,
                    storage_ip = id,
                    )
            rows_affected = db_handler.run_sql("update", query)
            if rows_affected==1:
                locked = True
                break
        if locked:
            break
        retries += 1

    if retries == MAX_RETRIES:
        response = make_request(
                    entity_type = ENTITY_TYPE,
                    type = "upload_ack",
                    auth = auth,
                    response_code = CODE_FAILURE,
                    filesize = filesize,
                    filename = filename,
                    ip = "",
                    )
    else:
        response = make_request(
                    entity_type = ENTITY_TYPE,
                    type = "upload_ack",
                    auth = auth,
                    response_code = CODE_SUCCESS,
                    filesize = filesize,
                    filename = filename,
                    ip = id,
                    )
    conn.send(response)

def handle_add_storage(conn, addr, req_dict, db_handler):
    auth = req_dict["auth"]
    storage_space_available = req_dict["storage_space"]
    used_storage_space = req_dict["used_space"]
    port_no = req_dict["port"]
    id = "{}:{}".format(addr[0], port_no)
    query = schemas.storage_check_query.format(storage_ip = id)
    id_count = db_handler.run_sql("get", query)
    id_count = id_count[0][0]
    if (id_count == 0):
        query = schemas.storage_insertion_query.format(
                storage_ip = id,
                storage_space = storage_space_available, 
                used_space = used_storage_space,
                status = 1,
                file_lock = ""
                )
        rows_affected = db_handler.run_sql("insert", query)
        if( rows_affected == 1):
            print("Database entry of", addr[0] +":"+ str(port_no), "made")
            response = make_request(
                        entity_type = ENTITY_TYPE,
                        type = "storage_added_ack",
                        auth = auth,
                        response_code = CODE_SUCCESS,
                        )
        else:
            response = make_request(
                        entity_type = ENTITY_TYPE,
                        type = "storage_added_ack",
                        auth = auth,
                        response_code = CODE_FAILURE,
                        )
    else : 
        print("This machine is already a part of our network")
        response = make_request(
                        entity_type = ENTITY_TYPE,
                        type = "storage_added_ack",
                        auth = auth,
                        response_code = CODE_SUCCESS,
                        )
    conn.send(response)

def handle_remove_storage(conn, addr, db_handler):
    pass
