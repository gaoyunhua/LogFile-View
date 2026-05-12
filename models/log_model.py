import sqlite3
from models.field_model import default_db_path

class LogModel:
    def __init__(self, db_path=default_db_path):
        self.db_path = db_path
        self.log_data = []  # List to store parsed log data
        self.init_db()

    def init_db(self):
        """Initialize the database and create the logs table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw TEXT
        )
        """)
        conn.commit()
        conn.close()

    def load_logs(self, file_path):
        """Load and parse a log file."""
        self.log_data = []  # Clear existing data
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Save only the raw log line
                    self.log_data.append({"raw": line.strip()})
            # Debugging statement
            # print(f "Loaded {len(self.log_data)} log lines.")
            # print(f"Log data: {self.log_data}")  # Debugging statement
        except Exception as e:
            raise IOError(f"Error reading file: {e}")

    def save_logs_to_db(self):
        """Save the loaded logs to the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        print(f"Saving logs to database: {self.log_data}")  # Debugging statement
        c.executemany("""
        INSERT INTO logs (raw)
        VALUES (?)
        """, [(log["raw"],) for log in self.log_data])
        conn.commit()
        conn.close()

    def get_logs_from_db(self):
        """Retrieve all logs from the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, raw FROM logs")
        rows = c.fetchall()
        conn.close()

        # Convert rows to a list of dictionaries
        self.log_data = [{"id": row[0], "raw": row[1]} for row in rows]
        print(f"Retrieved logs from database: {self.log_data}")  # Debugging statement
        return self.log_data