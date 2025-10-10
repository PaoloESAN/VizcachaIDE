"""
Autocomplete widget for code completion with documentation
"""

from PyQt5.QtWidgets import (QListWidget, QListWidgetItem, QLabel, QVBoxLayout,
                             QWidget, QStyledItemDelegate, QStyle)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QTextDocument


class CompletionItemDelegate(QStyledItemDelegate):
    """Custom delegate for rendering completion items with documentation"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        """Custom paint method to show method name and brief doc"""
        painter.save()

        # Get data
        item_data = index.data(Qt.UserRole)
        if not item_data:
            super().paint(painter, option, index)
            painter.restore()
            return

        name = item_data.get('name', '')
        signature = item_data.get('signature', '')
        doc = item_data.get('doc', '')
        kind = item_data.get('kind', 'function')

        # Draw background
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor("#0078D4"))
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor("#E5F3FF"))

        # Set up fonts
        name_font = QFont("Consolas", 10, QFont.Bold)
        sig_font = QFont("Consolas", 9)
        doc_font = QFont("Arial", 8)

        # Draw icon/kind indicator
        kind_color = {
            'function': QColor("#795E26"),
            'method': QColor("#795E26"),
            'variable': QColor("#001080"),
            'const': QColor("#0070C1"),
            'type': QColor("#267F99"),
            'package': QColor("#AF00DB"),
        }.get(kind, QColor("#000000"))

        painter.setPen(kind_color)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        kind_symbol = {
            'function': 'ƒ',
            'method': 'ƒ',
            'variable': '◆',
            'const': '◇',
            'type': '⊤',
            'package': '□',
        }.get(kind, '●')
        painter.drawText(option.rect.adjusted(5, 0, 0, 0), Qt.AlignVCenter, kind_symbol)

        # Calculate positions
        y_offset = option.rect.top()
        x_offset = option.rect.left() + 25

        # Draw name
        painter.setFont(name_font)
        if option.state & QStyle.State_Selected:
            painter.setPen(QColor("#FFFFFF"))
        else:
            painter.setPen(QColor("#000000"))
        painter.drawText(x_offset, y_offset + 15, name)

        # Draw signature
        if signature:
            painter.setFont(sig_font)
            if option.state & QStyle.State_Selected:
                painter.setPen(QColor("#E0E0E0"))
            else:
                painter.setPen(QColor("#666666"))
            painter.drawText(x_offset + painter.fontMetrics().horizontalAdvance(name) + 5,
                           y_offset + 15, signature)

        # Draw documentation (first line only)
        if doc:
            painter.setFont(doc_font)
            if option.state & QStyle.State_Selected:
                painter.setPen(QColor("#D0D0D0"))
            else:
                painter.setPen(QColor("#888888"))

            # Truncate doc if too long
            max_width = option.rect.width() - x_offset - 10
            metrics = painter.fontMetrics()
            doc_text = doc.split('\n')[0]  # First line only
            elided_doc = metrics.elidedText(doc_text, Qt.ElideRight, max_width)
            painter.drawText(x_offset, y_offset + 32, elided_doc)

        painter.restore()

    def sizeHint(self, option, index):
        """Return size hint for items"""
        return QSize(option.rect.width(), 45)


class AutocompleteWidget(QListWidget):
    """Autocomplete popup widget"""

    completion_selected = pyqtSignal(str)  # Emits the selected completion text

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up appearance
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)

        # Set custom delegate
        self.setItemDelegate(CompletionItemDelegate(self))

        # Set font
        font = QFont("Consolas", 10)
        self.setFont(font)

        # Set size
        self.setMaximumHeight(300)
        self.setMinimumWidth(400)

        # Style
        self.setStyleSheet("""
            QListWidget {
                background-color: #F3F3F3;
                border: 1px solid #CCCCCC;
                outline: none;
            }
            QListWidget::item {
                padding: 2px;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #0078D4;
                color: white;
            }
        """)

        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)

    def show_completions(self, completions, position):
        """Show autocomplete suggestions

        Args:
            completions: List of completion dictionaries with 'name', 'signature', 'doc', 'kind'
            position: QPoint position to show the widget
        """
        self.clear()

        if not completions:
            self.hide()
            return

        # Add items
        for completion in completions:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, completion)
            item.setText(completion.get('name', ''))
            self.addItem(item)

        # Select first item
        if self.count() > 0:
            self.setCurrentRow(0)

        # Position and show
        self.move(position)
        self.show()
        self.setFocus()

    def on_item_clicked(self, item):
        """Handle item click"""
        data = item.data(Qt.UserRole)
        if data:
            self.completion_selected.emit(data.get('name', ''))
        self.hide()

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter or event.key() == Qt.Key_Tab:
            # Accept current selection
            current_item = self.currentItem()
            if current_item:
                data = current_item.data(Qt.UserRole)
                if data:
                    self.completion_selected.emit(data.get('name', ''))
            self.hide()
        elif event.key() == Qt.Key_Escape:
            # Cancel
            self.hide()
        elif event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
            # Navigate
            super().keyPressEvent(event)
        else:
            # Pass to parent editor
            self.hide()
            if self.parent():
                self.parent().keyPressEvent(event)

    def focusOutEvent(self, event):
        """Hide when focus is lost"""
        self.hide()
        super().focusOutEvent(event)
