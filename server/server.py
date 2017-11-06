import os
import argparse
from threading import Thread

import database_utility as db_util
from ping_utility import ping_service
import schemas
#  Startup of server
#  Initialize Variables
PORT = 100000
ENTITIY_TYPE = "server"
OPEN_CONNECTION_LIMIT = 100

file_info = schemas.file
storage_info = schemas.storage

#  Load/Create Database
DATABASE_PATH = "./database_state.db"
db_handler = None

#  Parse Arguments

#  Create Database
db_handler = db_util.DB_Interface()
db_handler.connect_db()
print("DB created")

#  Start Ping Service
ping_thread = Thread(target = ping_service,
        args= (db_handler, storage_info["table_name"], "ip"))
ping_thread.daemon = True
ping_thread.start()
print("Ping created")

while True:
    #  Create an open socket
    #  Accept connection
    #  Fork a new process to handle this connection
    pass
