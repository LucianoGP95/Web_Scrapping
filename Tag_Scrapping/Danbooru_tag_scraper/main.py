import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                                QComboBox, QRadioButton, QPushButton, QVBoxLayout, 
                                QWidget, QFileDialog, QMessageBox, QButtonGroup)
from PySide6.QtCore import Qt
# Assuming the get_danbooru_tags module exists in the same directory
from get_danbooru_tags import get_tags_raw, get_tags_refined

class BaseApp(QMainWindow):
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        self.setWindowTitle("Danbooru tag downloader")
        self.setFixedSize(500, 300)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
    def switch_window(self, new_window):
        """Close current window and open a new one."""
        self.close()
        self.new_window = new_window()
        self.new_window.show()

class DownloaderApp(BaseApp):
    def __init__(self, root_path: str):
        super().__init__()  # Initialize the base class
        
        # Path creation
        self.root_path = root_path
        # Parameters
        self.base_url = 'https://danbooru.donmai.us/tags.json?limit=1000&search[hide_empty]=yes&search[is_deprecated]=no&search[order]=count'
        self.output_file_raw = None
        self.output_file_refined = None

        # Minimum post count section
        self.postcount_label = QLabel("Minimun tags' posts to add:")
        self.layout.addWidget(self.postcount_label)
        
        self.postcount_entry = QLineEdit("100")
        self.layout.addWidget(self.postcount_entry)

        # Category selection section
        self.category_label = QLabel("Tags selection:")
        self.layout.addWidget(self.category_label)
        
        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems([
            "All",
            "General",
            "Artist",
            "Copyright",
            "Character",
            "Meta",
            "Author"
        ])
        self.layout.addWidget(self.category_dropdown)
        
        # Rewrite existing files section
        self.rewrite_label = QLabel("Rewrite existent files:")
        self.layout.addWidget(self.rewrite_label)
        
        # Create a button group for radio buttons
        self.rewrite_group = QButtonGroup(self)
        
        self.no_button = QRadioButton("No")
        self.yes_button = QRadioButton("Yes")
        self.no_button.setChecked(True)  # Default to "No"
        
        self.rewrite_group.addButton(self.no_button, 0)
        self.rewrite_group.addButton(self.yes_button, 1)
        
        self.layout.addWidget(self.no_button)
        self.layout.addWidget(self.yes_button)

        # Action buttons
        self.get_raw_tags_button = QPushButton("Get raw tags!")
        self.get_raw_tags_button.clicked.connect(self.get_raw_tags)
        self.layout.addWidget(self.get_raw_tags_button)

        self.get_refined_tags_button = QPushButton("Get refined tags!")
        self.get_refined_tags_button.clicked.connect(self.get_refined_tags)
        self.layout.addWidget(self.get_refined_tags_button)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)

    def get_raw_tags(self):
        try:
            postcount = self.postcount_entry.text()
            category = self.category_dropdown.currentText()
            rewrite = self.yes_button.isChecked()

            safe_category = category.replace(" ", "_")
            self.output_file_raw = os.path.join(self.root_path, f"{safe_category}_raw_tags.csv")

            self.status_label.setText("Downloading raw tags...")
            get_tags_raw(self.base_url, self.output_file_raw, category,
                        postcount_filter=postcount, rewrite_existent=rewrite)

            QMessageBox.information(self, "Success", "Raw tags downloaded successfully!")
            self.status_label.setText("Raw tags downloaded")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download tags: {str(e)}")
            self.status_label.setText("Error downloading tags")

    def get_refined_tags(self):
        try:
            rewrite = self.yes_button.isChecked()
            category = self.category_dropdown.currentText()
            safe_category = category.replace(" ", "_")

            self.output_file_raw = os.path.join(self.root_path, f"{safe_category}_raw_tags.csv")
            self.output_file_refined = os.path.join(self.root_path, f"{safe_category}_tags.csv")

            if not os.path.exists(self.output_file_raw):
                QMessageBox.warning(self, "Warning", "Raw tags file doesn't exist. Please download raw tags first.")
                return

            self.status_label.setText("Refining tags...")
            get_tags_refined(self.output_file_raw, self.output_file_refined, rewrite_existent=rewrite)

            QMessageBox.information(self, "Success", "Tags refined successfully!")
            self.status_label.setText("Tags refined")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refine tags: {str(e)}")
            self.status_label.setText("Error refining tags")

class SettingsApp(BaseApp):
    def __init__(self):
        super().__init__()
        
        settings_label = QLabel("Settings Window")
        self.layout.addWidget(settings_label)
        
        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.switch_window(DownloaderApp))
        self.layout.addWidget(back_button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Use the absolute path for tags storage
    root_path = os.path.abspath("../scraped_tags")
    print(root_path)
    
    # Create the directory if it doesn't exist
    os.makedirs(root_path, exist_ok=True)
    
    main_window = DownloaderApp(root_path)
    main_window.show()
    
    sys.exit(app.exec())