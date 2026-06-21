from PySide6 import QtCore, QtGui, QtWidgets


class Label(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Label, self).__init__(parent)
        self.image = QtGui.QPixmap("image/placeholder.png")
        self.drawing = False
        self.lastPoint = QtCore.QPoint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(QtCore.QPoint(), self.image)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and QtCore.Qt.LeftButton and self.drawing:
            painter = QtGui.QPainter(self.image)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 3, QtCore.Qt.SolidLine))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == QtCore.Qt.LeftButton:
            self.drawing = False

    def sizeHint(self):
        return self.image.size()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = Label()
        self.textedit = QtWidgets.QTextEdit()

        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        lay = QtWidgets.QHBoxLayout(widget)
        lay.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
        lay.addWidget(self.textedit)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())