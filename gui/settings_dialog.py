"""
Settings/Configuration dialog for GoIDE
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
                             QSpinBox, QGroupBox, QFormLayout, QFileDialog,
                             QColorDialog, QFontDialog, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QColor


class SettingsDialog(QDialog):
    """Settings dialog for configuring GoIDE"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("GoIDE - Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Main layout
        layout = QVBoxLayout(self)

        # Tab widget
        tab_widget = QTabWidget()

        # Add tabs
        tab_widget.addTab(self.create_environment_tab(), "Environment")
        tab_widget.addTab(self.create_editor_tab(), "Editor")
        tab_widget.addTab(self.create_appearance_tab(), "Appearance")

        layout.addWidget(tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)

        layout.addLayout(button_layout)

    def create_environment_tab(self):
        """Create environment settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Go Configuration Group
        go_group = QGroupBox("Go Configuration")
        go_layout = QFormLayout()

        # Go executable path
        go_path_layout = QHBoxLayout()
        self.go_path_edit = QLineEdit()
        self.go_path_edit.setPlaceholderText("Path to go executable (e.g., /usr/bin/go)")
        go_path_layout.addWidget(self.go_path_edit)

        browse_go_button = QPushButton("Browse...")
        browse_go_button.clicked.connect(self.browse_go_path)
        go_path_layout.addWidget(browse_go_button)

        go_layout.addRow("Go Path:", go_path_layout)

        # GOPATH
        gopath_layout = QHBoxLayout()
        self.gopath_edit = QLineEdit()
        self.gopath_edit.setPlaceholderText("GOPATH (leave empty for default)")
        gopath_layout.addWidget(self.gopath_edit)

        browse_gopath_button = QPushButton("Browse...")
        browse_gopath_button.clicked.connect(self.browse_gopath)
        gopath_layout.addWidget(browse_gopath_button)

        go_layout.addRow("GOPATH:", gopath_layout)

        # GOROOT
        goroot_layout = QHBoxLayout()
        self.goroot_edit = QLineEdit()
        self.goroot_edit.setPlaceholderText("GOROOT (leave empty for default)")
        goroot_layout.addWidget(self.goroot_edit)

        browse_goroot_button = QPushButton("Browse...")
        browse_goroot_button.clicked.connect(self.browse_goroot)
        goroot_layout.addWidget(browse_goroot_button)

        go_layout.addRow("GOROOT:", goroot_layout)

        go_group.setLayout(go_layout)
        layout.addWidget(go_group)

        # Delve Configuration Group
        delve_group = QGroupBox("Delve Debugger Configuration")
        delve_layout = QFormLayout()

        # Delve executable path
        delve_path_layout = QHBoxLayout()
        self.delve_path_edit = QLineEdit()
        self.delve_path_edit.setPlaceholderText("Path to dlv executable (leave empty for PATH)")
        delve_path_layout.addWidget(self.delve_path_edit)

        browse_delve_button = QPushButton("Browse...")
        browse_delve_button.clicked.connect(self.browse_delve_path)
        delve_path_layout.addWidget(browse_delve_button)

        delve_layout.addRow("Delve Path:", delve_path_layout)

        delve_group.setLayout(delve_layout)
        layout.addWidget(delve_group)

        # Environment Variables Group
        env_group = QGroupBox("Additional Environment Variables")
        env_layout = QVBoxLayout()

        env_info = QLabel("Set additional environment variables (one per line, format: NAME=VALUE)")
        env_info.setWordWrap(True)
        env_layout.addWidget(env_info)

        from PyQt5.QtWidgets import QTextEdit
        self.env_vars_edit = QTextEdit()
        self.env_vars_edit.setMaximumHeight(100)
        self.env_vars_edit.setPlaceholderText("GOOS=linux\nGOARCH=amd64")
        env_layout.addWidget(self.env_vars_edit)

        env_group.setLayout(env_layout)
        layout.addWidget(env_group)

        layout.addStretch()
        return widget

    def create_editor_tab(self):
        """Create editor settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Font Group
        font_group = QGroupBox("Editor Font")
        font_layout = QFormLayout()

        # Font family
        self.font_family_combo = QComboBox()
        monospace_fonts = ["Consolas", "Courier New", "Monaco", "Menlo",
                          "DejaVu Sans Mono", "Liberation Mono", "Source Code Pro"]
        self.font_family_combo.addItems(monospace_fonts)
        font_layout.addRow("Font Family:", self.font_family_combo)

        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(11)
        font_layout.addRow("Font Size:", self.font_size_spin)

        # Preview
        self.font_preview_label = QLabel("Sample Text: func main() { fmt.Println(\"Hello\") }")
        self.font_preview_label.setStyleSheet("padding: 10px; background-color: #F0F0F0;")
        font_layout.addRow("Preview:", self.font_preview_label)

        # Update preview on change
        self.font_family_combo.currentTextChanged.connect(self.update_font_preview)
        self.font_size_spin.valueChanged.connect(self.update_font_preview)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        # Editor Behavior Group
        behavior_group = QGroupBox("Editor Behavior")
        behavior_layout = QFormLayout()

        # Tab size
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(2, 8)
        self.tab_size_spin.setValue(4)
        behavior_layout.addRow("Tab Size:", self.tab_size_spin)

        # Auto-indent
        self.auto_indent_check = QCheckBox("Enable auto-indentation")
        self.auto_indent_check.setChecked(True)
        behavior_layout.addRow("", self.auto_indent_check)

        # Show line numbers
        self.show_line_numbers_check = QCheckBox("Show line numbers")
        self.show_line_numbers_check.setChecked(True)
        behavior_layout.addRow("", self.show_line_numbers_check)

        # Word wrap
        self.word_wrap_check = QCheckBox("Enable word wrap")
        self.word_wrap_check.setChecked(False)
        behavior_layout.addRow("", self.word_wrap_check)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        layout.addStretch()
        return widget

    def create_appearance_tab(self):
        """Create appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Theme Group
        theme_group = QGroupBox("Color Theme")
        theme_layout = QFormLayout()

        # Editor theme
        self.editor_theme_combo = QComboBox()
        self.editor_theme_combo.addItems(["Light", "Dark", "Solarized Light", "Solarized Dark"])
        theme_layout.addRow("Editor Theme:", self.editor_theme_combo)

        # Console theme
        self.console_theme_combo = QComboBox()
        self.console_theme_combo.addItems(["Dark", "Light"])
        theme_layout.addRow("Console Theme:", self.console_theme_combo)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Colors Group
        colors_group = QGroupBox("Custom Colors")
        colors_layout = QFormLayout()

        # Background color
        bg_color_layout = QHBoxLayout()
        self.bg_color_button = QPushButton("Choose Color")
        self.bg_color_button.clicked.connect(lambda: self.choose_color('background'))
        bg_color_layout.addWidget(self.bg_color_button)
        self.bg_color_preview = QLabel("      ")
        self.bg_color_preview.setStyleSheet("background-color: #FFFFFF; border: 1px solid #000;")
        bg_color_layout.addWidget(self.bg_color_preview)
        bg_color_layout.addStretch()
        colors_layout.addRow("Background:", bg_color_layout)

        # Text color
        text_color_layout = QHBoxLayout()
        self.text_color_button = QPushButton("Choose Color")
        self.text_color_button.clicked.connect(lambda: self.choose_color('text'))
        text_color_layout.addWidget(self.text_color_button)
        self.text_color_preview = QLabel("      ")
        self.text_color_preview.setStyleSheet("background-color: #000000; border: 1px solid #000;")
        text_color_layout.addWidget(self.text_color_preview)
        text_color_layout.addStretch()
        colors_layout.addRow("Text:", text_color_layout)

        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)

        # UI Elements Group
        ui_group = QGroupBox("UI Elements")
        ui_layout = QFormLayout()

        # Show toolbar
        self.show_toolbar_check = QCheckBox("Show toolbar")
        self.show_toolbar_check.setChecked(True)
        ui_layout.addRow("", self.show_toolbar_check)

        # Show status bar
        self.show_status_bar_check = QCheckBox("Show status bar")
        self.show_status_bar_check.setChecked(False)
        ui_layout.addRow("", self.show_status_bar_check)

        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)

        layout.addStretch()
        return widget

    def browse_go_path(self):
        """Browse for Go executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Go Executable", "", "Executable Files (*)"
        )
        if file_path:
            self.go_path_edit.setText(file_path)

    def browse_gopath(self):
        """Browse for GOPATH directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select GOPATH Directory")
        if dir_path:
            self.gopath_edit.setText(dir_path)

    def browse_goroot(self):
        """Browse for GOROOT directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select GOROOT Directory")
        if dir_path:
            self.goroot_edit.setText(dir_path)

    def browse_delve_path(self):
        """Browse for Delve executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Delve Executable", "", "Executable Files (*)"
        )
        if file_path:
            self.delve_path_edit.setText(file_path)

    def update_font_preview(self):
        """Update font preview label"""
        font_family = self.font_family_combo.currentText()
        font_size = self.font_size_spin.value()
        font = QFont(font_family, font_size)
        self.font_preview_label.setFont(font)

    def choose_color(self, color_type):
        """Choose a color using color picker"""
        color = QColorDialog.getColor()
        if color.isValid():
            if color_type == 'background':
                self.bg_color_preview.setStyleSheet(
                    f"background-color: {color.name()}; border: 1px solid #000;"
                )
                self.settings.setValue("editor/background_color", color.name())
            elif color_type == 'text':
                self.text_color_preview.setStyleSheet(
                    f"background-color: {color.name()}; border: 1px solid #000;"
                )
                self.settings.setValue("editor/text_color", color.name())

    def load_settings(self):
        """Load settings from QSettings"""
        # Environment
        self.go_path_edit.setText(self.settings.value("env/go_path", ""))
        self.gopath_edit.setText(self.settings.value("env/gopath", ""))
        self.goroot_edit.setText(self.settings.value("env/goroot", ""))
        self.delve_path_edit.setText(self.settings.value("env/delve_path", ""))
        self.env_vars_edit.setPlainText(self.settings.value("env/extra_vars", ""))

        # Editor
        self.font_family_combo.setCurrentText(self.settings.value("editor/font_family", "Consolas"))
        self.font_size_spin.setValue(int(self.settings.value("editor/font_size", 11)))
        self.tab_size_spin.setValue(int(self.settings.value("editor/tab_size", 4)))
        self.auto_indent_check.setChecked(self.settings.value("editor/auto_indent", True, type=bool))
        self.show_line_numbers_check.setChecked(self.settings.value("editor/show_line_numbers", True, type=bool))
        self.word_wrap_check.setChecked(self.settings.value("editor/word_wrap", False, type=bool))

        # Appearance
        self.editor_theme_combo.setCurrentText(self.settings.value("appearance/editor_theme", "Light"))
        self.console_theme_combo.setCurrentText(self.settings.value("appearance/console_theme", "Dark"))
        self.show_toolbar_check.setChecked(self.settings.value("appearance/show_toolbar", True, type=bool))
        self.show_status_bar_check.setChecked(self.settings.value("appearance/show_status_bar", False, type=bool))

        # Colors
        bg_color = self.settings.value("editor/background_color", "#FFFFFF")
        self.bg_color_preview.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #000;")

        text_color = self.settings.value("editor/text_color", "#000000")
        self.text_color_preview.setStyleSheet(f"background-color: {text_color}; border: 1px solid #000;")

        # Update font preview
        self.update_font_preview()

    def apply_settings(self):
        """Apply and save settings"""
        # Environment
        self.settings.setValue("env/go_path", self.go_path_edit.text())
        self.settings.setValue("env/gopath", self.gopath_edit.text())
        self.settings.setValue("env/goroot", self.goroot_edit.text())
        self.settings.setValue("env/delve_path", self.delve_path_edit.text())
        self.settings.setValue("env/extra_vars", self.env_vars_edit.toPlainText())

        # Editor
        self.settings.setValue("editor/font_family", self.font_family_combo.currentText())
        self.settings.setValue("editor/font_size", self.font_size_spin.value())
        self.settings.setValue("editor/tab_size", self.tab_size_spin.value())
        self.settings.setValue("editor/auto_indent", self.auto_indent_check.isChecked())
        self.settings.setValue("editor/show_line_numbers", self.show_line_numbers_check.isChecked())
        self.settings.setValue("editor/word_wrap", self.word_wrap_check.isChecked())

        # Appearance
        self.settings.setValue("appearance/editor_theme", self.editor_theme_combo.currentText())
        self.settings.setValue("appearance/console_theme", self.console_theme_combo.currentText())
        self.settings.setValue("appearance/show_toolbar", self.show_toolbar_check.isChecked())
        self.settings.setValue("appearance/show_status_bar", self.show_status_bar_check.isChecked())

        QMessageBox.information(self, "Settings Saved",
                               "Settings have been saved. Some changes may require restarting the IDE.")

    def accept(self):
        """Save settings and close"""
        self.apply_settings()
        super().accept()

    def get_settings_dict(self):
        """Get all settings as a dictionary"""
        return {
            'env': {
                'go_path': self.go_path_edit.text(),
                'gopath': self.gopath_edit.text(),
                'goroot': self.goroot_edit.text(),
                'delve_path': self.delve_path_edit.text(),
                'extra_vars': self.env_vars_edit.toPlainText(),
            },
            'editor': {
                'font_family': self.font_family_combo.currentText(),
                'font_size': self.font_size_spin.value(),
                'tab_size': self.tab_size_spin.value(),
                'auto_indent': self.auto_indent_check.isChecked(),
                'show_line_numbers': self.show_line_numbers_check.isChecked(),
                'word_wrap': self.word_wrap_check.isChecked(),
            },
            'appearance': {
                'editor_theme': self.editor_theme_combo.currentText(),
                'console_theme': self.console_theme_combo.currentText(),
                'show_toolbar': self.show_toolbar_check.isChecked(),
                'show_status_bar': self.show_status_bar_check.isChecked(),
            }
        }
