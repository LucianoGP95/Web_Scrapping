from sqlite_handler import SQLite_Handler

db = SQLite_Handler(r"D:\1_P\1Art\new\archive.db")
db.consult_tables()
db.examine_table("archive")
db.close_conn()