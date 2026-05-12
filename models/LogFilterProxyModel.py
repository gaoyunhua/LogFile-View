import sqlite3
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from models.field_model import default_db_path


class LogFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, db_path=default_db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.filter_criteria = {}

    def setFilterCriteria(self, criteria):
        """Set the filter criteria and refresh the view."""
        self.filter_criteria = criteria
        self.invalidateFilter()  # Reapply the filter

    def filterAcceptsRow(self, source_row, source_parent):
        """Determine whether a row should be displayed based on the filter criteria."""
        if not self.filter_criteria:
            return True  # Show all rows if no filter criteria are set

        model = self.sourceModel()
        if model is None:
            return True

        # Get the field to filter on
        field_name = self.filter_criteria.get("field")
        if not field_name:
            return True  # Show all rows if no field is specified

        # Find the column index for the field
        column_index = None
        for col in range(model.columnCount()):
            if model.headerData(col, Qt.Horizontal, Qt.DisplayRole) == field_name:
                column_index = col
                break

        if column_index is None:
            return True  # Show all rows if the field is not found

        # Get the data for the specified field
        index = model.index(source_row, column_index, source_parent)
        data = model.data(index, Qt.DisplayRole)

        # Apply the filter criteria
        return self._matches_criteria(data)

    def _matches_criteria(self, data):
        """Check if the data matches the filter criteria."""
        if not self.filter_criteria:
            return True

        # Convert data to string for comparison
        data_str = str(data) if data is not None else ""

        # Determine the filter type (number or string)
        filter_type = self.filter_criteria.get("type", "string")

        if filter_type == "number":
            try:
                # Ensure data is not None or empty before converting to a number
                if data is None or data == "":
                    return False

                # Convert data to a number
                data_num = float(data)

                # Get low and high limits
                low = self.filter_criteria.get("low")
                high = self.filter_criteria.get("high")

                # Debugging log
                # print(f"Data: {data_num}, Low: {low}, High: {high}")

                # Validate and compare low limit
                if low is not None and low != "":
                    if data_num < float(low):
                        return False

                # Validate and compare high limit
                if high is not None and high != "":
                    if data_num > float(high):
                        return False
            except (ValueError, TypeError):
                # If conversion fails, the data does not match
                return False
        else:
            # Check low limit for strings
            low = self.filter_criteria.get("low")
            if low is not None and low != "":
                if data_str < str(low):
                    return False

            # Check high limit for strings
            high = self.filter_criteria.get("high")
            if high is not None and high != "":
                if data_str > str(high):
                    return False

        return True

    def save_filter_settings(self, field, low, high, filter_type):
        """Save the filter settings to the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Drop the existing table if it exists
        c.execute("DROP TABLE IF EXISTS filter_settings")

        # Create the table with the updated schema
        c.execute("""
            CREATE TABLE filter_settings (
                id INTEGER PRIMARY KEY,
                field TEXT,
                low TEXT,
                high TEXT,
                type TEXT
            )
        """)

        # Insert the new filter settings
        c.execute("INSERT INTO filter_settings (field, low, high, type) VALUES (?, ?, ?, ?)",
                  (field, low, high, filter_type))
        conn.commit()
        conn.close()

    def load_filter_settings(self):
        """Load the filter settings from the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check if the table exists and has the correct schema
        try:
            c.execute("SELECT field, low, high, type FROM filter_settings LIMIT 1")
        except sqlite3.OperationalError:
            # If the table or columns are missing, recreate the table
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

        # Fetch the filter settings
        c.execute("SELECT field, low, high, type FROM filter_settings LIMIT 1")
        row = c.fetchone()
        conn.close()

        if row:
            return {"field": row[0], "low": row[1], "high": row[2], "type": row[3]}
        return {}