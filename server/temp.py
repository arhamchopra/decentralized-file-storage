import MySQLdb as db

handler = db.connect(
        host="localhost",
        user = "root",
        passwd = "password",
        db = "MaidSafeDB",
        )
file_create_query1 = """INSERT StorageData(StorageIP, StorageSpace, UsedSpace, Status, FileLock) 
    VALUES ('www.google.com', 100, 20, 1, 'abc');"""
file_create_query2 = """INSERT StorageData(StorageIP, StorageSpace, UsedSpace, Status, FileLock) 
    VALUES ('www.rediff.com', 100, 20, 1, 'abc');"""
file_create_query3 = """INSERT StorageData(StorageIP, StorageSpace, UsedSpace, Status, FileLock) 
    VALUES ('www.fb.com', 100, 20, 1, 'abc');"""
file_create_query4 = """INSERT StorageData(StorageIP, StorageSpace, UsedSpace, Status, FileLock) 
    VALUES ('127.0.0.1', 100, 20, 1, 'abc');"""
cursor = handler.cursor()
cursor.execute(file_create_query1)
cursor.execute(file_create_query2)
cursor.execute(file_create_query3)
cursor.execute(file_create_query4)
print(handler.commit())

