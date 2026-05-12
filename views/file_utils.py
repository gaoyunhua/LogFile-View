import json
import sqlite3
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from models.field_model import default_db_path

def ensure_config_table():
    """Ensure the config table exists in log_viewer.db."""
    conn = sqlite3.connect(default_db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

# Ensure the config table exists when this module is run directly
if __name__ == "__main__":
    ensure_config_table()

def load_config(config_path):
    config = {}
    if not Path(config_path).exists():
        return config
    try:
        conn = sqlite3.connect(config_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM config")
        rows = cursor.fetchall()
        for key, value in rows:
            config[key] = value
        conn.close()
    except Exception as e:
        print(f"Failed to load config from DB: {e}")
    return config

def save_last_opened_file(config_path, file_path):
    config = load_config(config_path)
    config["last_opened_file"] = file_path
    try:
        conn = sqlite3.connect(config_path)
        cursor = conn.cursor()
        # Insert or update the last_opened_file key
        cursor.execute("""
            INSERT INTO config (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, ("last_opened_file", file_path))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to save last opened file to DB: {e}")

def load_last_opened_file(main_window):
    config = load_config(default_db_path)
    last_file = config.get("last_opened_file", "")
    if last_file and Path(last_file).exists():
        success = main_window.log_controller.load_log_file(last_file)
        if success:
            main_window.update_table_view()
            main_window.load_column_widths()
        else:
            QMessageBox.warning(main_window, "Warning", f"Failed to load last opened file: {last_file}")

def save_window_size(db_path, width, height):
    """Save the window size to the config table in the SQLite DB."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO config (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, ("window_size", f"{width},{height}"))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to save window size: {e}")

def load_window_size(db_path):
    """Load the window size from the config table in the SQLite DB."""
    if not Path(db_path).exists():
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key=?", ("window_size",))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            try:
                width, height = map(int, row[0].split(","))
                return width, height
            except Exception as e:
                print(f"Invalid window size format in DB: {e}")
    except Exception as e:
        print(f"Failed to load window size from DB: {e}")
    return None

def save_window_geometry(db_path, x, y, width, height):
    """Save the window geometry (position and size) to the config table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO config (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, ("window_geometry", f"{x},{y},{width},{height}"))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to save window geometry: {e}")

def load_window_geometry(db_path):
    """Load the window geometry (position and size) from the config table."""
    if not Path(db_path).exists():
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key=?", ("window_geometry",))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            try:
                x, y, width, height = map(int, row[0].split(","))
                if x<0:
                    x=0
                if y<0:
                    y=0
                return x, y, width, height
            except Exception as e:
                print(f"Invalid window geometry format in DB: {e}")
    except Exception as e:
        print(f"Failed to load window geometry from DB: {e}")
    return None