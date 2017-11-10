from common import *


ENTITY_TYPE="client"
AUTH=""

def conn_handler(conn, addr, db_handler):
    #  Based on the type of connection call different functions
    request = recv_line()
    req_dict = parse(request)
    
    if req_dict["type"] == "download":
        
    elif req_dict["type"] == "upload":
        pass
    elif req_dict["type"] == "add_storage":
        pass
    elif req_dict["type"] == "remove_storage":
        pass
    else:
        conn.close()

def handle_download(auth,filename):
    # Create a socket object

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
    
    sock.connect((SERVER_IP,SERVER_PORT))
    server_request=make_request(entity_type=ENTITY_TYPE,type="download",filename=filename,auth=AUTH)
    sock.send(bytes(server_request,'utf-8'))

    server_response=read_request(recv_line(sock))
    storage_id=server_response["ip_list"]

    sock.close()
    flag=0
    for id in storage_id:
    # connect to the server on local computer
        storage_ip=id.split(":")[0]
        storage_port=id.split(":")[1]
        try:
            sock.connect((storage_ip, storage_port))
            msg=make_request(entity_type=ENTITY_TYPE,type="download",filename=filename,auth=AUTH) 
            sock.send(bytes(msg,'utf-8'))
            with open(filename, 'wb') as f:
                print ('file opened')
                while True:
                    print('receiving data...')
                    data = sock.recv(1024)
                    print('data=%s'%(data))
                    if not (len(data)==1024):
                        f.write(data)
                        break
                    # write data to a file
                    f.write(data)

            f.close()
            flag=1
            break
        except:
            continue

    sock.close()
        
    if(flag==1):    
        print('Successfully got the file')
    elif(flag==0):
        print('Download error')
            # # receive data from the server
            # print (repr(sock.recv(1024)))

            # close the connection
            


def handle_upload(conn, addr, db_handler):
    pass

def handle_add_storage(conn, addr, db_handler):
    pass

def handle_remove_storage(conn, addr, db_handler):
    pass
