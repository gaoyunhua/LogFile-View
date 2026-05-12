from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout
import json
from pathlib import Path


class SettingsDialog(QDialog):
    def __init__(self, config_path="resources/config.json", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 200)

        self.config_path = Path(config_path)
        self.settings = self.load_settings()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Default log file directory
        self.default_dir_label = QLabel("Default Log File Directory:")
        self.default_dir_edit = QLineEdit(self)
        self.default_dir_edit.setText(self.settings.get("default_log_dir", ""))
        layout.addWidget(self.default_dir_label)
        layout.addWidget(self.default_dir_edit)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)

    def load_settings(self):
        """Load settings from the configuration file."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {}

    def save_settings(self):
        """Save settings to the configuration file."""
        self.settings["default_log_dir"] = self.default_dir_edit.text().strip()
        with open(self.config_path, "w") as f:
            json.dump(self.settings, f, indent=4)
        self.accept()