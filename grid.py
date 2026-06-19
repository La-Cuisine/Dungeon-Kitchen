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
    
) 

_wall = None

_col_cell = {"TL" : (None,None) , "TR" : (None,None) , "BL" : (None,None) , "BR" : (None,None) } #colision_cell

class View_Grid(QGraphicsView):
    _grid = None

    _Move_grid = None 

    def mouseMoveEvent(self, event):
        
        item = self.itemAt(event.pos())
        if isinstance(item,Grid):
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,True)
            if self._grid is None :
                self._grid = item
        if isinstance(item,Cell):
            item.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,True)
            if self._grid is None :
                self._grid = item.parentItem()
        if item is None and self._grid is not None :
           self._grid.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,False)
        return super().mouseMoveEvent(event)

class Window(QMainWindow):
    def __init__(self, n , s_cell):
        super().__init__()

        self.s_cell = s_cell
        self.size = n
        self.zoom = 1.15
        self.setMinimumSize(700, 520)
        #cree une scene graphique de taille 700x520 
        self.TheVoid = QGraphicsScene()
        self.TheVoid.setSceneRect(0,0,700, 520)
        # cree un espace de "visualisation"/"rendu" de la scene
        self.view = View_Grid(self.TheVoid)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(QBrush(QColor("#e8e8e8ff")))
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
 
    def wheelEvent(self, event):
        
        b_pos = self.view.mapToScene(event.position().toPoint())
        print(b_pos)
        angle = event.angleDelta().y()
        if angle > 0:
            
            Scale = self.zoom
        else:
            
            Scale = 1/self.zoom
        
        a_pos = self.view.mapToScene(event.position().toPoint())
        self.view.scale(Scale,Scale)

        self.view.translate(a_pos.x() - b_pos.x(),a_pos.y() - b_pos.y()) 

       
        return super().wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        global _wall
        self.view.fitInView(self.TheVoid.sceneRect(),Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        _wall.Align()
        scale = self.view.transform().m11()

        #for item in self.TheVoid.items():
            #if isinstance(item,Grid):
            #    item.setScale(1.0/scale)

            #if isinstance(item,layerrect):
            #    item.setScale(item.scale()/scale)
        
        print("here")
        super().resizeEvent(event)
    
        

class Grid(QGraphicsRectItem):

    def __init__(self,n,s_cell):
        super().__init__(0,0, n* s_cell, n* s_cell)
        self.n = n
        self.s_cell = s_cell
        self.setZValue(0)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        for i in range(n):
            for j in range(n):
                cell = Cell(s_cell*j,s_cell*i,s_cell,s_cell)
                cell.setPen(QPen(Qt.black,0.5))
                cell.setBrush(QBrush(QColor("Red")))
                cell.setParentItem(self)
        self.atoms= [item for item in self.childItems() if isinstance(item,Cell)]
        
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
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            l = self.n
            b = []
            b.append(self.atoms[0])
            b.append(self.atoms[l-1])
            b.append(self.atoms[(l-1)*l])
            b.append(self.atoms[(l-1)*l+(l-1)])
            self.check(b)
        return super().itemChange(change, value)

    def check(self, b : list[QGraphicsRectItem]):
        

        for i in range(len(b)):
                if i == 0:
                    if b[i].scenePos().x() > self.scene().sceneRect().center().x()+8 or b[i].scenePos().y() > self.scene().sceneRect().center().y()+8:
                         self.setPos(QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-self.s_cell))
                         return True
                elif i == 1:
                    if b[i].scenePos().x()+self.n*self.n-self.n< self.scene().sceneRect().center().x()-8 or b[i].scenePos().y()> self.scene().sceneRect().center().y()+8:
                        self.setPos(QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-(self.n*self.n-self.n)+self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-self.s_cell))
                        return True
                elif i == 2:
                    if b[i].scenePos().x()> self.scene().sceneRect().center().x()+8 or b[i].scenePos().y()+self.n*self.n-self.n< self.scene().sceneRect().center().y()-8:
                        self.setPos(QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-(self.n*self.n-self.n)+self.s_cell))
                        return True
                elif i == 3:
                    if b[i].scenePos().x()+self.n*self.n-self.n< self.scene().sceneRect().center().x()+8 or b[i].scenePos().y()+self.n*self.n< self.scene().sceneRect().center().y()-8:
                        self.setPos(QPointF(self._gpos.x()+self.scene().sceneRect().center().x()-(self.n*self.n-self.n)+self.s_cell,self._gpos.y()+self.scene().sceneRect().center().y()-(self.n*self.n-self.n)+self.s_cell))
                        return True
        return False
        


    def _sweep(self,b : Cell, correction : int ):
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

    #TENTATIVE D'APPLICATION D'UN AUTRE PARADIGLE INFRUCTUEUX
    def _step_axis(self, old_coord : float,new_coord : float, cons : float, axis : str, b : Cell, correction : int, step: int ):
        global _col_cell
        if _col_cell.get(b.getName())[0] is None or _col_cell.get(b.getName())[1] is None :
            return None
        print(" *-* ",_col_cell.get(b.getName())," *-* ")
        if axis == "x":
            if correction == 0:
                old_cell_coord = _col_cell.get(b.getName())[0].x() 
                new_cell_coord = _col_cell.get(b.getName())[1].x() 
            elif correction == 1:
                old_cell_coord = _col_cell.get(b.getName())[0].x()+self.n*self.n-self.n 
                new_cell_coord = _col_cell.get(b.getName())[1].x()+self.n*self.n-self.n 
            elif correction == 2:
                old_cell_coord = _col_cell.get(b.getName())[0].x() 
                new_cell_coord = _col_cell.get(b.getName())[1].x()
            elif correction == 3:
                old_cell_coord = _col_cell.get(b.getName())[0].x()+self.n*self.n-self.n 
                new_cell_coord = _col_cell.get(b.getName())[1].x()+self.n*self.n-self.n
        else :
            if correction == 0:
                old_cell_coord = _col_cell.get(b.getName())[0].y() 
                new_cell_coord = _col_cell.get(b.getName())[1].y() 
            elif correction == 1:
                old_cell_coord = _col_cell.get(b.getName())[0].y() 
                new_cell_coord = _col_cell.get(b.getName())[1].y() 
            elif correction == 2:
                old_cell_coord = _col_cell.get(b.getName())[0].y()+self.n*self.n-self.n 
                new_cell_coord = _col_cell.get(b.getName())[1].y()+self.n*self.n-self.n
            elif correction == 3:
                old_cell_coord = _col_cell.get(b.getName())[0].y()+self.n*self.n-self.n 
                new_cell_coord = _col_cell.get(b.getName())[1].y()+self.n*self.n-self.n

        print("------ ",old_cell_coord," <<>> ",new_cell_coord," ------")
        delta1 = new_cell_coord - old_cell_coord
        dist1 = abs(delta1)

        delta2 = new_coord - old_coord
        dist2 = abs(delta2)

        if dist1 == 0 or dist2 == 0 :
            print("HERE")
            return old_coord
        
        direction1 = math.copysign(1,delta1) # 1 prend le signe de delta
        steps1 = math.ceil(dist1/step)
        step_size1 = dist1 / steps1

        direction2 = math.copysign(1,delta2) # 1 prend le signe de delta
        steps2 = math.ceil(dist2/step)
        step_size2 = dist2 / steps2

        tmp = old_cell_coord
        pre_coord = old_coord
        print("^^^^ ",old_coord)
        print("$$1 : ",steps1," $$2 :",steps2)
        for i in range(min(steps1,steps2)):
            if i < steps1 :
                c_co = tmp + direction1 * step_size1
            if i < steps2 :    
                g_co = pre_coord + direction2 * step_size2
            if axis == "x":
                test = QPointF(c_co,cons)
            else:
                test = QPointF(cons,c_co)
            print(g_co," *** ",c_co)
            if self._coll_check(test,b):
                return pre_coord
            tmp = c_co
            pre_coord = g_co
        return pre_coord

    #FONCTION UTILISE PAR LA TENTATIVE INFRUCTUEUSE              
    def _coll_check(self, point : QPointF,b:Cell):
        global _wall

        item = QPainterPath()
        item.addRect(point.x(),point.y(),b.boundingRect().width(),b.boundingRect().height()) 

        col = _wall.mapFromScene(_wall.shape())
        if item.intersects(col):
            return True
        return False   
    

class Cell(QGraphicsRectItem):

    def __init__(self, x,y,w,h):
        super().__init__(x,y,w,h)
        self._name =""

    def itemChange(self, change, value):
        
        return super().itemChange(change, value)
    
    def setName(self,i: str):
        self._name = i
    
    def getName(self):
        return self._name

class InvisibleWallLimit(QGraphicsPathItem):

    def __init__(self,scene : QGraphicsScene):
        walls = QPainterPath()
        
        walls.addRect(scene.sceneRect().center().x(),-(scene.sceneRect().height()/2),1,2*scene.sceneRect().height())
        walls.addRect(scene.sceneRect().center().x()+2,-(scene.sceneRect().height()/2),2,2*scene.sceneRect().height())
        walls.addRect(-(scene.sceneRect().width()/2),scene.sceneRect().center().y(),2*scene.sceneRect().width(),1)
        walls.addRect(-(scene.sceneRect().width()/2),scene.sceneRect().center().y()+2,2*scene.sceneRect().width(),2)
        super().__init__(walls)
        self.setZValue(0)
        self.setPen(QPen(QColor("#3700ff"), 3))
        self.setBrush(QBrush(QColor("#1100ffff")))

    def Align(self):
        scene = self.scene().sceneRect()
        
        y = scene.top()  + (scene.height()- self.boundingRect().height()/2) /2 
        x = scene.left() + (scene.width() - self.boundingRect().width()/2) /2
        self.setPos(x,y)

    #ecrire une fonction update pour le rezize
    #def sizeupdate(self):
    #    self.shape().

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = Window(25,25)
    window.show()
    sys.exit(app.exec())
        