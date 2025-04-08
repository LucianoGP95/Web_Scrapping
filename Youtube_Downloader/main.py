import os, json
import tkinter as tk
import yt_dlp
from tkinter import ttk, filedialog, messagebox
from core_logic import Downloader

class BaseApp:
    def __init__(self, root):
        """Initialize the main application window."""
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("600x400")
        # Download Properties
        self.ask_download_list = tk.BooleanVar(value=False)

    def switch_window(self, new_window_class):
        for widget in self.root.winfo_children():
            widget.destroy()
        new_window_class(self.root, self.ask_download_list)

    def read_json(self, info_path, field):
        with open(self.info_path, "r") as config_file:
            config_data = json.load(config_file)
            return config_data[field]

class DownloaderApp(BaseApp):
    def __init__(self, root, ask_download_list=None):
        super().__init__(root)
        if ask_download_list:
            self.ask_download_list = ask_download_list
        self.info_path = os.path.join(os.getcwd(), "help.json")
        self.APP_VERSION = self.read_json(self.info_path, "version")

        menu = tk.Menu(root)
        root.config(menu=menu)
        about_menu = tk.Menu(menu)
        menu.add_cascade(label="Help", menu=about_menu)
        about_menu.add_command(label="Version", command=self._show_version)

        self.default_audio_folder = os.path.join(os.getcwd(), "downloads\\audio")
        self.default_video_folder = os.path.join(os.getcwd(), "downloads\\video")
        self.output_folder = self.default_audio_folder  # Default to audio

        self.url_label = ttk.Label(root, text="Video URL:")
        self.url_label.pack(pady=5)
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(root, width=80, textvariable=self.url_var)
        self.url_entry.pack(pady=5)

        self.folder_label = ttk.Label(root, text="Output Folder:")
        self.folder_label.pack(pady=5)
        
        self.folder_entry = ttk.Entry(root, width=80)
        self.folder_entry.insert(0, self.output_folder)  # Set default folder
        self.folder_entry.pack(pady=5)
        
        self.browse_button = ttk.Button(root, text="Browse", command=self.select_folder)
        self.browse_button.pack(pady=5)

        self.option_var = tk.StringVar(value="audio")
        self.audio_button = ttk.Radiobutton(root, text="Audio", variable=self.option_var, value="audio", command=self._update_output_folder)
        self.audio_button.pack()
        self.video_button = ttk.Radiobutton(root, text="Video", variable=self.option_var, value="video", command=self._update_output_folder)
        self.video_button.pack()

        self.download_button = ttk.Button(root, text="Download", command=self.start_download)
        self.download_button.pack(pady=20)

        self.progress_label = ttk.Label(root, text="Progress: Waiting")
        self.progress_label.pack(pady=5)

        self.settings_button = ttk.Button(root, text="Settings", command=lambda: self.switch_window(SettingsApp))
        self.settings_button.pack(pady=5)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def start_download(self):
        self._update_progress("Downloading")
        self.root.update_idletasks()  # Force UI update
        url = self.url_entry.get()
        output_folder = self.folder_entry.get()
        if not url or not output_folder:
            messagebox.showerror("Error", "Please enter a URL and select an output folder.")
            return

        downloader = Downloader(url, output_folder)

        if self.option_var.get() == "audio":
            downloader.get_audio_opts()
        else:
            downloader.get_video_opts()

        if "list=" in url and self.ask_download_list.get():
            confirmation = messagebox.askyesno("Playlist detected", "Do you want to download the full playlist?")
            if not confirmation:
                downloader.add_option("--no-playlist")

        self.download_button.config(state=tk.DISABLED)
        try:
            downloader.download_video()
            if self.option_var.get() == "audio":
                downloader.add_audio_metadata()
            self._update_progress("Finished")
            messagebox.showinfo("Success", "Download complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {e}")
        finally:
            self.download_button.config(state=tk.NORMAL)
            self._update_progress("Waiting")

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

    def _show_version(self):
        messagebox.showinfo("Version", self.APP_VERSION)

class SettingsApp(BaseApp):
    def __init__(self, root, ask_download_list=None):
        super().__init__(root)
        if ask_download_list:
            self.ask_download_list = ask_download_list
        self.root.geometry("600x300")
        self.root.title("YT Downloader: Settings Window")

        ttk.Label(root, text="Show playlist confirmation message?").pack(pady=10)
        self.ask_list_var = tk.StringVar(value=str(self.ask_download_list.get()))
        self.dropdown_list = ttk.Combobox(root, textvariable=self.ask_list_var, values=["False", "True"], state="readonly")
        self.dropdown_list.pack()

        button_frame = ttk.Frame(root)
        button_frame.pack(pady=20)

        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings)
        save_button.pack(side=tk.LEFT, padx=10)

        back_button = ttk.Button(button_frame, text="Not save", command=lambda: self.switch_window(lambda r: DownloaderApp(r, self.ask_download_list)))
        back_button.pack(side=tk.LEFT, padx=10)

    def save_settings(self):
        selected = self.ask_list_var.get()
        self.ask_download_list.set(selected == "True")
        messagebox.showinfo("Saved", f"Settings updated: ask_download_list = {self.ask_download_list.get()}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
