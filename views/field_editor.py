from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QCheckBox,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
import re
from views.reg_tester import RegexTester  # Import the RegexTester dialog


class FieldEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Field Editor")
        self.setGeometry(300, 300, 400, 250)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Field Name Input
        self.field_name_label = QLabel("Field Name:")
        self.field_name_edit = QLineEdit(self)
        layout.addWidget(self.field_name_label)
        layout.addWidget(self.field_name_edit)

        # Regex Input
        self.regex_label = QLabel("Regular Expression:")
        self.regex_edit = QLineEdit(self)
        layout.addWidget(self.regex_label)
        layout.addWidget(self.regex_edit)

        # Visibility (Display) Checkbox
        self.visibility_checkbox = QCheckBox("Display (Visible)")
        layout.addWidget(self.visibility_checkbox)

        # Sorted Checkbox
        self.sorted_checkbox = QCheckBox("Sorted")
        layout.addWidget(self.sorted_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        test_regex_button = QPushButton("Test Regex")  # Add Test Regex button
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(test_regex_button)  # Add Test Regex button to layout
        layout.addLayout(button_layout)

        # Connect buttons
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        test_regex_button.clicked.connect(self.open_regex_tester)  # Connect Test Regex button

        self.setLayout(layout)

    def get_field_data(self):
        """Return the field data entered by the user."""
        return {
            "field_name": self.field_name_edit.text().strip(),
            "regex": self.regex_edit.text().strip(),
            "visibility": self.visibility_checkbox.isChecked(),
            "sorted": self.sorted_checkbox.isChecked(),
        }

    def set_field_data(self, field_name, regex, visibility, sorted_field):
        """Set the field data in the editor."""
        self.field_name_edit.setText(field_name)
        self.regex_edit.setText(regex)
        self.visibility_checkbox.setChecked(visibility)
        self.sorted_checkbox.setChecked(sorted_field)

    def open_regex_tester(self):
        """Open the RegexTester window and pass the current regex."""
        regex = self.regex_edit.text().strip()
        if not regex:
            QMessageBox.warning(self, "Input Error", "Please enter a regular expression to test.")
            return

        # Open the RegexTester dialog
        tester = RegexTester(self)
        tester.set_regex(regex)  # Pass the regex to the tester
        tester.exec_()

