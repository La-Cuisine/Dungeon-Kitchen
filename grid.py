import sys
import math
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
    QGraphicsSceneWheelEvent,
    QGraphicsPixmapItem,
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
    QWheelEvent,
    QKeyEvent,  
) 

_wall = None

_col_cell = {"TL" : (None,None) , "TR" : (None,None) , "BL" : (None,None) , "BR" : (None,None) } #colision_cell

class View_Grid(QGraphicsView):
    _grid = None

    _shift_press = False

    zoomfac = 1.15
    zoom = 1
    zoomMax = 5
    zoomMin = 0.5

    def mouseMoveEvent(self, event):
        
        item = self.itemAt(event.pos())
        if isinstance(item,Grid):
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,True)
            if self._grid is None :
                self._grid = item
        if isinstance(item,Interface_Cell):
            item.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,True)
            if self._grid is None :
                self._grid = item.parentItem()
        if item is None and self._grid is not None :
           self._grid.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,False)
        return super().mouseMoveEvent(event)
    

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Shift:
            self._shift_press = True    
            
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        
        if event.key() == Qt.Key.Key_Shift:
            self._shift_press = False    
            
        return super().keyReleaseEvent(event)
    

    def wheelEvent(self, event):
        
        if self._shift_press == True : 
            
            global _wall

            angle = event.angleDelta().y()

            if angle > 0: 
                factor = self.zoomfac
                if factor * self.zoom <= self.zoomMin :
                    self.zoom  = factor*self.zoom 
                    self.scale(self.zoom,self.zoom)
            else:
                factor = 1/self.zoomfac
                if factor * self.zoom >= self.zoomMax :
                    self.zoom  = factor*self.zoom 
                    self.scale(self.zoom,self.zoom)


            if factor * self.zoom >= self.zoomMax or factor * self.zoom <= self.zoomMin :
                return super().wheelEvent(event)

            self.zoom  = factor*self.zoom 

            self.scale(self.zoom,self.zoom)

            #self.fitInView(self.scene().sceneRect(),Qt.AspectRatioMode.IgnoreAspectRatio)



            for item in self.scene().items():
                if isinstance(item,Grid):
                    item.setScale(self.zoom)
                    item.update()
                if isinstance(item,InvisibleWallLimit):
                    #item.setScale(self.zoom)
                    item.update()
            return super().wheelEvent(event)
    
        return super().wheelEvent(event)
    

    def resizeEvent(self, event: QResizeEvent):
        global _wall
        self.fitInView(self.scene().sceneRect(),Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        _wall.Align()
        scale = self.transform().m11()

        #for item in self.TheVoid.items():
            #if isinstance(item,Grid):
            #    item.setScale(1.0/scale)

            #if isinstance(item,layerrect):
            #    item.setScale(item.scale()/scale)
        
        print("here")
        super().resizeEvent(event)
    

class Window(QMainWindow):

   

    def __init__(self, n , s_cell):
        super().__init__()

        self.s_cell = s_cell
        self.size = n
        self.zoomfac = 1.15
        self.zoom = 1
        self.zoomMax = 5
        self.zoomMin = 0.5
        self.setMinimumSize(700, 520)
        #cree une scene graphique de taille 700x520 
        self.TheVoid = QGraphicsScene()
        self.TheVoid.setSceneRect(0,0,700, 520)
        # cree un espace de "visualisation"/"rendu" de la scene
        self.view = View_Grid(self.TheVoid)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(QBrush(QColor("#171717ff")))
        self.view.setAlignment(Qt.AlignmentFlag.AlignTop )
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        
        self.view.setMouseTracking(True)

        contain = QWidget()
        
        self.root_layout = QVBoxLayout(contain)
        #root_layout.setSpacing(12)
        self.root_layout.setContentsMargins(0, 0, 0, 0)        
        self.root_layout.addWidget(self.view)
        self.setCentralWidget(contain)
        global _wall
        _wall = InvisibleWallLimit(self.TheVoid)
        self.TheVoid.addItem(_wall)
        _wall.Align()
        
        self.world  = Grid(n,s_cell)
        (self.world.atoms[0]).setName("TL")
        (self.world.atoms[0]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        (self.world.atoms[n-1]).setName("TR")
        (self.world.atoms[n-1]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        (self.world.atoms[(n-1)*n]).setName("BL")
        (self.world.atoms[(n-1)*n]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        (self.world.atoms[(n-1)*n+(n-1)]).setName("BR")
        (self.world.atoms[(n-1)*n+(n-1)]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.TheVoid.addItem(self.world)
        global _col_cell
        print(_col_cell)
        
 
    
        

class Grid(QGraphicsRectItem):

    def __init__(self,n,s_cell):
        super().__init__(0,0, n* s_cell, n* s_cell)
        self.n = n
        self.s_cell = s_cell
        self.setZValue(0)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        for i in range(n):
            for j in range(n):
                cell = Interface_Cell(s_cell*j,s_cell*i,s_cell,s_cell)
                cell.setCoord(j,i)
                cell.setParentItem(self)
                if j<=i:
                    cell.setImage("sponge.jpg")
        self.atoms= [item for item in self.childItems() if isinstance(item,Interface_Cell)]
        
        self._gpos = QPointF(0,0)
        
    

    def itemChange(self, change, value):
        
        
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            global _col_cell
            global _wall
            new_pos = value
            old_pos = self.pos()
            l = self.n
            b = []
            b.append(self.atoms[0])
            b.append(self.atoms[l-1])
            b.append(self.atoms[(l-1)*l])
            b.append(self.atoms[(l-1)*l+(l-1)])

            for i in range(len(b)):
                if b[i].getName() !="":
                    _col_cell[b[i].getName()] = (_col_cell[b[i].getName()][1],_col_cell[b[i].getName()][1])
                    _col_cell[b[i].getName()] = (_col_cell[b[i].getName()][0],b[i].scenePos())
                    
            for i in range(len(b)):
                if i == 0:
                    if not (b[i].scenePos().x()< self.scene().sceneRect().center().x()-(self.n*self.s_cell/2) or b[i].scenePos().y() < self.scene().sceneRect().center().y()-(self.n*self.s_cell/2)) :

                        j = QGraphicsRectItem(b[i].scenePos().x(),b[i].scenePos().y(),b[i].boundingRect().width(),b[i].boundingRect().height())
                        if j.collidesWithPath(_wall.path()) == True:
                            print("55")
                            return QPointF(min(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))

                        inter =  self._sweep(b[i],i)
                        if inter is None : 
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            print("99")
                            return QPointF(min(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))
                        if b[i].scenePos().x() >= self.scene().sceneRect().center().x()+8 or b[i].scenePos().y() >= self.scene().sceneRect().center().y()+8:
                            self.ungrabMouse()
                            return QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-self.s_cell)
                    
                elif i == 1:
                    if not (b[i].scenePos().x()+self.n*self.n-self.n > self.scene().sceneRect().center().x()+(self.n*self.s_cell/2) or b[i].scenePos().y() < self.scene().sceneRect().center().y()-(self.n*self.s_cell/2)) :
                        j = QGraphicsRectItem(b[i].scenePos().x()+self.n*self.n-self.n,b[i].scenePos().y(),b[i].boundingRect().width(),b[i].boundingRect().height())
                        if j.collidesWithPath(_wall.path()) == True:
                            return QPointF(max(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))

                        inter =  self._sweep(b[i],i)
                        if inter is None : 
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(max(old_pos.x(),new_pos.x()),min(old_pos.y(),new_pos.y()))
                        print("B1 : ",b[i].scenePos().x()+self.n*self.n-self.n," XCEN :",self.scene().sceneRect().center().x()-8)
                        if b[i].scenePos().x()+self.n*self.n-self.n <= self.scene().sceneRect().center().x()-8 or b[i].scenePos().y()>= self.scene().sceneRect().center().y()+8:
                            self.ungrabMouse()
                            return QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-(self.n*self.n-self.n)+self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-self.s_cell)
                    
                elif i == 2:
                    if not (b[i].scenePos().y()+self.n*self.n-self.n > self.scene().sceneRect().center().y()+(self.n*self.s_cell/2) or b[i].scenePos().x() < self.scene().sceneRect().center().y()-(self.n*self.s_cell/2)) :
                        j = QGraphicsRectItem(b[i].scenePos().x(),b[i].scenePos().y()+self.n*self.n-self.n,b[i].boundingRect().width(),b[i].boundingRect().height())
                        if j.collidesWithPath(_wall.path()) == True:
                            return QPointF(min(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))

                        inter =  self._sweep(b[i],i)
                        if inter is None : 
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(min(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))
                        if b[i].scenePos().x()>= self.scene().sceneRect().center().x()+8 or b[i].scenePos().y()+self.n*self.n-self.n<= self.scene().sceneRect().center().y()-8:
                            self.ungrabMouse()
                            return QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-(self.n*self.n-self.n)+self.s_cell)
                    
                elif i == 3:
                    if not (b[i].scenePos().y()+self.n*self.n-self.n > self.scene().sceneRect().center().y()+(self.n*self.s_cell/2) or b[i].scenePos().x()+self.n*self.n-self.n > self.scene().sceneRect().center().x()+(self.n*self.s_cell/2)) :
                        j = QGraphicsRectItem(b[i].scenePos().x()+self.n*self.n-self.n,b[i].scenePos().y()+self.n*self.n-self.n,b[i].boundingRect().width(),b[i].boundingRect().height())
                        if j.collidesWithPath(_wall.path()) == True:
                            return QPointF(max(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))

                        inter =  self._sweep(b[i],i)
                        if inter is None : 
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(max(old_pos.x(),new_pos.x()),max(old_pos.y(),new_pos.y()))
                        if b[i].scenePos().x()+self.n*self.n-self.n<= self.scene().sceneRect().center().x()-8 or b[i].scenePos().y()+self.n*self.n-self.n<= self.scene().sceneRect().center().y()+8:
                            self.ungrabMouse()
                            return QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-(self.n*self.n-self.n)+self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-(self.n*self.n-self.n)+self.s_cell)
                    
            self.update()
        #if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
        #    l = self.n
        #    b = []
        #    b.append(self.atoms[0])
        #    b.append(self.atoms[l-1])
        #    b.append(self.atoms[(l-1)*l])
        #    b.append(self.atoms[(l-1)*l+(l-1)])
        #    self.check(b)

        return super().itemChange(change, value)



    #def check(self, b : list[QGraphicsRectItem]):
    #    
    #    for i in range(len(b)):
    #            if i == 0:
    #                if b[i].scenePos().x() > self.scene().sceneRect().center().x()+8 or b[i].scenePos().y() > self.scene().sceneRect().center().y()+8:
    #                     self.ungrabMouse()
    #                     self.setPos(QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-self.s_cell))
    #                     return True
    #            elif i == 1:
    #                if b[i].scenePos().x()+self.n*self.n-self.n< self.scene().sceneRect().center().x()-8 or b[i].scenePos().y()> self.scene().sceneRect().center().y()+8:
    #                    self.ungrabMouse()
    #                    self.setPos(QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-(self.n*self.n-self.n)+self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-self.s_cell))
    #                    return True
    #            elif i == 2:
    #                if b[i].scenePos().x()> self.scene().sceneRect().center().x()+8 or b[i].scenePos().y()+self.n*self.n-self.n< self.scene().sceneRect().center().y()-8:
    #                    self.ungrabMouse()
    #                    self.setPos(QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-(self.n*self.n-self.n)+self.s_cell))
    #                    return True
    #            elif i == 3:
    #                if b[i].scenePos().x()+self.n*self.n-self.n< self.scene().sceneRect().center().x()+8 or b[i].scenePos().y()+self.n*self.n< self.scene().sceneRect().center().y()-8:
    #                    self.ungrabMouse()
    #                    self.setPos(QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-(self.n*self.n-self.n)+self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-(self.n*self.n-self.n)+self.s_cell))
    #                    return True
    #    return False
        


    def _sweep(self,b : Interface_Cell, correction : int ):
        global _col_cell

        #print(_col_cell[b.getName()])
        w = b.boundingRect().width()+4
        h = b.boundingRect().height()+4
        if _col_cell.get(b.getName())[0] is None:
            return None
        if correction == 0:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x(),_col_cell.get(b.getName())[0].y()) 
            new_cell = QPointF(_col_cell.get(b.getName())[1].x(),_col_cell.get(b.getName())[1].y()) 
        elif correction == 2:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x(),_col_cell.get(b.getName())[0].y()+self.n*self.n-self.n) 
            new_cell = QPointF(_col_cell.get(b.getName())[1].x(),_col_cell.get(b.getName())[1].y()+self.n*self.n-self.n)
        elif correction == 1:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x()+self.n*self.n-self.n,_col_cell.get(b.getName())[0].y()) 
            new_cell = QPointF(_col_cell.get(b.getName())[1].x()+self.n*self.n-self.n,_col_cell.get(b.getName())[1].y()) 
        elif correction == 3:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x()+self.n*self.n-self.n,_col_cell.get(b.getName())[0].y()+self.n*self.n-self.n) 
            new_cell = QPointF(_col_cell.get(b.getName())[1].x()+self.n*self.n-self.n,_col_cell.get(b.getName())[1].y()+self.n*self.n-self.n)

        dx = new_cell.x() - old_cell.x() 
        dy = new_cell.y() - old_cell.y()

        # De l'intervalle [old;new] on obitent old et new 
        old = QPainterPath()
        old.addRect(QRectF(old_cell.x()-4,old_cell.y()-4,w,h))
        new = QPainterPath()
        new.addRect(QRectF(new_cell.x()-4,new_cell.y()-4,w,h))
        
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
   
    

class Interface_Cell(QGraphicsRectItem):

    def __init__(self, x,y,w,h):
        super().__init__(x,y,w,h)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)
        
        self._coord = (None,None)
        self._name =""
        self._img = None
        self._text = None
        self.w = w 
        self.h = h    


    def boundingRect(self):
        return super().boundingRect().adjusted(-1,-1,1,1)

    def paint(self, painter, option, /, widget = ...):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)  
        if self._img is None : 
            self.setPen(QPen(Qt.black,0.5))
            self.setBrush(QBrush(QColor("#686767ff")))
        
        

                

        return super().paint(painter, option, widget)
         
    def setCoord(self,x : int,y : int):
        self._coord = (x,y)
        

    def setName(self,i: str):
        self._name = i
    
    def getName(self):
        return self._name
    
    def setImage(self,Path : str) :
        if self._img is None:
            self._img = Img()
            self._img.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            self._img.setCacheMode(QGraphicsPathItem.CacheMode.DeviceCoordinateCache)
            self._img.setPixmap((QPixmap(Path).scaled(self.w,self.h,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)))
            self._img.setPos(self.w*self._coord[0],self.h*self._coord[1])
            self._img.setParentItem(self)
        else :
            self.scene().removeItem(self._img)
            del self._img 
            self._img = Img()
            self._img.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            self._img.setCacheMode(QGraphicsPathItem.CacheMode.DeviceCoordinateCache)
            self._img.setPixmap((QPixmap(Path).scaled(self.w,self.h,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)))
            self._img.setPos(self.w*self._coord[0],self.h*self._coord[1])
            self._img.setParentItem(self)
        self.update()


class Img(QGraphicsPixmapItem):


    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        return super().paint(painter, option, widget)

class InvisibleWallLimit(QGraphicsPathItem):

    def __init__(self,scene : QGraphicsScene):
        walls = QPainterPath()
        
        walls.addRect(scene.sceneRect().center().x(),-(scene.sceneRect().height()/2),1,2*scene.sceneRect().height())
        #walls.addRect(scene.sceneRect().center().x()+2,-(scene.sceneRect().height()/2),2,2*scene.sceneRect().height())
        walls.addRect(-(scene.sceneRect().width()/2),scene.sceneRect().center().y(),2*scene.sceneRect().width(),1)
        #walls.addRect(-(scene.sceneRect().width()/2),scene.sceneRect().center().y()+2,2*scene.sceneRect().width(),2)
        super().__init__(walls)
        self.setZValue(0)
        self.setPen(QPen(QColor("#8f8f8fff"), 2))
        #self.setBrush(QBrush(QColor("#ffffffff")))
        

    def Align(self):
        scene = self.scene().sceneRect()
        
        y = scene.top()  + (scene.height()- self.boundingRect().height()/2) /2 
        x = scene.left() + (scene.width() - self.boundingRect().width()/2) /2
        self.setPos(x,y)

    #ecrire une fonction update pour le rezize
    #def sizeupdate(self):
    #    self.shape().

    def sizeUpdate(self):
        print("LOLOLOLOLOLOLOLOLOL ",self.scene().sceneRect().width())
        walls = QPainterPath()
        walls.addRect(self.scene().sceneRect().center().x(),-(self.scene().sceneRect().height()/2),1,2*self.scene().sceneRect().height())
        #walls.addRect(self.scene().sceneRect().center().x()+2,-(self.scene().sceneRect().height()/2),2,2*self.scene().sceneRect().height())
        walls.addRect(-(self.scene().sceneRect().width()/2),self.scene().sceneRect().center().y(),2*self.scene().sceneRect().width(),1)
        #walls.addRect(-(self.scene().sceneRect().width()/2),self.scene().sceneRect().center().y()+2,2*self.scene().sceneRect().width(),2)
        self.setPath(walls)

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = Window(25,25)
    window.show()
    sys.exit(app.exec())