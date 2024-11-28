from collections import defaultdict
import sqlite3
import sys

from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QApplication, QMessageBox, QInputDialog

from addEditCoffeeForm import Ui_Form


def get_coffe_information(parent, title, text, type_of_data):
    information, ok = type_of_data(parent, title, text)
    if not ok:
        raise EmptyUserInputError
    return information


class EmptyUserInputError(Exception):
    pass


class AddEditCoffee(QWidget, Ui_Form):
    def __init__(self, connection):
        super().__init__()
        self.setupUi(self)

        self.types = defaultdict(list)
        self.changed = False
        self.connection = connection
        self.find_button.clicked.connect(self.make_table)
        self.add_button.clicked.connect(self.add_coffe)
        self.save_button.clicked.connect(self.save_changes)

        self.table.itemChanged.connect(self.item_changed)

    def make_table(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        name = '%' + self.name.text() + '%'
        cursor = self.connection.cursor()
        items = cursor.execute("""SELECT * FROM coffe WHERE
                                  variety LIKE ?
                               """, (name,))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([description[0] for description in
                                              cursor.description])

        for i, row in enumerate(items):
            self.types[i] = row
            self.table.setRowCount(self.table.rowCount() + 1)
            self.changed = False
            for j, item in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(item)))

        self.table.resizeColumnsToContents()
        self.changed = True

    def save_changes(self):
        answer = QMessageBox.question(
            self, "Подтверждение", "Вы точно желаете сохранить все изменения",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.connection.commit()

    def add_coffe(self):
        try:
            title = get_coffe_information(
                self, 'Название', 'Введите название кофе', QInputDialog.getText
            )

            degree_of_roasting = get_coffe_information(
                self, 'Степень прожарки', 'Введите степень прожарки', QInputDialog.getInt
            )

            in_grains = get_coffe_information(
                self, 'Молотое/в зернах', 'Молотое/в зернах', QInputDialog.getInt
            )

            taste_description = get_coffe_information(
                self, 'Описание вкуса', 'Введите описание вкуса', QInputDialog.getText
            )

            price = get_coffe_information(
                self, 'Цена', 'Введите цену', QInputDialog.getDouble
            )

            volume = get_coffe_information(
                self, 'Объем', 'Введите объем', QInputDialog.getInt
            )

            new_id = self.connection.cursor().execute(
                """SELECT MAX(id) + 1 FROM coffe"""
            ).fetchone()[0]
            self.connection.cursor().execute(
                """INSERT INTO coffe VALUES(?, ?, ?, ?, ?, ?, ?)""",
                (new_id, title, degree_of_roasting, in_grains,
                 taste_description, price, volume))
            self.connection.commit()
        except EmptyUserInputError:
            return

    def item_changed(self, item):
        if not self.changed:
            return

        row, column = item.row(), item.column()

        actions = {0: lambda x: x,
                   1: lambda x: x,
                   2: lambda x: int(x),
                   3: lambda x: int(x),
                   4: lambda x: x,
                   5: lambda x: float(x),
                   6: lambda x: float(x)}

        field = self.table.horizontalHeaderItem(column).text()
        try:
            self.connection.cursor().execute(
                f"""UPDATE coffe SET {field} = ?""",
                (actions[column](item.text()),))
        except Exception as mistake:
            message = QMessageBox(self)
            message.setText("Сожалеем, вы ввели неверные данные\n"
                            "Повторите попытку")
            message.setIcon(QMessageBox.Icon.Information)
            message.exec()
            self.make_table()