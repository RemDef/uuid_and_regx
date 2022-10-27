import uuid
import re
import sys

import pyperclip
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton
from PyQt5.QtGui import QPalette, QTextCharFormat

from windows.main_window import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.main = Ui_MainWindow()
        self.main.setupUi(self)
        QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), self, sys.exit)


        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.oldPos = self.pos()

        self.main.minimaze_button.setStyleSheet(
            "QPushButton"
            "{border-image: url(:/images/minimaze_deactive.png);}"
            "QPushButton::hover"
            "{border-image: url(:/images/minimaze_active.png);}"
        )

        self.main.close_button.setStyleSheet(
            "QPushButton"
            "{border-image: url(:/images/close_deactive.png);}"
            "QPushButton::hover"
            "{border-image: url(:/images/close_active.png);}"
        )

        self.main.minimaze_button.clicked.connect(self.minimize)
        self.main.close_button.clicked.connect(self.close)
        self.main.get_uuid.clicked.connect(self.get_uuid)
        self.main.copy_uuid.clicked.connect(self.copy_uuid)

        self.main.copied_label.setVisible(False)
        self.main.copied_label_regex.setVisible(False)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.start_timer)
        self.timer.setInterval(1000)  # 1 sec
        self.time = 2

        self.timer_regex = QtCore.QTimer(self)
        self.timer_regex.timeout.connect(self.start_timer_regex)
        self.timer_regex.setInterval(1000)  # 1 sec
        self.time_r = 2

        self.main.get_regex.clicked.connect(self.get_regex)
        self.main.line_str.textChanged.connect(self.text_to_regex)

        self.main.space_regex.clicked.connect(self.set_space_regex)

        self.main.start_end_str_regex.clicked.connect(self.set_start_end_regex)

        self.main.number_button.clicked.connect(self.set_number_regex)
        self.main.letter_button.clicked.connect(self.set_letter_regex)

        self.main.clear_regex_button.clicked.connect(self.clear_regex_area)
        self.main.copy_regex.clicked.connect(self.copy_regex)

    def clear_regex_area(self):
        self.main.line_regex.setText('')

    def set_letter_regex(self):
        index = self.main.line_regex.textCursor().position()
        reg_text = self.main.line_regex.toPlainText()
        text_ready = reg_text[:index] + '(?P<letter>\w)' + reg_text[index:]
        self.main.line_regex.setText(text_ready)

    def set_number_regex(self):
        index = self.main.line_regex.textCursor().position()
        reg_text = self.main.line_regex.toPlainText()
        text_ready = reg_text[:index] + '(?P<number>\d+)' + reg_text[index:]
        self.main.line_regex.setText(text_ready)

    def set_start_end_regex(self):
        regex_text = self.main.line_regex.toPlainText()
        regex_text = f'^(?i:{regex_text})$'
        self.main.line_regex.setText(regex_text)

    def set_space_regex(self):
        regex_text = self.main.line_regex.toPlainText()
        regex_text = regex_text.replace('  ', ' ')
        regex_text = regex_text.replace('  ', ' ')
        regex_text = regex_text.replace(' ', '\s')
        self.main.line_regex.setText(regex_text)

    def text_to_regex(self):
        _str = self.main.line_str.text()
        self.main.line_regex.setText(_str)

    def get_regex(self):
        result_r = None
        str = self.main.line_str.text()
        regex = self.main.line_regex.toPlainText()
        if str and regex:
            try:
                result = re.search(rf'{regex}', str)
                if result:
                    result_r = result.group(0)
                self.main.line_result.setText(result_r)
            except ValueError:
                ...

    def start_timer_regex(self):
        self.time_r -= 1  # !!!
        if self.time_r < 0:
            self.timer_regex.stop()
            self.main.copied_label_regex.setVisible(False)
            self.time_r = 2

    def start_timer(self):
        self.time -= 1  # !!!
        if self.time < 0:
            self.timer.stop()
            self.main.copied_label.setVisible(False)
            self.time = 2

    def copy_regex(self):
        self.main.copied_label_regex.setVisible(True)
        self.timer_regex.start()
        regex = self.main.line_regex.toPlainText()
        pyperclip.copy(regex)

    def copy_uuid(self):
        self.main.copied_label.setVisible(True)
        self.timer.start()
        _uuid = self.main.line_uuid.text()
        pyperclip.copy(_uuid)

    def get_uuid(self):
        self.main.line_uuid.setText(f'{uuid.uuid4()}')

    def close_prog(self):
        self.close()

    def minimize(self):
        self.showMinimized()

def setMoveWindow(widget):
    """
    Позволяет перемещать окно ухватившись не только за заголовок, а за произвольный виджит (widget).
    """
    win = widget.window()
    cursorShape = widget.cursor().shape()
    moveSource = getattr(widget, "mouseMoveEvent")
    pressSource = getattr(widget, "mousePressEvent")
    releaseSource = getattr(widget, "mouseReleaseEvent")

    def press(event):
        if event.button() == QtCore.Qt.LeftButton:
            # Корекция геометрии окна: учитываем размеры рамки и заголовока
            x_korr = win.frameGeometry().x() - win.geometry().x()
            y_korr = win.frameGeometry().y() - win.geometry().y()
            # Корекция геометрии виджита: учитываем смещение относительно окна
            parent = widget
            while not parent == win:
                x_korr -= parent.x()
                y_korr -= parent.y()
                parent = parent.parent()
            move.__dict__.update(
                {"lastPoint": event.pos(), "b_move": True,
                 "x_korr": x_korr, "y_korr": y_korr})
        else:
            move.__dict__.update({"b_move": False})
            widget.setCursor(cursorShape)
        return pressSource(event)

    def move(event):
        if move.b_move:
            x = event.globalX() + move.x_korr - move.lastPoint.x()
            y = event.globalY() + move.y_korr - move.lastPoint.y()
            win.move(x, y)
            #widget.setCursor(QtCore.Qt.SizeAllCursor)
        return moveSource(event)

    def release(event):
        move.__dict__.update({"b_move": False})
        widget.setCursor(cursorShape)
        return releaseSource(event)

    setattr(widget, "mouseMoveEvent", move)
    setattr(widget, "mousePressEvent", press)
    setattr(widget, "mouseReleaseEvent", release)
    move.__dict__.update({"b_move": False})
    return widget


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    setMoveWindow(main)
    main.show()
    sys.exit(app.exec_())