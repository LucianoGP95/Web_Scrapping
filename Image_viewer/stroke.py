import sys
import time
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog,
    QVBoxLayout, QWidget, QAction, QStackedLayout
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

beat_times = [1, 2, 3.5, 5, 6, 7.2, 8.5]

class VideoBeatPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player with Beat Overlay")
        self.setGeometry(100, 100, 800, 600)

        # Media player and video widget
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # Overlay label
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 72px;
            color: red;
            background-color: rgba(0, 0, 0, 100);
        """)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label.setSizePolicy(self.video_widget.sizePolicy())

        # Widget for stacking
        container = QWidget(self)
        stacked_layout = QStackedLayout(container)
        stacked_layout.addWidget(self.video_widget)
        stacked_layout.addWidget(self.label)

        self.setCentralWidget(container)

        # Timer
        self.start_time = None
        self.current_beat = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_beat)
        self.timer.start(10)

        self.init_menu()

    def init_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        open_action = QAction('Open Video', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )
        if file_name:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            self.media_player.play()
            self.start_time = time.time()
            self.current_beat = 0

    def check_beat(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            if self.current_beat < len(beat_times) and elapsed >= beat_times[self.current_beat]:
                self.trigger_cue("STROKE")
                self.current_beat += 1

    def trigger_cue(self, text):
        self.label.setText(text)
        QTimer.singleShot(300, lambda: self.label.setText(""))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoBeatPlayer()
    window.show()
    sys.exit(app.exec_())
