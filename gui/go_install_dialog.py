"""
Go installation dialog
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont
from core.go_installer import GoInstaller, GoInstallerThread


class GoInstallDialog(QDialog):
    """Modal dialog for Go installation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.installer = GoInstaller()
        self.installer_thread = None
        self.go_path = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Go Installation Required")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Go Programming Language Not Detected")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "VizcachaIDE requires Go to be installed to compile and run Go programs.\n\n"
            "You can install Go locally (recommended) or install it system-wide manually."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Installation info
        info_label = QLabel(
            "<b>Local Installation:</b><br>"
            "• Go will be installed in the IDE directory<br>"
            "• No system PATH modification needed<br>"
            "• Works immediately after installation<br>"
            "• Approximately 150MB download"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        self.status_text.setVisible(False)
        layout.addWidget(self.status_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.install_button = QPushButton("Install Go Locally")
        self.install_button.clicked.connect(self.start_installation)
        button_layout.addWidget(self.install_button)
        
        self.manual_button = QPushButton("I'll Install Manually")
        self.manual_button.clicked.connect(self.open_manual_instructions)
        button_layout.addWidget(self.manual_button)
        
        self.close_button = QPushButton("Close IDE")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def start_installation(self):
        """Start Go installation"""
        self.install_button.setEnabled(False)
        self.manual_button.setEnabled(False)
        self.close_button.setText("Cancel")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_text.setVisible(True)
        self.status_text.append("Starting installation...\n")
        
        # Create and start installer thread
        self.installer_thread = GoInstallerThread(self.installer)
        self.installer_thread.progress_updated.connect(self.update_progress)
        self.installer_thread.installation_finished.connect(self.installation_finished)
        self.installer_thread.start()
        
    def update_progress(self, percent, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(percent)
        self.status_text.append(message)
        
    def installation_finished(self, success, message):
        """Handle installation completion"""
        if success:
            self.status_text.append(f"\n✓ Success: {message}")
            self.go_path = message
            
            # Save Go path to settings
            settings = QSettings()
            settings.setValue("env/go_path", self.go_path)
            settings.setValue("env/go_local", True)
            
            QMessageBox.information(self, "Installation Complete",
                "Go has been installed successfully!\n\n"
                "VizcachaIDE is now ready to compile and run Go programs.")
            
            self.accept()
        else:
            self.status_text.append(f"\n✗ Error: {message}")
            QMessageBox.critical(self, "Installation Failed",
                f"Failed to install Go:\n{message}\n\n"
                "Please try manual installation or check your internet connection.")
            
            self.install_button.setEnabled(True)
            self.manual_button.setEnabled(True)
            self.close_button.setText("Close IDE")
    
    def open_manual_instructions(self):
        """Show manual installation instructions"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Manual Go Installation")
        msg.setIcon(QMessageBox.Information)
        msg.setText("To install Go manually:")
        msg.setInformativeText(
            "<b>Windows:</b><br>"
            "1. Visit <a href='https://go.dev/dl/'>https://go.dev/dl/</a><br>"
            "2. Download the Windows installer (.msi)<br>"
            "3. Run the installer and follow instructions<br>"
            "4. Restart VizcachaIDE<br><br>"
            
            "<b>macOS:</b><br>"
            "1. Visit <a href='https://go.dev/dl/'>https://go.dev/dl/</a><br>"
            "2. Download the macOS installer (.pkg)<br>"
            "3. Run the installer<br>"
            "4. Restart VizcachaIDE<br><br>"
            
            "<b>Linux:</b><br>"
            "Run: <code>sudo apt install golang-go</code><br>"
            "Or download from <a href='https://go.dev/dl/'>https://go.dev/dl/</a><br>"
            "Then restart VizcachaIDE"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        # Ask if user wants to close and install manually
        reply = QMessageBox.question(self, "Close IDE?",
            "Do you want to close VizcachaIDE to install Go manually?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.reject()
