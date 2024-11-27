import sys
import sqlite3

from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QApplication
from PyQt6 import uic


class CoffeView(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.find_button.clicked.connect(self.find_sorts)
        self.connection = sqlite3.connect('coffe_db')

    def find_sorts(self):
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


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = CoffeView()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())