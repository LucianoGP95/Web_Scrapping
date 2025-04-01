import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core_logic import Downloader

class BaseApp:
    def __init__(self, root):
        """Initialize the main application window."""
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("600x400")

    def switch_window(self, new_window):
        """Destroy current window and open a new one."""
        for widget in self.root.winfo_children():
            widget.destroy()
        new_window(self.root)

class DownloaderApp(BaseApp):
    def __init__(self, root):
        super().__init__(root)  # Initialize the base class

        # Default output folder (will update with radio button)
        self.default_audio_folder = os.path.join(os.getcwd(), "downloads\\audio")
        self.default_video_folder = os.path.join(os.getcwd(), "downloads\\video")
        self.output_folder = self.default_audio_folder  # Default to audio

        self.url_label = ttk.Label(root, text="Video URL:")
        self.url_label.pack(pady=5)
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(root, width=80, textvariable=self.url_var)
        self.url_entry.pack(pady=5)
        
        self.title_label = ttk.Label(root, text="Confirm Title:")
        self.title_label.pack(pady=5)
        
        self.title_var = tk.StringVar()
        self.title_var.trace_add("write", self._update_title)  # Add trace for updates
        self.title_entry = ttk.Entry(root, width=80, textvariable=self.title_var)  # Link StringVar to Entry
        self.title_entry.pack(pady=5)

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

        self.progress_label = ttk.Label(root, text="Progress: 0%")
        self.progress_label.pack(pady=5)

        self.settings_button = ttk.Button(root, text="Settings", command=lambda: self.switch_window(SettingsApp))
        self.settings_button.pack(pady=5)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def start_download(self):
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

        self.download_button.config(state=tk.DISABLED)
        try:
            downloader.download_video(progress_callback=self._update_progress)
            if self.option_var.get() == "audio":
                downloader.add_audio_metadata()
            messagebox.showinfo("Success", "Download complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {e}")
        finally:
            self.download_button.config(state=tk.NORMAL)

    def _update_output_folder(self):
        """Update the default folder when the format changes."""
        if self.option_var.get() == "audio":
            self.output_folder = self.default_audio_folder
        else:
            self.output_folder = self.default_video_folder

        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.output_folder)

    def _update_progress(self, percent):
        self.progress_label.config(text=f"Progress: {percent}")

    def _update_title(self, *args):
        # This function will now be triggered every time the title changes
        self.title_var.set("Hello World")
        print("Title changed:", self.title_str.get())  # Prints the current text in the title entry

class SettingsApp(BaseApp):
    def __init__(self, root):
        super().__init__(root)
        ttk.Label(root, text="Settings Window").pack(pady=10)
        back_button = ttk.Button(root, text="Back", command=lambda: self.switch_window(DownloaderApp))
        back_button.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
