from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt


class Theme:
    def __init__(self, name):
        self.name = name
        self.colors = {}
        
    def apply_to_widget(self, widget):
        palette = widget.palette()
        for role, color in self.colors.items():
            if isinstance(color, dict):
                for group, group_color in color.items():
                    palette.setColor(getattr(QPalette, group), 
                                   getattr(QPalette, role), 
                                   QColor(group_color))
            else:
                palette.setColor(getattr(QPalette, role), QColor(color))
        widget.setPalette(palette)


class VSCodeDarkTheme(Theme):
    def __init__(self):
        super().__init__("Dark")
        self.colors = {
            'Window': '#1e1e1e',
            'WindowText': '#d4d4d4',
            'Base': '#1e1e1e',
            'AlternateBase': '#252526',
            'ToolTipBase': '#1e1e1e',
            'ToolTipText': '#cccccc',
            'Text': '#d4d4d4',
            'Button': '#2d2d30',
            'ButtonText': '#cccccc',
            'BrightText': '#ffffff',
            'Link': '#4e94ce',
            'Highlight': '#264f78',
            'HighlightedText': '#ffffff',
        }
        
        self.editor = {
            'background': '#1e1e1e',
            'text': '#d4d4d4',
            'line_number_bg': '#1e1e1e',
            'line_number_fg': '#858585',
            'current_line': '#2a2a2a',
            'selection': '#264f78',
            'comment': '#6a9955',
            'keyword': '#569cd6',
            'string': '#ce9178',
            'number': '#b5cea8',
            'function': '#dcdcaa',
            'type': '#4ec9b0',
            'operator': '#d4d4d4',
        }
        
        self.console = {
            'background': '#1e1e1e',
            'text': '#cccccc',
            'error': '#f48771',
            'success': '#4ec9b0',
            'input': '#569cd6',
        }
        
        self.panel = {
            'background': '#252526',
            'border': '#3e3e42',
            'header_bg': '#2d2d30',
            'header_fg': '#cccccc',
        }


class VSCodeLightTheme(Theme):
    def __init__(self):
        super().__init__("Light")
        self.colors = {
            'Window': '#f3f3f3',
            'WindowText': '#000000',
            'Base': '#ffffff',
            'AlternateBase': '#f3f3f3',
            'ToolTipBase': '#ffffff',
            'ToolTipText': '#000000',
            'Text': '#000000',
            'Button': '#f3f3f3',
            'ButtonText': '#000000',
            'BrightText': '#ffffff',
            'Link': '#0078d4',
            'Highlight': '#0078d4',
            'HighlightedText': '#ffffff',
        }
        
        self.editor = {
            'background': '#ffffff',
            'text': '#000000',
            'line_number_bg': '#f5f5f5',
            'line_number_fg': '#237893',
            'current_line': '#f5f5f5',
            'selection': '#add6ff',
            'comment': '#008000',
            'keyword': '#0000ff',
            'string': '#a31515',
            'number': '#098658',
            'function': '#795e26',
            'type': '#267f99',
            'operator': '#000000',
        }
        
        self.console = {
            'background': '#ffffff',
            'text': '#000000',
            'error': '#cd3131',
            'success': '#16825d',
            'input': '#0000ff',
        }
        
        self.panel = {
            'background': '#f3f3f3',
            'border': '#dddddd',
            'header_bg': '#e7e7e7',
            'header_fg': '#000000',
        }


class MonokaiTheme(Theme):
    def __init__(self):
        super().__init__("Monokai")
        self.colors = {
            'Window': '#272822',
            'WindowText': '#f8f8f2',
            'Base': '#272822',
            'AlternateBase': '#3e3d32',
            'ToolTipBase': '#272822',
            'ToolTipText': '#f8f8f2',
            'Text': '#f8f8f2',
            'Button': '#3e3d32',
            'ButtonText': '#f8f8f2',
            'BrightText': '#ffffff',
            'Link': '#66d9ef',
            'Highlight': '#49483e',
            'HighlightedText': '#f8f8f2',
        }
        
        self.editor = {
            'background': '#272822',
            'text': '#f8f8f2',
            'line_number_bg': '#272822',
            'line_number_fg': '#90908a',
            'current_line': '#3e3d32',
            'selection': '#49483e',
            'comment': '#75715e',
            'keyword': '#f92672',
            'string': '#e6db74',
            'number': '#ae81ff',
            'function': '#a6e22e',
            'type': '#66d9ef',
            'operator': '#f92672',
        }
        
        self.console = {
            'background': '#272822',
            'text': '#f8f8f2',
            'error': '#f92672',
            'success': '#a6e22e',
            'input': '#66d9ef',
        }
        
        self.panel = {
            'background': '#3e3d32',
            'border': '#75715e',
            'header_bg': '#3e3d32',
            'header_fg': '#f8f8f2',
        }


class HalloweenTheme(Theme):
    def __init__(self):
        super().__init__("Halloween")
        self.colors = {
            'Window': '#1a0f0f',
            'WindowText': '#ff9933',
            'Base': '#1a0f0f',
            'AlternateBase': '#2a1515',
            'ToolTipBase': '#1a0f0f',
            'ToolTipText': '#ff9933',
            'Text': '#ff9933',
            'Button': '#2a1515',
            'ButtonText': '#ff9933',
            'BrightText': '#ffcc66',
            'Link': '#cc66ff',
            'Highlight': '#663399',
            'HighlightedText': '#ffcc66',
        }
        
        self.editor = {
            'background': '#1a0f0f',
            'text': '#ff9933',
            'line_number_bg': '#1a0f0f',
            'line_number_fg': '#996633',
            'current_line': '#2a1515',
            'selection': '#663399',
            'comment': '#666666',
            'keyword': '#cc66ff',
            'string': '#ffcc66',
            'number': '#ff6666',
            'function': '#99cc00',
            'type': '#ff9933',
            'operator': '#cc66ff',
        }
        
        self.console = {
            'background': '#1a0f0f',
            'text': '#ff9933',
            'error': '#ff3333',
            'success': '#99cc00',
            'input': '#ffcc66',
        }
        
        self.panel = {
            'background': '#2a1515',
            'border': '#663333',
            'header_bg': '#2a1515',
            'header_fg': '#ff9933',
        }


class ThemeManager:
    def __init__(self):
        self.themes = {
            'Dark': VSCodeDarkTheme(),
            'Light': VSCodeLightTheme(),
            'Monokai': MonokaiTheme(),
            'Halloween': HalloweenTheme(),
        }
        self.current_theme = self.themes['Dark']
    
    def get_theme(self, name):
        return self.themes.get(name, self.current_theme)
    
    def set_theme(self, name):
        if name in self.themes:
            self.current_theme = self.themes[name]
            return True
        return False
    
    def get_theme_names(self):
        return list(self.themes.keys())
    
    def apply_theme(self, app, theme_name=None):
        if theme_name:
            self.set_theme(theme_name)
        
        theme = self.current_theme
        palette = QPalette()
        
        for role_name, color in theme.colors.items():
            role = getattr(QPalette, role_name)
            palette.setColor(role, QColor(color))
        
        app.setPalette(palette)
        
        return self.get_stylesheet()
    
    def get_stylesheet(self):
        theme = self.current_theme
        
        if theme.name == "Dark":
            return """
                * {
                    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                }
                QPlainTextEdit {
                    font-family: "Consolas", "Courier New", monospace;
                }
                QMainWindow {
                    background-color: #1e1e1e;
                }
                QMenuBar {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border-bottom: 1px solid #3e3e42;
                    font-size: 13px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #3e3e42;
                }
                QMenuBar::item:pressed {
                    background-color: #007acc;
                }
                QMenu {
                    background-color: #252526;
                    color: #cccccc;
                    border: 1px solid #3e3e42;
                    font-size: 13px;
                }
                QMenu::item:selected {
                    background-color: #2a2d2e;
                }
                QToolBar {
                    background-color: #2d2d30;
                    border-bottom: 1px solid #3e3e42;
                    spacing: 3px;
                    padding: 3px;
                }
                QToolButton {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border: none;
                    padding: 5px 10px;
                    margin: 2px;
                    border-radius: 3px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QToolButton:hover {
                    background-color: #3e3e42;
                }
                QToolButton:pressed {
                    background-color: #007acc;
                }
                QToolButton:focus {
                    border: none;
                    outline: none;
                }
                QSplitter::handle {
                    background-color: #3e3e42;
                }
                QSplitter::handle:horizontal {
                    width: 2px;
                }
                QSplitter::handle:vertical {
                    height: 2px;
                }
                QTabWidget::pane {
                    border: 1px solid #3e3e42;
                    background-color: #1e1e1e;
                }
                QTabBar::tab {
                    background-color: #2d2d30;
                    color: #969696;
                    border: none;
                    padding: 8px 15px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border-top: 2px solid #007acc;
                }
                QTabBar::tab:hover {
                    background-color: #3e3e42;
                }
                QGroupBox {
                    color: #cccccc;
                    border: 1px solid #3e3e42;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                    color: #cccccc;
                }
                QPushButton {
                    background-color: #0e639c;
                    color: #ffffff;
                    border: none;
                    padding: 6px 15px;
                    border-radius: 3px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
                QPushButton:pressed {
                    background-color: #0d5a8f;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #3c3c3c;
                    color: #cccccc;
                    border: 1px solid #3e3e42;
                    padding: 5px;
                    border-radius: 3px;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                    border: 1px solid #007acc;
                }
                QComboBox QAbstractItemView {
                    background-color: #252526;
                    color: #cccccc;
                    selection-background-color: #2a2d2e;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 5px solid #cccccc;
                    margin-right: 5px;
                }
                QTextEdit, QPlainTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    selection-background-color: #264f78;
                }
                QTextEdit {
                    background-color: #3c3c3c;
                    color: #cccccc;
                    border: 1px solid #555555;
                }
                QCheckBox {
                    color: #cccccc;
                }
                QLabel {
                    color: #cccccc;
                }
                QScrollBar:vertical {
                    background-color: #1e1e1e;
                    width: 14px;
                }
                QScrollBar::handle:vertical {
                    background-color: #424242;
                    min-height: 20px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #4e4e4e;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    background-color: #1e1e1e;
                    height: 14px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #424242;
                    min-width: 20px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #4e4e4e;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                QTreeWidget, QListWidget {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #3e3e42;
                    alternate-background-color: #252526;
                }
                QTreeWidget::item:selected, QListWidget::item:selected {
                    background-color: #264f78;
                    color: #ffffff;
                }
                QTreeWidget::item:hover, QListWidget::item:hover {
                    background-color: #2a2d2e;
                }
                QHeaderView::section {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border: none;
                    border-right: 1px solid #3e3e42;
                    border-bottom: 1px solid #3e3e42;
                    padding: 4px;
                }
                QMessageBox {
                    background-color: #2d2d30;
                    color: #cccccc;
                }
                QMessageBox QLabel {
                    color: #cccccc;
                }
                QMessageBox QPushButton {
                    min-width: 80px;
                }
            """
        elif theme.name == "Light":
            return """
                * {
                    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                }
                QPlainTextEdit {
                    font-family: "Consolas", "Courier New", monospace;
                }
                QMainWindow {
                    background-color: #ffffff;
                }
                QMenuBar {
                    background-color: #f3f3f3;
                    color: #000000;
                    border-bottom: 1px solid #dddddd;
                    font-size: 13px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #e5e5e5;
                }
                QMenu {
                    background-color: #f3f3f3;
                    color: #000000;
                    border: 1px solid #dddddd;
                    font-size: 13px;
                }
                QMenu::item:selected {
                    background-color: #e5e5e5;
                }
                QToolBar {
                    background-color: #f3f3f3;
                    border-bottom: 1px solid #dddddd;
                    spacing: 3px;
                    padding: 3px;
                }
                QToolButton {
                    background-color: #f3f3f3;
                    color: #000000;
                    border: none;
                    padding: 5px 10px;
                    margin: 2px;
                    border-radius: 3px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QToolButton:hover {
                    background-color: #e5e5e5;
                }
                QSplitter::handle {
                    background-color: #dddddd;
                }
                QTabWidget::pane {
                    border: 1px solid #dddddd;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #f3f3f3;
                    color: #696969;
                    border: none;
                    padding: 8px 15px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    color: #000000;
                    border-top: 2px solid #0078d4;
                }
                QTabBar::tab:hover {
                    background-color: #e5e5e5;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: #ffffff;
                    border: none;
                    padding: 6px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #006cbe;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #dddddd;
                    padding: 5px;
                    border-radius: 3px;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                    border: 1px solid #0078d4;
                }
                QTreeWidget, QListWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #dddddd;
                    alternate-background-color: #f5f5f5;
                }
                QTreeWidget::item:selected, QListWidget::item:selected {
                    background-color: #add6ff;
                    color: #000000;
                }
                QTreeWidget::item:hover, QListWidget::item:hover {
                    background-color: #e5e5e5;
                }
                QHeaderView::section {
                    background-color: #f3f3f3;
                    color: #000000;
                    border: none;
                    border-right: 1px solid #dddddd;
                    border-bottom: 1px solid #dddddd;
                    padding: 4px;
                }
                QMessageBox {
                    background-color: #ffffff;
                    color: #000000;
                }
                QMessageBox QLabel {
                    color: #000000;
                }
                QMessageBox QPushButton {
                    min-width: 80px;
                }
            """
        elif theme.name == "Monokai":
            return """
                * {
                    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                }
                QPlainTextEdit {
                    font-family: "Consolas", "Courier New", monospace;
                }
                QMainWindow {
                    background-color: #272822;
                }
                QMenuBar {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                    border-bottom: 1px solid #75715e;
                    font-size: 13px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                    color: #f8f8f2;
                }
                QMenuBar::item:selected {
                    background-color: #49483e;
                }
                QMenuBar::item:pressed {
                    background-color: #66d9ef;
                    color: #272822;
                }
                QMenu {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                    border: 1px solid #75715e;
                    font-size: 13px;
                }
                QMenu::item:selected {
                    background-color: #49483e;
                }
                QToolBar {
                    background-color: #3e3d32;
                    border-bottom: 1px solid #75715e;
                    spacing: 3px;
                    padding: 3px;
                }
                QToolButton {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                    border: none;
                    padding: 5px 10px;
                    margin: 2px;
                    border-radius: 3px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QToolButton:hover {
                    background-color: #49483e;
                }
                QToolButton:pressed {
                    background-color: #66d9ef;
                    color: #272822;
                }
                QSplitter::handle {
                    background-color: #75715e;
                }
                QSplitter::handle:horizontal {
                    width: 2px;
                }
                QSplitter::handle:vertical {
                    height: 2px;
                }
                QTabWidget::pane {
                    border: 1px solid #75715e;
                    background-color: #272822;
                }
                QTabBar::tab {
                    background-color: #3e3d32;
                    color: #90908a;
                    border: none;
                    padding: 8px 15px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #272822;
                    color: #f8f8f2;
                    border-top: 2px solid #66d9ef;
                }
                QTabBar::tab:hover {
                    background-color: #49483e;
                    color: #f8f8f2;
                }
                QGroupBox {
                    color: #f8f8f2;
                    border: 1px solid #75715e;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #66d9ef;
                    color: #272822;
                    border: none;
                    padding: 6px 15px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #82e5ff;
                }
                QPushButton:pressed {
                    background-color: #4ac4e0;
                }
                QLineEdit, QSpinBox, QComboBox, QTextEdit {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                    border: 1px solid #75715e;
                    padding: 5px;
                    border-radius: 3px;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
                    border: 1px solid #66d9ef;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 5px solid #f8f8f2;
                    margin-right: 5px;
                }
                QTextEdit, QPlainTextEdit {
                    background-color: #272822;
                    color: #f8f8f2;
                    border: 1px solid #75715e;
                    selection-background-color: #49483e;
                }
                QCheckBox {
                    color: #f8f8f2;
                }
                QLabel {
                    color: #f8f8f2;
                }
                QScrollBar:vertical {
                    background-color: #272822;
                    width: 14px;
                }
                QScrollBar::handle:vertical {
                    background-color: #75715e;
                    min-height: 20px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #90908a;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    background-color: #272822;
                    height: 14px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #75715e;
                    min-width: 20px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #90908a;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                QTreeWidget, QListWidget {
                    background-color: #272822;
                    color: #f8f8f2;
                    border: 1px solid #75715e;
                    alternate-background-color: #3e3d32;
                }
                QTreeWidget::item:selected, QListWidget::item:selected {
                    background-color: #49483e;
                    color: #f8f8f2;
                }
                QTreeWidget::item:hover, QListWidget::item:hover {
                    background-color: #3e3d32;
                }
                QHeaderView::section {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                    border: none;
                    border-right: 1px solid #75715e;
                    border-bottom: 1px solid #75715e;
                    padding: 4px;
                }
                QMessageBox {
                    background-color: #3e3d32;
                    color: #f8f8f2;
                }
                QMessageBox QLabel {
                    color: #f8f8f2;
                }
                QMessageBox QPushButton {
                    min-width: 80px;
                }
            """
        else:
            return """
                * {
                    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
                }
                QPlainTextEdit {
                    font-family: "Consolas", "Courier New", monospace;
                }
                QMainWindow {
                    background-color: #1a0f0f;
                }
                QMenuBar {
                    background-color: #2a1515;
                    color: #ff9933;
                    border-bottom: 1px solid #663333;
                    font-size: 13px;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                    color: #ff9933;
                }
                QMenuBar::item:selected {
                    background-color: #3d2020;
                }
                QMenuBar::item:pressed {
                    background-color: #663399;
                    color: #ffcc66;
                }
                QMenu {
                    background-color: #2a1515;
                    color: #ff9933;
                    border: 1px solid #663333;
                    font-size: 13px;
                }
                QMenu::item:selected {
                    background-color: #3d2020;
                }
                QToolBar {
                    background-color: #2a1515;
                    border-bottom: 1px solid #663333;
                    spacing: 3px;
                    padding: 3px;
                }
                QToolButton {
                    background-color: #2a1515;
                    color: #ff9933;
                    border: none;
                    padding: 5px 10px;
                    margin: 2px;
                    border-radius: 3px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QToolButton:hover {
                    background-color: #3d2020;
                }
                QToolButton:pressed {
                    background-color: #663399;
                    color: #ffcc66;
                }
                QSplitter::handle {
                    background-color: #663333;
                }
                QSplitter::handle:horizontal {
                    width: 2px;
                }
                QSplitter::handle:vertical {
                    height: 2px;
                }
                QTabWidget::pane {
                    border: 1px solid #663333;
                    background-color: #1a0f0f;
                }
                QTabBar::tab {
                    background-color: #2a1515;
                    color: #996633;
                    border: none;
                    padding: 8px 15px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #1a0f0f;
                    color: #ff9933;
                    border-top: 2px solid #cc66ff;
                }
                QTabBar::tab:hover {
                    background-color: #3d2020;
                    color: #ff9933;
                }
                QGroupBox {
                    color: #ff9933;
                    border: 1px solid #663333;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #cc66ff;
                    color: #1a0f0f;
                    border: none;
                    padding: 6px 15px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #dd77ff;
                }
                QPushButton:pressed {
                    background-color: #aa55dd;
                }
                QLineEdit, QSpinBox, QComboBox, QTextEdit {
                    background-color: #2a1515;
                    color: #ff9933;
                    border: 1px solid #663333;
                    padding: 5px;
                    border-radius: 3px;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
                    border: 1px solid #cc66ff;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 5px solid #ff9933;
                    margin-right: 5px;
                }
                QTextEdit, QPlainTextEdit {
                    background-color: #1a0f0f;
                    color: #ff9933;
                    border: 1px solid #663333;
                    selection-background-color: #663399;
                }
                QCheckBox {
                    color: #ff9933;
                }
                QLabel {
                    color: #ff9933;
                }
                QScrollBar:vertical {
                    background-color: #1a0f0f;
                    width: 14px;
                }
                QScrollBar::handle:vertical {
                    background-color: #663333;
                    min-height: 20px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #996633;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar:horizontal {
                    background-color: #1a0f0f;
                    height: 14px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #663333;
                    min-width: 20px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #996633;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    width: 0px;
                }
                QTreeWidget, QListWidget {
                    background-color: #1a0f0f;
                    color: #ff9933;
                    border: 1px solid #663333;
                    alternate-background-color: #2a1515;
                }
                QTreeWidget::item:selected, QListWidget::item:selected {
                    background-color: #663399;
                    color: #ffcc66;
                }
                QTreeWidget::item:hover, QListWidget::item:hover {
                    background-color: #3d2020;
                }
                QHeaderView::section {
                    background-color: #2a1515;
                    color: #ff9933;
                    border: none;
                    border-right: 1px solid #663333;
                    border-bottom: 1px solid #663333;
                    padding: 4px;
                }
                QMessageBox {
                    background-color: #2a1515;
                    color: #ff9933;
                }
                QMessageBox QLabel {
                    color: #ff9933;
                }
                QMessageBox QPushButton {
                    min-width: 80px;
                }
            """
