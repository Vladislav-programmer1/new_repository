import sys
import sqlite3

from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QApplication
from PyQt6.QtGui import QAction

from release.AddEditCoffee import AddEditCoffee
from main_form import Ui_MainWindow


class CoffeView(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.set_interface()

        self.find_button.clicked.connect(self.find_sorts)
        self.connection = sqlite3.connect('../data/coffe_db')

        self.find_sorts()

    def set_interface(self):
        self.setupUi(self)
        menu = self.menuBar().addMenu('Действия')

        add_coffe_action = QAction('Окно добавления кофе', self)
        add_coffe_action.triggered.connect(self.open_add_edit_coffe_window)
        menu.addAction(add_coffe_action)

        main_action = QAction('Вернуться на главную страницу', self)
        main_action.triggered.connect(self.return_to_main)
        menu.addAction(main_action)

    def find_sorts(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

        name = '%' + self.name.text() + '%'
        cursor = self.connection.cursor()
        items = cursor.execute("""SELECT * FROM coffe WHERE
                                                    variety LIKE ?
                                                 """, (name,))
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([description[0] for description in
                                                    cursor.description])

        for i, row in enumerate(items):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, item in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(item)))

        self.tableWidget.resizeColumnsToContents()

    def open_add_edit_coffe_window(self):
        window = AddEditCoffee(self.connection)
        self.setCentralWidget(window)
        self.menuBar().show()

    def return_to_main(self):
        self.setCentralWidget(None)
        self.set_interface()

        self.find_sorts()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = CoffeView()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())