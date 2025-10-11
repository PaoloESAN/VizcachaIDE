"""
Code editor widget with Go syntax highlighting and breakpoint support
"""

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import (QColor, QPainter, QTextFormat, QFont, QSyntaxHighlighter,
                         QTextCharFormat, QPalette, QKeySequence)
import re


class LineNumberArea(QWidget):
    """Widget for displaying line numbers and breakpoints"""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

    def mousePressEvent(self, event):
        """Handle mouse clicks for breakpoint toggling"""
        if event.button() == Qt.LeftButton:
            # Calculate which line was clicked
            block_number = self.editor.firstVisibleBlock().blockNumber()
            top = int(self.editor.blockBoundingGeometry(
                self.editor.firstVisibleBlock()).translated(self.editor.contentOffset()).top())
            bottom = top + int(self.editor.blockBoundingRect(self.editor.firstVisibleBlock()).height())

            while block_number <= self.editor.document().blockCount():
                block = self.editor.document().findBlockByNumber(block_number)
                if not block.isValid():
                    break

                if top <= event.pos().y() < bottom:
                    self.editor.toggle_breakpoint_at_line(block_number + 1)
                    break

                top = bottom
                bottom = top + int(self.editor.blockBoundingRect(block).height())
                block_number += 1


class GoSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Go language"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            'break', 'case', 'chan', 'const', 'continue', 'default', 'defer',
            'else', 'fallthrough', 'for', 'func', 'go', 'goto', 'if', 'import',
            'interface', 'map', 'package', 'range', 'return', 'select', 'struct',
            'switch', 'type', 'var'
        ]

        for word in keywords:
            pattern = f'\\b{word}\\b'
            self.highlighting_rules.append((re.compile(pattern), keyword_format))

        # Built-in types
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#008080"))
        type_format.setFontWeight(QFont.Bold)

        types = [
            'bool', 'byte', 'complex64', 'complex128', 'error', 'float32', 'float64',
            'int', 'int8', 'int16', 'int32', 'int64', 'rune', 'string',
            'uint', 'uint8', 'uint16', 'uint32', 'uint64', 'uintptr'
        ]

        for word in types:
            pattern = f'\\b{word}\\b'
            self.highlighting_rules.append((re.compile(pattern), type_format))

        # Built-in functions
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#800080"))

        builtins = [
            'append', 'cap', 'close', 'complex', 'copy', 'delete', 'imag', 'len',
            'make', 'new', 'panic', 'print', 'println', 'real', 'recover'
        ]

        for word in builtins:
            pattern = f'\\b{word}\\b'
            self.highlighting_rules.append((re.compile(pattern), builtin_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r'`[^`]*`'), string_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF6600"))
        self.highlighting_rules.append((re.compile(r'\b\d+\.?\d*\b'), number_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'//[^\n]*'), comment_format))

        # Multi-line comment patterns
        self.multi_line_comment_format = comment_format
        self.comment_start = re.compile(r'/\*')
        self.comment_end = re.compile(r'\*/')

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Apply single-line rules
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)

        # Handle multi-line comments
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start.search(text)
            start_index = match.start() if match else -1

        while start_index >= 0:
            match = self.comment_end.search(text, start_index)
            if match:
                end_index = match.end()
                length = end_index - start_index
                self.setFormat(start_index, length, self.multi_line_comment_format)
                match = self.comment_start.search(text, end_index)
                start_index = match.start() if match else -1
            else:
                self.setCurrentBlockState(1)
                length = len(text) - start_index
                self.setFormat(start_index, length, self.multi_line_comment_format)
                break


class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers, syntax highlighting, and breakpoint support"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set font
        font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        self.setFont(font)

        # Tab settings
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        # Line number area
        self.line_number_area = LineNumberArea(self)

        # Breakpoints (line number -> True)
        self.breakpoints = set()

        # Current execution line
        self.current_line = None

        # Syntax highlighter
        self.highlighter = GoSyntaxHighlighter(self.document())

        # Autocomplete widget (initialized lazily)
        self.autocomplete_widget = None
        self.analyzer = None

        # File path (set by TabbedEditor)
        self.file_path = None

        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

        self.update_line_number_area_width(0)

        # Set color scheme
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.Text, QColor("#000000"))
        self.setPalette(palette)

    def line_number_area_width(self):
        """Calculate width needed for line number area"""
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        """Update margins for line number area"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update line number area on scroll"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(),
                                        self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        """Paint line numbers and breakpoints"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#F0F0F0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                line_num = block_number + 1

                # Draw breakpoint indicator
                if line_num in self.breakpoints:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor("#FF0000"))
                    painter.drawEllipse(3, top + 2, 12, 12)

                # Highlight current execution line
                if line_num == self.current_line:
                    painter.fillRect(0, top, self.line_number_area.width(),
                                   self.fontMetrics().height(), QColor("#FFFF00"))

                # Draw line number
                painter.setPen(QColor("#808080"))
                painter.drawText(0, top, self.line_number_area.width() - 5,
                               self.fontMetrics().height(),
                               Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def toggle_breakpoint(self):
        """Toggle breakpoint at current cursor position"""
        cursor = self.textCursor()
        line_number = cursor.blockNumber() + 1
        self.toggle_breakpoint_at_line(line_number)

    def toggle_breakpoint_at_line(self, line_number):
        """Toggle breakpoint at specific line"""
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
        else:
            self.breakpoints.add(line_number)
        self.line_number_area.update()

    def get_breakpoints(self):
        """Return list of breakpoint line numbers"""
        return sorted(list(self.breakpoints))

    def highlight_current_line(self, line_number):
        """Highlight the current execution line"""
        self.current_line = line_number

        # Scroll to line
        block = self.document().findBlockByLineNumber(line_number - 1)
        cursor = self.textCursor()
        cursor.setPosition(block.position())
        self.setTextCursor(cursor)
        self.centerCursor()

        # Update line number area to show highlight
        self.line_number_area.update()

        # Highlight the line in the editor
        extra_selections = []
        selection = QTextEdit.ExtraSelection()
        line_color = QColor("#FFFF00").lighter(160)
        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        cursor = QTextCursor(block)
        cursor.clearSelection()
        selection.cursor = cursor
        extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def clear_current_line_highlight(self):
        """Clear the current line highlight"""
        self.current_line = None
        self.setExtraSelections([])
        self.line_number_area.update()

    def show_autocomplete(self):
        """Show autocomplete suggestions"""
        # Lazy initialization
        if self.autocomplete_widget is None:
            from gui.autocomplete import AutocompleteWidget
            from core.go_analyzer import GoAnalyzer

            self.autocomplete_widget = AutocompleteWidget(self)
            self.autocomplete_widget.completion_selected.connect(self.insert_completion)
            self.analyzer = GoAnalyzer()

        # Get current code and cursor position
        code = self.toPlainText()
        cursor = self.textCursor()
        cursor_position = cursor.position()

        # Get completions
        completions = self.analyzer.get_completions(code, cursor_position, self.file_path)

        if completions:
            # Calculate position for autocomplete widget
            cursor_rect = self.cursorRect()
            global_pos = self.mapToGlobal(cursor_rect.bottomLeft())

            # Show completions
            self.autocomplete_widget.show_completions(completions, global_pos)

    def insert_completion(self, text):
        """Insert selected completion text

        Args:
            text: Text to insert
        """
        cursor = self.textCursor()
        position = cursor.position()
        code = self.toPlainText()

        word_start = position
        while word_start > 0 and (code[word_start - 1].isalnum() or code[word_start - 1] == '_'):
            word_start -= 1

        has_dot_before = word_start > 0 and code[word_start - 1] == '.'

        partial_word = code[word_start:position]

        if partial_word:
            cursor.setPosition(word_start)
            cursor.setPosition(position, cursor.KeepAnchor)
            cursor.removeSelectedText()

        # Insert completion
        cursor.insertText(text)

        # Check what's after cursor
        new_position = cursor.position()
        updated_code = self.toPlainText()
        has_content_after = new_position < len(updated_code) and updated_code[new_position:new_position + 1] in '("\'['

        if not has_content_after and (has_dot_before or text in ['append', 'len', 'make', 'print', 'println']):
            cursor.insertText('()')
            cursor.setPosition(cursor.position() - 1)

        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        """Handle key press events for auto-indentation and autocomplete"""
        # Ctrl+Space triggers autocomplete
        if event.key() == Qt.Key_Space and event.modifiers() == Qt.ControlModifier:
            self.show_autocomplete()
            return

        # Auto-pair completion for brackets, quotes, etc.
        pairs = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'"
        }
        
        text = event.text()
        if text in pairs:
            cursor = self.textCursor()
            
            # Check if next char is closing pair (skip insertion)
            position = cursor.position()
            code = self.toPlainText()
            next_char = code[position] if position < len(code) else ''
            
            # Skip if typing closing char and it's already there
            if text in (')', ']', '}') and next_char == text:
                cursor.movePosition(cursor.Right)
                self.setTextCursor(cursor)
                return
            
            # Insert pair
            closing = pairs[text]
            cursor.insertText(text + closing)
            cursor.movePosition(cursor.Left)
            self.setTextCursor(cursor)
            return
        
        # Skip over closing bracket if it's already there
        if text in (')', ']', '}'):
            cursor = self.textCursor()
            position = cursor.position()
            code = self.toPlainText()
            next_char = code[position] if position < len(code) else ''
            
            if next_char == text:
                cursor.movePosition(cursor.Right)
                self.setTextCursor(cursor)
                return

        # Handle autocomplete if visible
        if self.autocomplete_widget and self.autocomplete_widget.isVisible():
            if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape, Qt.Key_Tab):
                self.autocomplete_widget.keyPressEvent(event)
                return
            elif event.key() == Qt.Key_Backspace:
                # Backspace: update text then filter
                super().keyPressEvent(event)
                self.update_autocomplete_filter()
                return
            elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key_End):
                # Close on cursor move
                self.autocomplete_widget.hide()
                super().keyPressEvent(event)
                return
            elif event.text() and (event.text().isalnum() or event.text() == '_'):
                # Typing: update and filter
                super().keyPressEvent(event)
                self.update_autocomplete_filter()
                return
            elif event.text() in ('(', ')', '[', ']', '{', '}', ';', ',', ' ', '.'):
                # Close on special chars
                self.autocomplete_widget.hide()
                super().keyPressEvent(event)
                return

        # Delete pair on backspace if between matching brackets
        if event.key() == Qt.Key_Backspace:
            cursor = self.textCursor()
            position = cursor.position()
            code = self.toPlainText()
            
            if position > 0 and position < len(code):
                prev_char = code[position - 1]
                next_char = code[position]
                
                # Check if between matching pair
                pairs = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}
                if prev_char in pairs and pairs[prev_char] == next_char:
                    # Delete both characters
                    cursor.movePosition(cursor.Left)
                    cursor.movePosition(cursor.Right, cursor.KeepAnchor, 2)
                    cursor.removeSelectedText()
                    return

        # Auto-indent on new line
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            block_text = cursor.block().text()
            indent = len(block_text) - len(block_text.lstrip())

            super().keyPressEvent(event)

            # Add same indentation to new line
            if indent > 0:
                self.textCursor().insertText(' ' * indent)

            # Extra indent after { or :
            if block_text.rstrip().endswith('{') or block_text.rstrip().endswith(':'):
                self.textCursor().insertText('    ')  # 4 spaces
        else:
            super().keyPressEvent(event)

    def update_autocomplete_filter(self):
        """Update autocomplete filter based on current word being typed"""
        if not self.autocomplete_widget or not self.autocomplete_widget.isVisible():
            return

        cursor = self.textCursor()
        position = cursor.position()
        code = self.toPlainText()

        # Find word start (after dot)
        word_start = position
        while word_start > 0 and (code[word_start - 1].isalnum() or code[word_start - 1] == '_'):
            word_start -= 1

        # Check for dot before word
        if word_start > 0 and code[word_start - 1] == '.':
            # Get partial word
            partial_word = code[word_start:position]
            
            # Filter completions
            if not self.autocomplete_widget.filter_completions(partial_word):
                pass
        else:
            # No dot, hide
            self.autocomplete_widget.hide()

