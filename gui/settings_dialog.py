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

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("Aplicar")
        self.apply_button.clicked.connect(self.apply_settings_only)
        button_layout.addWidget(self.apply_button)

        self.ok_button = QPushButton("Aceptar")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

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
        self.font_preview_label.setStyleSheet("padding: 10px; border: 1px solid palette(mid);")
        self.font_preview_label.setAutoFillBackground(True)
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
        widget = QWidget()
        layout = QVBoxLayout(widget)

        theme_group = QGroupBox("Tema de la aplicación")
        theme_layout = QFormLayout()

        self.app_theme_combo = QComboBox()
        self.app_theme_combo.addItems(["Dark", "Light", "Monokai", "Halloween"])
        theme_layout.addRow("Tema:", self.app_theme_combo)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        ui_group = QGroupBox("Elementos UI")
        ui_layout = QFormLayout()

        self.show_toolbar_check = QCheckBox("Mostrar barra de herramientas")
        self.show_toolbar_check.setChecked(True)
        ui_layout.addRow("", self.show_toolbar_check)

        self.show_status_bar_check = QCheckBox("Mostrar barra de estado")
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
        font_family = self.font_family_combo.currentText()
        font_size = self.font_size_spin.value()
        font = QFont(font_family, font_size)
        self.font_preview_label.setFont(font)

    def load_settings(self):
        self.go_path_edit.setText(self.settings.value("env/go_path", ""))
        self.gopath_edit.setText(self.settings.value("env/gopath", ""))
        self.goroot_edit.setText(self.settings.value("env/goroot", ""))
        self.delve_path_edit.setText(self.settings.value("env/delve_path", ""))
        self.env_vars_edit.setPlainText(self.settings.value("env/extra_vars", ""))

        self.font_family_combo.setCurrentText(self.settings.value("editor/font_family", "Consolas"))
        self.font_size_spin.setValue(int(self.settings.value("editor/font_size", 11)))
        self.tab_size_spin.setValue(int(self.settings.value("editor/tab_size", 4)))
        self.auto_indent_check.setChecked(self.settings.value("editor/auto_indent", True, type=bool))
        self.show_line_numbers_check.setChecked(self.settings.value("editor/show_line_numbers", True, type=bool))
        self.word_wrap_check.setChecked(self.settings.value("editor/word_wrap", False, type=bool))

        self.app_theme_combo.setCurrentText(self.settings.value("appearance/theme", "Dark"))
        self.show_toolbar_check.setChecked(self.settings.value("appearance/show_toolbar", True, type=bool))
        self.show_status_bar_check.setChecked(self.settings.value("appearance/show_status_bar", False, type=bool))

        self.update_font_preview()

    def apply_settings_only(self):
        self.settings.setValue("env/go_path", self.go_path_edit.text())
        self.settings.setValue("env/gopath", self.gopath_edit.text())
        self.settings.setValue("env/goroot", self.goroot_edit.text())
        self.settings.setValue("env/delve_path", self.delve_path_edit.text())
        self.settings.setValue("env/extra_vars", self.env_vars_edit.toPlainText())

        self.settings.setValue("editor/font_family", self.font_family_combo.currentText())
        self.settings.setValue("editor/font_size", self.font_size_spin.value())
        self.settings.setValue("editor/tab_size", self.tab_size_spin.value())
        self.settings.setValue("editor/auto_indent", self.auto_indent_check.isChecked())
        self.settings.setValue("editor/show_line_numbers", self.show_line_numbers_check.isChecked())
        self.settings.setValue("editor/word_wrap", self.word_wrap_check.isChecked())

        self.settings.setValue("appearance/theme", self.app_theme_combo.currentText())
        self.settings.setValue("appearance/show_toolbar", self.show_toolbar_check.isChecked())
        self.settings.setValue("appearance/show_status_bar", self.show_status_bar_check.isChecked())

        QMessageBox.information(self, "Configuración aplicada",
                               "La configuración se aplicó correctamente. Cierra y reabre el diálogo para ver los cambios.")
        
        if self.parent():
            self.parent().apply_current_settings()

    def apply_settings(self):
        self.apply_settings_only()

    def accept(self):
        self.apply_settings_only()
        super().accept()

    def get_settings_dict(self):
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
                'theme': self.app_theme_combo.currentText(),
                'show_toolbar': self.show_toolbar_check.isChecked(),
                'show_status_bar': self.show_status_bar_check.isChecked(),
            }
        }
