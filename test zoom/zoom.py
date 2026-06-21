import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        pixmap = QPixmap('image/placeholder.png')
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene().addItem(self.image_item)
        self.setWindowTitle("QMainWindow WheelEvent")

    def wheelEvent(self,event):
        angle = event.angleDelta().y()
        zoomFactor = 1 + (angle/1000)
        self.scale(zoomFactor, zoomFactor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())