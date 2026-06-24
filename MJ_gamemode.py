import sys
from enum import Enum

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

z_dic = {}
layerwindow_dic = {}

_LimitBoundingLeft = None
_LimitBoundingRight = None

class EnumBound(Enum):
    LEFT = 0
    RIGHT = 1

_view_bounds = {"cw": 350.0, "ch": 260.0}

#METTRE DES FONCT / VAR EN PRIVE SI NECESSAIRE "__"


class View_GameMode(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)

        self._grid = None
        self._shift_press = False

        self._cell_select = None
        self._cell_select_use = False

        self.zoom = 1.0
        self._fitted_once = False

        self.profile_rect = ProfileBox(self,self.scene())


        self._Mxy = None

        self._Items_needs = []

        # Overlay fixe (bas a droite) affichant les proprietes d'une case :
        # widget enfant de la vue, donc insensible au zoom/pan, et
        # repositionne automatiquement au resize via align()
        #self._properties_overlay = Interface_Proprieties(self)
        #self.addItemNeeds(self._properties_overlay)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform) #antialiasing + meilleur rendu pour image 
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # desactive la barre de scroll-V VISUELEMENT UNIQUEMENT
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # desactive la barre de scroll-H VISUELEMENT UNIQUEMENT
        self.setBackgroundBrush(QBrush(QColor("#e8e8e8ff")))
        self.setAlignment(Qt.AlignmentFlag.AlignLeft) # force l'espace à ce coller gauche (permet par exemple un meilleur rendu du rectangle "profile_rect")
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

    
    def _update_world_bounds(self):
        global _LimitBoundingLeft, _view_bounds

        if self.scene() is None:
            return

        visible = self.mapToScene(self.viewport().rect()).boundingRect()
        _view_bounds["cw"] = visible.center().x()
        _view_bounds["ch"] = visible.center().y()

        if _LimitBoundingLeft is not None and _LimitBoundingRight is not None :
            _LimitBoundingLeft.sizeUpdate(visible)
            _LimitBoundingRight.sizeUpdate(visible)

    def resizeEvent(self, event: QResizeEvent):
        
        if not (event.oldSize().height() == -1 and event.oldSize().width() == -1):
            if event.size().height() > event.oldSize().height() and event.size().width() > event.oldSize().width(): 
                
                #adapte la view de façon proporttionnel à la scene
                self.fitInView(self.scene().sceneRect().adjusted(-1.1,-1.1,1.1,1.1),Qt.AspectRatioMode.KeepAspectRatioByExpanding) 
            elif event.size().height() < event.oldSize().height() and event.size().width() < event.oldSize().width():
                
                #adapte la view de façon proporttionnel à la scene
                self.fitInView(self.scene().sceneRect(),Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        #Force la scene à s'adapter correctement à la partie visible de la scene  (plus de scrolling H et V)
        self.setSceneRect(self.mapToScene(self.viewport().rect()).boundingRect())
        
        self._update_world_bounds()
        self.profile_rect.Align()
        scale = self.transform().m11()
        
        
        for item in self.scene().items():
            if isinstance(item,layerwindow):
                item.setScale(1.0/scale)
            
                
                
            #if isinstance(item,ProfileBox):
            #    item.setScale(item.scale()/scale)
        
        
        super().resizeEvent(event)
   



class MainWindow(QMainWindow):

    def __init__(self):
        """
        Constructeur : initialise les objets métier, configure la fenêtre
        et crée tous les widgets de l'interface.
        """
        super().__init__()   # Initialise QMainWindow (obligatoire)
        
        global _LimitBoundingLeft
        global _LimitBoundingRight
        
        self.setMinimumSize(700, 520)
        self.setWindowTitle("GameMode")

        #cree une scene graphique de taille 700x520 
        self.univers = QGraphicsScene()
        self.univers.setSceneRect(0,0,700, 520)
        # cree un espace de "visualisation"/"rendu" de la scene
        self.view = View_GameMode(self.univers)
        
        contain = QWidget()
        self.root_layout = QVBoxLayout(contain)
        #root_layout.setSpacing(12)
        self.root_layout.setContentsMargins(7, 7, 7, 7)        
        self.root_layout.addWidget(self.view)
        self.setCentralWidget(contain)
        
        self.LimitBoundingLeft = LimitBounding(EnumBound.LEFT,self.univers)  
        _LimitBoundingLeft = self.LimitBoundingLeft
        self.univers.addItem(self.LimitBoundingLeft)

        self.LimitBoundingRight = LimitBounding(EnumBound.RIGHT,self.univers)  
        _LimitBoundingRight = self.LimitBoundingRight
        self.univers.addItem(self.LimitBoundingRight)


        

        layer1 = layerwindow(50,80,200,500,3,"Black")
        layer2 = layerwindow(300,80,200,500,2,"Black")
        layer3 = layerwindow(300,80,200,500,4,"Black")
        z_dic[layer1] = layer1.zValue()
        z_dic[layer2] = layer2.zValue()
        z_dic[layer3] = layer2.zValue()         
        self.univers.addItem(layer1)
        self.univers.addItem(layer2)
        self.univers.addItem(layer3)
        
        
        
        #self.user_profile_1 = self.addButItem(15,20)
            
        
       
    


class layerwindow(QGraphicsItem):
    def __init__(self, x, y, w, h,z,color):
        super().__init__()
        self.setPos(x,y)
        self.rect = QRectF(0,0,w,h)
        self.color = QColor(color)
        self.setZValue(z)

        self._gpos = QPointF(50,80)
        self.round = 12

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)


        self.setOpacity(0.8)
            
        
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        self.child = childrect(0,0,w,26,self)
    
        

    #Met au premier plan et adapte le plan des elements entre self.Zvalue()----FirstPlane
    def mousePressEvent(self, event):
        i = list(z_dic.keys()).index(self)
        j=0
        m = max(z_dic,key = z_dic.get)
        
        for key,val in z_dic.items():

            if j > i :
                z_dic[key] = val-1
                key.setZValue(z_dic[key])
                
            j+=1
            key.setOpacity(0.7)
        self.setOpacity(0.8)
        self.setZValue(z_dic.get(m))
        return super().mousePressEvent(event)
    
    #Ne fait rien
    def mouseReleaseEvent(self, event):
        return super().mouseReleaseEvent(event)
    
    #Ajuste l'espace invisible autour l'objet (comparable à une hitbox)    
    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect,self.round,self.round)
        return path

    #Espace de rafraichissement un peu plus grand que le rect        
    def boundingRect(self):
        return self.rect.adjusted(-1,-1,1,1)

    #Dessine
    def paint(self, painter = None, option = None, widget = None):
        painter.setPen(QPen(Qt.black,0))
        painter.setBrush(QBrush(self.color))
        painter.drawRoundedRect(self.rect,self.round,self.round)
        
    
    def itemChange(self, change, value):
        
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            global _LimitBoundingLeft    
            new_pos = value
            old_pos = self.pos()

            cw = _view_bounds["cw"]
            ch = _view_bounds["ch"]


            if _LimitBoundingLeft is not None :    
                if _LimitBoundingLeft.collidesWithItem(self) and _LimitBoundingRight.collidesWithItem(self):
                    if new_pos.x() < cw/2 and new_pos.y() < ch/2:
                       
                        return QPointF(max(old_pos.x(), new_pos.x()), max(old_pos.y(), new_pos.y()))
                    if new_pos.x() < cw/2 and new_pos.y() > ch/2:
                       
                        return QPointF(max(old_pos.x(), new_pos.x()), min(old_pos.y(), new_pos.y()))
                    if new_pos.x() > cw/2 and new_pos.y() < ch/2:
                       
                        return QPointF(min(old_pos.x(), new_pos.x()), max(old_pos.y(), new_pos.y()))       
                    if new_pos.x() > cw/2 and new_pos.y() > ch/2:
                       
                        return QPointF(min(old_pos.x(), new_pos.x()), min(old_pos.y(), new_pos.y()))         
                if _LimitBoundingLeft.collidesWithItem(self):  

                    return QPointF(max(old_pos.x(), new_pos.x()), max(old_pos.y(), new_pos.y()))
                if _LimitBoundingRight.collidesWithItem(self):  

                    return QPointF(min(old_pos.x(), new_pos.x()), min(old_pos.y(), new_pos.y()))
                #inter = self._sweep(self.boundingRect(), i)
                #if inter is None:
                #    return super().itemChange(change, value)
                #col = _LimitBounding.mapFromScene(_LimitBounding.shape())
                #if inter.intersects(col):
                #    print("OPP")
                #    return QPointF(min(old_pos.x(), new_pos.x()), min(old_pos.y(), new_pos.y()))
                #if self.boundingRect().x() >= cw + 8 or self.boundingRect().y() >= ch + 8:
                #    print("TPPP")
                #    self.ungrabMouse()
                #    return QPointF(self._gpos.x() + cw - self.s_cell, self._gpos.y() + ch - self.s_cell)
                #self.update()

        return super().itemChange(change, value)
    


class childrect(QGraphicsItem):

    def __init__(self, x, y, w, h, parent):
        super().__init__(parent)
        self.setPos(x,y)
        self.rect = QRectF(0,0,w,h)
        self.color = parent.color
        self.setOpacity(1)
        self.parent = parent
        self.round = 10
        # Defini l'espace comme un lieu ne pouvant pas faire bouger layerwindow
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)
        self.button = self.addButItem(88/100*w,y-1)
        
        

    #Ajuste l'espace invisible autour l'objet (comparable à une hitbox)    
    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect,self.round,self.round)
        return path

    #Espace de rafraichissement un peu plus grand que le rect    
    def boundingRect(self):
        return self.rect.adjusted(-1,-1,1,1)

    #Dessine
    def paint(self, painter = None, option = None, widget = None):
        painter.setPen(QPen(Qt.black,0))
        painter.setBrush(QBrush(self.color))
        painter.drawRoundedRect(self.rect,self.round,self.round)
    

    def addButItem(self,x,y):
        
        button = QPushButton("✕") # cree la donnée bouton
        button.setFixedSize(26, 26)
        button.clicked.connect(self.close) # Bouton clické -> lance close()
        # Fait une beauté au bouton
        button.setStyleSheet("""
                QPushButton {
                             background : transparent;
                             border : none ;
                            font-size : 17px;
                             }
                QPushButton:hover {
                             font-size : 19px;
                             }""")
        
        #conteneur du boutton
        cont = QGraphicsProxyWidget(self)
        cont.setWidget(button)
        
        cont.setPos(x,y)
        
       
        return cont

    #Ferme et supprime toute le layerwindow (voir s'il faudra le suppr ou le concerver à l'avanir)
    def close(self):
        scene = self.scene()
        if scene is not None :
            scene.removeItem(self.parent)
            del self.parent           
            del self

class LimitBounding(QGraphicsPathItem):
    """Croix de murs invisibles utilisee par Grid pour limiter le
    deplacement. Sa position/etendue suit desormais la zone REELLEMENT
    VISIBLE dans la vue (passee via sizeUpdate), et non plus le centre
    fixe de la sceneRect d'origine -> elle reste coherente quand on
    zoome ou qu'on redimensionne la fenetre."""

    def __init__(self, n : EnumBound ,scene: QGraphicsScene):
        super().__init__()
        self.setZValue(0)
        self.setPen(QPen(QColor("#ff0000"), 5))
        self.setPos(0, 0)
        self.n = n 
        self.sizeUpdate(scene.sceneRect())

    def sizeUpdate(self, visible_rect: QRectF):
        cx = visible_rect.topLeft().x()
        cy = visible_rect.topLeft().y()
        span_w = max(visible_rect.width(), 1.0) * 1
        span_h = max(visible_rect.height(), 1.0) * 1

        walls = QPainterPath()
        if self.n.value == 0 :
            walls.addRect(cx, cy, span_w, 1)
            walls.addRect(cx, cy,1, span_h)
        if self.n.value == 1 :    
            walls.addRect(cx+span_w, cy,1, span_h)
            walls.addRect(cx, cy+span_h+73,span_w, 1)
        self.setPath(walls)


class ProfileBox(QLabel):
    W = 120
    H = 600

    def __init__(self, parent_view : QGraphicsView, scene : QGraphicsScene):
        super().__init__(parent_view)
        self.setFixedSize(self.W, self.H)
        
        self.profs = []
        self.nbprofs = 0
        self.scene = scene
        

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        self.raise_()
        self._reposition()
        self.profile(4)


    def _reposition(self):
        parent = self.parent()
        if parent is not None:
            print(parent.height())
            self.move(4, (parent.height()-self.H)/2)


    def Align(self):
        self._reposition()

    def profile(self,n : int):
        for i in range(n):
            self.profs.append(Profile(self,n,i,i))
        self.nbprofs = n

    def prof_remove(self,id):

        for i in self.profs:
            if isinstance(i,Profile):
                if i.get_id() == id:
                    self.profs.remove(i)
                    i.deleteLater()

        
                    


    #def profs_replace(self,i,id):
        
                

        
class Profile(QPushButton):
    WH=80
    def __init__(self, parent : ProfileBox,nb_joueurs : int, n : int, id : int):
        super().__init__(parent)
        self._idplayer = id 
        self.ficheIsOpen=False
        self.place = n
        self.scene = parent.scene
        pos_h = (parent.height()-self.WH)/2/nb_joueurs
        gap = 0
        if n > 0 :
            gap = 52
        for _ in range(n):
            
            pos_h = pos_h + (parent.height()-self.WH)/2/nb_joueurs + gap

        self.setGeometry((parent.width()-self.WH)/2,pos_h,self.WH,self.WH)
        self.setStyleSheet("border-radius : 40px;"       
                           "border : 2px solid black;"
                           "background-color: black;")
        
        self.clicked.connect(self.openFiche)
        

    def get_id(self):
        return self._idplayer    
    
    def openFiche(self):
        global layerwindow_dic
        global z_dic
        scale = self.parent().parent().transform().m11()
        layerwindow_dic["profile"+str(self.place)] = layerwindow(50,80,200,500,self.place,"Black")
        layerwindow_dic["profile"+str(self.place)].setScale(1/scale)
        z_dic[layerwindow_dic["profile"+str(self.place)]] = layerwindow_dic["profile"+str(self.place)].zValue()
        self.scene.addItem(layerwindow_dic["profile"+str(self.place)])

    def setPlace(self,new_place:int):
        
        global layerwindow_dic
        global z_dic
        tmp = "profile"+str(self.place)
        layerwindow_dic["profile"+str(new_place)] =  layerwindow_dic[tmp]
        
        z_dic[layerwindow_dic["profile"+str(new_place)]] = z_dic[layerwindow_dic[tmp]] 
        
        z_dic.pop(layerwindow_dic[tmp],None)
        layerwindow_dic.pop(tmp,None)
        self.place = new_place



        
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    gamemode = MainWindow()
    gamemode.show()
    sys.exit(app.exec())