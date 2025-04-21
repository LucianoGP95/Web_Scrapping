from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import QTimer, Qt


class TimelineWidget(QWidget):
    def __init__(self, beat_times, media_player, duration=10000, parent=None):
        super().__init__(parent)
        self.beat_times = beat_times  # in ms
        self.media_player = media_player
        self.duration = duration  # ms window of visible time ahead
        self.flash_color = QColor("red")
        self.flash_alpha = 0

        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.fade_flash)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(16)

    def flash(self):
        self.flash_alpha = 255
        self.flash_timer.start(30)

    def fade_flash(self):
        if self.flash_alpha > 0:
            self.flash_alpha -= 15
            self.update()
        else:
            self.flash_timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # Draw flash if active
        if self.flash_alpha > 0:
            c = QColor(self.flash_color)
            c.setAlpha(self.flash_alpha)
            painter.fillRect(self.rect(), c)

        # Draw timeline
        bar_y = self.height() // 2
        painter.setPen(QPen(QColor("gray"), 2))
        painter.drawLine(0, bar_y, self.width(), bar_y)

        # Draw beat markers
        current_pos = self.media_player.position()
        for beat in self.beat_times:
            rel = (beat - current_pos) / self.duration
            if 0 <= rel <= 1:
                x = int(rel * self.width())
                painter.setPen(QPen(QColor("red"), 3))
                painter.drawEllipse(x - 3, bar_y - 3, 6, 6)
