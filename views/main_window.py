import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QMenuBar, QAction, QFileDialog,
    QMessageBox, QToolBar, QStyle, QHeaderView, QLineEdit
)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from models.LogFilterProxyModel import LogFilterProxyModel
from models.log_table_model import LogTableModel  # Updated import
from models.log_model import LogModel
from models.utils import get_header_data


from views.field_list import FieldList
from views.reg_tester import RegexTester
from views.settings_dialog import SettingsDialog
from views.FilterSettingsDialog import FilterSettingsDialog
from views.field_editor import FieldEditor
from views.custom_header_view import CustomHeaderView
import pandas as pd
import re

from .ui_setup import setup_ui
from .menu_setup import setup_menu
from .toolbar_setup import setup_toolbar
from .file_utils import (
    load_last_opened_file,
    save_last_opened_file,
    load_config,
    save_window_geometry,
    load_window_geometry,
)

from models.field_model import default_db_path

class MainWindow(QMainWindow):
#    CONFIG_PATH = "resources/config.json"

    def __init__(self, log_controller, field_controller):
        super().__init__()
        self.setWindowTitle("Log Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.log_controller = log_controller
        self.field_controller = field_controller


        setup_ui(self)
        # setup_menu(self)  # <-- Remove or comment out this line
        self.init_menu()    # <-- Add this line to use your own menu setup
        setup_toolbar(self)

        # Load filter settings on startup
        settings = self.proxy_model.load_filter_settings()
        self.proxy_model.setFilterCriteria(settings)

        # Load the last opened file and fields on startup
        load_last_opened_file(self)
        self.refresh_data()

        # After setting the model in __init__ or after loading a file
        self.load_column_widths()

        # Restore window geometry from config db if available
        geometry = load_window_geometry(default_db_path)
        if geometry:
            x, y, width, height = geometry
            self.setGeometry(x, y, width, height)
        else:
            self.setGeometry(100, 100, 800, 600)

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Table view
        self.table_view = QTableView()
        layout.addWidget(self.table_view)

        # Initialize the models and set them for the table view
        log_data = [{"raw": "Log entry 1"}, {"raw": "Log entry 2"}]
        visible_fields = {"field1": "Field 1", "field2": "Field 2"}
        self.log_table_model = LogTableModel(log_data, visible_fields, self)
        self.proxy_model = LogFilterProxyModel(db_path=default_db_path, parent=self)
        self.proxy_model.setSourceModel(self.log_table_model)  # Set the source model

        # Set the proxy model for the table view
        self.table_view.setModel(self.proxy_model)

        # Configure the horizontal header
        custom_header = CustomHeaderView(Qt.Horizontal, self.table_view)
        self.table_view.setHorizontalHeader(custom_header)
        header = self.table_view.horizontalHeader()
        header.sectionDoubleClicked.connect(self.open_field_editor)  # Open field editor on double-click
        header.sectionResized.connect(lambda: self.save_column_widths())

        # Ensure the horizontal header is visible
        header.setVisible(True)

        self.table_view.setHorizontalHeader(header)

        # Enable word wrapping and adjust row height
        self.table_view.setWordWrap(True)
        # self.table_view.resizeRowsToContents()  # Adjust row height to fit wrapped text

    def init_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        export_action = QAction("Export to Excel", self)
        export_action.triggered.connect(self.export_to_excel)
        file_menu.addAction(export_action)

        copy_action = QAction("Copy Selected Data", self)
        copy_action.triggered.connect(self.copy_selected_data)
        file_menu.addAction(copy_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        field_list_action = QAction("Field List", self)
        field_list_action.triggered.connect(self.open_field_list)
        tools_menu.addAction(field_list_action)

        regex_tester_action = QAction("Regex Tester", self)
        regex_tester_action.triggered.connect(self.open_regex_tester)
        tools_menu.addAction(regex_tester_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)

        filter_settings_action = QAction("Filter Settings", self)
        filter_settings_action.triggered.connect(self.open_filter_settings)
        tools_menu.addAction(filter_settings_action)

        # --- DB menu for SQLite settings ---
        db_menu = menubar.addMenu("Field Settings")

        backup_db_action = QAction("Backup Field Settings", self)
        backup_db_action.triggered.connect(self.backup_db_settings)
        db_menu.addAction(backup_db_action)

        load_db_action = QAction("Load Field Settings", self)
        load_db_action.triggered.connect(self.load_db_settings)
        db_menu.addAction(load_db_action)

        refresh_db_action = QAction("Refresh Field Settings", self)
        refresh_db_action.triggered.connect(self.refresh_db_settings)
        db_menu.addAction(refresh_db_action)

    def init_ribbon_toolbar(self):
        """Initialize the ribbon-style toolbar."""
        toolbar = QToolBar("Ribbon Toolbar", self)
        self.addToolBar(toolbar)

        # Add Open File button with system icon
        open_action = QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton), "Open File", self)
        open_action.setToolTip("Open a log file")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        # Add Field List button
        field_list_action = QAction(QIcon("resources/icons/fields.png"), "Field List", self)
        field_list_action.setToolTip("Manage field definitions")
        field_list_action.triggered.connect(self.open_field_list)
        if field_list_action.icon().isNull():  # Check if the icon is missing
            field_list_action.setText("Field List")
        toolbar.addAction(field_list_action)

        # Add Regex Tester button
        regex_tester_action = QAction(QIcon("resources/icons/regex.png"), "Regex Tester", self)
        regex_tester_action.setToolTip("Test regular expressions")
        regex_tester_action.triggered.connect(self.open_regex_tester)
        if regex_tester_action.icon().isNull():  # Check if the icon is missing
            regex_tester_action.setText("Regex Tester")
        toolbar.addAction(regex_tester_action)

        # Add Settings button
        settings_action = QAction(QIcon("resources/icons/settings.png"), "Settings", self)
        settings_action.setToolTip("Open application settings")
        settings_action.triggered.connect(self.open_settings)
        if settings_action.icon().isNull():  # Check if the icon is missing
            settings_action.setText("Settings")
        toolbar.addAction(settings_action)

        # Add Copy Data button with system icon
        copy_action = QAction(self.style().standardIcon(QStyle.SP_DirLinkIcon), "Copy Data", self)
        copy_action.setToolTip("Copy selected data to clipboard")
        copy_action.triggered.connect(self.copy_selected_data)
        toolbar.addAction(copy_action)

        # Add Filter Settings button with system icon
        filter_settings_action = QAction(self.style().standardIcon(QStyle.SP_VistaShield), "Filter Settings", self)
        filter_settings_action.setToolTip("Define and apply filters")
        filter_settings_action.triggered.connect(self.open_filter_settings)
        toolbar.addAction(filter_settings_action)



    def open_file(self):
        """Open a log file."""
        # Get last opened file from config
        config = load_config(default_db_path)
        last_file = config.get("last_opened_file", "")
        initial_dir = ""
        if last_file and Path(last_file).exists():
            initial_dir = str(Path(last_file).parent)
        # Use initial_dir as the starting directory for the dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Log File",
            initial_dir,
            "Log Files (*.log *.txt);;All Files (*)"
        )
        if file_path:
            success = self.log_controller.load_log_file(file_path)
            if not success:
                QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}")
            else:
                QMessageBox.information(self, "Success", f"File loaded successfully: {file_path}")
                self.update_table_view()  # Update the table view with the loaded data
                #self.save_last_opened_file(file_path)  # Save the file path to the configuration
                save_last_opened_file(default_db_path, file_path)  # Save the file path to the database

                # Update the window title to include the file name and directory
                self.setWindowTitle(f"Log Viewer - {file_path}")

    def open_field_list(self):
        """Open the Field List dialog."""
        dialog = FieldList(self.field_controller, self)
        dialog.fields_updated.connect(self.refresh_data)  # Connect signal to refresh data
        dialog.exec_()

    def refresh_data(self):
        """Refresh the table view data."""
        # Retrieve all fields from the FieldController
        fields = self.field_controller.get_all_fields()

        # Pass all fields to the LogController
        log_data = self.log_controller.get_logs(fields)

        # Filter fields based on visibility for display
        visible_fields = {name: data for name, data in fields.items() if data.get("visibility", False)}

        # Update the table model with visible fields
        self.log_table_model = LogTableModel(log_data, visible_fields, self)
        self.proxy_model.setSourceModel(self.log_table_model)  # Update the proxy model's source model

        # Notify the view that the data has changed
        self.log_table_model.layoutChanged.emit()

        # Set the "Raw Log" column width to a fixed value (e.g., 10 pixels)

        # Adjust column widths for other columns
#        header = self.table_view.horizontalHeader()
#        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Ensure "Raw Log" column remains fixed
#        self.table_view.resizeColumnsToContents()  # Resize other columns
#        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Restore "Raw Log" column to interactive mode
        # Check the current width of the "Raw Log" column and set it to 10 if it exceeds 100
        raw_log_column_width = self.table_view.columnWidth(0)  # Get the width of the "Raw Log" column
        if raw_log_column_width > 100:
            self.table_view.setColumnWidth(0, 10)  # Set the width to 10 pixels if it exceeds 100


        # Adjust row heights dynamically based on data, except for the "Raw Log" column
        for row in range(self.log_table_model.rowCount()):
            max_height = 25  # Default row height
            for col in range(1, self.log_table_model.columnCount()):  # Skip the "Raw Log" column (assumed to be column 0)
                index = self.log_table_model.index(row, col)
                text = self.log_table_model.data(index, Qt.DisplayRole)
                if text:
                    font_metrics = self.table_view.fontMetrics()
                    text_rect = font_metrics.boundingRect(text)
                    max_height = max(max_height, text_rect.height() + 10)  # Add padding
            self.table_view.setRowHeight(row, max_height)

    def open_regex_tester(self):
        """Open the Regex Tester dialog."""
        dialog = RegexTester(self)
        dialog.exec_()

    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(parent=self)
        if dialog.exec_():
            QMessageBox.information(self, "Settings", "Settings saved successfully.")

    def update_table_view(self):
        """Update the table view with the loaded log data."""
        # Retrieve all fields from the FieldController
        fields = self.field_controller.get_all_fields()

        # Pass all fields to the LogController
        log_data = self.log_controller.get_logs(fields)

        # Filter fields based on visibility for display
        visible_fields = {name: data for name, data in fields.items() if data.get("visibility", False)}

        # Update the table model with visible fields
        self.log_table_model = LogTableModel(log_data, visible_fields, self)
        self.table_view.setModel(self.log_table_model)

        # Restore column widths
        self.load_column_widths()   # <--- REMOVE THIS LINE

    def export_to_excel(self):
        """Export the data currently displayed in the table view to an Excel file, excluding the raw log column."""
        # Get the model from the table view
        model = self.proxy_model.sourceModel()
        if model is None:
            QMessageBox.warning(self, "Warning", "No data to export.")
            return

        # Convert the model data to a list of dictionaries, excluding the "Raw Log" column
        data = []
        for row in range(model.rowCount()):
            row_data = {}
            for column in range(1, model.columnCount()):  # Start from column 1 to skip "Raw Log"
                header = model.headerData(column, Qt.Horizontal, Qt.DisplayRole)
                value = model.data(model.index(row, column), Qt.DisplayRole)
                row_data[header] = value
                #print(header)
            data.append(row_data)

        # Convert the data to a DataFrame
        df = pd.DataFrame(data)
        #print("Exporting data:", data)
        # Open a file dialog to select the save location
        def clean_cell(val):
            if isinstance(val, str):
                # Remove non-printable/control characters (except \t, \n, \r)
                return re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u4e00-\u9fff]', '', val)
            return val

        df = df.map(clean_cell)        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)")
        if not file_path:
            return  # User canceled the save dialog

        # Ensure the file has the correct extension
        if not file_path.endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            # Save the DataFrame to an Excel file
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Success", f"Data exported successfully to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {e}")

    def save_column_widths(self):
        """Save the column widths and display order to the fields table in log_viewer.db, skipping the 'Raw Log' column."""
        header = self.table_view.horizontalHeader()
        model = self.proxy_model.sourceModel()
        if model is None:
            return

        # Use the header text to match the field name for each column
        for visual_index in range(1, header.count()):  # Skip 'Raw Log' at index 0
            logical_index = header.logicalIndex(visual_index)
            field_name = model.headerData(logical_index, Qt.Horizontal, Qt.DisplayRole)
            if not field_name or field_name == "Raw Log":
                continue
            column_width = self.table_view.columnWidth(logical_index)
            display_order = visual_index  # displayorder starts from 1
            field_data = self.field_controller.get_field_data(field_name)
            self.field_controller.field_model.update_field(
                old_name=field_name,
                new_name=field_name,
                regex=field_data.get("regex", ""),
                visibility=field_data.get("visibility", True),
                sorted_field=field_data.get("sorted", False),
                displayorder=display_order,
                columnwidth=column_width
            )

    def load_column_widths(self):
        """Load the column widths and display order from the fields table in log_viewer.db, skipping the 'Raw Log' column."""
        # Get all fields ordered by displayorder
        fields = self.field_controller.get_all_fields()
        # Sort by displayorder
        sorted_fields = sorted(fields.items(), key=lambda item: item[1].get("displayorder", 0))
        for idx, (field_name, field_data) in enumerate(sorted_fields, start=1):  # start=1 to skip 'Raw Log'
            # Set column width for each field (column 0 is 'Raw Log')
            self.table_view.setColumnWidth(idx, field_data.get("columnwidth", 100))
        # Optionally, set the 'Raw Log' column width to a fixed value
        self.table_view.setColumnWidth(0, 10)




    def closeEvent(self, event):
        """Handle the close event to save settings."""
        self.save_column_widths()

        # Save the normal geometry (includes decorations, excludes maximized/minimized state)
        window_geometry = self.geometry()

        save_geom = window_geometry
        x = save_geom.x()
        y = save_geom.y()
        width = save_geom.width()
        height = save_geom.height()

        save_window_geometry(default_db_path, x, y, width, height)
        super().closeEvent(event)



    def open_field_editor(self, section_index):
        """Open the field item edit window for the clicked column."""
        if section_index == 0:
            QMessageBox.warning(self, "Warning", "The 'Raw Log' column cannot be edited.")
            return

        # Get the field name corresponding to the clicked column
        field_names = list(self.log_table_model.visible_fields.keys())
        if section_index - 1 < len(field_names):
            field_name = field_names[section_index - 1]
            # Open the field editor dialog
            editor = FieldEditor(self)
            field_data = self.field_controller.get_field_data(field_name)
            #QMessageBox.information(self, "Success", f"Field '{field_data}' updated successfully.")
            editor.set_field_data(
                field_name=field_name,
                regex=field_data.get("regex", ""),
                visibility=field_data.get("visibility", True),
                sorted_field=field_data.get("sorted", False),
            )

            if editor.exec_():
                # Get updated field data from the editor
                updated_data = editor.get_field_data()
                self.field_controller.update_field(
                    old_name=field_name,
                    new_name=updated_data["field_name"],
                    regex=updated_data["regex"],
                    visibility=updated_data["visibility"],
                    sorted_field=updated_data["sorted"],
                )
                #QMessageBox.information(self, "Success", f"Field '{updated_data}' updated successfully.")
                self.refresh_data()  # Refresh the table view

    def copy_selected_data(self):
        """Copy all selected data from the main table to the clipboard."""
        model = self.proxy_model.sourceModel()
        if not model:
            QMessageBox.warning(self, "Warning", "No data to copy.")
            return

        # Get the selected indexes
        selected_indexes = self.table_view.selectionModel().selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "No data selected.")
            return

        # Sort the selected indexes by row and column
        selected_indexes = sorted(selected_indexes, key=lambda index: (index.row(), index.column()))

        # Build the data string
        copied_data = ""
        current_row = -1
        for index in selected_indexes:
            if index.row() != current_row:
                # Add a newline for a new row
                if current_row != -1:
                    copied_data += "\n"
                current_row = index.row()
            else:
                # Add a tab between columns
                copied_data += "\t"
            copied_data += str(model.data(index, Qt.DisplayRole))

        # Copy the data to the clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(copied_data)
        QMessageBox.information(self, "Success", "Selected data copied to clipboard.")

    def on_search_text_changed(self, text):
        """Filter rows based on quick search text."""
        self.proxy_model.setSearchText(text)

    def on_column_filter_applied(self, column_index, allowed_values):
        """Apply a column filter from the header dropdown."""
        self.proxy_model.setColumnFilter(column_index, allowed_values)

    def apply_filter(self):
        """Apply the filter text to the proxy model."""
        filter_text = self.filter_input.text()
        self.proxy_model.setFilterText(filter_text)

    def open_filter_settings(self):
        """Open the Filter Settings dialog."""
        # Retrieve the list of field names from the field controller
        field_names = list(self.field_controller.get_all_fields().keys())

        # Pass the field names to the FilterSettingsDialog
        dialog = FilterSettingsDialog(self.proxy_model, field_names, self)
        dialog.load_settings()  # Load existing settings
        if dialog.exec_():
            # Apply the new filter settings
            settings = self.proxy_model.load_filter_settings()
            self.proxy_model.setFilterCriteria(settings)

    def headerData(self, section, orientation, role):
        """Provide header data for the table."""
        return get_header_data(section, orientation, role, self.visible_fields)

    def backup_db_settings(self):
        """Backup the SQLite DB settings file."""
        src_path = default_db_path
        file_path, _ = QFileDialog.getSaveFileName(self, "Backup DB Settings", "", "SQLite DB (*.db)")
        if not file_path:
            return
        try:
            import shutil
            shutil.copyfile(src_path, file_path)
            QMessageBox.information(self, "Success", f"DB settings backed up to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to backup DB settings: {e}")

    def load_db_settings(self):
        """Load/restore the SQLite DB settings file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load DB Settings", "", "SQLite DB (*.db)")
        if not file_path:
            return
        try:
            import shutil
            shutil.copyfile(file_path, default_db_path)
            # Re-initialize the proxy model to use the new DB
            self.proxy_model = LogFilterProxyModel(db_path=default_db_path, parent=self)
            self.proxy_model.setSourceModel(self.log_table_model)
            self.table_view.setModel(self.proxy_model)
            # Reload filter settings and refresh data
            settings = self.proxy_model.load_filter_settings()
            self.proxy_model.setFilterCriteria(settings)
            self.refresh_data()
            QMessageBox.information(self, "Success", f"DB settings loaded from {file_path} and UI refreshed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load DB settings: {e}")

    def refresh_db_settings(self):
        """Reload settings from the SQLite DB."""
        # Reload filter settings and refresh data
        settings = self.proxy_model.load_filter_settings()
        self.proxy_model.setFilterCriteria(settings)
        self.refresh_data()
        QMessageBox.information(self, "Refreshed", "DB settings refreshed.")