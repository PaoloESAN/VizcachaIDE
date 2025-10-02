"""
Console widget for displaying output, errors, and accepting input
"""

from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor, QColor, QFont, QPalette
from PyQt5.QtCore import Qt, pyqtSignal


class ConsoleWidget(QTextEdit):
    """Console for program output and errors with input support"""

    input_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Input state
        self.input_enabled = False
        self.input_start_pos = 0
        self.waiting_for_input = False

        # Set font
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.setFont(font)

        # Set color scheme
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor("#1E1E1E"))
        palette.setColor(QPalette.Text, QColor("#D4D4D4"))
        self.setPalette(palette)

        # Welcome message
        self.append_output("VizcachaIDE Console - Ready\n")

    def append_output(self, text):
        """Append normal output text"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Set text color for normal output
        format = cursor.charFormat()
        format.setForeground(QColor("#D4D4D4"))
        cursor.setCharFormat(format)

        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

        # Auto-enable input when we see output (program might be waiting)
        if self.waiting_for_input and not self.input_enabled:
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self.enable_input)

    def append_error(self, text):
        """Append error text in red"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Set text color for errors
        format = cursor.charFormat()
        format.setForeground(QColor("#F48771"))
        cursor.setCharFormat(format)

        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def append_success(self, text):
        """Append success text in green"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Set text color for success
        format = cursor.charFormat()
        format.setForeground(QColor("#4EC9B0"))
        cursor.setCharFormat(format)

        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear(self):
        """Clear console output"""
        super().clear()
        self.waiting_for_input = False

    def enable_input(self):
        """Enable user input mode"""
        if self.input_enabled:
            return
        self.input_enabled = True
        self.setReadOnly(False)
        self.input_start_pos = self.textCursor().position()
        self.setFocus()

    def disable_input(self):
        """Disable user input mode"""
        self.input_enabled = False
        self.setReadOnly(True)

    def set_waiting_for_input(self, waiting):
        """Mark that program is waiting for input"""
        self.waiting_for_input = waiting

    def keyPressEvent(self, event):
        """Handle key press events for input"""
        if not self.input_enabled:
            super().keyPressEvent(event)
            return

        # Handle Enter key to submit input
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)

            # Get the input text
            cursor.setPosition(self.input_start_pos)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            input_text = cursor.selectedText()

            # Add newline to console
            self.append("\n")

            # Disable input and emit signal
            self.disable_input()
            self.input_submitted.emit(input_text)
            return

        # Handle backspace - prevent deleting before input start
        if event.key() == Qt.Key_Backspace:
            if self.textCursor().position() <= self.input_start_pos:
                return

        # Handle cursor movement - keep cursor after input start
        cursor = self.textCursor()
        if cursor.position() < self.input_start_pos:
            cursor.setPosition(self.input_start_pos)
            self.setTextCursor(cursor)

        super().keyPressEvent(event)
