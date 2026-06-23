"""
Call stack viewer widget for debugging
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont, QPalette


class CallStackWidget(QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        font = QFont("Consolas", 9)
        font.setWeight(QFont.Medium)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
            font.setWeight(QFont.Medium)
        self.setFont(font)

        self.setAlternatingRowColors(True)
        
        self.setAutoFillBackground(True)

    def update_callstack(self, stack_frames):
        self.clear()

        for frame in stack_frames:
            item = QListWidgetItem(frame)
            self.addItem(item)

    def clear(self):
        super().clear()
