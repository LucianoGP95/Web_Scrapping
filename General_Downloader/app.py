import sys
import os
import json
import subprocess
import time
import pygetwindow as gw
import pyperclip
import keyboard
from itertools import count
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QHBoxLayout, QProgressBar
)
from PySide6.QtCore import QThread, Signal

# --- Utility function ---
def detect_urls(workflow, galleries):
    browser_windows = [
        w for w in gw.getWindowsWithTitle("")
        if any(gallery in w.title for gallery in galleries) and not w.isMinimized
    ]

    if not browser_windows:
        return []

    browser_windows[0].activate()
    time.sleep(0.3)

    urls = set()
    for _ in count():
        keyboard.press_and_release("ctrl+l")
        time.sleep(0.2)
        keyboard.press_and_release("ctrl+c")
        time.sleep(0.3)
        set_url = pyperclip.paste()
        if not set_url.startswith("http"):
            continue
        if set_url in urls:
            break
        if any(set_url.startswith(w) for w in workflow):
            urls.add(set_url)
        keyboard.press_and_release("ctrl+tab")
        time.sleep(0.3)
    return list(urls)

# --- Thread class ---
class DownloadWorker(QThread):
    progress_percent = Signal(int)
    progress = Signal(str)
    finished = Signal(str)

    def __init__(self, base_dir):
        super().__init__()
        self.base_dir = base_dir
        self._cancelled = False
        self.process = None

    def cancel(self):
        self._cancelled = True
        if self.process and self.process.poll() is None:
            try:
                self.process.kill()
                self.progress.emit("Subprocess killed.")
            except Exception as e:
                self.progress.emit(f"Error killing subprocess: {e}")

    def run(self):
        galleries = ["Rule", "pixiv", "Danbooru", "danbooru"]
        workflow = [
            "https://rule34.xxx",
            "https://www.pixiv.net/en/artworks",
            "https://www.pixiv.net/en/users",
            "https://danbooru.donmai.us/posts"
        ]

        urls = detect_urls(workflow, galleries)
        if not urls:
            self.finished.emit("No valid gallery URLs found.")
            return

        self.progress.emit(f"Found {len(urls)} URL(s). Starting download...")

        config_path = r"D:\1_P\Web_Scraper\Pixiv_Downloader\config\config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        sources = {
            "pixiv": {"key": "pixiv", "url_prefix": "https://www.pixiv.net/en/artworks"},
            "pixiv_authors": {"key": "pixiv", "url_prefix": "https://www.pixiv.net/en/users"},
            "rule34": {"key": "rule34", "url_prefix": "https://rule34.xxx"},
            "danbooru": {"key": "danbooru", "url_prefix": "https://danbooru.donmai.us/posts"}
        }

        total = len(urls)
        for idx, url in enumerate(urls, 1):
            if self._cancelled:
                self.finished.emit("Download cancelled by user.")
                return
            # Determine the source for every url
            source = next((name for name, info in sources.items() if url.startswith(info["url_prefix"])), None)
            if not source:
                self.progress.emit(f"Unknown source: {url}")
                continue
            # Get path from the widget (override) or from the specific source setting in config.json
            base_dir_local = self.base_dir or config["extractor"][sources[source]["key"]]["base-directory"]
            archive_dir = os.path.join(os.path.dirname(base_dir_local), "archive.db")
            os.makedirs(base_dir_local, exist_ok=True)

            command = [
                "gallery-dl",
                "-d", base_dir_local,
                "--download-archive", archive_dir,
                "--config", ".\\config\\config.json",
                "--write-metadata",
                url
            ]
            self.progress.emit(f"Downloading: {url}")
            try:
                self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                stdout_lines = []
                for line in self.process.stdout:
                    if self._cancelled:
                        self.progress.emit("Cancelled.")
                        self.finished.emit("Download cancelled.")
                        return
                    if line.strip():
                        stdout_lines.append(line.strip())
                        self.progress.emit(line.strip())
                # Join the output after process ends
                stdout = "\n".join(stdout_lines)

                if self._cancelled:
                    self.progress.emit("Cancelled.")
                    self.finished.emit("Download cancelled.")
                    return

                if stdout[0] == "#":
                    self.progress.emit(f"Warning: File already in database:")

                for line in stdout.splitlines():
                    if line.strip():
                        self.progress.emit(line.strip())

                percent = int((idx / total) * 100)
                self.progress_percent.emit(percent)
            except Exception as e:
                self.progress.emit(f"Error: {e}")

        self.finished.emit("All downloads completed.")

class AuthorsUpdate(QThread):
    progress_percent = Signal(int)
    progress = Signal(str)
    finished = Signal(str)

    def __init__(self, base_dir):
        super().__init__()
        self.base_dir = base_dir
        self._cancelled = False
        self.process = None

    def cancel(self):
        self._cancelled = True
        if self.process and self.process.poll() is None:
            try:
                self.process.kill()
                self.progress.emit("Subprocess killed.")
            except Exception as e:
                self.progress.emit(f"Error killing subprocess: {e}")

    def run(self):
        try:
            author_file = os.path.join(os.getcwd(), "config/authors.json")
            with open(author_file, "r", encoding="utf-8") as f:
                author_data = json.load(f)
        except Exception as e:
            self.progress.emit(f"Error reading author file: {e}")
            self.finished.emit("Author update failed.")
            return

        urls = [url for url in author_data.values()]
        if not urls:
            self.progress.emit("No valid author URLs.")
            self.finished.emit("Aborting.")
            return

        author_amount = len(urls)
        print(f"Updating {len(urls)} authors...")
        authors = [author for author in author_data.keys()]
        [print(f"{author}  total tracking: {author_amount}") for author in authors]

        self.progress.emit(f"Found {len(urls)} URL(s). Starting download...")

        config_path = r"D:\1_P\Web_Scraper\Pixiv_Downloader\config\config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            total = len(urls)
        for idx, url in enumerate(urls, 1):
            if self._cancelled:
                self.finished.emit("Download cancelled by user.")
                return
            # Get path from the widget (override) or from the specific source setting in config.json
            base_dir_local = self.base_dir or config["extractor"]["pixiv"]["base-directory"]
            archive_dir = os.path.join(os.path.dirname(base_dir_local), "archive.db")
            os.makedirs(base_dir_local, exist_ok=True)

            command = [
                "gallery-dl",
                "-d", base_dir_local,
                "--download-archive", archive_dir,
                "--config", ".\\config\\config.json",
                "--write-metadata",
                url
            ]
            self.progress.emit(f"Downloading: {url}")
            try:
                self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                stdout_lines = []
                for line in self.process.stdout:
                    if self._cancelled:
                        self.progress.emit("Cancelled.")
                        self.finished.emit("Download cancelled.")
                        return
                    if line.strip():
                        stdout_lines.append(line.strip())
                        self.progress.emit(line.strip())
                # Join the output after process ends
                stdout = "\n".join(stdout_lines)

                if self._cancelled:
                    self.progress.emit("Cancelled.")
                    self.finished.emit("Download cancelled.")
                    return

                if stdout[0] == "#":
                    self.progress.emit(f"Warning: File already in database:")

                for line in stdout.splitlines():
                    if line.strip():
                        self.progress.emit(line.strip())
                percent = int((idx / total) * 100)
                self.progress_percent.emit(percent)
            except Exception as e:
                self.progress.emit(f"Error: {e}")

        self.finished.emit("All downloads completed.")


# --- GUI App ---
class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gallery Downloader GUI")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Optional: Enter base directory...")
        layout.addWidget(QLabel("Base Directory Override:"))
        layout.addWidget(self.dir_input)

        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Download")
        self.start_button.clicked.connect(self.start_download)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)

        self.author_button = QPushButton("Update authors")
        self.author_button.setEnabled(True)
        self.author_button.clicked.connect(self.author_download)

        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.cancel_button)
        btn_layout.addWidget(self.author_button)
        layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.output_log)

        self.setLayout(layout)
        self.thread = None

    def start_download(self):
        self.output_log.clear()
        base_dir = self.dir_input.text().strip() or None
        self.output_log.append("Scanning for gallery URLs...")
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.thread = DownloadWorker(base_dir)
        self.thread.progress.connect(self.output_log.append)
        self.thread.progress_percent.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def cancel_download(self):
        if self.thread:
            self.output_log.append("Cancelling download...")
            self.thread.cancel()

    def author_download(self):
        self.output_log.clear()
        base_dir = self.dir_input.text().strip() or None
        self.output_log.append("Scanning for listed author URLs...")
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.thread = AuthorsUpdate(base_dir)
        self.thread.progress.connect(self.output_log.append)
        self.thread.progress_percent.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, message):
        self.output_log.append(message)
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.thread = None

# --- Main ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec())
