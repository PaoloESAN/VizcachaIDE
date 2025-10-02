"""
Call stack viewer widget for debugging
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont


class CallStackWidget(QListWidget):
    """Widget for displaying the call stack during debugging"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set font
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.setFont(font)

        # Set alternating row colors
        self.setAlternatingRowColors(True)

    def update_callstack(self, stack_frames):
        """Update the call stack display

        Args:
            stack_frames: List of stack frame strings
        """
        self.clear()

        for frame in stack_frames:
            item = QListWidgetItem(frame)
            self.addItem(item)

    def clear(self):
        """Clear the call stack"""
        super().clear()
