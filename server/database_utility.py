import MySQLdb as db

DB_NAME = "MaidSafeDB"
class DB_Interface():
    handler = None

    def connect_db(self):
        try:
            self.handler = db.connect(
                    host="localhost",
                    user = "root",
                    passwd = "password",
                    db = DB_NAME,
                    )
            print("The db does exist")
        except:
            print("The db does not exist")
            self.handler = db.connect(
                    host="localhost",
                    user = "root",
                    passwd = "password",
                    )
            self.create_db();

    def create_db(self):
        db_create_query = """CREATE DATABASE IF NOT EXISTS {};""".format(DB_NAME)
        self.run_sql(db_create_query)
        db_select_query = """USE {};""".format(DB_NAME)
        self.run_sql(db_select_query)

        file_create_query = """CREATE TABLE IF NOT EXISTS FileData(
                FileId INT PRIMARY KEY,
                FileName TEXT,
                Owner TEXT,
                IP_list VARCHAR(255),
                Size REAL
                );"""
        self.run_sql(file_create_query)

        storage_create_query = """CREATE TABLE IF NOT EXISTS StorageData(
                StorageId INT PRIMARY KEY,
                StorageIP TEXT,
                StorageSpace REAL,
                UsedSpace REAL,
                Status INT,
                FileLock TEXT
                );"""
        self.run_sql(storage_create_query)
        self.handler.commit()

    def run_sql(self, sql_statement):
        cursor = self.handler.cursor()
        return cursor.execute(sql_statement)

