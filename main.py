#!/usr/bin/env python3
"""
VizcachaIDE - A beginner-friendly Go IDE similar to Thonny
Main entry point for the application
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VizcachaIDE")
    app.setOrganizationName("VizcachaIDE")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
