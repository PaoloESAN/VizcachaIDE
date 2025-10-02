"""
Main window for VizcachaIDE application
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QAction, QFileDialog, QMessageBox, QToolBar)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence, QIcon, QFont

from gui.tabbed_editor import TabbedEditor
from gui.console import ConsoleWidget
from gui.variables import VariablesWidget
from gui.callstack import CallStackWidget
from core.runner import GoRunner
from core.debugger import GoDebugger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings()

        # Initialize components
        self.runner = GoRunner()
        self.debugger = GoDebugger()

        self.init_ui()
        self.connect_signals()
        self.restore_state()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("VizcachaIDE - Beginner-friendly Go IDE")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Initialize widgets first (before menu/toolbar that reference them)
        # Left panel: Tabbed Editor
        self.editor = TabbedEditor()

        # Right panel: Variables and Call Stack
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.variables_widget = VariablesWidget()
        self.callstack_widget = CallStackWidget()

        right_layout.addWidget(self.variables_widget, 2)
        right_layout.addWidget(self.callstack_widget, 1)

        # Console widget
        self.console = ConsoleWidget()

        # Now create toolbar and menu bar (they reference self.editor)
        self.create_toolbar()
        self.create_menu_bar()

        # Main splitter (horizontal)
        main_splitter = QSplitter(Qt.Horizontal)

        # Add to main splitter
        main_splitter.addWidget(self.editor)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([800, 400])

        # Vertical splitter for editor and console
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.addWidget(main_splitter)
        vertical_splitter.addWidget(self.console)
        vertical_splitter.setSizes([600, 200])

        main_layout.addWidget(vertical_splitter)

    def create_menu_bar(self):
        """Create menu bar with File, Edit, Run, Debug menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(lambda: self.editor.current_editor() and self.editor.current_editor().undo())
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(lambda: self.editor.current_editor() and self.editor.current_editor().redo())
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(lambda: self.editor.current_editor() and self.editor.current_editor().cut())
        edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(lambda: self.editor.current_editor() and self.editor.current_editor().copy())
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(lambda: self.editor.current_editor() and self.editor.current_editor().paste())
        edit_menu.addAction(paste_action)

        # Run menu
        run_menu = menubar.addMenu("&Run")

        self.run_action = QAction("&Run", self)
        self.run_action.setShortcut("F5")
        self.run_action.triggered.connect(self.run_code)
        run_menu.addAction(self.run_action)

        self.stop_action = QAction("&Stop", self)
        self.stop_action.setShortcut("Shift+F5")
        self.stop_action.triggered.connect(self.stop_execution)
        self.stop_action.setEnabled(False)
        run_menu.addAction(self.stop_action)

        run_menu.addSeparator()

        configure_action = QAction("&Configure...", self)
        configure_action.triggered.connect(self.show_settings)
        run_menu.addAction(configure_action)

        # Debug menu
        debug_menu = menubar.addMenu("&Debug")

        self.debug_action = QAction("Start &Debugging", self)
        self.debug_action.setShortcut("F6")
        self.debug_action.triggered.connect(self.start_debug)
        debug_menu.addAction(self.debug_action)

        self.step_over_action = QAction("Step &Over", self)
        self.step_over_action.setShortcut("F7")
        self.step_over_action.triggered.connect(self.step_over)
        self.step_over_action.setEnabled(False)
        debug_menu.addAction(self.step_over_action)

        self.step_into_action = QAction("Step &Into", self)
        self.step_into_action.setShortcut("F8")
        self.step_into_action.triggered.connect(self.step_into)
        self.step_into_action.setEnabled(False)
        debug_menu.addAction(self.step_into_action)

        self.step_out_action = QAction("Step O&ut", self)
        self.step_out_action.setShortcut("F9")
        self.step_out_action.triggered.connect(self.step_out)
        self.step_out_action.setEnabled(False)
        debug_menu.addAction(self.step_out_action)

        debug_menu.addSeparator()

        self.toggle_breakpoint_action = QAction("Toggle &Breakpoint", self)
        self.toggle_breakpoint_action.setShortcut("F10")
        self.toggle_breakpoint_action.triggered.connect(self.toggle_breakpoint)
        debug_menu.addAction(self.toggle_breakpoint_action)

    def create_toolbar(self):
        """Create toolbar with common actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Run button
        self.run_btn_action = QAction("▶ Run", self)
        self.run_btn_action.triggered.connect(self.run_code)
        toolbar.addAction(self.run_btn_action)

        # Stop button
        self.stop_btn_action = QAction("⬛ Stop", self)
        self.stop_btn_action.triggered.connect(self.stop_execution)
        self.stop_btn_action.setEnabled(False)
        toolbar.addAction(self.stop_btn_action)

        toolbar.addSeparator()

        # Debug button
        self.debug_btn_action = QAction("🐛 Debug", self)
        self.debug_btn_action.triggered.connect(self.start_debug)
        toolbar.addAction(self.debug_btn_action)

        # Step Over
        self.step_over_btn = QAction("↷ Step Over", self)
        self.step_over_btn.triggered.connect(self.step_over)
        self.step_over_btn.setEnabled(False)
        toolbar.addAction(self.step_over_btn)

        # Step Into
        self.step_into_btn = QAction("↓ Step Into", self)
        self.step_into_btn.triggered.connect(self.step_into)
        self.step_into_btn.setEnabled(False)
        toolbar.addAction(self.step_into_btn)

        # Step Out
        self.step_out_btn = QAction("↑ Step Out", self)
        self.step_out_btn.triggered.connect(self.step_out)
        self.step_out_btn.setEnabled(False)
        toolbar.addAction(self.step_out_btn)

    def connect_signals(self):
        """Connect signals and slots"""
        self.runner.output_received.connect(self.console.append_output)
        self.runner.error_received.connect(self.console.append_error)
        self.runner.execution_finished.connect(self.on_execution_finished)

        self.debugger.output_received.connect(self.console.append_output)
        self.debugger.error_received.connect(self.console.append_error)
        self.debugger.variables_updated.connect(self.variables_widget.update_variables)
        self.debugger.callstack_updated.connect(self.callstack_widget.update_callstack)
        self.debugger.current_line_changed.connect(self.editor.highlight_current_line)
        self.debugger.debug_finished.connect(self.on_debug_finished)

        # Connect console input to runner
        self.console.input_submitted.connect(self.on_console_input)

        # Connect tabbed editor signals
        self.editor.active_file_changed.connect(self.on_active_file_changed)

    def on_active_file_changed(self, file_path):
        """Handle active file change in tabbed editor"""
        self.update_window_title()

    # File operations
    def new_file(self):
        """Create a new file in a new tab"""
        self.editor.new_tab()
        self.update_window_title()

    def open_file(self):
        """Open an existing file in a new tab"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Go File", "", "Go Files (*.go);;All Files (*)"
        )

        if filename:
            if self.editor.open_file(filename):
                self.settings.setValue("last_file", filename)
                self.update_window_title()

    def save_file(self):
        """Save the current tab"""
        return self.editor.save_current_tab()

    def save_file_as(self):
        """Save the current tab with a new name"""
        return self.editor.save_current_tab_as()

    def update_window_title(self):
        """Update window title with current file name"""
        current_file = self.editor.current_file_path()
        if current_file:
            import os
            self.setWindowTitle(f"VizcachaIDE - {os.path.basename(current_file)}")
        else:
            self.setWindowTitle("VizcachaIDE - Untitled")

    # Execution operations
    def run_code(self):
        """Run the current Go code"""
        current_file = self.editor.current_file_path()
        if not current_file:
            QMessageBox.warning(self, "No File", "Please save your file before running.")
            return

        self.console.clear()
        self.run_action.setEnabled(False)
        self.run_btn_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.stop_btn_action.setEnabled(True)

        self.runner.run(current_file)
        # Enable input after a short delay to allow process to start
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(200, self.console.enable_input)

    def stop_execution(self):
        """Stop the current execution"""
        self.runner.stop()
        self.debugger.stop()

    def on_execution_finished(self, exit_code):
        """Handle execution finished"""
        self.console.disable_input()
        self.run_action.setEnabled(True)
        self.run_btn_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.stop_btn_action.setEnabled(False)

        if exit_code == 0:
            self.console.append_output("\n[Process finished successfully]")
        else:
            self.console.append_error(f"\n[Process exited with code {exit_code}]")

    def on_console_input(self, text):
        """Handle input submitted from console"""
        self.runner.write_input(text)
        # Check if process is still running before re-enabling input
        # Wait longer to allow program output to appear first
        from PyQt5.QtCore import QTimer, QProcess
        if self.runner.process and self.runner.process.state() == QProcess.Running:
            QTimer.singleShot(150, self.console.enable_input)

    # Debug operations
    def start_debug(self):
        """Start debugging session"""
        current_file = self.editor.current_file_path()
        if not current_file:
            QMessageBox.warning(self, "No File", "Please save your file before debugging.")
            return

        self.console.clear()
        self.variables_widget.clear()
        self.callstack_widget.clear()

        self.debug_action.setEnabled(False)
        self.debug_btn_action.setEnabled(False)
        self.step_over_action.setEnabled(True)
        self.step_into_action.setEnabled(True)
        self.step_out_action.setEnabled(True)
        self.step_over_btn.setEnabled(True)
        self.step_into_btn.setEnabled(True)
        self.step_out_btn.setEnabled(True)
        self.stop_action.setEnabled(True)
        self.stop_btn_action.setEnabled(True)

        breakpoints = self.editor.get_all_breakpoints()
        self.debugger.start(current_file, breakpoints)

    def step_over(self):
        """Step over current line"""
        self.debugger.step_over()

    def step_into(self):
        """Step into function"""
        self.debugger.step_into()

    def step_out(self):
        """Step out of current function"""
        self.debugger.step_out()

    def toggle_breakpoint(self):
        """Toggle breakpoint at current line"""
        self.editor.toggle_breakpoint()

    def on_debug_finished(self):
        """Handle debug session finished"""
        self.debug_action.setEnabled(True)
        self.debug_btn_action.setEnabled(True)
        self.step_over_action.setEnabled(False)
        self.step_into_action.setEnabled(False)
        self.step_out_action.setEnabled(False)
        self.step_over_btn.setEnabled(False)
        self.step_into_btn.setEnabled(False)
        self.step_out_btn.setEnabled(False)
        self.stop_action.setEnabled(False)
        self.stop_btn_action.setEnabled(False)

        self.editor.clear_current_line_highlight()

    def show_settings(self):
        """Show settings/configuration dialog"""
        from gui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(self)
        if dialog.exec_() == SettingsDialog.Accepted:
            # Settings were saved, optionally apply some immediately
            self.apply_current_settings()

    def apply_current_settings(self):
        """Apply current settings to the IDE"""
        # Apply font settings to all open editors
        font_family = self.settings.value("editor/font_family", "Consolas")
        font_size = int(self.settings.value("editor/font_size", 11))

        for i in range(self.editor.count()):
            editor_widget = self.editor.widget(i)
            if editor_widget:
                font = QFont(font_family, font_size)
                editor_widget.setFont(font)

        # Apply word wrap
        word_wrap = self.settings.value("editor/word_wrap", False, type=bool)
        for i in range(self.editor.count()):
            editor_widget = self.editor.widget(i)
            if editor_widget:
                from PyQt5.QtWidgets import QPlainTextEdit
                if word_wrap:
                    editor_widget.setLineWrapMode(QPlainTextEdit.WidgetWidth)
                else:
                    editor_widget.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Show/hide toolbar
        show_toolbar = self.settings.value("appearance/show_toolbar", True, type=bool)
        if hasattr(self, 'toolbar'):
            for toolbar in self.findChildren(QToolBar):
                toolbar.setVisible(show_toolbar)

    def restore_state(self):
        """Restore window state from settings"""
        last_file = self.settings.value("last_file", "")
        if last_file:
            self.editor.open_file(last_file)

        # Apply settings on startup
        self.apply_current_settings()

    def closeEvent(self, event):
        """Handle window close event"""
        # Check all tabs for unsaved changes
        for i in range(self.editor.count()):
            tab_editor = self.editor.widget(i)
            if not self.editor.check_save_needed(tab_editor):
                event.ignore()
                return
        event.accept()
