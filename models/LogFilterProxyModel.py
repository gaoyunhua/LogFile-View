import sqlite3
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from models.field_model import default_db_path


class LogFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, db_path=default_db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.filter_criteria = {}
        self.column_filters = {}  # {column_index: set(allowed_values)}
        self.search_text = ""

    def lessThan(self, left, right):
        """Compare two items for sorting, trying numeric comparison first."""
        left_data = self.sourceModel().data(left, Qt.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.DisplayRole)

        if left_data is None:
            return True
        if right_data is None:
            return False

        # Try numeric comparison
        try:
            return float(left_data) < float(right_data)
        except (ValueError, TypeError):
            pass

        # Fall back to case-insensitive string comparison
        return str(left_data).lower() < str(right_data).lower()

    def setFilterCriteria(self, criteria):
        """Set the range filter criteria and refresh the view."""
        self.filter_criteria = criteria
        self.invalidateFilter()

    def setColumnFilter(self, column_index, allowed_values):
        """Set filter for a specific column (set of allowed values)."""
        if allowed_values is None:
            self.column_filters.pop(column_index, None)
        else:
            self.column_filters[column_index] = allowed_values
        self.invalidateFilter()

    def clearColumnFilter(self, column_index):
        """Remove filter for a specific column."""
        self.column_filters.pop(column_index, None)
        self.invalidateFilter()

    def clearAllColumnFilters(self):
        """Remove all column filters."""
        self.column_filters.clear()
        self.invalidateFilter()

    def setSearchText(self, text):
        """Set the quick search text and refresh the view."""
        self.search_text = text.strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Determine whether a row should be displayed based on all filter layers."""
        model = self.sourceModel()
        if model is None:
            return True

        # Layer 1: Range filter
        if not self._matches_range_filter(source_row, source_parent, model):
            return False

        # Layer 2: Column filters
        if not self._matches_column_filters(source_row, source_parent, model):
            return False

        # Layer 3: Quick search text
        if not self._matches_search_text(source_row, source_parent, model):
            return False

        return True

    def _matches_range_filter(self, source_row, source_parent, model):
        """Check if row passes the range filter criteria."""
        if not self.filter_criteria:
            return True

        field_name = self.filter_criteria.get("field")
        if not field_name:
            return True

        column_index = None
        for col in range(model.columnCount()):
            if model.headerData(col, Qt.Horizontal, Qt.DisplayRole) == field_name:
                column_index = col
                break

        if column_index is None:
            return True

        index = model.index(source_row, column_index, source_parent)
        data = model.data(index, Qt.DisplayRole)
        return self._matches_criteria(data)

    def _matches_column_filters(self, source_row, source_parent, model):
        """Check if row passes all active column filters."""
        for col_index, allowed_values in self.column_filters.items():
            if col_index >= model.columnCount():
                continue
            index = model.index(source_row, col_index, source_parent)
            data = model.data(index, Qt.DisplayRole)
            cell_value = str(data) if data else ""
            if cell_value not in allowed_values:
                return False
        return True

    def _matches_search_text(self, source_row, source_parent, model):
        """Check if any column in the row contains the search text."""
        if not self.search_text:
            return True

        for col in range(model.columnCount()):
            index = model.index(source_row, col, source_parent)
            data = model.data(index, Qt.DisplayRole)
            if data and self.search_text in str(data).lower():
                return True
        return False

    def _matches_criteria(self, data):
        """Check if the data matches the range filter criteria."""
        if not self.filter_criteria:
            return True

        data_str = str(data) if data is not None else ""
        filter_type = self.filter_criteria.get("type", "string")

        if filter_type == "number":
            try:
                if data is None or data == "":
                    return False
                data_num = float(data)
                low = self.filter_criteria.get("low")
                high = self.filter_criteria.get("high")
                if low is not None and low != "":
                    if data_num < float(low):
                        return False
                if high is not None and high != "":
                    if data_num > float(high):
                        return False
            except (ValueError, TypeError):
                return False
        else:
            low = self.filter_criteria.get("low")
            if low is not None and low != "":
                if data_str < str(low):
                    return False
            high = self.filter_criteria.get("high")
            if high is not None and high != "":
                if data_str > str(high):
                    return False

        return True

    def save_filter_settings(self, field, low, high, filter_type):
        """Save the filter settings to the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS filter_settings")
        c.execute("""
            CREATE TABLE filter_settings (
                id INTEGER PRIMARY KEY,
                field TEXT,
                low TEXT,
                high TEXT,
                type TEXT
            )
        """)
        c.execute(
            "INSERT INTO filter_settings (field, low, high, type) VALUES (?, ?, ?, ?)",
            (field, low, high, filter_type)
        )
        conn.commit()
        conn.close()

    def load_filter_settings(self):
        """Load the filter settings from the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("SELECT field, low, high, type FROM filter_settings LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("DROP TABLE IF EXISTS filter_settings")
            c.execute("""
                CREATE TABLE filter_settings (
                    id INTEGER PRIMARY KEY,
                    field TEXT,
                    low TEXT,
                    high TEXT,
                    type TEXT
                )
            """)
        c.execute("SELECT field, low, high, type FROM filter_settings LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            return {"field": row[0], "low": row[1], "high": row[2], "type": row[3]}
        return {}
