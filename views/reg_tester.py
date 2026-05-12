import re
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox, QHBoxLayout

class RegexTester(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Regex Tester")
        self.setGeometry(300, 300, 500, 300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Regex Input (Editable)
        self.regex_label = QLabel("Regular Expression:")
        self.regex_edit = QLineEdit(self)  # Make regex input editable
        layout.addWidget(self.regex_label)
        layout.addWidget(self.regex_edit)

        # Sample Text Input (Editable)
        self.sample_text_label = QLabel("Sample Text:")
        self.sample_text_edit = QLineEdit(self)  # Make sample text input editable
        layout.addWidget(self.sample_text_label)
        layout.addWidget(self.sample_text_edit)

        # Result Display
        self.result_label = QLabel("Result:")
        self.result_edit = QLineEdit(self)
        self.result_edit.setReadOnly(True)  # Keep the result read-only
        layout.addWidget(self.result_label)
        layout.addWidget(self.result_edit)

        # Buttons
        button_layout = QHBoxLayout()
        test_button = QPushButton("Test")
        close_button = QPushButton("Close")
        button_layout.addWidget(test_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Connect buttons
        test_button.clicked.connect(self.test_regex)
        close_button.clicked.connect(self.reject)

        self.setLayout(layout)

    def set_regex(self, regex):
        """Set the regular expression in the tester."""
        self.regex_edit.setText(regex)

    def test_regex(self):
        """Test the regular expression against the sample text."""
        regex = self.regex_edit.text().strip()
        sample_text = self.sample_text_edit.text().strip()

        if not regex:
            QMessageBox.warning(self, "Input Error", "Please enter a valid regular expression.")
            return

        if not sample_text:
            QMessageBox.warning(self, "Input Error", "Please enter sample text to test.")
            return

        try:
            # Apply the regex
            match = re.search(regex, sample_text)
            if match:
                self.result_edit.setText(f"Match found: {match.group(0)}")
            else:
                self.result_edit.setText("No match found.")
        except re.error as e:
            QMessageBox.critical(self, "Regex Error", f"Invalid regular expression: {e}")
