"""
Main window for VizcachaIDE application
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QAction, QFileDialog, QMessageBox, QToolBar, QActionGroup)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence, QIcon, QFont, QColor

from gui.tabbed_editor import TabbedEditor
from gui.console import ConsoleWidget
from gui.variables import VariablesWidget
from gui.callstack import CallStackWidget
from gui.themes import ThemeManager
from core.runner import GoRunner
from core.debugger import GoDebugger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        
        self.theme_manager = ThemeManager()

        self.runner = GoRunner()
        self.debugger = GoDebugger()

        self.init_ui()
        self.connect_signals()
        self.restore_state()
        self.apply_theme()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("VizcachaIDE - Beginner-friendly Go IDE")
        self.setGeometry(100, 100, 1200, 800)

        # Set window icon
        import os
        import sys

        # Get the base path (different for bundled and development)
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # Running in development
            base_path = os.path.dirname(os.path.dirname(__file__))

        icon_path = os.path.join(base_path, "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

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
        
        edit_menu.addSeparator()
        
        preferences_action = QAction("&Preferences...", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self.show_settings)
        edit_menu.addAction(preferences_action)

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

        self.build_action = QAction("&Build", self)
        self.build_action.setShortcut("Ctrl+B")
        self.build_action.triggered.connect(self.build_code)
        run_menu.addAction(self.build_action)

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

        # View menu
        view_menu = menubar.addMenu("&View")
        
        theme_menu = view_menu.addMenu("&Theme")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        
        for theme_name in self.theme_manager.get_theme_names():
            theme_action = QAction(theme_name, self)
            theme_action.setCheckable(True)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.change_theme(name))
            theme_group.addAction(theme_action)
            theme_menu.addAction(theme_action)
            
            if theme_name == self.settings.value("appearance/theme", "Dark"):
                theme_action.setChecked(True)
        
        view_menu.addSeparator()
        
        self.toggle_toolbar_action = QAction("Show &Toolbar", self)
        self.toggle_toolbar_action.setCheckable(True)
        self.toggle_toolbar_action.setChecked(True)
        self.toggle_toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(self.toggle_toolbar_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        terminal_action = QAction("Open &Terminal", self)
        terminal_action.setShortcut("Ctrl+`")
        terminal_action.triggered.connect(self.open_terminal)
        tools_menu.addAction(terminal_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

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

        # Build button
        self.build_btn_action = QAction("🔨 Build", self)
        self.build_btn_action.triggered.connect(self.build_code)
        toolbar.addAction(self.build_btn_action)

        toolbar.addSeparator()

        # Terminal button
        self.terminal_btn_action = QAction("⚡ Terminal", self)
        self.terminal_btn_action.triggered.connect(self.open_terminal)
        self.terminal_btn_action.setToolTip("Open terminal in current file directory")
        toolbar.addAction(self.terminal_btn_action)

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

        # Save the file before running
        if not self.save_file():
            # If save failed or was cancelled, don't run
            return

        self.console.clear()
        self.run_action.setEnabled(False)
        self.run_btn_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.stop_btn_action.setEnabled(True)

        # Mark console as waiting for input
        self.console.set_waiting_for_input(True)

        self.runner.run(current_file)

    def build_code(self):
        """Build the current Go code"""
        current_file = self.editor.current_file_path()
        if not current_file:
            QMessageBox.warning(self, "No File", "Please save your file before building.")
            return

        # Save the file before building
        if not self.save_file():
            # If save failed or was cancelled, don't build
            return

        self.console.clear()
        self.console.append_output(f"Building: {current_file}\n")
        self.console.append_output("-" * 50 + "\n")

        import os
        import subprocess

        # Get Go executable path
        go_path = self.settings.value("env/go_path", "go")
        if not go_path:
            go_path = "go"

        # Get output executable name
        base_name = os.path.splitext(os.path.basename(current_file))[0]
        output_name = base_name + ".exe" if os.name == 'nt' else base_name

        # Get environment variables
        env = self._get_go_environment()

        try:
            # Build the Go file
            result = subprocess.run(
                [go_path, "build", "-o", output_name, os.path.basename(current_file)],
                cwd=os.path.dirname(current_file),
                capture_output=True,
                text=True,
                env=env
            )

            if result.returncode == 0:
                self.console.append_success(f"\n[Build successful: {output_name}]\n")
            else:
                self.console.append_error(result.stderr)
                self.console.append_error(f"\n[Build failed with code {result.returncode}]\n")

        except Exception as e:
            self.console.append_error(f"\nError: {str(e)}\n")
    
    def _get_go_environment(self):
        """Get environment variables for Go execution
        
        Returns:
            dict: Environment variables with Go paths
        """
        import os
        
        # Check if using local Go installation
        is_local = self.settings.value("env/go_local", False, type=bool)
        
        if is_local:
            # Use local Go installation environment
            from core.go_installer import GoInstaller
            installer = GoInstaller()
            return installer.get_go_env()
        else:
            # Return system environment
            return os.environ.copy()

    def stop_execution(self):
        """Stop the current execution"""
        self.runner.stop()
        self.debugger.stop()

    def on_execution_finished(self, exit_code):
        """Handle execution finished"""
        self.console.set_waiting_for_input(False)
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

    # Debug operations
    def start_debug(self):
        """Start debugging session"""
        current_file = self.editor.current_file_path()
        if not current_file:
            QMessageBox.warning(self, "No File", "Please save your file before debugging.")
            return

        # Save the file before debugging
        if not self.save_file():
            # If save failed or was cancelled, don't debug
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

    def change_theme(self, theme_name):
        self.settings.setValue("appearance/theme", theme_name)
        self.apply_theme()
    
    def apply_theme(self):
        theme_name = self.settings.value("appearance/theme", "Dark")
        
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        stylesheet = self.theme_manager.apply_theme(app, theme_name)
        app.setStyleSheet(stylesheet)
        
        theme = self.theme_manager.current_theme
        
        for i in range(self.editor.count()):
            editor_widget = self.editor.widget(i)
            if editor_widget:
                self.apply_editor_theme(editor_widget, theme)
        
        if hasattr(self, 'console'):
            self.apply_console_theme(theme)
    
    def apply_editor_theme(self, editor, theme):
        from PyQt5.QtGui import QPalette
        palette = editor.palette()
        palette.setColor(QPalette.Base, QColor(theme.editor['background']))
        palette.setColor(QPalette.Text, QColor(theme.editor['text']))
        editor.setPalette(palette)
        
        current_font = editor.font()
        current_font.setWeight(QFont.Medium)
        editor.setFont(current_font)
        
        if hasattr(editor, 'highlighter'):
            editor.highlighter.update_colors(theme.editor)
    
    def apply_console_theme(self, theme):
        from PyQt5.QtGui import QPalette
        palette = self.console.palette()
        palette.setColor(QPalette.Base, QColor(theme.console['background']))
        palette.setColor(QPalette.Text, QColor(theme.console['text']))
        self.console.setPalette(palette)
    
    def toggle_toolbar(self):
        show = self.toggle_toolbar_action.isChecked()
        for toolbar in self.findChildren(QToolBar):
            toolbar.setVisible(show)
        self.settings.setValue("appearance/show_toolbar", show)

    def apply_current_settings(self):
        font_family = self.settings.value("editor/font_family", "Consolas")
        font_size = int(self.settings.value("editor/font_size", 11))

        for i in range(self.editor.count()):
            editor_widget = self.editor.widget(i)
            if editor_widget:
                font = QFont(font_family, font_size)
                font.setWeight(QFont.Medium)
                editor_widget.setFont(font)

        word_wrap = self.settings.value("editor/word_wrap", False, type=bool)
        for i in range(self.editor.count()):
            editor_widget = self.editor.widget(i)
            if editor_widget:
                from PyQt5.QtWidgets import QPlainTextEdit
                if word_wrap:
                    editor_widget.setLineWrapMode(QPlainTextEdit.WidgetWidth)
                else:
                    editor_widget.setLineWrapMode(QPlainTextEdit.NoWrap)

        show_toolbar = self.settings.value("appearance/show_toolbar", True, type=bool)
        self.toggle_toolbar_action.setChecked(show_toolbar)
        for toolbar in self.findChildren(QToolBar):
            toolbar.setVisible(show_toolbar)
        
        self.apply_theme()

    def open_terminal(self):
        """Open integrated terminal in current file directory with Go environment"""
        import os
        import subprocess
        import platform

        # Get current file path
        current_file = self.editor.current_file_path()
        
        if current_file:
            # Get directory of current file
            work_dir = os.path.dirname(current_file)
        else:
            # Use workspace directory or home directory
            work_dir = os.path.expanduser("~")

        # Get Go environment variables
        env = self._get_go_environment()

        # Detect OS and open appropriate terminal
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows: Create a batch file to set environment and open terminal
                batch_file = os.path.join(work_dir, "_vizcacha_terminal.bat")
                with open(batch_file, 'w') as f:
                    f.write('@echo off\n')
                    # Set environment variables
                    if 'GOROOT' in env:
                        f.write(f'set GOROOT={env["GOROOT"]}\n')
                    if 'GOPATH' in env:
                        f.write(f'set GOPATH={env["GOPATH"]}\n')
                    if 'PATH' in env:
                        f.write(f'set PATH={env["PATH"]}\n')
                    f.write(f'cd /d "{work_dir}"\n')
                    f.write('echo VizcachaIDE Terminal - Go environment ready\n')
                    f.write('echo.\n')
                    f.write('go version\n')
                    f.write('echo.\n')
                    f.write('cmd /K\n')
                
                # Open CMD with batch file
                subprocess.Popen(['cmd', '/C', 'start', 'cmd', '/K', batch_file],
                               cwd=work_dir,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
                
            elif system == "Darwin":  # macOS
                # macOS: Create a script and open Terminal
                script_file = os.path.join(work_dir, ".vizcacha_terminal.sh")
                with open(script_file, 'w') as f:
                    f.write('#!/bin/bash\n')
                    if 'GOROOT' in env:
                        f.write(f'export GOROOT="{env["GOROOT"]}"\n')
                    if 'GOPATH' in env:
                        f.write(f'export GOPATH="{env["GOPATH"]}"\n')
                    if 'PATH' in env:
                        f.write(f'export PATH="{env["PATH"]}"\n')
                    f.write(f'cd "{work_dir}"\n')
                    f.write('echo "VizcachaIDE Terminal - Go environment ready"\n')
                    f.write('go version\n')
                    f.write('bash\n')
                
                os.chmod(script_file, 0o755)
                
                script = f'tell application "Terminal" to do script "{script_file}"'
                subprocess.Popen(['osascript', '-e', script])
                
            else:  # Linux
                # Linux: Create a script and open terminal
                script_file = os.path.join(work_dir, ".vizcacha_terminal.sh")
                with open(script_file, 'w') as f:
                    f.write('#!/bin/bash\n')
                    if 'GOROOT' in env:
                        f.write(f'export GOROOT="{env["GOROOT"]}"\n')
                    if 'GOPATH' in env:
                        f.write(f'export GOPATH="{env["GOPATH"]}"\n')
                    if 'PATH' in env:
                        f.write(f'export PATH="{env["PATH"]}"\n')
                    f.write(f'cd "{work_dir}"\n')
                    f.write('echo "VizcachaIDE Terminal - Go environment ready"\n')
                    f.write('go version\n')
                    f.write('bash\n')
                
                os.chmod(script_file, 0o755)
                
                terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'xterm']
                for terminal in terminals:
                    try:
                        if terminal == 'gnome-terminal':
                            subprocess.Popen([terminal, '--', 'bash', '-c', f'bash {script_file}'])
                        elif terminal == 'konsole':
                            subprocess.Popen([terminal, '-e', 'bash', script_file])
                        else:
                            subprocess.Popen([terminal, '-e', f'bash {script_file}'])
                        break
                    except FileNotFoundError:
                        continue
            
            self.console.append_success(f"\n[Terminal opened in: {work_dir}]\n")
            self.console.append_success("[Go environment configured automatically]\n")
        except Exception as e:
            QMessageBox.warning(self, "Terminal Error", 
                              f"Failed to open terminal:\n{str(e)}\n\nPlease open terminal manually.")

    def show_about(self):
        """Show About dialog"""
        import os
        import sys
        from PyQt5.QtGui import QPixmap

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About VizcachaIDE")

        # Set logo icon
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(__file__))

        logo_path = os.path.join(base_path, "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            msg_box.setIconPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        msg_box.setText(
            "<h3>VizcachaIDE</h3>"
            "<p>Beginner-friendly Go IDE</p>"
        )
        msg_box.setInformativeText(
            "<p><b>Author:</b> Marks Calderon<br>"
            "<b>Contact:</b> hola@codeplai.pe<br>"
            "CEO of Codeplai Games<br>"
            "Peru</p>"
            "<p><b>License:</b> MIT License<br>"
            "Copyright (c) 2025 Marks Calderon - Codeplai Games</p>"
        )
        msg_box.exec_()

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
