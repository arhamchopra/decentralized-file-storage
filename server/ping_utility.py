import os
import time

import schemas

PING_TIMEOUT = 0.5
#  Change the way response to queries are handled
def ping_service(db_handler, ip_table_name, ip_col_name):
    while True:
        #  Get the list of ips from DB
        id_list = db_handler.run_sql("get", schemas.storage_ip_get_query)
        #  Ping each ip and update the status of corresponding ip if necessary
        for id in id_list:
            ip = id[0].split(":")[0]
            port = id[0].split(":")[1]
            response = os.system(
                    "ping -c 1 -W 1 {} >> /dev/null".format(ip))
            try:
                if response == 0:
                    query = schemas.storage_status_update_query.format(
                            status=1, storage_ip=ip)
                    db_handler.run_sql("update", query)
                else:
                    query = schemas.storage_status_update_query.format(0, ip)
                    db_handler.run_sql("update", query)
            except:
                print("Error in pinging ip: {}".format(ip))
        #  Wait for some time before repeating
        time.sleep(PING_TIMEOUT)
