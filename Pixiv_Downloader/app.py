import os
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
        self.root.geometry("300x160")
        self.db = JSONhandler("pixiv.db", "./database")
        self.db.close_conn(verbose=False)

    def switch_window(self, new_window):
        """Destroy current window and open a new one."""
        for widget in self.root.winfo_children():
            widget.destroy()
        new_window(self.root)

class DownloaderApp(BaseApp):
    def __init__(self, root, root_path: str, output_path: str):
        super().__init__(root)  # Initialize the base class
        # Path creation
        self.root_path = root_path
        self.output_path = output_path
        # Parameters
        self.author_file = ".\\config\\authors.txt"
        self.author_urls = get_config(self.author_file)
        # Widgets
        self.output_label = ttk.Label(root, text="Output Folder:")
        self.output_label.pack(pady=5)

        self.output_var = tk.StringVar(value=self.output_path)
        self.output_entry = ttk.Entry(root, width=60, textvariable=self.output_var)
        self.output_entry.pack(pady=5)

        self.get_authors_button = ttk.Button(root, text="Get authors!", command=self.get_authors)
        self.get_authors_button.pack(pady=5)
        
        self.get_tabs_button = ttk.Button(root, text="Get tabs!", command=self.get_tabs)
        self.get_tabs_button.pack(pady=5)

    def get_authors(self):
        update_authors(self.author_urls, self.output_path)
        self.db.process_jsons(self.output_path, "test")

    def get_tabs(self):
        download_tabs()
        self.db.process_jsons(self.output_path, "test")

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
        back_button = ttk.Button(root, text="Back", command=lambda: self.switch_window(DownloaderApp))
        back_button.pack(pady=20)

if __name__ == "__main__":
    root_path = os.getcwd()
    output_path = os.path.join(root_path, "config/config.txt")
    output_file = get_config(output_path)
    root = tk.Tk()
    app = DownloaderApp(root, root_path, output_file.get("directory_path"))
    root.mainloop()