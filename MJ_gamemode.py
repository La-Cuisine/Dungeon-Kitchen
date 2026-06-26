import sys
import random
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
    QGraphicsOpacityEffect,
    
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

    launch_dices = None

    def __init__(self, scene):
        super().__init__(scene)

        self._grid = None
        self._shift_press = False

        self._cell_select = None
        self._cell_select_use = False

        self.zoom = 1.0
        self._fitted_once = False

        self.dices_box = DicesBox(self,self.scene())
        self.profile_rect = ProfileBox(self,self.scene())
        self.Dice_result = Dice_result(self)

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

    def getDiceResult(self):
        return self.Dice_result
    
    def setButtonDices(self, button : Launch_Dices_Buttons):
        self.launch_dices = button

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
        self.dices_box.Align()
        self.Dice_result.Align()
        if self.launch_dices is not None :
            self.launch_dices.Align()
        scale = self.transform().m11()
        
        
        for item in self.scene().items():
            if isinstance(item,layerwindow):
                item.setScale(1.0/scale)
            
                
                
            #if isinstance(item,ProfileBox):
            #    item.setScale(item.scale()/scale)
        
        
        super().resizeEvent(event)
   
    def mousePressEvent(self, event):
        if self.Dice_result.isVisible():
            if not self.Dice_result.geometry().contains(event.position().toPoint()):
                self.Dice_result.hide()

        return super().mousePressEvent(event)



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

    def __init__(self, parent_view : View_GameMode, scene : QGraphicsScene):
        super().__init__(parent_view)
        self.setFixedSize(self.W, self.H)
        
        self.profs = []
        self.nbprofs = 0
        self.scene = scene
        

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        self.raise_()
        self._reposition()
        
        #add 4 profil
        self.add_profile()
        self.add_profile()
        self.add_profile()
        self.add_profile()
        
        


    def _reposition(self):
        parent = self.parent()
        if parent is not None:
            self.move(4, (parent.height()-self.H)/2)


    def Align(self):
        self._reposition()

    def profile(self,n : int):
        for i in range(n):
            self.profs.append(Interface_Profile(self,n,i,i))
        self.nbprofs = n

    def add_profile(self):
        n = self.nbprofs
        if n>0:
            for i in range(n):
                self.profs[i].setNbjoueur(n+1)    
                self.profs[i].Inter_Place()
            self.profs.append(Interface_Profile(self,n+1,self.profs[n-1].get_place()+1,self.profs[n-1].get_place()+1))
            self.nbprofs = self.nbprofs + 1
        else : 
            self.profs.append(Interface_Profile(self,n+1,0,0))
            self.nbprofs = self.nbprofs + 1

    """
     prof_remove qui utilise profs_replace peuvent etre utiliser si un joeur ce deconnecte
    """    
    #Supprime le profile graphiquement
    def prof_remove(self,id):

        for i in self.profs:
            if isinstance(i,Interface_Profile):
                if i.get_id() == id:
                    m = i.place
                    i.deleteLater()
                    self.profs_replace(m,self.nbprofs)
                    self.nbprofs = self.nbprofs - 1 
                    self.profs.remove(i)
                    break

        
    #Ecrase le p profile et replace le tout          
    def profs_replace(self,p,n):
        if p != n :
            for i in range(p+1,n):
                self.profs[i].setPlace_Overwrite(i-1)
        
        for i in range(n):
                if i <p :
                    self.profs[i].setNbjoueur(n-1)    
                self.profs[i].Inter_Place()

        
                

        
class Interface_Profile(QPushButton):
    WH=80
    def __init__(self, parent : ProfileBox,nb_joueurs : int, n : int, id : int):
        super().__init__(parent)
        self._idplayer = id 
        self.ficheIsOpen=False
        self.place = n
        self.scene = parent.scene
        self.nb_joueurs = nb_joueurs
        
        self.Inter_Place()
        
        self.setStyleSheet("border-radius : 40px;"       
                           "border : 2px solid black;"
                           "background-color: black;")
        
        
        

        
        self.clicked.connect(self.openFiche)
        

    def get_id(self):
        return self._idplayer  

    def get_place(self):
        return self.place 
    
    def openFiche(self):
        global layerwindow_dic
        global z_dic
        scale = self.parent().parent().transform().m11()
        layerwindow_dic["profile"+str(self.place)] = layerwindow(50+self.place*35,80+self.place*8,200,500,self.place,"Black")
        layerwindow_dic["profile"+str(self.place)].setScale(1/scale)
        z_dic[layerwindow_dic["profile"+str(self.place)]] = layerwindow_dic["profile"+str(self.place)].zValue()
        self.scene.addItem(layerwindow_dic["profile"+str(self.place)])
        
    def setPlace_Overwrite(self,new_place:int):
        global layerwindow_dic
        global z_dic
        tmp = "profile"+str(self.place)
        layerwindow_dic["profile"+str(new_place)] =  layerwindow_dic[tmp]
        
        z_dic[layerwindow_dic["profile"+str(new_place)]] = z_dic[layerwindow_dic[tmp]] 
        
        z_dic.pop(layerwindow_dic[tmp],None)
        layerwindow_dic.pop(tmp,None)
        self.place = new_place
        self.nb_joueurs = self.nb_joueurs - 1
        
        

    def Inter_Place(self):
        pos_h = (self.parent().height()-self.WH)/2/self.nb_joueurs
        gap = 0
        if self.place > 0 :
            gap = 52
        for _ in range(self.place):
            pos_h = pos_h + (self.parent().height()-self.WH)/2/self.nb_joueurs + gap
        
        self.setGeometry((self.parent().width()-self.WH)/2,pos_h,self.WH,self.WH)
        

    def setNbjoueur(self,n : int):
        self.nb_joueurs = n


#Maitre D'Orchestres des Dés du DESTIN
class DicesBox(QLabel):

    W = 500
    H = 80
    DiceLauchable = False
    CheckFinish = True
    
    
    def __init__(self, parent_view : View_GameMode, scene : QGraphicsScene):
        super().__init__(parent_view)
        
        self.setFixedSize(self.W, self.H)
        
        self.scene = scene
        self.dice_laucher = None

        self.setStyleSheet(
            "background-color: transparent;"
            "color: #ffffff;"
            "font-size: 12px;"
            "border-radius: 3px;")
        
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        
        self.raise_()
        self._reposition()

        self.dicebox = []
        self.dicebox.append(DiceBox(self,4,0))
        self.dicebox.append(DiceBox(self,6,1))
        self.dicebox.append(DiceBox(self,8,2))
        self.dicebox.append(DiceBox(self,10,3))
        self.dicebox.append(DiceBox(self,12,4))
        self.dicebox.append(DiceBox(self,20,5))
        self.dicebox.append(DiceBox(self,100,6))

        
    def _reposition(self):
        parent = self.parent()
        if parent is not None:
            self.move((parent.width()-self.W)/2,parent.height()-self.H-50)


    def Align(self):
        self._reposition()        

    def getLaucheable(self):
        return self.DiceLauchable
        
    def CheckLaucheable(self):
        if self.DiceLauchable == False :
            for i in self.dicebox :
                if i.getNbDice() !=0:
                    if self.DiceLauchable == False:
                        self.DiceLauchable = True
                    break
        if self.DiceLauchable == True : 
            if  self.dice_laucher is None:
                self.dice_laucher = Launch_Dices_Buttons(self.parent(),self)
                self.dice_laucher.hide()
                self.parent().setButtonDices(self.dice_laucher)
            j = 0    
            for i in self.dicebox : 
                if i.getNbDice() !=0:
                    print("CHECK : ",i.getNbDice())
                    self.dice_laucher.updateDicesData(j,i.getNbDice())
                j = j +1
            self.dice_laucher.connectLauch()
            self.dice_laucher.setVisible(True)
    
    def mousePressEvent(self, ev):
        if self.CheckFinish == True :
            self.CheckFinish = False
            print("GO")
            self.CheckLaucheable()
            self.CheckFinish = True
        
        if self.parent().getDiceResult().isVisible():
            if not self.parent().getDiceResult().geometry().contains(ev.position().toPoint()):
                self.parent().getDiceResult().hide()
    
        return super().mousePressEvent(ev)

    def Reset(self):
        for i in self.dicebox :
            i.reset()
            self.dice_laucher.reset()
            self.DiceLauchable = False



class DiceBox(QLabel):
    W = 40
    H = 80
    _NbDiceTextZone = None
    _NbDiceSelected = 0
    

    def __init__(self, parent_view : QLabel,Nat : int, place : int):
        
        
        
        super().__init__(parent_view)
        

        self.setFixedSize(self.W, self.H)
        
        self.Nat = Nat
        self.place = place
        self.round = 4


        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        self.raise_()
        self._reposition()

        self._text_zone()
        self.dices_buttons = Dices_Buttons(self,self._NbDiceTextZone)
        

    def _reposition(self):
        pos_w = (self.parent().width()-self.W)/2/7 
        gap = 0
        if self.place > 0 :
            gap = 35
        for _ in range(self.place):
            pos_w = pos_w + (self.parent().width()-self.W)/2/7 + gap 
        
        self.move(pos_w-5,self.parent().height()-self.H+2)
        #parent = self.parent()
        #if parent is not None:
        #    self.move((parent.width()-self.W)/2,parent.height()-self.H-50)

    
    def UpdateNbDice(self):
        if self._NbDiceSelected == 10:
            return self._NbDiceSelected     
        self._NbDiceSelected = self._NbDiceSelected +1 
        return self._NbDiceSelected 

    def getNbDice(self):
        return self._NbDiceSelected

    def Align(self):
        self._reposition()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)  
        

        space = self.rect().toRectF()

        draw = QPainterPath()
        
        draw.moveTo(space.left(),space.bottom()/1.9)        
        draw.lineTo(space.left(),space.top() + self.round)       
        draw.quadTo(space.left(),space.top(),space.left()+self.round,space.top())
        draw.lineTo(space.right()-self.round,space.top())             
        draw.quadTo(space.right(),space.top(),space.right(),space.top()+self.round)
        draw.lineTo(space.right(),space.bottom()/1.9)
        draw.lineTo(space.right()/2,space.bottom()/1.9-8)

        draw.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#7dd856")))
        painter.drawPath(draw)

        

        font = painter.font()
        font.setBold(True)
        font.setPixelSize(20)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#000000")))
        if self.Nat !=100:
            painter.drawText(draw.boundingRect(),Qt.AlignmentFlag.AlignCenter, str(self.Nat))
        else:
            painter.drawText(draw.boundingRect(),Qt.AlignmentFlag.AlignCenter, "00")

        draw.clear()

        draw.moveTo(space.right(),space.bottom()/1.9)
        draw.lineTo(space.right(),space.bottom()-15)        
        draw.lineTo(space.left(),space.bottom()-15)
        draw.lineTo(space.left(),space.bottom()/1.9)     
        draw.lineTo(space.right()/2,space.bottom()/1.9-8)  

        draw.closeSubpath()
        
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawPath(draw)

        


    def _text_zone(self):

        space = self.rect().toRectF()
        draw = QPainterPath()

        draw.moveTo(space.right(),space.bottom()/1.9)
        draw.lineTo(space.right(),space.bottom()-15)        
        draw.lineTo(space.left(),space.bottom()-15)
        draw.lineTo(space.left(),space.bottom()/1.9)     
        draw.lineTo(space.right()/2,space.bottom()/1.9-8)  
        draw.closeSubpath()

        self._NbDiceTextZone = draw.boundingRect()

    def mousePressEvent(self, event):
        space = self.rect().toRectF()
        Zone = QRectF(space.left(),space.top(),space.right(),space.bottom()-15)
        if Zone.contains(event.position()):
            print("eee")
            self.UpdateNbDice()
            self.dices_buttons.setTextDice(self._NbDiceSelected)
            

        return super().mousePressEvent(event)    

    def reset(self):
        self._NbDiceSelected = 0
        self.dices_buttons.EmptyText()


class Dices_Buttons(QLabel):

    def __init__(self, parent_view : QLabel, Rect : QRectF):
        super().__init__(parent_view)
        

        self.setFixedSize(Rect.width(), Rect.height())
        self.space = Rect
        


        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "background-color: transparent;"
            "color: #ffffff;"
            "font-size: 15px;"
            "border-radius: 3px;")
        
        
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        self.raise_()
        self._reposition()
        print()

    
    def _reposition(self):
        self.move(self.space.left(),self.space.top())
        

    def Align(self):
        self._reposition()

    def setTextDice(self,n:int):
        self.setText(str(n))
    
    def EmptyText(self):
        self.setText("")

    



class Launch_Dices_Buttons(QPushButton):

    W = 80
    H = 40
    _dataSet = False
    Result = ""

    def __init__(self, parent_view : View_GameMode, Coworker : DiceBox):
        
        #self._parent = Launch_Dices_Buttons(parent_view)
        
        super().__init__(parent_view)
        
        

        self.setFixedSize(self.W, self.H)
        self.coworker = Coworker
        self.Dices = []
        for _ in range(7):
            self.Dices.append(0)
        
        #self.setStyleSheet(
        #    "border : 1px solid black;"
        #    "background-color: black;"
        #    "color: #ffffff;"
        #    "font-size: 15px;"
        #    "border-radius: 12px;")
        
        self.setStyleSheet("""
        QPushButton {
            border : 1px solid black;
            background-color: black;
            color: #ffffff;
            font-size: 15px;
            border-radius: 12px;
        }
        QPushButton:hover {
            
            font-size: 15.5px;
        }
        """)


        
        E = QGraphicsOpacityEffect(self)
        E.setOpacity(0.8)
        self.setGraphicsEffect(E)
              
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        
        self.raise_()
        self._reposition()

        self.setText("LANCER")

    
    def _reposition(self):
        self.move((self.parent().width()-self.W)/2,(self.parent().height()-self.H)/2+110)
        

    def Align(self):
        self._reposition()

    
    def updateDicesData(self,i,n):
        
        self.Dices[i] = n
        print(self.Dices)
        if self._dataSet == False: #A voir si on le conserve
            self._dataSet = True
    
    def connectLauch(self):
        self.clicked.connect(self.lauch)
    
    def disconnectLauch(self):
        self.clicked.disconnect(self.lauch)

    def getResult(self):
        return self.Result

    def lauch(self):
        hasard = {}
        j=0
        for i in self.Dices:
            print(self.Dices)
            if i != 0:
                m = self._convert(j)
                if m not in hasard:
                     hasard[m] = []
                for _ in range(i):
                    hasard[m].append(random.randint(1,m))
            j=j+1
        self.Result =  self.resultToString(hasard)
        self.coworker.Reset()
        self.parent().getDiceResult().setProperties(self.Result)


    
    def _convert(self,i:int):
        if i == 0 :
            return 4
        elif i == 1 :
            return 6
        elif i == 2 :
            return 8
        elif i == 3 :
            return 10
        elif i == 4 :
            return 12
        elif i == 5 :
            return 20
        elif i == 6 :
            return 100

    def resultToString(self,val: dict[int,list]):
        t = ""
        s = 0
        for i in val.keys():
            if i != -1 :
                
                for j in val[i] :
                    s = s + j
                    if i == 100:
                        t = t + str(j) + "(d00) "
                    else :
                        t = t + str(j) + "(d"+str(i)+") "
    
        t = t + "= "+str(s)
        print(t)
        return t

    def reset_data(self):
        for i in range(7):
            self.Dices[i]=0
    
    def reset(self):
        self.reset_data()
        self.disconnectLauch()
        self.hide()

    
class Dice_result(QWidget):
    
    W = 80*2.5
    H = 40*2.5
    MARGIN = 8

    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.setFixedSize(self.W, self.H)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        E = QGraphicsOpacityEffect(self)
        E.setOpacity(0.8)
        self.setGraphicsEffect(E)

        self.text = ""
        self.round = 5

        self._reposition()
        self.hide()

    def _reposition(self):
        self.move((self.parent().width()-self.W)/2,(self.parent().height()-self.H)/2+80)

    # Repositionne au resize de la vue (appele depuis View_Grid.resizeEvent,
    # comme pour Interface_MouseCoord)
    def Align(self):
        self._reposition()

    # Met a jour le texte affiche et (re)affiche le panneau en bas a droite
    def setProperties(self, text: str):
        self.text = text
        self._reposition()
        self.raise_()
        self.show()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        painter.setPen(QPen(Qt.black, 1.5))
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawRoundedRect(rect, self.round, self.round)

        header_rect = rect.adjusted(0, 8, 0, 0)
        font = painter.font()
        font.setBold(True)
        font.setPixelSize(15)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#e1dfdf")))
        painter.drawText(header_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, "Resultat")

        body_rect = rect.adjusted(10, 32, -10, -10)
        font.setBold(True)
        font.setPixelSize(13)
        painter.setFont(font)
        painter.drawText(
            body_rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap,
            self.text,
        )

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    gamemode = MainWindow()
    gamemode.show()
    sys.exit(app.exec())