from database import JSONhandler
import sqlite3

# Now check the results using your SQLite_Handler
db = JSONhandler(r"D:\1_P\1Art\5_AI\archive.db")
db.consult_tables()
archive = db.examine_table("archive")
print(len(archive))
db.close_conn()
