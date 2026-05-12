from PyQt5.QtWidgets import QAction

def setup_menu(main_window):
    menubar = main_window.menuBar()

    file_menu = menubar.addMenu("File")
    open_action = QAction("Open", main_window)
    open_action.triggered.connect(main_window.open_file)
    file_menu.addAction(open_action)

    export_action = QAction("Export to Excel", main_window)
    export_action.triggered.connect(main_window.export_to_excel)
    file_menu.addAction(export_action)

    copy_action = QAction("Copy Selected Data", main_window)
    copy_action.triggered.connect(main_window.copy_selected_data)
    file_menu.addAction(copy_action)

    tools_menu = menubar.addMenu("Tools")
    field_list_action = QAction("Field List", main_window)
    field_list_action.triggered.connect(main_window.open_field_list)
    tools_menu.addAction(field_list_action)

    regex_tester_action = QAction("Regex Tester", main_window)
    regex_tester_action.triggered.connect(main_window.open_regex_tester)
    tools_menu.addAction(regex_tester_action)

    settings_action = QAction("Settings", main_window)
    settings_action.triggered.connect(main_window.open_settings)
    tools_menu.addAction(settings_action)

    filter_settings_action = QAction("Filter Settings", main_window)
    filter_settings_action.triggered.connect(main_window.open_filter_settings)
    tools_menu.addAction(filter_settings_action)