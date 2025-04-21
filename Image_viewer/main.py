import sys, os, random
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QVBoxLayout, QWidget, QAction, QInputDialog, QActionGroup
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QSettings


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Image Viewer")
        self.setGeometry(200, 200, 800, 600)
        self.setMouseTracking(True)

        self.settings = QSettings("MyCompany", "ImageViewer")
        self.slideshow_time = int(self.settings.value("slideshow_time", 3000))
        self.order_mode = self.settings.value("order_mode", "normal")

        self.image_paths = []
        self.current_index = 0
        self.fullscreen = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next)

        self.hide_ui_timer = QTimer()
        self.hide_ui_timer.setSingleShot(True)
        self.hide_ui_timer.timeout.connect(self.hide_controls)

        # UI Elements
        self.label = QLabel("Open a folder to start", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel { background-color: black; color: white; }")

        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.slideshow_button = QPushButton("Start Slideshow")
        self.fullscreen_button = QPushButton("Fullscreen")
        self.counter_label = QLabel("0 / 0")
        self.counter_label.setStyleSheet("color: black;")

        self.prev_button.clicked.connect(self.show_previous)
        self.next_button.clicked.connect(self.show_next)
        self.slideshow_button.clicked.connect(self.toggle_slideshow)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.slideshow_button)
        button_layout.addWidget(self.fullscreen_button)
        button_layout.addWidget(self.counter_label)

        layout = QVBoxLayout()
        layout.addWidget(self.label, stretch=1) 
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Menu
        open_action = QAction("Open Folder", self)
        open_action.triggered.connect(self.open_folder)

        set_time_action = QAction("Set Slideshow Time", self)
        set_time_action.triggered.connect(self.set_slideshow_time)

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(set_time_action)

        # Order mode actions
        order_menu = self.menuBar().addMenu("Order Mode")
        self.order_group = QActionGroup(self)

        self.normal_order_action = QAction("Normal", self, checkable=True)
        self.random_order_action = QAction("Random", self, checkable=True)
        self.random_by_folders_action = QAction("Random by Folders", self, checkable=True)

        self.order_group.addAction(self.normal_order_action)
        self.order_group.addAction(self.random_order_action)
        self.order_group.addAction(self.random_by_folders_action)

        order_menu.addAction(self.normal_order_action)
        order_menu.addAction(self.random_order_action)
        order_menu.addAction(self.random_by_folders_action)

        self.normal_order_action.triggered.connect(lambda: self.set_order_mode("normal"))
        self.random_order_action.triggered.connect(lambda: self.set_order_mode("random"))
        self.random_by_folders_action.triggered.connect(lambda: self.set_order_mode("random_by_folders"))

        # Restore previous mode
        if self.order_mode == "random":
            self.random_order_action.setChecked(True)
        elif self.order_mode == "random_by_folders":
            self.random_by_folders_action.setChecked(True)
        else:
            self.normal_order_action.setChecked(True)

    def set_order_mode(self, mode):
        self.order_mode = mode
        self.settings.setValue("order_mode", mode)
        if self.image_paths:
            self.prepare_image_list(self.last_folder)
            self.current_index = 0
            self.show_image()

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.last_folder = folder
            self.prepare_image_list(folder)
            self.current_index = 0
            if self.image_paths:
                self.show_image()

    def prepare_image_list(self, folder):
        grouped = defaultdict(list)
        for root, _, files in os.walk(folder):
            for file in sorted(files):
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
                    grouped[root].append(os.path.join(root, file))

        if self.order_mode == "random":
            self.image_paths = [img for imgs in grouped.values() for img in imgs]
            random.shuffle(self.image_paths)
        elif self.order_mode == "random_by_folders":
            folders = list(grouped.keys())
            random.shuffle(folders)
            self.image_paths = []
            for folder in folders:
                self.image_paths.extend(grouped[folder])
        else:  # normal
            self.image_paths = [img for folder in sorted(grouped.keys()) for img in grouped[folder]]

    def show_image(self):
        if not self.image_paths:
            return
        pixmap = QPixmap(self.image_paths[self.current_index])
        if not pixmap.isNull():
            self.label.setPixmap(pixmap.scaled(
                self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.counter_label.setText(f"{self.current_index + 1} / {len(self.image_paths)}")

    def resizeEvent(self, event):
        self.show_image()

    def show_next(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.show_image()

    def show_previous(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.show_image()

    def toggle_slideshow(self):
        if self.timer.isActive():
            self.timer.stop()
            self.slideshow_button.setText("Start Slideshow")
        else:
            self.timer.start(self.slideshow_time)
            self.slideshow_button.setText("Stop Slideshow")

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.showNormal()
            self.menuBar().show()
            self.prev_button.show()
            self.next_button.show()
            self.slideshow_button.show()
            self.fullscreen_button.setText("Fullscreen")
            self.fullscreen_button.show()
            self.hide_ui_timer.stop()
        else:
            self.showFullScreen()
            self.fullscreen_button.setText("Exit Fullscreen")
            self.hide_controls()
        self.fullscreen = not self.fullscreen

    def show_controls(self):
        if self.fullscreen:
            self.prev_button.show()
            self.next_button.show()
            self.slideshow_button.show()
            self.fullscreen_button.show()
            self.menuBar().show()
            self.hide_ui_timer.start(1000)

    def hide_controls(self):
        if self.fullscreen:
            self.prev_button.hide()
            self.next_button.hide()
            self.slideshow_button.hide()
            self.fullscreen_button.hide()
            self.menuBar().hide()

    def mouseMoveEvent(self, event):
        self.show_controls()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()

    def set_slideshow_time(self):
        time, ok = QInputDialog.getInt(
            self, "Set Slideshow Time", "Time per slide (ms):",
            self.slideshow_time, 100, 10000, 100)
        if ok:
            self.slideshow_time = time
            self.settings.setValue("slideshow_time", time)
            if self.timer.isActive():
                self.timer.stop()
                self.timer.start(self.slideshow_time)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
