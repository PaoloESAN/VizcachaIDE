"""
Variables inspector widget for displaying program variables during debugging
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette


class VariablesWidget(QTreeWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setHeaderLabels(["Name", "Type", "Value"])
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.Stretch)

        font = QFont("Consolas", 9)
        font.setWeight(QFont.Medium)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
            font.setWeight(QFont.Medium)
        self.setFont(font)

        self.setAlternatingRowColors(True)

        self.setSortingEnabled(True)
        
        self.setAutoFillBackground(True)

    def update_variables(self, variables):
        self.clear()

        for var in variables:
            self.add_variable(var)

        self.expandAll()

    def add_variable(self, var, parent=None):
        if parent is None:
            item = QTreeWidgetItem(self)
        else:
            item = QTreeWidgetItem(parent)

        item.setText(0, var.get('name', ''))
        item.setText(1, var.get('type', ''))
        item.setText(2, var.get('value', ''))

        if 'children' in var and var['children']:
            for child in var['children']:
                self.add_variable(child, item)

        return item

    def clear(self):
        super().clear()
