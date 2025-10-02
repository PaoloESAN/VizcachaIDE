"""
Tabbed editor widget for managing multiple open files
"""

from PyQt5.QtWidgets import QTabWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal
from gui.editor import CodeEditor


class TabbedEditor(QTabWidget):
    """Tabbed widget containing multiple code editors"""

    # Signal emitted when the active file changes
    active_file_changed = pyqtSignal(str)  # file_path or empty string

    def __init__(self, parent=None):
        super().__init__(parent)

        # Enable tab closing
        self.setTabsClosable(True)
        self.setMovable(True)

        # Connect signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.on_tab_changed)

        # Create initial untitled tab
        self.new_tab()

    def new_tab(self, file_path=None, content=""):
        """Create a new tab with a code editor

        Args:
            file_path: Path to the file (None for untitled)
            content: Initial content for the editor

        Returns:
            The created CodeEditor instance
        """
        editor = CodeEditor()
        editor.setPlainText(content)

        # Set file path as property
        editor.file_path = file_path

        # Generate tab title
        if file_path:
            import os
            tab_title = os.path.basename(file_path)
        else:
            # Count untitled tabs
            untitled_count = sum(1 for i in range(self.count())
                               if self.tabText(i).startswith("Untitled"))
            tab_title = f"Untitled {untitled_count + 1}" if untitled_count > 0 else "Untitled"

        # Add tab
        index = self.addTab(editor, tab_title)
        self.setCurrentIndex(index)

        # Connect document modified signal to update tab title
        editor.document().modificationChanged.connect(
            lambda modified: self.update_tab_title(editor, modified)
        )

        return editor

    def close_tab(self, index):
        """Close a tab at the given index

        Args:
            index: Index of the tab to close
        """
        if self.count() <= 1:
            # Don't close the last tab, just clear it
            editor = self.widget(0)
            if self.check_save_needed(editor):
                editor.clear()
                editor.file_path = None
                self.setTabText(0, "Untitled")
            return

        editor = self.widget(index)

        if self.check_save_needed(editor):
            self.removeTab(index)

    def check_save_needed(self, editor):
        """Check if the editor has unsaved changes

        Args:
            editor: CodeEditor instance to check

        Returns:
            True if it's safe to proceed, False if user cancelled
        """
        if editor.document().isModified():
            file_name = editor.file_path if editor.file_path else "Untitled"
            import os
            if editor.file_path:
                file_name = os.path.basename(file_name)

            reply = QMessageBox.question(
                self, "Unsaved Changes",
                f"Do you want to save changes to '{file_name}'?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                return self.save_current_tab()
            elif reply == QMessageBox.Cancel:
                return False

        return True

    def save_current_tab(self):
        """Save the current tab

        Returns:
            True if saved successfully, False otherwise
        """
        editor = self.current_editor()
        if not editor:
            return False

        if editor.file_path:
            return self.save_to_file(editor, editor.file_path)
        else:
            return self.save_current_tab_as()

    def save_current_tab_as(self):
        """Save the current tab with a new file name

        Returns:
            True if saved successfully, False otherwise
        """
        from PyQt5.QtWidgets import QFileDialog

        editor = self.current_editor()
        if not editor:
            return False

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Go File", "", "Go Files (*.go);;All Files (*)"
        )

        if filename:
            if not filename.endswith('.go'):
                filename += '.go'
            return self.save_to_file(editor, filename)

        return False

    def save_to_file(self, editor, filename):
        """Save editor content to a file

        Args:
            editor: CodeEditor instance
            filename: Path to save to

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())

            editor.file_path = filename
            editor.document().setModified(False)

            # Update tab title
            import os
            index = self.indexOf(editor)
            self.setTabText(index, os.path.basename(filename))

            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False

    def update_tab_title(self, editor, modified):
        """Update tab title to show modified state

        Args:
            editor: CodeEditor instance
            modified: Whether the document is modified
        """
        index = self.indexOf(editor)
        if index >= 0:
            current_title = self.tabText(index)

            # Remove existing asterisk if present
            if current_title.endswith('*'):
                current_title = current_title[:-1]

            # Add asterisk if modified
            if modified:
                self.setTabText(index, current_title + '*')
            else:
                self.setTabText(index, current_title)

    def current_editor(self):
        """Get the current active editor

        Returns:
            CodeEditor instance or None
        """
        return self.currentWidget()

    def current_file_path(self):
        """Get the file path of the current editor

        Returns:
            File path string or None
        """
        editor = self.current_editor()
        return editor.file_path if editor else None

    def open_file(self, file_path):
        """Open a file in a new tab or switch to it if already open

        Args:
            file_path: Path to the file to open

        Returns:
            True if successful, False otherwise
        """
        # Check if file is already open
        for i in range(self.count()):
            editor = self.widget(i)
            if editor.file_path == file_path:
                self.setCurrentIndex(i)
                return True

        # Open in new tab
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.new_tab(file_path, content)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
            return False

    def on_tab_changed(self, index):
        """Handle tab change event

        Args:
            index: New tab index
        """
        if index >= 0:
            editor = self.widget(index)
            if editor and editor.file_path:
                self.active_file_changed.emit(editor.file_path)
            else:
                self.active_file_changed.emit("")

    def close_all_tabs(self):
        """Close all tabs (used when closing the application)

        Returns:
            True if all tabs closed successfully, False if user cancelled
        """
        while self.count() > 0:
            if not self.close_tab(0):
                return False
        return True

    def get_all_breakpoints(self):
        """Get breakpoints from the current editor

        Returns:
            List of breakpoint line numbers
        """
        editor = self.current_editor()
        return editor.get_breakpoints() if editor else []

    def highlight_current_line(self, line_number):
        """Highlight a line in the current editor

        Args:
            line_number: Line number to highlight
        """
        editor = self.current_editor()
        if editor:
            editor.highlight_current_line(line_number)

    def clear_current_line_highlight(self):
        """Clear current line highlight in the current editor"""
        editor = self.current_editor()
        if editor:
            editor.clear_current_line_highlight()

    def toggle_breakpoint(self):
        """Toggle breakpoint in the current editor"""
        editor = self.current_editor()
        if editor:
            editor.toggle_breakpoint()
