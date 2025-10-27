"""
Code editor widget with Go syntax highlighting and breakpoint support
"""

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import (QColor, QPainter, QTextFormat, QFont, QSyntaxHighlighter,
                         QTextCharFormat, QPalette, QKeySequence, QTextCursor)
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

    def __init__(self, parent=None, theme_colors=None):
        super().__init__(parent)
        self.theme_colors = theme_colors or {}
        self.highlighting_rules = []
        self.setup_formats()

    def setup_formats(self):
        self.highlighting_rules = []
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme_colors.get('keyword', "#0000FF")))
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

        type_format = QTextCharFormat()
        type_format.setForeground(QColor(self.theme_colors.get('type', "#008080")))
        type_format.setFontWeight(QFont.Bold)

        types = [
            'bool', 'byte', 'complex64', 'complex128', 'error', 'float32', 'float64',
            'int', 'int8', 'int16', 'int32', 'int64', 'rune', 'string',
            'uint', 'uint8', 'uint16', 'uint32', 'uint64', 'uintptr'
        ]

        for word in types:
            pattern = f'\\b{word}\\b'
            self.highlighting_rules.append((re.compile(pattern), type_format))

        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor(self.theme_colors.get('function', "#800080")))

        builtins = [
            'append', 'cap', 'close', 'complex', 'copy', 'delete', 'imag', 'len',
            'make', 'new', 'panic', 'print', 'println', 'real', 'recover'
        ]

        for word in builtins:
            pattern = f'\\b{word}\\b'
            self.highlighting_rules.append((re.compile(pattern), builtin_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme_colors.get('string', "#008000")))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r'`[^`]*`'), string_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme_colors.get('number', "#FF6600")))
        self.highlighting_rules.append((re.compile(r'\b\d+\.?\d*\b'), number_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme_colors.get('comment', "#808080")))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'//[^\n]*'), comment_format))

        self.multi_line_comment_format = comment_format
        self.comment_start = re.compile(r'/\*')
        self.comment_end = re.compile(r'\*/')
    
    def update_colors(self, theme_colors):
        self.theme_colors = theme_colors
        self.setup_formats()
        self.rehighlight()

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

        font = QFont("Consolas", 11)
        font.setWeight(QFont.Medium)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
            font.setWeight(QFont.Medium)
        self.setFont(font)

        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        self.line_number_area = LineNumberArea(self)

        self.breakpoints = set()

        self.current_line = None

        self.highlighter = GoSyntaxHighlighter(self.document())

        self.autocomplete_widget = None
        self.analyzer = None

        self.file_path = None

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

        self.update_line_number_area_width(0)

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
        painter = QPainter(self.line_number_area)
        
        bg_color = self.palette().color(QPalette.Base)
        if bg_color.lightness() < 128:
            painter.fillRect(event.rect(), bg_color.lighter(110))
        else:
            painter.fillRect(event.rect(), QColor("#F0F0F0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                line_num = block_number + 1

                if line_num in self.breakpoints:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor("#FF0000"))
                    painter.drawEllipse(3, top + 2, 12, 12)

                if line_num == self.current_line:
                    painter.fillRect(0, top, self.line_number_area.width(),
                                   self.fontMetrics().height(), QColor("#FFFF00"))

                text_color = self.palette().color(QPalette.Text)
                if text_color.lightness() < 128:
                    painter.setPen(QColor("#FFFFFF").darker(150))
                else:
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
    
    def move_line_up(self):
        """Move current line or selection up"""
        cursor = self.textCursor()
        
        # Single line handling
        block_num = cursor.blockNumber()
        
        # Can't move up if on first line
        if block_num == 0:
            return
        
        # Remember cursor position within line
        cursor_pos_in_line = cursor.positionInBlock()
        
        # Get current and previous line text
        current_block = cursor.block()
        current_text = current_block.text()
        prev_block = current_block.previous()
        prev_text = prev_block.text()
        
        # Store the start position of previous block
        prev_start = prev_block.position()
        
        # Begin edit block for undo
        cursor.beginEditBlock()
        
        # Select both lines (previous and current)
        cursor.setPosition(prev_start)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)  # newline
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)  # current line
        
        # Replace with swapped lines
        cursor.insertText(current_text + '\n' + prev_text)
        
        cursor.endEditBlock()
        
        # Now set cursor position on the moved line
        # The moved line is now at prev_start position
        new_cursor = self.textCursor()
        new_cursor.setPosition(prev_start + min(cursor_pos_in_line, len(current_text)))
        self.setTextCursor(new_cursor)
    
    def move_line_down(self):
        """Move current line or selection down"""
        cursor = self.textCursor()
        
        # Single line handling
        block_num = cursor.blockNumber()
        total_blocks = self.document().blockCount()
        
        # Can't move down if on last line
        if block_num >= total_blocks - 1:
            return
        
        # Remember cursor position within line
        cursor_pos_in_line = cursor.positionInBlock()
        
        # Get current and next line text
        current_block = cursor.block()
        current_text = current_block.text()
        next_block = current_block.next()
        next_text = next_block.text()
        
        # Store the start position of current block
        current_start = current_block.position()
        
        # Begin edit block for undo
        cursor.beginEditBlock()
        
        # Select both lines (current and next)
        cursor.setPosition(current_start)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)  # newline
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)  # next line
        
        # Replace with swapped lines
        cursor.insertText(next_text + '\n' + current_text)
        
        cursor.endEditBlock()
        
        # Now set cursor position on the moved line
        # The moved line is now at current_start + len(next_text) + 1
        new_cursor = self.textCursor()
        new_cursor.setPosition(current_start + len(next_text) + 1 + min(cursor_pos_in_line, len(current_text)))
        self.setTextCursor(new_cursor)

    def show_autocomplete(self):
        """Show autocomplete suggestions"""
        # Lazy initialization - only create when first needed
        if self.autocomplete_widget is None:
            from gui.autocomplete import AutocompleteWidget
            self.autocomplete_widget = AutocompleteWidget(self)
            self.autocomplete_widget.completion_selected.connect(self.insert_completion)
        
        if self.analyzer is None:
            from core.go_analyzer import GoAnalyzer
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
            text: Text to insert (can be simple text or snippet)
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

        # Check if this is a snippet
        snippet_text = None
        if self.analyzer and hasattr(self.analyzer, 'snippets'):
            for snippet_key, snippet_data in self.analyzer.snippets.items():
                if snippet_data['name'] == text:
                    snippet_text = snippet_data['snippet']
                    break
        
        if snippet_text:
            # Insert snippet with proper indentation
            current_line = cursor.block().text()
            indent = len(current_line) - len(current_line.lstrip())
            
            # Split snippet by lines and add indentation
            lines = snippet_text.split('\n')
            formatted_lines = []
            for i, line in enumerate(lines):
                if i == 0:
                    formatted_lines.append(line)
                else:
                    # Add base indentation + line's relative indentation
                    line_indent = len(line) - len(line.lstrip('\t'))
                    formatted_lines.append(' ' * indent + ' ' * (line_indent * 4) + line.lstrip('\t'))
            
            final_text = '\n'.join(formatted_lines)
            cursor.insertText(final_text)
            
            # Try to position cursor at the empty line inside the block
            # Find the position of \n\t\n pattern (empty line in block)
            if '\n\t\n' in snippet_text or (len(lines) > 1 and lines[1].strip() == ''):
                # Move cursor up one line and to end of line
                cursor.movePosition(cursor.Up)
                cursor.movePosition(cursor.EndOfLine)
                self.setTextCursor(cursor)
            return

        # Regular completion insertion
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
        # Handle Alt+Up/Down for moving lines
        if event.modifiers() == Qt.AltModifier:
            if event.key() == Qt.Key_Up:
                self.move_line_up()
                return
            elif event.key() == Qt.Key_Down:
                self.move_line_down()
                return
        
        # Check for Ctrl+S or other important shortcuts - let them pass through
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_S:
                # Let Ctrl+S pass through to parent handlers
                super().keyPressEvent(event)
                return
            elif event.key() == Qt.Key_Space:
                # Ctrl+Space triggers autocomplete
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
            elif event.text() in ('(', ')', '[', ']', '{', '}', ';', ',', ' '):
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
            
            # Calculate current indentation
            indent = len(block_text) - len(block_text.lstrip())
            
            # Check the actual cursor position in the line
            cursor_pos_in_block = cursor.positionInBlock()
            text_before_cursor = block_text[:cursor_pos_in_block]
            text_after_cursor = block_text[cursor_pos_in_block:]
            
            # Check if cursor is between braces {}
            between_braces = text_before_cursor.rstrip().endswith('{') and text_after_cursor.lstrip().startswith('}')
            
            # Check if line ends with opening brace
            stripped_text = block_text.rstrip()
            needs_extra_indent = False
            
            # Only check for keywords if we're at the end of the line and it ends with {
            if stripped_text.endswith('{') and not between_braces:
                needs_extra_indent = True
            
            # Insert new line
            super().keyPressEvent(event)
            
            # Add base indentation
            if indent > 0:
                self.textCursor().insertText(' ' * indent)
            
            # Add extra indentation if needed
            if needs_extra_indent:
                self.textCursor().insertText('    ')  # 4 spaces
            elif between_braces:
                # Special case: cursor between braces
                # Add indented line and closing brace line
                self.textCursor().insertText('    ')  # 4 spaces for content
                cursor_after_indent = self.textCursor()
                cursor_after_indent.insertText('\n' + ' ' * indent)
                self.setTextCursor(cursor_after_indent)
                # Move cursor back to indented position
                cursor_after_indent.movePosition(QTextCursor.Up)
                cursor_after_indent.movePosition(QTextCursor.EndOfLine)
                self.setTextCursor(cursor_after_indent)
        else:
            super().keyPressEvent(event)
            
            # Trigger autocomplete check for regular typing
            if event.text() and (event.text().isalnum() or event.text() in ('_', '.')):
                self._trigger_autocomplete_check()
    
    def _trigger_autocomplete_check(self):
        """Check if we should trigger autocomplete based on current context"""
        cursor = self.textCursor()
        position = cursor.position()
        code = self.toPlainText()
        
        if position == 0:
            return
            
        prev_char = code[position - 1] if position > 0 else ''
        
        # Always show after dot
        if prev_char == '.':
            self.show_autocomplete()
            return
        
        # Find word being typed
        word_start = position
        while word_start > 0 and (code[word_start - 1].isalnum() or code[word_start - 1] == '_'):
            word_start -= 1
        
        word_length = position - word_start
        
        # Show after 2+ chars if after dot, or 3+ chars otherwise
        if word_length >= 2:
            if word_start > 0 and code[word_start - 1] == '.':
                self.show_autocomplete()
            elif word_length >= 3:
                self.show_autocomplete()
    
    def update_autocomplete_filter(self):
        if not self.autocomplete_widget or not self.autocomplete_widget.isVisible():
            return

        cursor = self.textCursor()
        position = cursor.position()
        code = self.toPlainText()

        word_start = position
        while word_start > 0 and (code[word_start - 1].isalnum() or code[word_start - 1] == '_'):
            word_start -= 1

        if word_start > 0 and code[word_start - 1] == '.':
            partial_word = code[word_start:position]
            if not self.autocomplete_widget.filter_completions(partial_word):
                pass
        else:
            if word_start < position:
                partial_word = code[word_start:position]
                if not self.autocomplete_widget.filter_completions(partial_word):
                    self.autocomplete_widget.hide()
            else:
                self.autocomplete_widget.hide()
