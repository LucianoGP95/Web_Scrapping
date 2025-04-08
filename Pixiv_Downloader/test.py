import os
from database import Database

root_path = os.getcwd()
db_path = os.path.join(root_path, "database")
print(db_path)

database = Database("pixiv.db", "./database")
database.close_conn()