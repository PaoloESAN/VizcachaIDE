#!/usr/bin/env python3
"""
VizcachaIDE - A beginner-friendly Go IDE similar to Thonny
Main entry point for the application
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
from gui.main_window import MainWindow
from gui.go_install_dialog import GoInstallDialog
from core.go_installer import GoInstaller


def check_go_installation():
    """Check if Go is installed and show installation dialog if needed
    
    Returns:
        bool: True if Go is available, False if user cancelled
    """
    installer = GoInstaller()
    is_installed, go_path, version = installer.detect_go()
    
    if is_installed:
        # Save Go path to settings
        settings = QSettings()
        settings.setValue("env/go_path", go_path)
        if go_path == installer.get_local_go_path():
            settings.setValue("env/go_local", True)
        print(f"Go detected: {version}")
        return True
    
    # Go not found, show installation dialog
    dialog = GoInstallDialog()
    result = dialog.exec_()
    
    if result == GoInstallDialog.Accepted:
        # Go was installed successfully
        return True
    else:
        # User cancelled or closed dialog
        return False


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VizcachaIDE")
    app.setOrganizationName("VizcachaIDE")

    # Check Go installation before showing main window
    if not check_go_installation():
        print("Go installation required. Exiting...")
        sys.exit(0)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
