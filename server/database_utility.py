import MySQLdb as db

import schemas

class DB_Interface():
    handler = None

    def connect_db(self):
        try:
            self.handler = db.connect(
                    host="localhost",
                    user = "root",
                    passwd = "password",
                    db = schemas.DB_NAME,
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
        self.run_raw_sql(schemas.db_create_query)
        self.run_raw_sql(schemas.db_select_query)
        self.run_raw_sql(schemas.file_create_query)
        self.run_raw_sql(schemas.storage_create_query)
        self.handler.commit()

    def run_raw_sql(self, sql_statement):
        cursor = self.handler.cursor()
        return cursor.execute(sql_statement)

    def run_sql(self, type, sql_statement):
        if type == "get":
            return self.query_sql(sql_statement)
        elif type == "create" or type == "update" or type == "insert":
            try:
                return self.update_sql(sql_statement)
            except: #MySQLdb.IntegrityError raised on failure of an insert
                return 0

    def query_sql(self, sql_statement):
        cursor = self.handler.cursor()
        cursor.execute(sql_statement)
        data = cursor.fetchall()
        if len(data)!=0:
            return [list(elem) for elem in data]
        else:
            return []


    def update_sql(self, sql_statement):
        cursor = self.handler.cursor()
        cursor.execute(sql_statement)
        rows_edited = cursor.rowcount
        self.handler.commit()
        return rows_edited
