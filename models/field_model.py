import sqlite3

default_db_path = "log_viewer.db"

class FieldModel:
    def __init__(self, db_path=default_db_path):
        self.db_path = db_path
        self.init_db()
        self.fields = {
            "field1": {"regex": ".*", "visibility": True, "sorted": False, "displayorder": 0, "columnwidth": 100},
            "field2": {"regex": "\\d+", "visibility": True, "sorted": True, "displayorder": 1, "columnwidth": 100},
        }

    def init_db(self):
        """Initialize the database and create the fields table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS fields (
            field_name TEXT PRIMARY KEY,
            regex TEXT,
            visibility INTEGER,
            sorted INTEGER,
            displayorder INTEGER DEFAULT 0,
            columnwidth INTEGER DEFAULT 100
        )
        """)
        # Add columns if upgrading an old DB
        try:
            c.execute("ALTER TABLE fields ADD COLUMN displayorder INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE fields ADD COLUMN columnwidth INTEGER DEFAULT 100")
        except sqlite3.OperationalError:
            pass
        conn.commit()
        conn.close()

    def get_all_fields(self):
        """Retrieve all field definitions from the database, ordered by displayorder."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT field_name, regex, visibility, sorted, displayorder, columnwidth FROM fields ORDER BY displayorder ASC")
        rows = c.fetchall()
        conn.close()

        # Convert rows to a dictionary
        fields = {
            row[0]: {
                "regex": row[1],
                "visibility": bool(row[2]),
                "sorted": bool(row[3]),
                "displayorder": row[4],
                "columnwidth": row[5]
            }
            for row in rows
        }
        return fields

    def add_field(self, field_name, regex, visibility=False, sorted=False, displayorder=0, columnwidth=100):
        """Add a new field definition to the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("""
            INSERT INTO fields (field_name, regex, visibility, sorted, displayorder, columnwidth)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (field_name, regex, int(visibility), int(sorted), displayorder, columnwidth))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Field already exists
        finally:
            conn.close()

    def update_field(self, old_name, new_name, regex, visibility, sorted_field, displayorder=0, columnwidth=100):
        """Update an existing field definition in the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            if old_name != new_name:
                # Check if the new name already exists
                c.execute("SELECT 1 FROM fields WHERE field_name = ?", (new_name,))
                if c.fetchone():
                    return False  # New field name already exists

            # Update the field
            c.execute("""
            UPDATE fields
            SET field_name = ?, regex = ?, visibility = ?, sorted = ?, displayorder = ?, columnwidth = ?
            WHERE field_name = ?
            """, (new_name, regex, int(visibility), int(sorted_field), displayorder, columnwidth, old_name))
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_field(self, field_name):
        """Delete a field definition from the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM fields WHERE field_name = ?", (field_name,))
        conn.commit()
        conn.close()

    def get_field_data(self, field_name):
        """Retrieve the data for a specific field directly from the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT regex, visibility, sorted, displayorder, columnwidth FROM fields WHERE field_name = ?", (field_name,))
        row = c.fetchone()
        conn.close()

        if row:
            return {
                "regex": row[0],
                "visibility": bool(row[1]),
                "sorted": bool(row[2]),
                "displayorder": row[3],
                "columnwidth": row[4]
            }
        return {}

    @staticmethod
    def add_displayorder_and_columnwidth_to_fields_table(db_path=default_db_path):
        """Add displayorder and columnwidth columns to the fields table if they do not exist."""
        import sqlite3
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE fields ADD COLUMN displayorder INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            c.execute("ALTER TABLE fields ADD COLUMN columnwidth INTEGER DEFAULT 100")
        except sqlite3.OperationalError:
            pass  # Column already exists
        conn.commit()
        conn.close()


    def refine_displayorder(self):
        """
        Ensure displayorder is unique and starts from 1, ordered by current displayorder then field_name.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Get all field names ordered by current displayorder and field_name
        c.execute("SELECT field_name FROM fields ORDER BY displayorder ASC, field_name ASC")
        rows = c.fetchall()
        # Assign new displayorder starting from 1
        for idx, (field_name,) in enumerate(rows, start=1):
            c.execute("UPDATE fields SET displayorder = ? WHERE field_name = ?", (idx, field_name))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Run this script to add displayorder and columnwidth columns to the fields table
    # FieldModel.add_displayorder_and_columnwidth_to_fields_table(default_db_path)
    # Refine displayorder to be unique and start from 1
    fm = FieldModel(default_db_path)
    fm.refine_displayorder()
    print("Columns 'displayorder' and 'columnwidth' ensured in 'fields' table and displayorder refined.")
