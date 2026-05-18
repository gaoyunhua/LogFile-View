from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton,
    QScrollArea, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt


class ColumnFilterPopup(QWidget):
    """Popup widget showing checkboxes for unique column values (Excel AutoFilter style)."""
    filterApplied = pyqtSignal(int, object)  # (column_index, set of allowed values or None)

    def __init__(self, column_index, unique_values, currently_checked=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.column_index = column_index
        self.unique_values = sorted(unique_values, key=lambda x: str(x).lower())
        self.currently_checked = currently_checked
        self.checkboxes = []

        self.setMinimumWidth(200)
        self.setMaximumHeight(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Select All / Deselect All
        self.select_all_cb = QCheckBox("(Select All)")
        self.select_all_cb.setChecked(self._all_checked())
        self.select_all_cb.stateChanged.connect(self._on_select_all_changed)
        layout.addWidget(self.select_all_cb)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        # Scrollable area for value checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)

        for value in self.unique_values:
            display_text = value if value else "(empty)"
            cb = QCheckBox(display_text)
            if self.currently_checked is None:
                cb.setChecked(True)
            else:
                cb.setChecked(value in self.currently_checked)
            cb.stateChanged.connect(self._on_item_changed)
            scroll_layout.addWidget(cb)
            self.checkboxes.append((value, cb))

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        clear_button = QPushButton("Clear Filter")
        ok_button.clicked.connect(self._on_ok)
        cancel_button.clicked.connect(self.close)
        clear_button.clicked.connect(self._on_clear)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def _all_checked(self):
        """Check if all values should be considered checked."""
        return self.currently_checked is None

    def _on_select_all_changed(self, state):
        """Toggle all checkboxes."""
        checked = state == Qt.Checked
        for _, cb in self.checkboxes:
            cb.setChecked(checked)

    def _on_item_changed(self):
        """Update Select All checkbox state when individual items change."""
        all_checked = all(cb.isChecked() for _, cb in self.checkboxes)
        none_checked = not any(cb.isChecked() for _, cb in self.checkboxes)
        self.select_all_cb.blockSignals(True)
        if all_checked:
            self.select_all_cb.setChecked(True)
        elif none_checked:
            self.select_all_cb.setChecked(False)
        else:
            self.select_all_cb.setTristate(True)
            self.select_all_cb.setCheckState(Qt.PartiallyChecked)
        self.select_all_cb.blockSignals(False)

    def _on_ok(self):
        """Apply the filter with checked values."""
        checked_values = set()
        for value, cb in self.checkboxes:
            if cb.isChecked():
                checked_values.add(value)

        # If all are checked, clear the filter (no filtering needed)
        if len(checked_values) == len(self.unique_values):
            self.filterApplied.emit(self.column_index, None)
        else:
            self.filterApplied.emit(self.column_index, checked_values)
        self.close()

    def _on_clear(self):
        """Clear the filter for this column (show all)."""
        self.filterApplied.emit(self.column_index, None)
        self.close()
