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
    QLabel, QLineEdit, QTextEdit, QHBoxLayout, QProgressBar, QCheckBox,
    QFileDialog, QMessageBox, QDialog, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import QThread, Signal, QSettings, Qt
from utils.db_functions import fetch_all_from_db

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

# --- Consolidated Worker Thread Class ---
class DownloadWorker(QThread):
    progress_percent = Signal(int)
    progress = Signal(str)
    finished = Signal(str)

    def __init__(self, base_dir, archive_path, mode="tabs"):
        super().__init__()
        self.base_dir = base_dir
        self.archive_path = archive_path
        self._cancelled = False
        self.process = None
        self.r18_only = False
        self.no_subfolders = False
        self.only_metadata = False
        self.skip_archive = False
        self.mode = mode  # "tabs" or "authors"

    def cancel(self):
        self._cancelled = True
        if self.process and self.process.poll() is None:
            try:
                self.process.kill()
                self.progress.emit("Subprocess killed.")
            except Exception as e:
                self.progress.emit(f"Error killing subprocess: {e}")

    def get_author_urls(self):
        try:
            author_file = os.path.join(os.getcwd(), "config/authors.json")
            with open(author_file, "r", encoding="utf-8") as f:
                author_data = json.load(f)
                
            urls = list(author_data.values())
            if not urls:
                self.progress.emit("No valid author URLs.")
                return None, None
                
            authors = list(author_data.keys())
            self.progress.emit(f"Tracking authors:")
            for author in authors:
                self.progress.emit(f"   {author}")
            
            return urls, authors
        except Exception as e:
            self.progress.emit(f"Error reading author file: {e}")
            return None, None

    def get_browser_urls(self):
        galleries = ["Rule", "pixiv", "Danbooru", "danbooru", "Kemono", "Gelbooru"]
        workflow = [
            "https://rule34.xxx",
            "https://www.pixiv.net/en/artworks",
            "https://www.pixiv.net/en/users",
            "https://danbooru.donmai.us/posts",
            "https://kemono.su/fanbox/user",
            "https://kemono.su/patreon/user",
            "https://gelbooru.com/index"
        ]
        return detect_urls(workflow, galleries)

    def run(self):
        # Step 1: Get URLs based on mode
        if self.mode == "authors":
            urls, authors = self.get_author_urls()
            if not urls:
                self.finished.emit("Author update failed.")
                return
            self.progress.emit(f"Found {len(urls)} author URL(s). Starting download...")
            self.finished.emit(f"Total tracking: {len(urls)}")
        else:  # tabs mode
            urls = self.get_browser_urls()
            if not urls:
                self.finished.emit("No valid gallery URLs found.")
                return
            self.progress.emit(f"Found {len(urls)} URL(s). Starting download...")

        # Step 2: Load config
        config_path = os.path.join(os.getcwd(), "config", "config.json")
        if not os.path.exists(config_path):
            self.progress.emit(f"Config file not found: {config_path}")
            self.finished.emit("Configuration error")
            return
            
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Step 3: Define sources for URL matching
        sources = {
            "pixiv": {"key": "pixiv", "url_prefix": "https://www.pixiv.net/en/artworks"},
            "pixiv_authors": {"key": "pixiv", "url_prefix": "https://www.pixiv.net/en/users"},
            "rule34": {"key": "rule34", "url_prefix": "https://rule34.xxx"},
            "danbooru": {"key": "danbooru", "url_prefix": "https://danbooru.donmai.us/posts"},
            "kemono": {"key": "kemono", "url_prefix": "https://kemono.su/"},
            "gelbooru": {"key": "gelbooru", "url_prefix": "https://gelbooru.com/index.php?page=post&s=view&id="}
        }

        # Step 4: Process each URL
        total = len(urls)
        for idx, url in enumerate(urls, 1):
            if self._cancelled:
                self.finished.emit("Download cancelled by user.")
                return
                
            # Determine the source for the URL (for tabs mode)
            # For authors mode, we assume it's pixiv
            if self.mode == "tabs":
                source = next((name for name, info in sources.items() if url.startswith(info["url_prefix"])), None)
                if not source:
                    self.progress.emit(f"Unknown source: {url}")
                    continue
                source_key = sources[source]["key"]
            else:
                source_key = "pixiv"  # Default for author mode
                
            # Get path from the widget (override) or from the specific source setting in config.json
            base_dir_local = self.base_dir or config["extractor"][source_key]["base-directory"]
            
            # Use provided archive path or generate default
            archive_path_local = self.archive_path
            if not archive_path_local:
                archive_path_local = os.path.join(os.path.dirname(base_dir_local), "archive.db")
            
            # Ensure directories exist
            os.makedirs(base_dir_local, exist_ok=True)
            os.makedirs(os.path.dirname(archive_path_local), exist_ok=True)

            # Build the gallery-dl command
            command = [
                "gallery-dl",
                "-d", base_dir_local,
                "--config", ".\\config\\config.json",
                "--write-metadata",
            ]

            if self.only_metadata:
                command += ["--no-download"]
            
            # Only add the archive option if we're NOT skipping the archive
            if not self.skip_archive:
                command += ["--download-archive", archive_path_local]
                self.progress.emit(f"DEBUG: Using archive path: {archive_path_local}")

            # Add R-18 filter if requested
            if self.r18_only:
                if self.mode == "authors" or source_key == "pixiv":
                    command += ["--filter", "'R-18' in tags or 'R-18G' in tags"]
                elif source_key in ("danbooru", "rule34"):
                    command += ["--filter", "rating == 'explicit' or rating == 'e'"]
                elif source_key == "kemono":
                    command += ["--filter", "'R-18' in tags or 'explicit' in tags"]
                elif source_key == "gelbooru":
                    command += ["--filter", "rating == 'e' or rating == 'explicit'"]

            if self.no_subfolders:
                command += ["--directory", ""]

            # URL must go last
            command.append(url)

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

                if stdout and stdout[0] == "#":
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
        self.setMinimumWidth(600)
        
        # Initialize settings
        self.settings = QSettings("GalleryDL", "DownloaderApp")
        
        layout = QVBoxLayout()

        # Base directory input
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Optional: Enter base directory...")
        self.dir_input.setText(self.settings.value("base_directory", ""))
        dir_browse_btn = QPushButton("Browse...")
        dir_browse_btn.clicked.connect(self.browse_directory)
        
        dir_layout.addWidget(QLabel("Base Directory:"))
        dir_layout.addWidget(self.dir_input, 1)
        dir_layout.addWidget(dir_browse_btn)
        layout.addLayout(dir_layout)
        
        # Archive database input
        archive_layout = QHBoxLayout()
        self.archive_input = QLineEdit()
        self.archive_input.setPlaceholderText("Optional: Enter archive.db path...")
        self.archive_input.setText(self.settings.value("archive_path", ""))
        archive_browse_btn = QPushButton("Browse...")
        archive_browse_btn.clicked.connect(self.browse_archive)
        
        archive_layout.addWidget(QLabel("Archive DB:"))
        archive_layout.addWidget(self.archive_input, 1)
        archive_layout.addWidget(archive_browse_btn)
        layout.addLayout(archive_layout)

        # Button layout
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("Get opened tabs")
        self.start_button.clicked.connect(self.start_download)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_download)

        self.view_db_button = QPushButton("View Database")
        self.view_db_button.setEnabled(True)
        self.view_db_button.clicked.connect(self.show_database)

        self.author_button = QPushButton("Update authors")
        self.author_button.setEnabled(True)
        self.author_button.clicked.connect(self.author_download)

        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.author_button)
        btn_layout.addWidget(self.view_db_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Load checkbox states from settings
        check_layout = QHBoxLayout()
        self.r18_checkbox = QCheckBox("Only R-18")
        self.r18_checkbox.setChecked(self.settings.value("r18_only", False, type=bool))
        
        self.no_subfolders_checkbox = QCheckBox("No subfolders")
        self.no_subfolders_checkbox.setChecked(self.settings.value("no_subfolders", False, type=bool))
        
        self.only_metadata_checkbox = QCheckBox("Only metadata")
        self.only_metadata_checkbox.setChecked(self.settings.value("only_metadata", False, type=bool))
        
        self.no_archive_checkbox = QCheckBox("Don't archive")
        self.no_archive_checkbox.setChecked(self.settings.value("skip_archive", False, type=bool))

        # Connect checkbox state changes to save settings
        self.r18_checkbox.stateChanged.connect(lambda: self.save_checkbox_settings())
        self.no_subfolders_checkbox.stateChanged.connect(lambda: self.save_checkbox_settings())
        self.only_metadata_checkbox.stateChanged.connect(lambda: self.save_checkbox_settings())
        self.no_archive_checkbox.stateChanged.connect(lambda: self.save_checkbox_settings())

        check_layout.addWidget(self.r18_checkbox)
        check_layout.addWidget(self.no_subfolders_checkbox)
        check_layout.addWidget(self.only_metadata_checkbox)
        check_layout.addWidget(self.no_archive_checkbox)
        layout.addLayout(check_layout)

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.output_log)

        self.setLayout(layout)
        self.thread = None

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Base Directory")
        if directory:
            self.dir_input.setText(directory)
            self.settings.setValue("base_directory", directory)

    def browse_archive(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Select Archive Database File",
            self.archive_input.text() or os.path.join(os.getcwd(), "archive.db"),
            "Database Files (*.db);;All Files (*)",
            options=options
        )
        if file_name:
            self.archive_input.setText(file_name)
            self.settings.setValue("archive_path", file_name)

    def save_checkbox_settings(self):
        # Save checkbox states whenever they change
        self.settings.setValue("r18_only", self.r18_checkbox.isChecked())
        self.settings.setValue("no_subfolders", self.no_subfolders_checkbox.isChecked())
        self.settings.setValue("only_metadata", self.only_metadata_checkbox.isChecked())
        self.settings.setValue("skip_archive", self.no_archive_checkbox.isChecked())

    def save_settings(self):
        # Save text input values
        self.settings.setValue("base_directory", self.dir_input.text())
        self.settings.setValue("archive_path", self.archive_input.text())

    def setup_worker(self, mode):
        """Set up worker thread with common configurations"""
        base_dir = self.dir_input.text().strip() or None
        archive_path = self.archive_input.text().strip() or None
        
        # Save settings whenever a download is started
        self.save_settings()
        
        self.start_button.setEnabled(False)
        self.author_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        self.thread = DownloadWorker(base_dir, archive_path, mode=mode)
        self.thread.r18_only = self.r18_checkbox.isChecked()
        self.thread.no_subfolders = self.no_subfolders_checkbox.isChecked()
        self.thread.only_metadata = self.only_metadata_checkbox.isChecked()
        self.thread.skip_archive = self.no_archive_checkbox.isChecked()
        self.thread.progress.connect(self.output_log.append)
        self.thread.progress_percent.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_finished)
        return self.thread

    def start_download(self):
        self.output_log.clear()
        self.output_log.append("Scanning for gallery URLs...")
        self.setup_worker(mode="tabs").start()

    def author_download(self):
        self.output_log.clear()
        self.output_log.append("Scanning for listed author URLs...")
        self.setup_worker(mode="authors").start()

    def cancel_download(self):
        if self.thread:
            self.output_log.append("Cancelling download...")
            self.thread.cancel()

    def on_finished(self, message):
        self.output_log.append(message)
        self.start_button.setEnabled(True)
        self.author_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.thread = None
        
    def closeEvent(self, event):
        # Save settings when the app is closed
        self.save_settings()
        self.save_checkbox_settings()
        super().closeEvent(event)

    def show_database(self):
        db_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            "",
            "SQLite Database (*.db);;All Files (*)"
        )
        if not db_path:
            return  # user cancelled

        headers = []
        rows = []

        try:
            headers, rows = fetch_all_from_db(db_path, table="archive")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read database:\n{e}")
            return

        dlg = QDialog(self)
        dlg.setWindowFlags(Qt.Window)
        dlg.setWindowTitle(f"Database Contents for: {os.path.basename(db_path)}")
        layout = QVBoxLayout(dlg)

        table = QTableWidget()
        table.setRowCount(len(rows))
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))
        layout.addWidget(table)

        dlg.setLayout(layout)
        dlg.resize(800, 400)
        dlg.exec()

# --- Main ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec())