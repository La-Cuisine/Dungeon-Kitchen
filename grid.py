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

_col_cell = {"TL" : (None,None) , "TR" : (None,None) , "BL" : (None,None) , "BR" : (None,None) }


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
        (self.world.atoms[0]).setName("TL")
        (self.world.atoms[0]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        
        (self.world.atoms[n-1]).setName("TR")
        (self.world.atoms[n-1]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)

        (self.world.atoms[(n-1)*n]).setName("BL")
        (self.world.atoms[(n-1)*n]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)

        (self.world.atoms[(n-1)*n+(n-1)]).setName("BR")
        (self.world.atoms[(n-1)*n+(n-1)]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)

        self.TheVoid.addItem(self.world)
        global _col_cell
        print(_col_cell)
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
        self.atoms= [item for item in self.childItems() if isinstance(item,Cell)]

        
    

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
                        return QPointF(min(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))
                    else:
                        inter =  self._sweep(b[i],j,i)
                        if inter is None : 
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(min(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))
                elif i == 1:
                    j = QGraphicsRectItem(b[i].scenePos().x()+self.n*self.n-self.n,b[i].scenePos().y(),b[i].boundingRect().width(),b[i].boundingRect().height())
                    if j.collidesWithPath(_wall.path()) == True:
                        return QPointF(max(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))
                    else:
                        inter =  self._sweep(b[i],j,i)
                        if inter is None : 
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(max(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))
                elif i == 2:
                    j = QGraphicsRectItem(b[i].scenePos().x(),b[i].scenePos().y()+self.n*self.n-self.n,b[i].boundingRect().width(),b[i].boundingRect().height())
                    if j.collidesWithPath(_wall.path()) == True:
                        return QPointF(min(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))
                    else:
                        inter =  self._sweep(b[i],j,i)
                        if inter is None : 
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(min(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))
                elif i == 3:
                    j = QGraphicsRectItem(b[i].scenePos().x()+self.n*self.n-self.n,b[i].scenePos().y()+self.n*self.n-self.n,b[i].boundingRect().width(),b[i].boundingRect().height())
                    if j.collidesWithPath(_wall.path()) == True:
                        return QPointF(max(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))
                    else:
                        inter =  self._sweep(b[i],j,i)
                        if inter is None : 
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(max(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))
                
            
        return super().itemChange(change, value)

    def _sweep(self,b : Cell, r : QGraphicsRectItem, correction : int ):
        global _col_cell

        
        w = b.boundingRect().width()
        h = b.boundingRect().height()
        if _col_cell.get(b.getName())[0] is None:
            return None
        if correction == 0:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x(),_col_cell.get(b.getName())[0].y()) 
            new_cell = QPointF(_col_cell.get(b.getName())[1].x(),_col_cell.get(b.getName())[1].y()) 
        elif correction == 1:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x()+self.n*self.n-self.n,_col_cell.get(b.getName())[0].y()) 
            new_cell = QPointF(_col_cell.get(b.getName())[1].x()+self.n*self.n-self.n,_col_cell.get(b.getName())[1].y()) 
        elif correction == 2:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x(),_col_cell.get(b.getName())[0].y()+self.n*self.n-self.n) 
            new_cell = QPointF(_col_cell.get(b.getName())[1].x(),_col_cell.get(b.getName())[1].y()+self.n*self.n-self.n)
        elif correction == 3:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x()+self.n*self.n-self.n,_col_cell.get(b.getName())[0].y()+self.n*self.n-self.n) 
            new_cell = QPointF(_col_cell.get(b.getName())[1].x()+self.n*self.n-self.n,_col_cell.get(b.getName())[1].y()+self.n*self.n-self.n)

        dx = new_cell.x() - old_cell.x() 
        dy = new_cell.y() - old_cell.y()

        # De l'intervalle [old;new] on obitent old et new 
        old = QPainterPath()
        old.addRect(QRectF(old_cell.x(),old_cell.y(),w,h))
        new = QPainterPath()
        new.addRect(QRectF(new_cell.x(),new_cell.y(),w,h))
        
        # De l'intervalle [old;new] on determine ]old;new[
        intersection = QPainterPath()
        if dx !=0:
            intersection.moveTo(old_cell.x(),old_cell.y())
            intersection.lineTo(old_cell.x()+w,old_cell.y())
            intersection.lineTo(new_cell.x()+w,new_cell.y())
            intersection.lineTo(new_cell.x(),new_cell.y())
            
            intersection.closeSubpath()

            intersection.moveTo(old_cell.x(),old_cell.y()+h)
            intersection.lineTo(old_cell.x()+w,old_cell.y()+h)
            intersection.lineTo(new_cell.x()+w,new_cell.y()+h)
            intersection.lineTo(new_cell.x(),new_cell.y()+h)

            intersection.closeSubpath()

        if dy !=0:
            intersection.moveTo(old_cell.x(),old_cell.y())
            intersection.lineTo(old_cell.x(),old_cell.y()+h)
            intersection.lineTo(new_cell.x(),new_cell.y()+h)
            intersection.lineTo(new_cell.x(),new_cell.y())
            
            intersection.closeSubpath()

            intersection.moveTo(old_cell.x()+w,old_cell.y())
            intersection.lineTo(old_cell.x()+w,old_cell.y()+h)
            intersection.lineTo(new_cell.x()+w,new_cell.y()+h)
            intersection.lineTo(new_cell.x()+w,new_cell.y())

            intersection.closeSubpath()
        
        return old.united(new).united(intersection)

class Cell(QGraphicsRectItem):

    def __init__(self, x,y,w,h):
        super().__init__(x,y,w,h)
        self._name =""

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged:
            global _col_cell
            if self._name != "":
                _col_cell[self._name] = (self.scenePos(),value) #(old_pos,new_pos)
            #print(_col_cell)
        return super().itemChange(change, value)
    
    def setName(self,i: str):
        self._name = i
    
    def getName(self):
        return self._name

class InvisibleWallLimit(QGraphicsPathItem):

    def __init__(self,scene : QGraphicsScene):
        walls = QPainterPath()
        
        walls.addRect(scene.sceneRect().center().x()-10,0,10,scene.sceneRect().height())
        walls.addRect(0,scene.sceneRect().center().y()-10,scene.sceneRect().width(),10)
        super().__init__(walls)
        self.setZValue(0)
        self.setPen(QPen(QColor("#3700ff"), 3))
        self.setBrush(QBrush(QColor("#1100ffff")))

    #ecrire une fonction update pour le rezize

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = Window(25,25)
    window.show()
    sys.exit(app.exec())
        