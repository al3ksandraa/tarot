import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
import random


class MeaningsWindow(QMainWindow):  # значение карт
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/meanings.ui', self)
        self.setWindowTitle('Значения карт')
        self.setWindowIcon(QIcon('pictures/icons/tarot.ico'))  # иконка окна

        self.db = sqlite3.connect("db/meanings.db")  # подключение БД
        self.cur = self.db.cursor()

        self.window_notes = NotesWindow()  # окно заметок
        self.btn_notes.clicked.connect(lambda: self.show_window(self.window_notes))

        # виджеты выбора карты
        self.senior.currentIndexChanged.connect(lambda: self.set_data(self.senior.currentIndex() - 1, 'senior_arcana'))
        self.wands.currentIndexChanged.connect(lambda: self.set_data(self.wands.currentIndex(), 'wands'))
        self.cups.currentIndexChanged.connect(lambda: self.set_data(self.cups.currentIndex(), 'cups'))
        self.swords.currentIndexChanged.connect(lambda: self.set_data(self.swords.currentIndex(), 'swords'))
        self.pentacles.currentIndexChanged.connect(lambda: self.set_data(self.pentacles.currentIndex(), 'pentacles'))

        # по умолчанию при открытии окна выводится информация об Аркане 0 (Шут)
        self.set_data(0, 'senior_arcana')
        self.senior.setCurrentIndex(1)

    def set_data(self, key, table):  # отображение информации о карте
        # если выбрана карта (в виджете ComboBox первый элемент пустой)
        if key != -1 and table == 'senior_arcana' or \
           key != 0 and table != 'senior_arcana':

            name = self.cur.execute(f"""SELECT name FROM {table}
                WHERE key = {key}""").fetchone()  # название карты
            description = self.cur.execute(f"""SELECT description FROM {table}
                WHERE key = {key}""").fetchone()  # описание
            direct = self.cur.execute(f"""SELECT direct FROM {table}
                WHERE key = {key}""").fetchone()  # значение в прямом положении
            inverted = self.cur.execute(f"""SELECT inverted FROM {table}
                WHERE key = {key}""").fetchone()  # значение в перевернутом положении

            # изображение карты
            self.image.setPixmap(QPixmap(f'pictures/{table}/{key}.png'))

            self.name.setText(*name)
            self.description.setPlainText(*description)
            self.direct.setHtml(*direct)
            self.inverted.setHtml(*inverted)

            # отображение заметок к карте (если окно заметок открыто)
            self.window_notes.set_notes(key, table)

            # обнуление остальных ComboBox-ов
            if table != 'senior_arcana':
                self.senior.setCurrentIndex(0)
            if table != 'wands':
                self.wands.setCurrentIndex(0)
            if table != 'cups':
                self.cups.setCurrentIndex(0)
            if table != 'swords':
                self.swords.setCurrentIndex(0)
            if table != 'pentacles':
                self.pentacles.setCurrentIndex(0)

            if table == 'senior_arcana':
                self.senior.setCurrentIndex(key + 1)
            elif table == 'wands':
                self.wands.setCurrentIndex(key)
            elif table == 'cups':
                self.cups.setCurrentIndex(key)
            elif table == 'swords':
                self.swords.setCurrentIndex(key)
            elif table == 'pentacles':
                self.pentacles.setCurrentIndex(key)

    def show_window(self, window):
        window.show()


class NotesWindow(QMainWindow):  # заметки к карте
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/notes.ui', self)
        self.setWindowTitle('Заметки')
        self.setWindowIcon(QIcon('pictures/icons/notes.ico'))  # иконка окна

        self.db = sqlite3.connect("db/meanings.db")  # подключение БД
        self.cur = self.db.cursor()

        self.btn_save.clicked.connect(self.save)  # кнопка сохранения

        self.key = None  # номер карты
        self.table = ''  # таблица/группа карты

    def save(self):  # сохранение данных в БД
        if self.table:
            text = self.text.toPlainText()

            self.cur.execute('UPDATE ' + self.table + ' SET notes = "' + text + '" WHERE key = ' + str(self.key))
            self.db.commit()

    def set_notes(self, key, table):  # отображение заметок (при выборе карты в окне значений)
        # сохранение номера и таблицы карты
        self.key = key
        self.table = table

        notes = self.cur.execute(f"""SELECT notes FROM {table}
            WHERE key = {key}""").fetchone()

        self.text.setPlainText(str(*notes))  # отображение заметок


class DayCardWindow(QMainWindow):  # карта дня
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/day_card.ui', self)
        self.setWindowTitle('Карта дня')
        self.setWindowIcon(QIcon('pictures/icons/tarot.ico'))  # иконка окна

        self.db = sqlite3.connect("db/meanings.db")  # подключение БД
        self.cur = self.db.cursor()

        self.random_card()  # при создании окна сразу будет выбираться случайная карта

        # при нажатии на кнопку карта дня выберется заново
        self.btn_new.clicked.connect(self.random_card)

    def random_card(self):
        # случайный выбор группы карт
        table = random.choice(['senior_arcana', 'wands', 'cups', 'swords', 'pentacles'])
        # выбор случайной карты
        if table == 'senior_arcana':
            key = random.randint(0, 21)  # старших арканов 22, а карт в других группах по 14
        else:
            key = random.randint(1, 14)

        self.image.setPixmap(QPixmap(f'pictures/{table}/{key}.png'))  # изображение карты

        # название и значение карты (из базы данных)
        name = self.cur.execute(f"""SELECT name FROM {table}
            WHERE key = {key}""").fetchone()
        meaning = self.cur.execute(f"""SELECT day_card FROM {table}
            WHERE key = {key}""").fetchone()

        self.name.setText(*name)
        self.meaning.setPlainText(*meaning)

        # при нажатии на кнопку откроется полное описание карты (класс MeaningsWindow)
        self.btn_description.clicked.connect(lambda: self.show_info(table, key))

    def show_info(self, table, key):
        ex.window_meanings.set_data(key, table)
        ex.window_meanings.show()


class LayoutsWindow(QMainWindow):  # схемы некоторых раскладов
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/layouts.ui', self)
        self.setWindowTitle('Расклады')
        self.setWindowIcon(QIcon('pictures/icons/tarot.ico'))  # иконка окна

        self.db = sqlite3.connect("db/meanings.db")  # подключение БД
        self.cur = self.db.cursor()

        self.choice.currentIndexChanged.connect(lambda: self.set_data(self.choice.currentIndex() + 1))

        # по умолчанию
        self.set_data(1)
        self.choice.setCurrentIndex(0)

    def set_data(self, key):
        self.image.setPixmap(QPixmap(f'pictures/layouts/{key}.png'))
        data = self.cur.execute(f'''SELECT data FROM layouts
                  WHERE key = {key}''').fetchone()
        self.text.setPlainText(*data)


class InfoWindow(QMainWindow):  # справочная информация
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/info.ui', self)
        self.setWindowTitle('О Таро')
        self.setWindowIcon(QIcon('pictures/icons/tarot.ico'))  # иконка окна

        self.db = sqlite3.connect("db/meanings.db")  # подключение БД
        self.cur = self.db.cursor()

        self.choice.currentIndexChanged.connect(lambda: self.set_data(self.choice.currentIndex() + 1))

        # по умолчанию
        self.set_data(1)
        self.choice.setCurrentIndex(0)

    def set_data(self, key):
        data = self.cur.execute(f'''SELECT data FROM info
                          WHERE key = {key}''').fetchone()
        self.text.setHtml(*data)


class MainWindow(QMainWindow):  # основное окно
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main.ui', self)
        self.setWindowTitle('Справочник по картам Таро')
        self.setWindowIcon(QIcon('pictures/icons/tarot.ico'))  # иконка окна

        # self.setWindowFlags(QtCore.Qt.WindowType.MSWindowsFixedSizeDialogHint)

        self.window_meanings = MeaningsWindow()  # окно значений карт
        self.window_day_card = DayCardWindow()  # окно "карта дня"
        self.window_layouts = LayoutsWindow()  # окно с раскладами
        self.window_info = InfoWindow()  # окно со справочной информацией о картах

        self.image.setPixmap(QPixmap(f'pictures/main_window.png'))
        self.btn_meaning.clicked.connect(lambda: self.show_window(self.window_meanings))
        self.btn_day_card.clicked.connect(lambda: self.show_window(self.window_day_card))
        self.btn_layouts.clicked.connect(lambda: self.show_window(self.window_layouts))
        self.btn_info.clicked.connect(lambda: self.show_window(self.window_info))

    def show_window(self, window):  # отображение окна при нажатии на кнопку
        window.show()

    def closeEvent(self, event):  # при закрытии основного окна завершает работу вся программа
        app.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
