import sys
import time
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog,
    QVBoxLayout, QWidget, QAction
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from timeline import TimelineWidget

# Mock beat times in seconds
beat_times = [1, 2, 3.5, 5, 6, 7.2, 8.5]

# Convert to ms
beat_times_sec = [1, 2, 3.5, 5, 6, 7.2, 8.5]
beat_times = [int(b * 1000) for b in beat_times_sec]

class VideoBeatPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player with Beat Sync")
        self.setGeometry(100, 100, 800, 600)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)

        self.timeline = TimelineWidget(beat_times=beat_times, media_player=self.media_player)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.timeline)
        layout.setStretch(0, 1)
        layout.setStretch(1, 0)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

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
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv *.mov)")
        if file_name:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            self.media_player.play()
            self.start_time = time.time()
            self.current_beat = 0

    def check_beat(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            if self.current_beat < len(beat_times_sec) and elapsed >= beat_times_sec[self.current_beat]:
                self.timeline.flash()
                self.current_beat += 1

    def trigger_cue(self, text):
        self.label.setText(text)
        QTimer.singleShot(300, lambda: self.label.setText(""))  # Clear after 300ms

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoBeatPlayer()
    window.show()
    sys.exit(app.exec_())
