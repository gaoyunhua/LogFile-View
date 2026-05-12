from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QCheckBox
)
from views.field_editor import FieldEditor


class FieldList(QDialog):
    # Signal to notify that field data has been modified
    fields_updated = pyqtSignal()

    def __init__(self, field_model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Field Definitions")
        self.setGeometry(300, 300, 800, 400)

        self.field_model = field_model  # Reference to the FieldModel
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Table to display field definitions
        self.field_table = QTableWidget(self)
        self.field_table.setColumnCount(4)
        self.field_table.setHorizontalHeaderLabels(["Field Name", "Display", "Sorted", "Regular Expression"])
        self.load_fields()
        layout.addWidget(self.field_table)

        # Buttons for actions
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        edit_button = QPushButton("Edit")
        delete_button = QPushButton("Delete")
        close_button = QPushButton("Close")

        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Connect buttons to their actions
        add_button.clicked.connect(self.add_field)
        edit_button.clicked.connect(self.edit_field)
        delete_button.clicked.connect(self.delete_field)
        close_button.clicked.connect(self.close)

    def load_fields(self):
        """Load field definitions into the table."""
        self.field_table.setRowCount(0)  # Clear the table
        fields = self.field_model.get_all_fields()
        #print(f"Loaded fields: {fields}")  # Debugging statement
        for row, (field_name, field_data) in enumerate(fields.items()):
            self.field_table.insertRow(row)

            # Field Name (Non-editable)
            field_item = QTableWidgetItem(field_name)
            field_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Disable editing
            self.field_table.setItem(row, 0, field_item)

            # Display (Visibility) Checkbox (Disabled)
            visibility_checkbox = QCheckBox()
            visibility_checkbox.setChecked(field_data.get("visibility", False))
            visibility_checkbox.setEnabled(False)  # Disable checkbox
            self.field_table.setCellWidget(row, 1, visibility_checkbox)

            # Sorted Checkbox (Disabled)
            sorted_checkbox = QCheckBox()
            sorted_checkbox.setChecked(field_data.get("sorted", False))
            sorted_checkbox.setEnabled(False)  # Disable checkbox
            self.field_table.setCellWidget(row, 2, sorted_checkbox)

            # Regular Expression (Non-editable)
            regex_item = QTableWidgetItem(field_data.get("regex", ""))
            regex_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Disable editing
            self.field_table.setItem(row, 3, regex_item)

        # Automatically adjust column widths to fit content
        self.field_table.resizeColumnsToContents()

    def add_field(self):
        """Add a new field definition."""
        editor = FieldEditor(self)
        if editor.exec_():  # If the dialog is accepted
            field_data = editor.get_field_data()
            field_name = field_data["field_name"]
            regex = field_data["regex"]
            visibility = field_data["visibility"]
            sorted_field = field_data["sorted"]

            if field_name and regex:
                if self.field_model.add_field(field_name, regex, visibility, sorted_field):
                    self.load_fields()
                    self.fields_updated.emit()  # Emit signal to notify main window
                else:
                    QMessageBox.warning(self, "Error", f"Field '{field_name}' already exists.")
            else:
                QMessageBox.warning(self, "Input Error", "Field name and regex cannot be empty.")

    def edit_field(self):
        """Edit the selected field definition."""
        selected_row = self.field_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a field to edit.")
            return

        field_name = self.field_table.item(selected_row, 0).text()
        regex = self.field_table.item(selected_row, 3).text()
        visibility = self.field_table.cellWidget(selected_row, 1).isChecked()
        sorted_field = self.field_table.cellWidget(selected_row, 2).isChecked()

        editor = FieldEditor(self)
        editor.set_field_data(field_name, regex, visibility, sorted_field)

        if editor.exec_():  # If the dialog is accepted
            field_data = editor.get_field_data()
            new_field_name = field_data["field_name"]
            new_regex = field_data["regex"]
            new_visibility = field_data["visibility"]
            new_sorted = field_data["sorted"]

            if new_field_name and new_regex:
                if self.field_model.update_field(field_name, new_field_name, new_regex, new_visibility, new_sorted):
                    self.load_fields()
                    self.fields_updated.emit()  # Emit signal to notify main window
                else:
                    QMessageBox.warning(self, "Error", f"Field '{new_field_name}' already exists.")
            else:
                QMessageBox.warning(self, "Input Error", "Field name and regex cannot be empty.")

    def delete_field(self):
        """Delete the selected field definition."""
        selected_row = self.field_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a field to delete.")
            return

        field_name = self.field_table.item(selected_row, 0).text()
        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to delete the field '{field_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.field_model.delete_field(field_name)
            self.load_fields()
            self.fields_updated.emit()  # Emit signal to notify main window