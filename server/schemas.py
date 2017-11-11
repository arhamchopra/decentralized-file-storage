
DB_NAME = "MaidSafeDB"
file_schema = {
        "field1" : "type1",
        }

file = {
        "table_name" : "FileData",
        "schema" : file_schema
        }

storage_schema = {
        "field1" : "type1",
        "ip" : "string"
        }

storage = {
        "table_name" : "StorageData",
        "schema" : storage_schema
        }

#  Creation Statements
db_create_query = """CREATE DATABASE IF NOT EXISTS {};""".format(DB_NAME)
db_select_query = """USE {};""".format(DB_NAME)
file_create_query = """CREATE TABLE IF NOT EXISTS FileData(
        FileId INT PRIMARY KEY AUTO_INCREMENT,
        FileName TEXT,
        Owner TEXT,
        IP_List VARCHAR(255),
        Size REAL
        );"""
storage_create_query = """CREATE TABLE IF NOT EXISTS StorageData( 
        StorageId INT PRIMARY KEY AUTO_INCREMENT, 
        StorageIP TEXT,
        StorageSpace REAL,
        UsedSpace REAL,
        Status INT,
        FileLock TEXT
        );"""

STORAGE_IP_DOWN = 0
STORAGE_IP_UP = 1
STORAGE_IP_LOCKED = 2


#  Query Statements
get_ip_status = """
        SELECT Status 
        FROM StorageData
        WHERE StorageIP={storage_ip!r};
        """
file_ip_get_query = """
        SELECT IP_List
        FROM FileData
        WHERE FileName={filename!r};
        """
storage_ip_get_query = """
        SELECT StorageIP 
        FROM StorageData 
        WHERE Status <> {};
        """.format(STORAGE_IP_LOCKED)
storage_status_update_query = """
        UPDATE StorageData 
        SET Status={status} 
        WHERE StorageIP={storage_ip!r};
        """
storage_insertion_query = """
        INSERT INTO StorageData
        (StorageIP, StorageSpace, UsedSpace, Status, FileLock)
        VALUES ({storage_ip!r},{storage_space},{used_space},{status},{file_lock!r});
        """
storage_check_query = """
        SELECT count(*)
        FROM StorageData
        WHERE StorageIP = {storage_ip!r};
        """