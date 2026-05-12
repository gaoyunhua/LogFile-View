from PyQt5.QtWidgets import QToolBar, QAction, QStyle
from PyQt5.QtGui import QIcon

def setup_toolbar(main_window):
    toolbar = QToolBar("Ribbon Toolbar", main_window)
    main_window.addToolBar(toolbar)

    open_action = QAction(main_window.style().standardIcon(QStyle.SP_DialogOpenButton), "Open File", main_window)
    open_action.setToolTip("Open a log file")
    open_action.triggered.connect(main_window.open_file)
    toolbar.addAction(open_action)

    field_list_action = QAction(QIcon("resources/icons/fields.png"), "Field List", main_window)
    field_list_action.setToolTip("Manage field definitions")
    field_list_action.triggered.connect(main_window.open_field_list)
    if field_list_action.icon().isNull():
        field_list_action.setText("Field List")
    toolbar.addAction(field_list_action)

    regex_tester_action = QAction(QIcon("resources/icons/regex.png"), "Regex Tester", main_window)
    regex_tester_action.setToolTip("Test regular expressions")
    regex_tester_action.triggered.connect(main_window.open_regex_tester)
    if regex_tester_action.icon().isNull():
        regex_tester_action.setText("Regex Tester")
    toolbar.addAction(regex_tester_action)

    settings_action = QAction(QIcon("resources/icons/settings.png"), "Settings", main_window)
    settings_action.setToolTip("Open application settings")
    settings_action.triggered.connect(main_window.open_settings)
    if settings_action.icon().isNull():
        settings_action.setText("Settings")
    toolbar.addAction(settings_action)

    copy_action = QAction(main_window.style().standardIcon(QStyle.SP_DirLinkIcon), "Copy Data", main_window)
    copy_action.setToolTip("Copy selected data to clipboard")
    copy_action.triggered.connect(main_window.copy_selected_data)
    toolbar.addAction(copy_action)

    filter_settings_action = QAction(main_window.style().standardIcon(QStyle.SP_VistaShield), "Filter Settings", main_window)
    filter_settings_action.setToolTip("Define and apply filters")
    filter_settings_action.triggered.connect(main_window.open_filter_settings)
    toolbar.addAction(filter_settings_action)