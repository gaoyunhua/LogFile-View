from PyQt5.QtWidgets import QTableView, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from models.LogFilterProxyModel import LogFilterProxyModel
from models.log_table_model import LogTableModel
from views.filterable_header_view import FilterableHeaderView

def setup_ui(main_window):
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    table_view = QTableView()
    layout.addWidget(table_view)

    log_data = [{"raw": "Log entry 1"}, {"raw": "Log entry 2"}]
    visible_fields = {"field1": "Field 1", "field2": "Field 2"}
    log_table_model = LogTableModel(log_data, visible_fields, main_window)
    proxy_model = LogFilterProxyModel(db_path="settings.db", parent=main_window)
    proxy_model.setSourceModel(log_table_model)

    table_view.setModel(proxy_model)
    table_view.setSortingEnabled(True)
    table_view.setAlternatingRowColors(True)
    table_view.setStyleSheet("QTableView { alternate-background-color: #f5f5f5; }")

    custom_header = FilterableHeaderView(Qt.Horizontal, table_view)
    table_view.setHorizontalHeader(custom_header)
    header = table_view.horizontalHeader()
    header.sectionDoubleClicked.connect(main_window.open_field_editor)
    header.filterApplied.connect(main_window.on_column_filter_applied)
    header.setSortIndicatorShown(True)
    header.setVisible(True)
    table_view.setHorizontalHeader(header)
    table_view.setWordWrap(True)

    main_window.table_view = table_view
    main_window.log_table_model = log_table_model
    main_window.proxy_model = proxy_model