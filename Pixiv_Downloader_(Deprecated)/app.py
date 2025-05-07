import os, json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core_logic import update_authors, download_tabs
from database import JSONhandler
from utilities import get_config

class BaseApp:
    def __init__(self, root):
        """Initialize the main application window."""
        self.root = root
        self.root.title("Danbooru tag downloader")
        self.root.geometry("300x200")
        self.db = JSONhandler("pixiv.db", "./database")
        self.db.close_conn(verbose=False)

    def switch_window(self, new_window):
        """Destroy current window and open a new one."""
        for widget in self.root.winfo_children():
            widget.destroy()
        new_window(self.root)

class DownloaderApp(BaseApp):
    def __init__(self, root, root_path: str, base_dir: str):
        super().__init__(root)  # Initialize the base class
        # Path creation
        self.root_path = root_path
        self.base_dir = base_dir
        # Parameters
        self.author_file = ".\\config\\authors.txt"
        self.author_urls = get_config(self.author_file)
        # Widgets
        self.output_label = ttk.Label(root, text="Output Folder:")
        self.output_label.pack(pady=5)

        self.output_var = tk.StringVar(value=self.base_dir)
        self.output_entry = ttk.Entry(root, width=60, textvariable=self.output_var)
        self.output_entry.pack(pady=5)

        self.get_authors_button = ttk.Button(root, text="Get authors!", command=self.get_authors)
        self.get_authors_button.pack(pady=5)
        
        self.get_tabs_button = ttk.Button(root, text="Get tabs!", command=self.get_tabs)
        self.get_tabs_button.pack(pady=5)

        self.check_database = ttk.Button(root, text="Check database", command=lambda: self.switch_window(SettingsApp))
        self.check_database.pack(pady=20)

    def get_authors(self):
        update_authors(self.author_urls, self.base_dir, self.db)
        self.update_database()

    def get_tabs(self):
        download_tabs(self.base_dir, self.db)
        self.update_database()

    def update_database(self):
        self.db.reconnect("pixiv.db", verbose=False)
        #self.db.pre_download_duplicated_check(self.base_dir)
        self.db.process_jsons(self.base_dir)
        self.db.close_conn(verbose=False)

    def select_file(self):
        file_selected = filedialog.askopenfilename()
        if file_selected:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_selected)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def _update_output_folder(self):
        """Update the default folder when the format changes."""
        if self.option_var.get() == "audio":
            self.output_folder = self.default_audio_folder
        else:
            self.output_folder = self.default_video_folder

        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.output_folder)

    def _update_progress(self, status):
        self.progress_label.config(text=f"Progress: {status}")

class SettingsApp(BaseApp):
    def __init__(self, root):
        super().__init__(root)
        ttk.Label(root, text="Settings Window").pack(pady=10)
        back_button = ttk.Button(root, text="Back", command=lambda: self.switch_window(self, DownloaderApp, root_path, base_dir))
        back_button.pack(pady=20)

if __name__ == "__main__":
    root_path = os.getcwd()
    config_path = os.path.join(root_path, "config\\config.json")
    print(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    base_dir = config["extractor"]["pixiv"]["base-directory"]
    root = tk.Tk()
    app = DownloaderApp(root, root_path, base_dir)
    root.mainloop()