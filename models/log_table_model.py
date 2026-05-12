from PyQt5.QtCore import QAbstractTableModel, Qt
from models.utils import get_header_data  # Import the utility function


class LogTableModel(QAbstractTableModel):
    def __init__(self, log_data, visible_fields, parent=None):
        super().__init__(parent)
        self.log_data = log_data
        self.visible_fields = visible_fields

    def rowCount(self, parent=None):
        return len(self.log_data)

    def columnCount(self, parent=None):
        # Include the "Raw Log" column in addition to visible fields
        return 1 + len(self.visible_fields)

    def data(self, index, role):
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        # Validate the row index
        if row < 0 or row >= len(self.log_data):
            return None

        if role == Qt.DisplayRole:
            if column == 0:
                return self.log_data[row].get("raw", "")
            else:
                field_name = list(self.visible_fields.keys())[column - 1]
                return self.log_data[row].get(field_name, "")

        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter  # Align text with wrapping

        return None

    def headerData(self, section, orientation, role):
        """Provide header data for the table."""
        return get_header_data(section, orientation, role, self.visible_fields)