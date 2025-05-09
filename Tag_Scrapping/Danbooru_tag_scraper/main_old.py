import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from get_danbooru_tags import get_tags_raw, get_tags_refined

class BaseApp:
    def __init__(self, root):
        """Initialize the main application window."""
        self.root = root
        self.root.title("Danbooru tag downloader")
        self.root.geometry("500x260")

    def switch_window(self, new_window):
        """Destroy current window and open a new one."""
        for widget in self.root.winfo_children():
            widget.destroy()
        new_window(self.root)

class DownloaderApp(BaseApp):
    def __init__(self, root, root_path: str):
        super().__init__(root)  # Initialize the base class
        # Path creation
        self.root_path = root_path
        # Parameters
        self.base_url = 'https://danbooru.donmai.us/tags.json?limit=1000&search[hide_empty]=yes&search[is_deprecated]=no&search[order]=count'
        self.output_file_raw = os.path.join(self.root_path, "raw_tags.csv")
        self.output_file_refined = os.path.join(self.root_path, "tags.csv")

        self.postcount_label = ttk.Label(root, text="Minimun tags' posts to add:")
        self.postcount_label.pack(pady=5)
        self.postcount_var = tk.StringVar(root, value='100')
        self.postcount_entry = ttk.Entry(root, width=50, textvariable=self.postcount_var)
        self.postcount_entry.pack(pady=5)

        self.category_label = ttk.Label(root, text="Tags selection:")
        self.category_label.pack(pady=5)
        self.category_var = tk.StringVar(value="All")
        self.dropdown = ttk.Combobox(root, textvariable=self.category_var, values=["All", "Author", "Meta"])
        self.dropdown.pack()
        #self.dropdown.bind("<<ComboboxSelected>>", lambda event: self._update_output_folder())
        
        self.rewrite_existent = ttk.Label(root, text="Rewrite existent files:")
        self.rewrite_existent.pack(pady=5)
        self.rewrite_existent_var = tk.BooleanVar(value=False)
        self.no_button = ttk.Radiobutton(root, text="No", variable=self.rewrite_existent_var, value=False)
        self.no_button.pack()
        self.yes_button = ttk.Radiobutton(root, text="Yes", variable=self.rewrite_existent_var, value=True)
        self.yes_button.pack()

        self.get_raw_tags_button = ttk.Button(root, text="Get raw tags!", command=self.get_tags)
        self.get_raw_tags_button.pack(pady=5)

        self.get_refined_tags_button = ttk.Button(root, text="Get refined tags!", command=self.get_tags)
        self.get_refined_tags_button.pack(pady=5)

    def get_tags(self):
        get_tags_raw(self.base_url, self.output_file_raw, self.category_var.get(), postcout_filter=self.postcount_var.get(), rewrite_existent=self.rewrite_existent_var.get())

    def refine_tags(self):
        get_tags_refined(self.output_file_raw, self.output_file_refined, rewrite_existent=self.rewrite_existent_var.get())

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
    root = tk.Tk()
    app = DownloaderApp(root, os.path.abspath("../scraped_tags"))
    root.mainloop()
