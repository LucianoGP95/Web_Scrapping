import os, json, time, re, sys, shutil, sqlite3
# Secondary requirements: pip install openpyxl
################################################################################
class Database:
    '''SQLite custom handler'''
    def __init__(self, db_name: str, rel_path=None):
        if rel_path is None:
            self.db_path: str = os.path.join(os.path.abspath("../database/"), db_name)
        else:  # Optional relative path definition
            try:
                self.db_path: str = os.path.join(os.path.abspath(rel_path), db_name)
            except OSError as e:
                print(f"Error with custom path creation: {e}")
        
        self.conn = None
        self.cursor = None
        if not os.path.exists(self.db_path):  # Check if the database file exists before connecting
            print(f"Database *{db_name}* created in: {self.db_path}")
        else:
            print(f"Database *{db_name}* found in: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)  # Preventive connection/creation to the database
        self.cursor = self.conn.cursor()
        print(f"Database *{db_name}* connected.")

    def rename_table(self, old_name: str, new_name: str, verbose=True):
        old_name = re.sub(r'\W', '_', old_name)  # To avoid illegal symbols
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
            print(f"Table *{table_name}* renamed from *{old_name}* to *{new_name}*") if verbose else None
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
                    column_name = columns_info[0][1]
                    self.cursor.execute(f"DELETE FROM {table_name} WHERE {column_name} = '{row}'")
                    self.conn.commit()
                    print(f"{row} dropped successfully.")
                print(f"Row(s) deleted from table *{table_name}*")
                self.examine_table(table_name)
            else:
                print("Operation canceled.")
        except Exception as e:
            raise Exception(f"Error while deleting row(s): {str(e)}")

    def consult_tables(self, order=None, filter=None, verbose=True):
        '''Shows all the tables in the database. Allows for filtering.'''
        show_order = "name" if order is None else order  # Default order
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' ORDER BY {show_order}")
        if filter:  # First, filters by the full name
            tables = [table[0] for table in cursor.fetchall() if filter.lower() in table[0].lower()]
            if not tables:  # If not successful, filters by initial string
                tables = [table[0] for table in cursor.fetchall() if table[0].lower().startswith(filter.lower())]
        else:
            tables = [table[0] for table in cursor.fetchall()]
        
        _, db_name = os.path.split(self.db_path)
        if verbose:
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
                column_names = []  # Preallocation
                for column in columns:  # Get column names
                    column_name = column[1]
                    column_names.append(column_name)
                column_names = tuple(column_names)
                print(f"    Rows: {rows}\n    Columns: {columns_number}")
                cursor.execute(f"SELECT * FROM {table};")
                rows = cursor.fetchall()
                print(f"Columns name: {column_names}")
                for row in rows:  # Gets values row by row
                    print(f"    {row}")
        except Exception as e:
            raise Exception(f"Error while examining tables: {str(e)}")

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
        if rel_path is not None:  # Check if a new relative path was provided
            self.db_path = os.path.join(os.path.abspath(rel_path), database)
        try:
            self.conn.close()  # Ensure the database is closed
        except Exception:
            pass
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to {self.db_path}") if verbose else None
        except Exception as e:
            print(f"Error trying to connect: {e}")
            self.db_path = old_db_path  # Returns to the last valid path

    def clear_database(self, override=False):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")  # Get a list of all tables in the database
            tables = cursor.fetchall()
            _, file = os.path.split(self.db_path)
            if not override:  # Override confirmation to dispatch multiple databases (WARNING, abstract a confirmation check to a superior level)
                confirmation = input(f"Warning: This action will clear all data from the database {file}.\nDo you want to continue? (y/n): ").strip().lower()
            else:
                confirmation = "y"
            if confirmation == 'y':
                for table in tables:  # Loop through the tables and delete them
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
        '''Modifies the input parameter to handle several types and always return an iterable'''
        if isinstance(input, str):
            input = [input]
            return input
        elif isinstance(input, (list, tuple)):
            return input
        else:
            raise Exception(f"Unsupported input format: Try str, list, tuple.")

class JSONhandler(Database):
    def __init__(self, db_name: str, rel_path=None):
        """Initialize the JSONhandler with the database connection."""
        # Call the parent class constructor (Database's __init__)
        super().__init__(db_name, rel_path)

    def _sanitize_table_name(self, table_name):
        """Sanitize the table name to ensure it follows SQLite's naming rules."""
        # Replace special characters with underscores
        table_name = re.sub(r'\W', '_', table_name)
        # If the name starts with a number, prefix it with an underscore
        if table_name[0].isdigit():
            table_name = f"_{table_name}"
        return table_name

    def _create_table_dynamic(self, table_name, metadata):
        table_name = self._sanitize_table_name(table_name)
        try:
            # Ensure table exists
            self.cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" (filename TEXT);')

            # Get existing columns
            self.cursor.execute(f'PRAGMA table_info("{table_name}")')
            existing_columns = {row[1] for row in self.cursor.fetchall()}

            # Add missing columns
            for key, value in metadata.items():
                if key not in existing_columns:
                    if isinstance(value, int):
                        dtype = "INTEGER"
                    elif isinstance(value, float):
                        dtype = "REAL"
                    else:
                        dtype = "TEXT"
                    try:
                        self.cursor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{key}" {dtype};')
                    except sqlite3.Error as e:
                        print(f"Failed to add column {key}: {e}")

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating table {table_name}: {e}")

    def _insert_metadata_dynamic(self, table_name, metadata):
        table_name = self._sanitize_table_name(table_name)
        # Convert lists/dicts to strings
        for key in metadata:
            if isinstance(metadata[key], (list, dict)):
                metadata[key] = json.dumps(metadata[key], ensure_ascii=False)

        keys = list(metadata.keys())
        placeholders = ", ".join(["?" for _ in keys])
        column_names = ", ".join([f'"{k}"' for k in keys])
        values = [metadata[k] for k in keys]

        try:
            self.cursor.execute(
                f'INSERT OR IGNORE INTO "{table_name}" ({column_names}) VALUES ({placeholders});',
                values
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting into table {table_name}: {e}")

    def process_jsons(self, folder_path):
            """Process all JSON files in a directory and insert their metadata into the database."""
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".json"):
                        json_path = os.path.join(root, file)
                        parent_folder = os.path.basename(root)  # Extract the parent folder as the table name
                        
                        # Read and insert the metadata from the JSON file
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # Use all data as metadata
                        data["filename"] = file.split(".")[0]
                        if isinstance(data.get("tags"), list):
                            data["tags"] = ";".join(data["tags"])

                        self._create_table_dynamic(parent_folder, data)
                        self._insert_metadata_dynamic(parent_folder, data)
                        
                        # Optionally, delete the JSON file after processing it
                        os.remove(json_path)

    def is_url_downloaded(self, id):
            """Check if the URL has already been downloaded across all tables."""
            id = int(id)
            try:
                # Get a list of all tables in the database
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = self.cursor.fetchall()
                
                # Iterate through each table and check if the URL exists
                for table in tables:
                    table_name = table[0]
                    table_name = self._sanitize_table_name(table_name)
                    
                    # Check if the filename exists in the table
                    self.cursor.execute(f'''
                        SELECT COUNT(*) FROM {table_name} WHERE filename = ?;
                    ''', (id,))
                    count = self.cursor.fetchone()[0]
                    
                    if count > 0:  # If the URL exists in any table, return True
                        return True
                return False  # Return False if the URL doesn't exist in any table
            except sqlite3.Error as e:
                print(f"Error checking URL across all tables: {e}")
                return False

    def pre_download_duplicated_check(self, base_dir):
        # Get all table names dynamically
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.cursor.fetchall()]

        # Initialize an empty set to store known filenames
        known_files = set()

        # Iterate over all tables and get filenames
        for table in tables:
            try:
                self.cursor.execute(f"SELECT filename FROM {table}")
                # Add filenames to the known_files set
                known_files.update(row[0] for row in self.cursor.fetchall())
            except Exception as e:
                print(f"Error querying table {table}: {e}")

        # Walk through all subdirectories to find and remove duplicates
        removed = 0
        for dirpath, _, filenames in os.walk(base_dir):
            for fname in filenames:
                if fname in known_files:
                    print("Found repeated file(s)!")
                    fpath = os.path.join(dirpath, fname)
                    try:
                        os.remove(fpath)
                        removed += 1
                        print(f"Deleted: {fpath}")
                    except Exception as e:
                        print(f"Failed to delete {fpath}: {e}")
                    print(f"\n✅ Done. Deleted {removed} duplicate files.")


if __name__ == "__main__":
    handler = JSONhandler("pixiv.db", rel_path="./database")
    handler.process_jsons(r"D:\1_P\Web_Scraper\Pixiv_Downloader")  # <- asegúrate de pasar la ruta correcta
    handler.consult_tables()
    handler.examine_table("_102818725_user_xkjh3858")