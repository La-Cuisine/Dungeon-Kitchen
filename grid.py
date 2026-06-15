import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGraphicsItem,
    QVBoxLayout,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QStatusBar,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsProxyWidget,
    QScrollArea,
    QScrollBar,
    QGraphicsPathItem,
)
from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QRectF, 
    QSize,
    QPointF,
    
    
)
from PySide6.QtGui import (
    QFont,
    QColor,
    QPalette,
    QBrush,
    QPen,
    QPainter,
    QPainterPath,
    QResizeEvent,
    QIcon,
    QPixmap,
    
) 

_wall = None

class Window(QMainWindow):
    def __init__(self, n , s_cell):
        super().__init__()

        self.s_cell = s_cell
        self.size = n

        self.setMinimumSize(700, 520)
        #cree une scene graphique de taille 700x520 
        self.TheVoid = QGraphicsScene()
        self.TheVoid.setSceneRect(0,0,700, 520)
        # cree un espace de "visualisation"/"rendu" de la scene
        self.view = QGraphicsView(self.TheVoid)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(QBrush(QColor("#e8e8e8ff")))
        self.view.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        

        contain = QWidget()
        
        self.root_layout = QVBoxLayout(contain)
        #root_layout.setSpacing(12)
        self.root_layout.setContentsMargins(0, 0, 0, 0)        
        self.root_layout.addWidget(self.view)
        self.setCentralWidget(contain)
        global _wall
        _wall = InvisibleWallLimit(self.TheVoid)
        
        self.TheVoid.addItem(_wall)

        self.world  = Grid(n,s_cell)
        self.TheVoid.addItem(self.world)

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        zoomFactor = 1 + (angle/1000)
        self.view.scale(zoomFactor,zoomFactor)
        return super().wheelEvent(event)
        

class Grid(QGraphicsRectItem):

    def __init__(self,n,s_cell):
        super().__init__(0,0, n* s_cell, n* s_cell)
        self.n = n
        self.s_cell = s_cell
        self.setZValue(0)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)
        for i in range(n):
            for j in range(n):
                cell = Cell(s_cell*j,s_cell*i,s_cell,s_cell)
                cell.setPen(QPen(Qt.black,0.5))
                cell.setBrush(QBrush(QColor("Red")))
                cell.setParentItem(self)
        self.atoms=self.childItems()

    

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            new_pos = value
            old_pos = self.pos()
            l = self.n
            b = []
            b.append(self.atoms[0])
            b.append(self.atoms[l-1])
            b.append(self.atoms[(l-1)*l])
            b.append(self.atoms[(l-1)*l+(l-1)])
            global _wall
            
            for i in range(len(b)):
                if i == 0:
                    j = QGraphicsRectItem(b[i].scenePos().x(),b[i].scenePos().y(),b[i].boundingRect().width(),b[i].boundingRect().height())
                    if j.collidesWithPath(_wall.path()) == True:
                        print("1111")
                        _colpos = QPointF(min(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))
                        return   _colpos
                elif i == 1:
                    j = QGraphicsRectItem(b[i].scenePos().x()+25*25-25,b[i].scenePos().y(),b[i].boundingRect().width(),b[i].boundingRect().height())
                    if j.collidesWithPath(_wall.path()) == True:
                        return QPointF(max(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))
                elif i == 2:
                    j = QGraphicsRectItem(b[i].scenePos().x(),b[i].scenePos().y()+25*25-25,b[i].boundingRect().width(),b[i].boundingRect().height())
                    if j.collidesWithPath(_wall.path()) == True:
                        return QPointF(min(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))
                elif i == 3:
                    j = QGraphicsRectItem(b[i].scenePos().x()+25*25-25,b[i].scenePos().y()+25*25-25,b[i].boundingRect().width(),b[i].boundingRect().height())
                    if j.collidesWithPath(_wall.path()) == True:
                        return QPointF(max(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))
                
            
        return super().itemChange(change, value)

    
        

class Cell(QGraphicsRectItem):

    def __init__(self, x,y,w,h):
        super().__init__(x,y,w,h)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged:
            new_pos = value
            old_pos = self.scenePos()
        return super().itemChange(change, value)

class InvisibleWallLimit(QGraphicsPathItem):

    def __init__(self,scene : QGraphicsScene):
        walls = QPainterPath()
        
        walls.addRect(scene.sceneRect().center().x(),0,1,scene.sceneRect().height())
        walls.addRect(0,scene.sceneRect().center().y(),scene.sceneRect().width(),1)
        super().__init__(walls)
        self.setZValue(0)
        self.setPen(QPen(QColor("#3700ff"), 3))
        self.setBrush(QBrush(QColor("#1100ffff")))

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = Window(25,25)
    window.show()
    sys.exit(app.exec())
        