#V19.0 25/01/2024
import os, json, time, re, sys, shutil, sqlite3
#Secondary requirements: pip install openpyxl
################################################################################
class Database:
    '''SQLite custom handler'''
    def __init__(self, db_name: str, rel_path=None):
        if rel_path == None:
            self.db_path: str = os.path.join(os.path.abspath("../database/"), db_name)
        else: #Optional relative path definition
            try:
                self.db_path: str = os.path.join(os.path.abspath(rel_path), db_name)
            except OSError as e:
                print(f"Error with custom path creation: {e}")
        self.conn = None
        self.cursor = None
        self.conn = sqlite3.connect(self.db_path) #Preventive connection/creation to the database
        self.cursor = self.conn.cursor()
        if not os.path.exists(self.db_path): 
            print(f"Database *{db_name}* created in: {self.db_path}")
        else: 
            print(f"Database *{db_name}* found in: {self.db_path}")

    def rename_table(self, old_name: str, new_name: str, verbose=True):
        old_name = re.sub(r'\W', '_', old_name) #To avoid illegal symbols
        new_name = re.sub(r'\W', '_', new_name)
        try:
            self.cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name};")
            self.conn.commit()
            print(f"Table *{old_name}* renamed to *{new_name}*") if verbose else None
        except sqlite3.OperationalError as e:
            error_message = str(e)
            if "there is already another table" in error_message:
                print(f"Table *{new_name}* already exists. Skipping renaming.") if verbose else None
            else:
                raise Exception(f"Error while renaming table: {error_message}")

    def rename_column(self, table_name, old_name, new_name, verbose=True):
        try:
            quoted_table_name = f'"{table_name}"'
            quoted_old_name = f'"{old_name}"'
            quoted_new_name = f'"{new_name}"'
            self.cursor.execute(f"ALTER TABLE {quoted_table_name} RENAME COLUMN {quoted_old_name} TO {quoted_new_name};")
            self.conn.commit()
            print(f"Table *{table_name}* renamed from *{old_name}* to *{new_name}*") if verbose == True else None
        except Exception as e:
            print(f"Error renaming column: {e}")

    def delete_table(self, table_name: str):
        try:
            print(f"Warning: This action will drop the table {table_name}.")
            confirmation = input("Do you want to continue? (y/n): ").strip().lower()
            if confirmation == 'y':
                self.cursor.execute(f"DROP TABLE {table_name};")
                self.conn.commit()
                print(f"{table_name} dropped successfully.")
                print(f"Table *{table_name}* deleted")
                self.consult_tables()
            else:
                print("Operation canceled.")
        except Exception as e:
            raise Exception(f"Error while deleting table: {str(e)}")

    def delete_row(self, row_name: str, table_name: str):
        '''Drops row(s) from the desired table'''
        row_name = self._input_handler(row_name)
        try:
            print(f"Warning: This action will drop row(s) from {table_name}.")
            confirmation = input("Do you want to continue? (y/n): ").strip().lower()
            if confirmation == 'y':
                for row in row_name:
                    self.cursor.execute(f"PRAGMA table_info({table_name})")
                    columns_info = self.cursor.fetchall()
                    column_name= columns_info[0][1]
                    self.cursor.execute(f"DELETE FROM {table_name} WHERE {column_name} = '{row}'")
                    self.conn.commit()
                    print(f"{row} dropped successfully.")
                print(f"Row(s) deleted from table *{table_name}*")
                self.examine_table(table_name)
            else:
                print("Operation canceled.")
        except Exception as e:
            raise Exception(f"Error while deleting table: {str(e)}")

    def consult_tables(self, order=None, filter=None, verbose=True):
        '''Shows all the tables in the database. Allows for filtering.'''
        show_order="name" if order == None else order #Default order
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' ORDER BY {show_order}")
        if filter:  #First, filters by the full name
            tables = [table[0] for table in cursor.fetchall() if filter.lower() in table[0].lower()]
            if not tables: #If not successful, filters by initial string
                tables = [table[0] for table in cursor.fetchall() if table[0].lower().startswith(filter.lower())]
        else:
            tables = [table[0] for table in cursor.fetchall()]
        _, db_name = os.path.split(self.db_path)
        if verbose == True:
            print(f"*{db_name}* actual contents:")
            for table in tables:
                print(f"    {table}")
        return tables

    def examine_table(self, table_name: str):
        '''Prints the desired table or tables if given in list or tuple format'''
        table_name = self._input_handler(table_name)
        try:
            cursor = self.conn.cursor()
            for i, table in enumerate(table_name):
                print(f"table {i+1}: {table}")
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                rows = cursor.fetchone()[0]
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                columns_number = len(columns)
                column_names = []; rows = [] #Preallocation
                for column in columns: #Get column names
                    column_name = column[1]
                    column_names.append(column_name)
                column_names = tuple(column_names)
                print(f"    Rows: {rows}\n    Columns: {columns_number}")
                cursor.execute(f"SELECT * FROM {table};")
                rows = cursor.fetchall()
                print(f"Columns name: {column_names}")
                for row in rows: #Gets values row by row
                    print(f"    {row}")
        except Exception as e:
            raise Exception(f"Error while examining tables: {(e)}")

    def close_conn(self, verbose=True):
        '''Closes the database connection when done'''
        try:
            self.conn.close()  
            print(f"Closed connection to: {self.db_path}") if verbose else None
        except Exception as e:
            print(f"Error clearing the database: {str(e)}")

    def reconnect(self, database, rel_path=None, verbose=True):
        '''Connects to either the same database or another database.'''
        old_db_path = self.db_path
        if rel_path is not None:  #Check if a new relative path was provided
            self.db_path = os.path.join(os.path.abspath(rel_path), database)
        try:
            self.conn.close()  #Ensure the database is closed
        except Exception:
            pass
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to {self.db_path}") if verbose else None
        except Exception as e:
            print(f"Error trying to connect: {e}")
            self.db_path = old_db_path #Returns to the last valid path

    def clear_database(self, override=False):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") #Get a list of all tables in the database
            tables = cursor.fetchall()
            _, file = os.path.split(self.db_path)
            if override == False: #Override confirmation to dispatch multiple databases (WARNING, abstract a confirmation check to a superior level) 
                confirmation = input(f"Warning: This action will clear all data from the database {file}.\nDo you want to continue? (y/n): ").strip().lower()
            else:
                confirmation = "y"
            if confirmation == 'y':
                for table in tables: #Loop through the tables and delete them
                    table_name = table[0]
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                self.conn.commit()
                print(f"Database *{file}* cleared successfully.")
            else:
                print("Operation canceled.")
        except Exception as e:
            print(f"Error clearing the database: {str(e)}")
    '''internal methods'''
    def _input_handler(self, input):
        '''Modfifies the input parameter to handle several types and always return and iterable'''
        if isinstance(input, str):
            input = [input]
            return input
        elif isinstance(input, (list, tuple)):
            return input
        else:
            raise Exception(f"Unsupported input format: Try str, list, tuple.")

class JSONhandler(Database):
    def __init__(self, db_name: str, rel_path=None):
        super().__init__(db_name, rel_path)

    def process_jsons(self, output_path: str, table_name: str):
        '''Scans for JSON metadata files in directory and saves contents to DB'''
        json_files = []
        for root, _, files in os.walk(output_path):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))
        
        print(f"Found {len(json_files)} metadata files.")
        for json_path in json_files:
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.insert_metadata(data, table_name)
                os.remove(json_path)  # delete after processing
                print(f"Processed and deleted: {json_path}")
            except Exception as e:
                print(f"Error processing {json_path}: {e}")

    def insert_metadata(self, data: dict, table_name: str):
        '''Handles insertion of JSON metadata into the database'''
        # Normalize table name
        table_name = re.sub(r'\W', '_', table_name)
        
        # Create table if doesn't exist (dynamic columns based on keys)
        keys = list(data.keys())
        columns_sql = ', '.join([f'"{k}" TEXT' for k in keys])
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql})''')

        # Insert row
        values = tuple(str(data.get(k, "")) for k in keys)
        placeholders = ', '.join(['?' for _ in keys])
        self.cursor.execute(f'''INSERT INTO "{table_name}" ({", ".join(keys)}) VALUES ({placeholders})''', values)
        self.conn.commit()
