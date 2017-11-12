import random
import socket

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
        handle_upload2(conn, addr, req_dict, db_handler)
    elif req_dict["type"] == "add_storage":
        handle_add_storage(conn, addr, req_dict, db_handler)
    elif req_dict["type"] == "remove_storage":
        pass
    elif req_dict["type"] == "upload_complete_ack":
        handle_upload_complete(conn, addr, req_dict, db_handler)

    conn.close()

def _remove_lock(db_handler, filename, locked_ip, filesize):
    query = schemas.lock_remove_query.format(
            old_filelock = filename,
            old_status = schemas.STORAGE_IP_LOCKED,
            storage_ip = locked_ip,
            filesize = filesize,
            )
    print(query)
    rows_affected = db_handler.run_sql("update", query)
    if(rows_affected == 1):
        print("Lock was removed")
        return True
    else:
        print("Lock could not be removed")
        return False

def get_filedata(db_handler, filename, auth, filesize):
    query = schemas.file_check_query.format(
            filename = filename,
            owner = auth,
            filesize = filesize,
            )
    print("get_file_data_query")
    print(query)
    file_data = db_handler.run_sql("get", query)
    if len(file_data) == 0:
        return None
    else:
        return file_data[0]

def _insert_file(db_handler, filename, auth, ip, filesize):
    query = schemas.file_add_query.format(
            filename = filename,
            owner = auth,
            ip_list = str(ip),
            filesize = filesize,
            )
    print("add_file_data_query")
    print(query)
    rows_affected = db_handler.run_sql("create", query)
    if rows_affected == 1:
        return True
    else:
        return False

def _update_file(db_handler, filename, auth, ip_list, filesize):
    query = schemas.file_update_query.format(
            filename = filename,
            owner = auth,
            ip_list = str(ip_list),
            filesize = filesize,
            )
    print("update_file_data_query")
    print(query)
    rows_affected = db_handler.run_sql("update", query)
    if rows_affected == 1:
        return True
    else:
        return False

def add_file(db_handler, filename, auth, ip, filesize):
    file_data = get_filedata(db_handler, filename, auth, filesize)
    print("Get file data")
    print(file_data)
    count = 0
    if not file_data:
        is_done = _insert_file(db_handler, filename, auth, ip, filesize)
        if is_done:
            count = 1
        else:
            count = 0

    else:
        print(file_data)
        file_data[3] += ", " + str(ip)
        no_copies = file_data
        is_done = _update_file(db_handler, filename, auth, 
                file_data[3], filesize)
        if is_done:
            count = len(file_data[3].split(", "))
        else:
            count = -1*len(file_data[3].split(", "))
    
    print("Got count")
    print(count)
    return count 

def handle_download(conn, addr, req_dict, db_handler):
    filename = req_dict["filename"]
    auth = req_dict["auth"]
    query = schemas.file_ip_get_query.format(
            filename=filename,
            owner=auth.split(":")[0]
            )
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

def get_new_upload_id(db_handler, filename, filesize):
    new_id = None
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
                new_id = id
                locked = True
                break
        if locked:
            break
        retries += 1
    print("Got id")

    if retries == MAX_RETRIES:
        return None
    else:
        return new_id

def handle_upload2(conn, addr, req_dict, db_handler):
    auth = req_dict["auth"]
    filename = req_dict["filename"]
    filesize = req_dict["filesize"]
    if "response_code" in req_dict.keys() and \
        req_dict["response_code"] == CODE_FAILURE:
        locked_ip = req_dict["ip"]
        is_removed = _remove_lock(db_handler, filename, locked_ip)
        if is_removed:
            print("Lock removed")
        else:
            print("Lock not removed")

    new_id = get_new_upload_id(db_handler, filename, filesize)
    print("Hello")
    if new_id:
        response = make_request(
                    entity_type = ENTITY_TYPE,
                    type = "upload_ack",
                    auth = auth,
                    response_code = CODE_SUCCESS,
                    filesize = filesize,
                    filename = filename,
                    ip = new_id,
                    )
    else:
        response = make_request(
                    entity_type = ENTITY_TYPE,
                    type = "upload_ack",
                    auth = auth,
                    response_code = CODE_FAILURE,
                    filesize = filesize,
                    filename = filename,
                    ip = "",
                    )
    print(response)
    conn.send(response)

def handle_upload_temp(conn, addr, req_dict, db_handler):
    auth = req_dict["auth"]
    filename = req_dict["filename"]
    filesize = req_dict["filesize"]
    if "response_code" in req_dict.keys() and \
        req_dict["response_code"] == CODE_FAILURE:
        locked_ip = req_dict["ip"]
        is_removed = _remove_lock(db_handler, filename, locked_ip, filesize)
        if is_removed:
            print("Lock removed")
        else:
            print("Lock not removed")

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

def handle_upload_complete(conn, addr, req_dict, db_handler):
    auth = req_dict["auth"]
    filename = req_dict["filename"]
    filesize = req_dict["filesize"]
    locked_ip = req_dict["ip"]

    conn.close()

    print("Trying to add")
    no_added = add_file(db_handler, filename, auth, locked_ip, filesize)
    if no_added<=0:
        print("There was some error")
        is_removed = _remove_lock(db_handler, filename, locked_ip, filesize)
        print("Trying to remove lock from ")
        print(locked_ip)
        if not is_removed:
            print("Lock could not be removed")

        return

    if no_added == MAX_COPIES:
        is_removed = _remove_lock(db_handler, filename, locked_ip, filesize)
        print("Trying to remove lock from ")
        print(locked_ip)
        if not is_removed:
            print("Lock could not be removed")

        return

    new_id = get_new_upload_id(db_handler, filename, filesize)

    is_removed = _remove_lock(db_handler, filename, locked_ip, filesize)
    print("Trying to remove lock from ")
    print(locked_ip)
    if not is_removed:
        print("Lock could not be removed")


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    storage_ip = locked_ip.split(":")[0]
    storage_port = int(locked_ip.split(":")[1])
    sock.connect((storage_ip, storage_port))

    if new_id:
        response = make_request(
                    entity_type = ENTITY_TYPE,
                    type = "copy",
                    auth = auth,
                    response_code = CODE_SUCCESS,
                    filesize = filesize,
                    filename = filename,
                    ip = new_id,
                    )
    else:
        response = make_request(
                    entity_type = ENTITY_TYPE,
                    type = "copy",
                    auth = auth,
                    response_code = CODE_FAILURE,
                    filesize = filesize,
                    filename = filename,
                    ip = "",
                    )
    print(response)
    sock.send(response)
    sock.close()

def handle_remove_storage(conn, addr, db_handler):
    pass
