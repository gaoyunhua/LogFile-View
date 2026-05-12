import sys
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from models.log_model import LogModel
from models.field_model import FieldModel
from controllers.log_controller import LogController
from controllers.field_controller import FieldController


def main():
    app = QApplication(sys.argv)

    # Initialize models
    log_model = LogModel()
    field_model = FieldModel()

    # Initialize controllers
    log_controller = LogController(log_model)
    field_controller = FieldController(field_model)

    # Initialize main window
    main_window = MainWindow(log_controller, field_controller)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
