from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt

class FilterSettingsDialog(QDialog):
    def __init__(self, filter_model, field_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Settings")
        self.setGeometry(300, 300, 400, 300)

        self.filter_model = filter_model
        self.field_names = field_names  # List of field names

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Field Selection
        field_layout = QHBoxLayout()
        field_label = QLabel("Field:")
        self.field_selector = QComboBox(self)
        self.field_selector.addItems(self.field_names)
        field_layout.addWidget(field_label)
        field_layout.addWidget(self.field_selector)
        layout.addLayout(field_layout)

        # Type Selection (Number or String)
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        self.number_radio = QRadioButton("Number")
        self.string_radio = QRadioButton("String")
        self.string_radio.setChecked(True)  # Default to string
        self.type_group = QButtonGroup(self)
        self.type_group.addButton(self.number_radio)
        self.type_group.addButton(self.string_radio)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.number_radio)
        type_layout.addWidget(self.string_radio)
        layout.addLayout(type_layout)

        # Low Limit Input
        low_layout = QHBoxLayout()
        low_label = QLabel("Low Limit:")
        self.low_input = QLineEdit(self)
        low_layout.addWidget(low_label)
        low_layout.addWidget(self.low_input)
        layout.addLayout(low_layout)

        # High Limit Input
        high_layout = QHBoxLayout()
        high_label = QLabel("High Limit:")
        self.high_input = QLineEdit(self)
        high_layout.addWidget(high_label)
        high_layout.addWidget(self.high_input)
        layout.addLayout(high_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        clear_button = QPushButton("Clear All Filters")  # New button to clear filters
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        save_button.clicked.connect(self.save_settings)
        clear_button.clicked.connect(self.clear_filters)  # Connect clear button to clear_filters method
        cancel_button.clicked.connect(self.reject)

    def save_settings(self):
        """Save the filter settings to the database."""
        field = self.field_selector.currentText()
        low = self.low_input.text().strip()
        high = self.high_input.text().strip()
        filter_type = "number" if self.number_radio.isChecked() else "string"

        if not low and not high:
            QMessageBox.warning(self, "Warning", "Please enter at least one limit.")
            return

        # Save to the database via the filter model
        self.filter_model.save_filter_settings(field, low, high, filter_type)
        QMessageBox.information(self, "Success", "Filter settings saved successfully.")
        self.accept()

    def clear_filters(self):
        """Clear all filter fields and reset the filter criteria."""
        self.field_selector.setCurrentIndex(0)  # Reset to the first field
        self.low_input.clear()  # Clear low limit
        self.high_input.clear()  # Clear high limit
        self.string_radio.setChecked(True)  # Reset type to string

        # Reset the filter criteria in the proxy model
        self.filter_model.setFilterCriteria({})  # Clear all filter criteria

        QMessageBox.information(self, "Info", "All filters have been cleared.")

    def load_settings(self):
        """Load the filter settings from the database."""
        settings = self.filter_model.load_filter_settings()
        self.field_selector.setCurrentText(settings.get("field", ""))
        self.low_input.setText(settings.get("low", ""))
        self.high_input.setText(settings.get("high", ""))
        filter_type = settings.get("type", "string")
        if filter_type == "number":
            self.number_radio.setChecked(True)
        else:
            self.string_radio.setChecked(True)
