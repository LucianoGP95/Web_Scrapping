import os, json, time, re, sys, shutil, sqlite3
import hashlib
# Secondary requirements: pip install openpyxl
################################################################################
class SQLite_Handler:
    '''SQLite custom handler'''

    def __init__(self, db_name: str, db_folder_path: str = None, rel_path: bool = False):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Memory database shortcut
        if db_name == ":memory:":
            self.db_path = ":memory:"
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("Test database created in RAM")
            return
        # Check if db_name looks like a valid absolute or relative file path
        if os.path.isabs(db_name) or os.path.sep in db_name:
            self.db_path = os.path.abspath(db_name)
            db_dir = os.path.dirname(self.db_path)
            os.makedirs(db_dir, exist_ok=True)
            # Optionally validate the file extension
            if not self.db_path.lower().endswith(".db"):
                raise ValueError("Database file path must end with '.db'")
            # Proceed to connect
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✅ Database loaded from full path: {self.db_path}")
            return
        else:
            # Validate simple db_name
            if not re.match(r'^[\w\-. ]+\.db$', db_name):
                raise ValueError("Database name must be a valid filename ending in '.db'")
            if not rel_path and db_folder_path is None:
                db_dir = os.path.abspath(os.path.join(base_dir, "../database/"))
            elif rel_path and db_folder_path is not None:
                db_dir = os.path.abspath(os.path.join(base_dir, db_folder_path))
            elif db_folder_path is not None:
                db_dir = os.path.abspath(db_folder_path)
            else:
                raise ValueError("Invalid combination of db_folder_path and rel_path.")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, db_name)
        # Connect and log
        if not os.path.exists(self.db_path):
            print(f"✅ Database *{db_name}* created in: {self.db_path}")
        else:
            print(f"✅ Database *{db_name}* found in: {self.db_path}")

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def get_key_info(self, foreign_keys: bool=False):
        '''Access PRAGMA configrations of the database'''
        foreign_keys = "ON" if foreign_keys == True else "OFF"
        self.cursor.execute(f"PRAGMA foreign_keys = {foreign_keys}")

    def get_table_info(self, table_name: str):
        '''Uses PRAGMA to show table info'''
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        rows = self.cursor.fetchall()
        print("\nTable schema:")
        for row in rows:
            print(row)

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
        return rows

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

    def delete_row(self, row_name: str | list, table_name: str):
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

    def close_conn(self, verbose=True):
        '''Closes the database connection when done'''
        try:
            self.conn.close()
            print(f"Closed connection to: {self.db_path}") if verbose else None
        except Exception as e:
            print(f"Error clearing the database: {str(e)}")

    def reconnect(self, database=None, rel_path=None, verbose=True):
        '''Reconnects to the current or a new database.'''
        old_db_path = self.db_path

        if database is not None:
            # Update db_path only if a new database name is provided
            if rel_path is not None:
                self.db_path = os.path.join(os.path.abspath(rel_path), database)
            else:
                self.db_path = os.path.join(os.path.abspath("../database/"), database)

        try:
            self.conn.close()  # Ensure the previous connection is closed
        except Exception:
            pass

        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to {self.db_path}") if verbose else None
        except Exception as e:
            print(f"Error trying to connect: {e}")
            self.db_path = old_db_path  # Restore the last valid path

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
            if confirmation == "y":
                for table in tables:  # Loop through the tables and delete them
                    table_name = table[0]
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                self.conn.commit()
                print(f"Database *{file}* cleared successfully.")
            else:
                print("Operation canceled.")
        except Exception as e:
            print(f"Error clearing the database: {str(e)}")

    """Internal methods"""
    def _input_handler(self, input):
        '''Modifies the input parameter to handle several types and always return an iterable'''
        if isinstance(input, str):
            input = [input]
            return input
        elif isinstance(input, (list, tuple, set)):
            return input
        else:
            raise Exception(f"Unsupported input format: Try str, list, tuple, set.")

class JSONhandler(SQLite_Handler):
    def __init__(self, db_name, db_folder_path=None, rel_path=False):
        super().__init__(db_name, db_folder_path, rel_path)
        self.init_db(self.db_path)
        self.counter = 0

    def _sanitize_table_name(self, table_name):
        table_name = re.sub(r'\W', '_', table_name)
        if table_name[0].isdigit():
            table_name = f"_{table_name}"
        return table_name

    @staticmethod
    def init_db(db_path):
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tagged_archive (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        rating TEXT,
                        character_tags TEXT,
                        author_tags TEXT,
                        general_tags TEXT,
                        source TEXT,
                        model TEXT,
                        score REAL,
                        SHA256 TEXT UNIQUE
                    )
                """)
                conn.commit()
                print(f"✅ Database initialized: {db_path}")
        except Exception as e:
            print(f"❌ Failed to init {db_path}: {e}")

    @staticmethod
    def insert_to_db(db_path, filename, rating, character_tags, general_tags, sha256, 
                     author_tags=None, source=None, model=None, score=None):
        character_tags = ", ".join(character_tags) if isinstance(character_tags, (list, tuple)) else character_tags
        author_tags = ", ".join(author_tags) if isinstance(author_tags, (list, tuple)) else author_tags
        general_tags = ", ".join(general_tags) if isinstance(general_tags, (list, tuple)) else general_tags
        
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR IGNORE INTO tagged_archive 
                    (filename, rating, character_tags, author_tags, general_tags, source, model, score, SHA256)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    filename,
                    rating if rating else "",
                    character_tags,
                    author_tags if author_tags else "",
                    general_tags,
                    source if source else "",
                    model if model else "",
                    score,
                    sha256,
                ))
                conn.commit()
                print(f"💾 Saved {filename} to: {db_path}")
        except Exception as e:
            print(f"❌ Failed to save to {db_path}: {e}")

    @staticmethod
    def compute_sha256(filepath):
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error computing SHA256 for {filepath}: {e}")
            return "unknown"

    def detect_source(self, data):
        if data.get("category") == "pixiv":
            return "pixiv"
        if "illust_ai_type" in data and "x_restrict" in data:
            return "pixiv"
        if data.get("url", "").startswith("https://i.pximg.net"):
            return "pixiv"
        return "unknown"

    def parse_pixiv(self, data, fallback_hash=None):
        filename = data.get("filename", "unknown")
        rating = data.get("rating") or str(data.get("x_restrict", ""))
        author_name = data.get("user", {}).get("name", "")
        score = data.get("total_bookmarks", 0)
        sha256 = data.get("sha256") or fallback_hash or "unknown"

        return {
            "filename": filename,
            "rating": rating,
            "character_tags": "",
            "general_tags": "",
            "author_tags": author_name,
            "source": "pixiv",
            "model": "",
            "score": score,
            "sha256": sha256
        }

    def batch_process_jsons(self, folder_path):
        # First pass: count all valid JSONs
        all_json_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".json") and re.search(r'_p\d+\.(jpg|png|jpeg|webp)\.json$', file):
                    all_json_files.append(os.path.join(root, file))
        
        total = len(all_json_files)
        print(f"📦 Found {total} JSON files to process")
    # Second pass: process them
        for i, json_path in enumerate(all_json_files, start=1):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            source = self.detect_source(data)
            if source == "pixiv":
                # Compute SHA256 if image exists
                image_base = os.path.splitext(json_path)[0]
                image_path = next((image_base + ext for ext in [".jpg", ".png", ".jpeg", ".webp"] if os.path.isfile(image_base + ext)), None)
                sha256 = self.compute_sha256(image_path) if image_path else self.fallback_hash(json_path)
                data["sha256"] = sha256
                extracted = self.parse_pixiv(data, fallback_hash=sha256)

                extracted = self.parse_pixiv(data)
                self.insert_to_db(
                    self.db_path,
                    extracted["filename"],
                    extracted["rating"],
                    extracted["character_tags"],
                    extracted["general_tags"],
                    extracted["sha256"],
                    extracted["author_tags"],
                    extracted["source"],
                    extracted["model"],
                    extracted["score"],
                )
            else:
                print(f"⚠️ Unsupported source: {source} in {json_path}")
            
            if i % 10 == 0 or i == total:
                print(f"📄 Progress: {i}/{total}")
            # os.remove(json_path)

    def fallback_hash(self, path):
        """Generate a fallback SHA256 from the path."""
        try:
            name = os.path.basename(path)
            return hashlib.sha256(name.encode()).hexdigest()
        except Exception as e:
            print(f"⚠️ Failed to compute fallback hash for {path}: {e}")
            return "unknown"

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
    handler = JSONhandler(r"D:\1_P\1Art\5_AI\0_Database\json_test.db")
    #handler.clear_database()
    #handler.batch_process_jsons(r"D:\1_P\1Art\5_AI\Followed_authors")
    handler.consult_tables()
    handler.examine_table("tagged_archive")
    handler.close_conn()
    #handler.examine_table("_102818725_user_xkjh3858")