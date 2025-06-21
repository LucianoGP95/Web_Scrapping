import os
import json
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                QRadioButton, QMessageBox, QFileDialog, QButtonGroup,
                                QComboBox, QFrame, QProgressBar, QDialog)
from PySide6.QtCore import Qt, QThread, Signal, QEventLoop
from core_logic import Downloader


class DownloadThread(QThread):
    """Thread for handling downloads without freezing the UI"""
    progress_update = Signal(str)
    download_complete = Signal(bool, str)
    
    def __init__(self, url, output_folder, download_type, normalize_audio, ask_download_list, download_playlist=True):
        super().__init__()
        self.url = url
        self.output_folder = output_folder
        self.download_type = download_type
        self.normalize_audio = normalize_audio
        self.ask_download_list = ask_download_list
        self.is_playlist = "list=" in url
        self.download_playlist = download_playlist
    
    def run(self):
        try:
            downloader = Downloader(self.url, self.output_folder)
            
            # Set progress callback
            def progress_callback(percent):
                self.progress_update.emit(str(percent))
            
            downloader.set_progress_callback(progress_callback)
            
            # Configure options based on download type
            if self.download_type == "audio":
                downloader.get_audio_opts()
            else:
                downloader.get_video_opts()
            
            # Handle playlist option
            if self.is_playlist and not self.download_playlist:
                downloader.add_option("--no-playlist")
            
            # Download and process
            result = downloader.download_video()
            metadata_result = ""
            
            if self.download_type == "audio":
                metadata_result = downloader.add_audio_metadata()
            
            complete_message = f"{result}\n{metadata_result}" if metadata_result else result
            self.download_complete.emit(True, complete_message)
        except Exception as e:
            self.download_complete.emit(False, f"Download failed: {str(e)}")


class BaseWindow(QMainWindow):
    """Base window class with common functionality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(700, 500)
        
        # Default settings
        self.ask_download_list = True
        self.normalize_audio = True
        
        # Default paths
        self.default_audio_folder = os.path.join(os.getcwd(), "downloads", "audio")
        self.default_video_folder = os.path.join(os.getcwd(), "downloads", "video")
        self.info_path = os.path.join(os.getcwd(), "config", "help.json")  # Fixed path
        
        # Create directories if they don't exist
        os.makedirs(self.default_audio_folder, exist_ok=True)
        os.makedirs(self.default_video_folder, exist_ok=True)
        os.makedirs(os.path.dirname(self.info_path), exist_ok=True)  # Create config dir
        
        # Load app version from json file
        try:
            with open(self.info_path, "r") as config_file:
                config_data = json.load(config_file)
                self.APP_VERSION = config_data.get("version", "1.0.0")  # Use .get() for safety
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.APP_VERSION = "1.0.0"  # Default version if file not found
    
    def show_message(self, title, message, icon=QMessageBox.Information):
        """Show a message box with the given title and message"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec()
    
    def show_version(self):
        """Show the app version"""
        self.show_message("Version", f"YouTube Downloader v{self.APP_VERSION}")


class MainWindow(BaseWindow):
    """Main application window"""
    
    def __init__(self, settings=None):
        super().__init__()
        
        # Apply settings if provided
        if settings:
            self.ask_download_list = settings.get('ask_download_list', True)
            self.normalize_audio = settings.get('normalize_audio', True)
        
        self.output_folder = self.default_audio_folder  # Default to audio folder
        self.download_thread = None  # Initialize download thread reference
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle("YouTube Downloader")
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # URL input section
        url_label = QLabel("Video URL:")
        url_label.setStyleSheet("font-weight: bold;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL here...")
        
        # Folder selection section
        folder_label = QLabel("Output Folder:")
        folder_label.setStyleSheet("font-weight: bold;")
        
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setText(self.output_folder)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_input, 3)
        folder_layout.addWidget(browse_button, 1)
        
        # Download type selection
        type_label = QLabel("Download Type:")
        type_label.setStyleSheet("font-weight: bold;")
        
        type_layout = QHBoxLayout()
        self.type_group = QButtonGroup(self)
        
        self.audio_radio = QRadioButton("Audio (MP3)")
        self.video_radio = QRadioButton("Video (MP4)")
        self.type_group.addButton(self.audio_radio, 1)
        self.type_group.addButton(self.video_radio, 2)
        self.audio_radio.setChecked(True)  # Default to audio
        
        # Connect radio buttons to folder update
        self.audio_radio.clicked.connect(self.update_output_folder)
        self.video_radio.clicked.connect(self.update_output_folder)
        
        type_layout.addWidget(self.audio_radio)
        type_layout.addWidget(self.video_radio)
        type_layout.addStretch()
        
        # Progress section
        progress_frame = QFrame()
        progress_frame.setFrameShape(QFrame.StyledPanel)
        progress_layout = QVBoxLayout(progress_frame)
        
        self.progress_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.download_button = QPushButton("Download")
        self.download_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 16px;")
        self.download_button.setMinimumHeight(40)
        self.download_button.clicked.connect(self.start_download)
        
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_version)
        
        button_layout.addWidget(self.download_button, 2)
        button_layout.addWidget(self.settings_button, 1)
        button_layout.addWidget(self.about_button, 1)
        
        # Add everything to main layout
        main_layout.addWidget(url_label)
        main_layout.addWidget(self.url_input)
        main_layout.addWidget(folder_label)
        main_layout.addLayout(folder_layout)
        main_layout.addWidget(type_label)
        main_layout.addLayout(type_layout)
        main_layout.addWidget(progress_frame)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def select_folder(self):
        """Open dialog to select output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self.folder_input.setText(folder)
            self.output_folder = folder
    
    def update_output_folder(self):
        """Update the default output folder based on selected download type"""
        if self.audio_radio.isChecked():
            self.folder_input.setText(self.default_audio_folder)
            self.output_folder = self.default_audio_folder
        else:
            self.folder_input.setText(self.default_video_folder)
            self.output_folder = self.default_video_folder
    
    def update_progress(self, progress_str):
        """Update the progress bar and label"""
        try:
            # Handle different progress string formats
            if isinstance(progress_str, str):
                # Extract percentage from string like '87.5%' or just '87.5'
                clean_progress = progress_str.replace('%', '').strip()
                progress_val = float(clean_progress)
            else:
                progress_val = float(progress_str)
            
            # Clamp progress between 0 and 100
            progress_val = max(0, min(100, progress_val))
            
            self.progress_bar.setValue(int(progress_val))
            self.progress_label.setText(f"Downloading: {progress_val:.1f}%")
        except (ValueError, AttributeError, TypeError):
            # If the progress string can't be converted to a number,
            # just show the message
            self.progress_label.setText("Downloading...")
    
    def download_finished(self, success, message):
        """Handle download completion"""
        if success:
            self.progress_bar.setValue(100)
            self.progress_label.setText("Download complete!")
            
            # Show only the first few lines if message is very long
            if isinstance(message, str) and len(message.splitlines()) > 10:
                short_message = "\n".join(message.splitlines()[:10])
                short_message += f"\n\n... and {len(message.splitlines()) - 10} more items"
                self.show_message("Success", short_message)
            else:
                self.show_message("Success", str(message))
        else:
            self.progress_label.setText("Download failed!")
            self.show_message("Error", str(message), QMessageBox.Critical)
        
        # Re-enable the download button and clean up thread
        self.download_button.setEnabled(True)
        if self.download_thread:
            self.download_thread.deleteLater()
            self.download_thread = None
    
    def start_download(self):
        """Start the download process"""
        url = self.url_input.text().strip()
        output_folder = self.folder_input.text().strip()
        
        # Validate input
        if not url:
            self.show_message("Error", "Please enter a YouTube URL", QMessageBox.Warning)
            return
        
        if not output_folder:
            self.show_message("Error", "Please select an output folder", QMessageBox.Warning)
            return
        
        # Ensure output folder exists
        try:
            os.makedirs(output_folder, exist_ok=True)
        except OSError as e:
            self.show_message("Error", f"Cannot create output folder: {str(e)}", QMessageBox.Critical)
            return
        
        # Check if it's a playlist and confirm if needed
        is_playlist = "list=" in url
        download_playlist = True
        
        if is_playlist and self.ask_download_list:
            reply = QMessageBox.question(
                self, 
                "Playlist Detected",
                "Do you want to download the entire playlist?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            download_playlist = (reply == QMessageBox.Yes)
        
        # Determine download type
        download_type = "audio" if self.audio_radio.isChecked() else "video"
        
        # Disable download button during download
        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting download...")
        
        # Clean up previous thread if it exists
        if self.download_thread:
            self.download_thread.quit()
            self.download_thread.wait()
            self.download_thread.deleteLater()
        
        # Create and start download thread
        self.download_thread = DownloadThread(
            url, 
            output_folder, 
            download_type, 
            self.normalize_audio, 
            self.ask_download_list,
            download_playlist
        )
        self.download_thread.progress_update.connect(self.update_progress)
        self.download_thread.download_complete.connect(self.download_finished)
        self.download_thread.start()
    
    def open_settings(self):
        """Open the settings window"""
        settings_dialog = SettingsWindow(self.ask_download_list, self.normalize_audio)
        if settings_dialog.exec():
            # Update settings if dialog was accepted
            self.ask_download_list = settings_dialog.ask_download_list
            self.normalize_audio = settings_dialog.normalize_audio
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop download thread if running
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.quit()
            self.download_thread.wait(3000)  # Wait up to 3 seconds
        event.accept()


class SettingsWindow(QDialog):  # Changed from QMainWindow to QDialog
    """Settings window dialog"""
    
    def __init__(self, ask_download_list, normalize_audio, parent=None):
        super().__init__(parent)
        
        # Store current settings
        self.ask_download_list = ask_download_list
        self.normalize_audio = normalize_audio
        
        # Set window properties
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 300)
        self.setModal(True)  # Make dialog modal
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Playlist confirmation setting
        playlist_label = QLabel("Show playlist download confirmation message?")
        playlist_label.setStyleSheet("font-weight: bold;")
        
        self.playlist_combo = QComboBox()
        self.playlist_combo.addItems(["True", "False"])
        self.playlist_combo.setCurrentText(str(self.ask_download_list))
        
        # Audio normalization setting
        normalize_label = QLabel("Normalize audio?")
        normalize_label.setStyleSheet("font-weight: bold;")
        
        self.normalize_combo = QComboBox()
        self.normalize_combo.addItems(["True", "False"])
        self.normalize_combo.setCurrentText(str(self.normalize_audio))
        
        # Add explanation labels
        playlist_explanation = QLabel("When enabled, asks for confirmation before downloading playlists")
        playlist_explanation.setStyleSheet("color: gray; font-style: italic;")
        
        normalize_explanation = QLabel("Normalizes audio volume levels (recommended)")
        normalize_explanation.setStyleSheet("color: gray; font-style: italic;")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # Add everything to main layout
        main_layout.addWidget(playlist_label)
        main_layout.addWidget(self.playlist_combo)
        main_layout.addWidget(playlist_explanation)
        main_layout.addSpacing(10)
        main_layout.addWidget(normalize_label)
        main_layout.addWidget(self.normalize_combo)
        main_layout.addWidget(normalize_explanation)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
    
    def save_settings(self):
        """Save settings and close dialog"""
        self.ask_download_list = self.playlist_combo.currentText() == "True"
        self.normalize_audio = self.normalize_combo.currentText() == "True"
        
        # Show confirmation message
        QMessageBox.information(
            self,
            "Settings Saved",
            f"Settings updated:\n"
            f"- Ask for playlist confirmation: {self.ask_download_list}\n"
            f"- Normalize audio: {self.normalize_audio}"
        )
        
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply some basic styling
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())