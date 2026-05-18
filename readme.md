# Log File Viewer

A PyQt5 desktop application for parsing, viewing, and analyzing log files using user-defined regex fields.

## Features

- **Log Viewing** - Open `.log` or `.txt` files and display raw log lines in a table
- **Field Extraction** - Define named fields with regular expressions to extract structured data columns from each log line
- **Field Management** - Add, edit, delete, reorder, and resize field columns; control visibility per field
- **Filtering** - Apply numeric or string range filters on any extracted field
- **Sorted Fields** - Mark fields as "sorted" to filter out lines that don't match at least one sorted field's regex
- **Regex Tester** - Interactive dialog to test regex patterns against sample text
- **Export to Excel** - Export visible table data (excluding raw column) to `.xlsx`
- **Copy to Clipboard** - Copy selected table cells
- **Persistent Settings** - SQLite database stores field definitions, column widths, display order, filter settings, last opened file, and window geometry
- **Custom Header** - Movable, resizable columns with word-wrap support
- **DB Backup/Restore** - Backup and load field settings from external `.db` files

## Architecture

The project follows the MVC (Model-View-Controller) pattern:

```
LogFileView/
├── main.py                       # Entry point
├── controllers/
│   ├── log_controller.py         # Log file loading, regex extraction, sorting
│   └── field_controller.py       # Field CRUD operations
├── models/
│   ├── log_model.py              # Raw log data storage
│   ├── field_model.py            # Field definitions (SQLite persistence)
│   ├── log_table_model.py        # Qt table model for display
│   ├── LogFilterProxyModel.py    # Qt proxy model for filtering
│   └── utils.py                  # Header data utility
├── views/
│   ├── main_window.py            # Main application window
│   ├── ui_setup.py               # UI initialization
│   ├── menu_setup.py             # Menu bar setup
│   ├── toolbar_setup.py          # Toolbar setup
│   ├── file_utils.py             # Config load/save utilities
│   ├── field_list.py             # Field definitions list dialog
│   ├── field_editor.py           # Single field edit dialog
│   ├── reg_tester.py             # Regex tester dialog
│   ├── settings_dialog.py        # Application settings dialog
│   ├── FilterSettingsDialog.py   # Filter settings dialog
│   └── custom_header_view.py     # Custom table header with word-wrap
├── utils/
│   └── regex_utils.py            # Regex matching utility
├── resources/
│   └── icons/                    # Toolbar icons
├── database/
│   └── schema.sql                # SQLite schema reference
└── requirements.txt              # Python dependencies
```

## Requirements

- Python 3.8+
- Windows (primary target platform)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gaoyunhua/LogFile-View.git
   cd LogFile-View
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### Basic Workflow

1. **Open a log file** - Use `File > Open` or the toolbar button to load a `.log` or `.txt` file
2. **Define fields** - Use `Tools > Field List` to create regex-based field definitions
3. **View extracted data** - Fields marked as visible will appear as columns in the main table
4. **Filter data** - Use `Tools > Filter Settings` to apply range filters on any field
5. **Export results** - Use `File > Export to Excel` to save the current view as `.xlsx`

### Field Properties

| Property | Description |
|----------|-------------|
| Field Name | Unique identifier for the field |
| Regex | Regular expression to extract data from each log line |
| Display | Whether the field is shown as a column |
| Sorted | If enabled, lines not matching this regex are excluded |

## Building Executable

To build a standalone Windows executable using PyInstaller:
```bash
pyinstaller main.spec
```

The output will be in the `dist/` directory.

## Author

Sam Gao (sam.gao@sharkninja.com)
