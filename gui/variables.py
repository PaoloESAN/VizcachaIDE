"""
Variables inspector widget for displaying program variables during debugging
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class VariablesWidget(QTreeWidget):
    """Widget for displaying variables during debugging"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set headers
        self.setHeaderLabels(["Name", "Type", "Value"])
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.Stretch)

        # Set font
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.setFont(font)

        # Set alternating row colors
        self.setAlternatingRowColors(True)

        # Enable sorting
        self.setSortingEnabled(True)

    def update_variables(self, variables):
        """Update the variables display

        Args:
            variables: List of dictionaries with 'name', 'type', 'value', and optional 'children'
        """
        self.clear()

        for var in variables:
            self.add_variable(var)

        # Expand all items by default
        self.expandAll()

    def add_variable(self, var, parent=None):
        """Add a variable to the tree

        Args:
            var: Dictionary with 'name', 'type', 'value', and optional 'children'
            parent: Parent tree item (None for root level)
        """
        if parent is None:
            item = QTreeWidgetItem(self)
        else:
            item = QTreeWidgetItem(parent)

        item.setText(0, var.get('name', ''))
        item.setText(1, var.get('type', ''))
        item.setText(2, var.get('value', ''))

        # Add children if present (for structs, slices, maps)
        if 'children' in var and var['children']:
            for child in var['children']:
                self.add_variable(child, item)

        return item

    def clear(self):
        """Clear all variables"""
        super().clear()
