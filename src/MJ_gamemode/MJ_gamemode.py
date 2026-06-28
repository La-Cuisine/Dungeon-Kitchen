from __future__ import annotations

import sys
import random
from enum import Enum

import json
import requests
import time
from PySide6.QtCore import QThread, Signal, QMimeData # Remplacement du QTimer

# La grille est injectée depuis gui_fonctions via MainWindow.set_map()

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
    QFileDialog,
    QGraphicsPathItem,
    QGraphicsOpacityEffect,
    QLineEdit,
    QGraphicsEllipseItem,
    
    
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
    QIntValidator,
    QWheelEvent,
    QDrag,
    
)

z_dic = {}
layerwindow_dic = {}

_LimitBoundingLeft = None
_LimitBoundingRight = None

class EnumBound(Enum):
    LEFT = 0
    RIGHT = 1

_view_bounds = {"cw": 350.0, "ch": 260.0}
_wall = None

#METTRE DES FONCT / VAR EN PRIVE SI NECESSAIRE "__"


class View_GameMode(QGraphicsView):

    launch_dices = None

    def __init__(self, scene):
        super().__init__(scene)
        
        self.setAcceptDrops(True)
        self._grid = None
        self._shift_press = False

        self._cell_select = None
        self._cell_select_use = False

        self.zoom = 1.0
        self._fitted_once = False

        self.plus = Enter_Dice_Option_Const(self,"+")
        self.moins = Enter_Dice_Option_Const(self,"-")
        self.profile_rect = ProfileBox(self,self.scene())
        self.adventage_dice = Retry_Dice(self)
        self.dices_box = DicesBox(self,self.scene())
        self.Dice_result = Dice_result(self)
        self.space_dice_const = Space_Dice_Constante(self,self.scene(),self.dices_box)
        

        self._Mxy = None

        self._Items_needs = []

        # Overlay fixe (bas a droite) affichant les proprietes d'une case :
        # widget enfant de la vue, donc insensible au zoom/pan, et
        # repositionne automatiquement au resize via align()
        #self._properties_overlay = Interface_Proprieties(self)
        #self.addItemNeeds(self._properties_overlay)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform) #antialiasing + meilleur rendu pour image 
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # desactive la barre de scroll-V VISUELEMENT UNIQUEMENT
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # desactive la barre de scroll-H VISUELEMENT UNIQUEMENT
        self.setBackgroundBrush(QBrush(QColor("#e8e8e8ff")))
        self.setAlignment(Qt.AlignmentFlag.AlignLeft) # force l'espace à ce coller gauche (permet par exemple un meilleur rendu du rectangle "profile_rect")
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

    def getDicesBox(self):
        return self.dices_box

    def getDiceResult(self):
        return self.Dice_result
    
    def getAdvantageDice(self):
        return self.adventage_dice
    
    def getplusDice(self):
        return self.plus

    def getmoinsDice(self):
        return self.moins

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
            
        import src.MJ_application.grid as _grid_mod
        _grid_mod._view_bounds["cw"] = visible.center().x()
        _grid_mod._view_bounds["ch"] = visible.center().y()
        
        if getattr(_grid_mod, '_wall', None) is not None:
            _grid_mod._wall.sizeUpdate(visible)

    def resizeEvent(self, event: QResizeEvent):
        if not self._fitted_once and self.scene() is not None:
            self.fitInView(
                self.scene().sceneRect(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            )
            self.zoom = self.transform().m11()
            self._fitted_once = True

        self._update_world_bounds()
        
        self.profile_rect.Align()
        self.dices_box.Align()
        self.Dice_result.Align()
        self.adventage_dice.Align()
        self.space_dice_const.Align()
        self.plus.Align()
        self.moins.Align()

        if self.launch_dices is not None :
            self.launch_dices.Align()
        scale = self.transform().m11()
        for item in self.scene().items():
            if isinstance(item, layerwindow):
                item.setScale(1.0 / scale)

        super().resizeEvent(event)
        

    zoomfac = 1.15
    zoomMax = 8.0
    zoomMin = 0.15

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        if angle == 0:
            event.ignore()
            return

        factor = self.zoomfac if angle > 0 else 1 / self.zoomfac
        new_zoom = max(self.zoomMin, min(self.zoomMax, self.zoom * factor))
        applied = new_zoom / self.zoom

        if applied != 1.0:
            self.zoom = new_zoom
            self.scale(applied, applied)
            # REMOVED self.centerOn(self._scene_center) 
            self._update_world_bounds()

        event.accept()

    def mousePressEvent(self, event):
        if self.Dice_result.isVisible():
            if not self.Dice_result.geometry().contains(event.position().toPoint()):
                self.Dice_result.hide()
                self.adventage_dice.disconnectLauch()
                self.adventage_dice.hide()

        view_pt = event.position().toPoint()
        item = self.itemAt(view_pt)
        candidate = item
        while candidate is not None:
            if candidate == self._grid:
                candidate.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
                break
            candidate = candidate.parentItem()

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._grid is not None:
            self._grid.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            
        return super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        """Accepte l'élément qui entre sur la vue s'il contient du texte (notre code couleur Hex)."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        """Action au moment de relâcher le clic sur la grille."""
        if event.mimeData().hasText():
            payload = event.mimeData().text()
            
            # Position de la souris convertie pour s'adapter au zoom de la carte
            scene_pos = self.mapToScene(event.position().toPoint())
            
            # On récupère la taille et le parent via la grille si elle existe
            size = 40
            parent_item = None
            if getattr(self, '_grid', None) is not None:
                size = getattr(self._grid, 's_cell', 50) * 0.8
                parent_item = self._grid

            # Centrage visuel du pion par rapport à la pointe de la souris
            x = scene_pos.x() - size / 2
            y = scene_pos.y() - size / 2

            # Pion "image de personnage" (préfixe IMG::) ou pion de couleur unie
            if payload.startswith("IMG::"):
                image_path = payload[len("IMG::"):]
                new_token = Token(x, y, size, parent=parent_item, image_path=image_path)
            else:
                # Création du Token "physique"
                new_token = Token(x, y, size, payload, parent=parent_item)
            
            # Si pas de grille en parent, on l'ajoute directement à la scène
            if parent_item is None:
                self.scene().addItem(new_token)
                
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

class MainWindow(QMainWindow):

    def __init__(self, scene=None, world=None, wall=None):
        """
        Constructeur : initialise les objets métier, configure la fenêtre
        et crée tous les widgets de l'interface.
        """
        super().__init__()   # Initialise QMainWindow (obligatoire)
        
        global _LimitBoundingLeft
        global _LimitBoundingRight
        
        self.setMinimumSize(700, 520)
        self.setWindowTitle("GameMode")

        # Crée une scène graphique de taille 700x520 
        self.univers = QGraphicsScene()
        self.univers.setSceneRect(0, 0, 700, 520)
        
        # Crée un espace de "visualisation"/"rendu" de la scène
        self.view = View_GameMode(self.univers)
        
        # --- CONFIGURATION DU LAYOUT PRINCIPAL ---
        contain = QWidget()
        self.root_layout = QVBoxLayout(contain)
        self.root_layout.setContentsMargins(7, 7, 7, 7)        
        
        # On ajoute d'abord la vue (la carte) au layout !
        self.root_layout.addWidget(self.view)
        
        # palette de pions
        token_container = QWidget()
        self.token_layout = QHBoxLayout(token_container)
        self.token_layout.setContentsMargins(4, 4, 4, 4)
        self.token_layout.setSpacing(12) # <-- gap fixe entre chaque pion
        self.token_layout.addWidget(QLabel("<b>Pions :</b>"))
        
        # Liste de couleurs pour nos pions
        colors = ["#c91400", "#2ecc71", "#3498db", "#f1c40f", "#9b59b6", "#e67e22", "#000000", "#170079", "#FFFFFF", "#AD3B70"]
        for color in colors:
            token_widget = DraggableTokenWidget(color_hex=color)
            self.token_layout.addWidget(token_widget)

        # Bouton "+" (à droite de la palette) pour ajouter un pion personnalisé à partir d'une image
        self.add_character_btn = QPushButton("+")
        self.add_character_btn.setFixedSize(30, 30)
        self.add_character_btn.setToolTip("Ajouter un personnage (image) à la palette")
        self.add_character_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_character_btn.setStyleSheet(
            "QPushButton {"
            "background-color: #2b2b2b;"
            "color: #e1dfdf;"
            "border-radius: 15px;"
            "border: 2px solid #555;"
            "font-weight: bold;"
            "}"
            "QPushButton:hover { background-color: #3a3a3a; }"
        )
        self.add_character_btn.clicked.connect(self._add_character_token)
        self.token_layout.addWidget(self.add_character_btn)

        self.token_layout.addStretch() # Repousse la palette vers la gauche

        # Zone de défilement horizontale : si la palette est plus large que
        # l'espace disponible, une scrollbar apparait au lieu de compresser les pions
        token_scroll = QScrollArea()
        token_scroll.setWidget(token_container)
        token_scroll.setWidgetResizable(False) # garde la taille naturelle du contenu -> permet le scroll au lieu d'écraser les pions
        token_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        token_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        token_scroll.setFixedHeight(50) # juste assez haut pour les pions (30px) + marges
        
        # On ajoute la zone de défilement de la palette en dessous de la carte
        self.root_layout.addWidget(token_scroll)
        
        self.setCentralWidget(contain)
        # -----------------------------------------
        
        self.LimitBoundingLeft = LimitBounding(EnumBound.LEFT, self.univers)  
        _LimitBoundingLeft = self.LimitBoundingLeft
        self.univers.addItem(self.LimitBoundingLeft)

        self.LimitBoundingRight = LimitBounding(EnumBound.RIGHT, self.univers)  
        _LimitBoundingRight = self.LimitBoundingRight
        self.univers.addItem(self.LimitBoundingRight)

        # ── Carte de la session (injectée depuis gui_fonctions) ──────────
        if world is not None:
            self.set_map(scene, world, wall)
            
        self.api_url = "http://localhost:8080/api_dice.php" # <-- Pensez à mettre votre URL
        
        self.dice_poller = DicePollerThread(self.api_url)
        self.dice_poller.new_roll.connect(self.display_network_dice)
        self.dice_poller.start()
    
    def display_network_dice(self, data):
        # On n'affiche que les jets des joueurs (pas ceux que le MJ vient de lancer)
        if data.get("player") != "Maître du Jeu":
            display_text = f"Joueur: {data['player']}\n{data['details']}\n= {data['total']}"
            self.view.getDiceResult().setProperties(display_text)

    def _add_character_token(self):
        """Ouvre un sélecteur de fichier pour choisir l'image d'un personnage,
        puis ajoute un nouveau pion (affichant cette image) dans la palette,
        juste avant le bouton '+'."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir l'image du personnage",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not file_path:
            return  # L'utilisateur a annulé la sélection

        new_token_widget = DraggableTokenWidget(image_path=file_path)
        insert_index = self.token_layout.indexOf(self.add_character_btn)
        self.token_layout.insertWidget(insert_index, new_token_widget)
            
    # Arrêt propre du thread à la fermeture de la fenêtre
    def closeEvent(self, event):
        if hasattr(self, 'dice_poller'):
            self.dice_poller.stop()
        super().closeEvent(event)

    def set_map(self, scene, world, wall):
        """Injecte la grille existante depuis gui_fonctions.
        Peut etre appele avant ou apres show().
        """
        # Retirer une ancienne grille si present
        if getattr(self, 'map_grid', None) is not None:
            self.univers.removeItem(self.map_grid)

        self.map_grid = world
        self.map_grid.setZValue(-1)   # sous les profils, des, etc.

        # Cree un mur invisible pour la scene du gamemode
        # et met a jour la globale _wall du module grid.
        from src.MJ_application.grid import InvisibleWallLimit as _IWL
        import src.MJ_application.grid as _grid_mod
        if getattr(self, '_map_wall', None) is not None:
            self.univers.removeItem(self._map_wall)
        self._map_wall = _IWL(self.univers)
        _grid_mod._wall = self._map_wall
        self.univers.addItem(self._map_wall)

        self.univers.setItemIndexMethod(
            QGraphicsScene.ItemIndexMethod.NoIndex
        )
        self.univers.addItem(self.map_grid)

        # Reference directe sur la grille pour la vue
        self.view._grid = self.map_grid


class layerwindow(QGraphicsItem):
    def __init__(self, x, y, w, h,z,color, b : Interface_Profile):
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
        
        self.child = childrect(0,0,w,26,self,b)
    
        

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

    def __init__(self, x, y, w, h, parent, b : Interface_Profile):
        super().__init__(parent)
        self.setPos(x,y)
        self.rect = QRectF(0,0,w,h)
        self.color = parent.color
        self.setOpacity(1)
        self.parent = parent
        self.round = 10
        self.b = b
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
            self.b.setCreateWind(False)
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
    createwindow = False
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
        
        
        
        self.setFiche()
        
        self.clicked.connect(self.openFiche)
        

    def get_id(self):
        return self._idplayer  

    def get_place(self):
        return self.place

    def setCreateWind(self, b :bool):
        self.createwindow = False
    
    def setFiche(self):
        scale = self.parent().parent().transform().m11()
        layerwindow_dic["profile"+str(self.place)] = layerwindow(50+self.place*35,80+self.place*8,200,500,self.place,"Black",self)
        layerwindow_dic["profile"+str(self.place)].setScale(1/scale)
        z_dic[layerwindow_dic["profile"+str(self.place)]] = layerwindow_dic["profile"+str(self.place)].zValue()


    def openFiche(self):
        global layerwindow_dic
        global z_dic
        if self.createwindow == False:
            scale = self.parent().parent().transform().m11()
            layerwindow_dic["profile"+str(self.place)] = layerwindow(50+self.place*35,80+self.place*8,200,500,self.place,"Black",self)
            layerwindow_dic["profile"+str(self.place)].setScale(1/scale)
            z_dic[layerwindow_dic["profile"+str(self.place)]] = layerwindow_dic["profile"+str(self.place)].zValue()
            self.scene.addItem(layerwindow_dic["profile"+str(self.place)])
            self.createwindow = True
        
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

        self.Adventage_dice = self.parent().getAdvantageDice()
        self.more = self.parent().getplusDice() 
        self.moins = self.parent().getmoinsDice()

        
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
            self.dice_laucher.setconst(self.more.getRes(),0)
            self.dice_laucher.setconst(self.moins.getRes(),1)
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
                self.Adventage_dice.disconnectLauch()
                self.Adventage_dice.hide()
                
    
        return super().mousePressEvent(ev)

    def Reset(self):
        for i in self.dicebox :
            i.reset()
            self.more.resetRes()
            self.moins.resetRes()
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
    Const = {0:0,1:0}
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
        
        
    def getData(self):
        return self.Dices

    def setconst(self,const, i : int ):
        self.Const[i] = const
    
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
            if i != 0:
                m = self._convert(j)
                if m not in hasard:
                     hasard[m] = []
                for _ in range(i):
                    hasard[m].append(random.randint(1,m))
            j=j+1
        
        # Le formatage existant
        self.Result = self.resultToString(hasard)
        
        try:
            details_str = self.Result.split("=")[0].strip()
            total_val = int(self.Result.split("=")[1].strip())
        except:
            details_str = self.Result
            total_val = 0

        self.parent().getAdvantageDice().setconst(self.Const)
        self.parent().getAdvantageDice().setData(self.Dices)  
        self.parent().getAdvantageDice().connectLauch() 

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
        signe = 0
        for i in self.Const.keys():
            if self.Const[i] !=0:
                if signe == 0 :
                    s = s + self.Const[i]
                    t = t + str(self.Const[i])
                    signe = 1
                else : 
                    s = s- self.Const[i]
                    t = t + " -"+str(self.Const[i])


        t = t + "= "+str(s)
        self.parent().getAdvantageDice().setpred(s)
        print(t)
        return t

    def reset_data(self):
        for i in range(7):
            self.Dices[i]=0
    
    def reset(self):
        self.Const = {0:0,1:0}
        self.reset_data()
        self.disconnectLauch()
        self.hide()


class Retry_Dice(QPushButton):

    W = 80
    H = 25

    Result = ""
    pre_res = -1
    min = 1601
    Const = {0:0,1:0}

    def __init__(self, parent_view : View_GameMode):
        
        super().__init__(parent_view)
        
        

        self.setFixedSize(self.W, self.H)
        
        self.Dices = []
        for _ in range(7):
            self.Dices.append(0)

        self.hide()

        self.setStyleSheet("""
        QPushButton {
            border : 1px solid black;
            background-color: black;
            color: #ffffff;
            font-size: 13px;
            border-radius: 5px;
        }
        QPushButton:hover {
            
            font-size: 13.5px;
        }
        """)


        
        E = QGraphicsOpacityEffect(self)
        E.setOpacity(0.8)
        self.setGraphicsEffect(E)
              
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        
        self.raise_()
        self._reposition()

        self.setText("RELANCER")

    
    def _reposition(self):
        self.move((self.parent().width()-self.W)/2-((80*2.5)/1.4),(self.parent().height()-self.H)/2+115)
        

    def Align(self):
        self._reposition()

    def setpred(self,pred : int):
        self.pre_res = pred

    def setconst(self,const : dict):
        for i in const.keys() : 
            self.Const[i] = const[i]
    
    def setData(self,d : list):
        for i in range(7):
            self.Dices[i] = d[i]
        

    def updateDicesData(self,i,n):
        
        self.Dices[i] = n
        print(self.Dices)
        if self._dataSet == False: #A voir si on le conserve
            self._dataSet = True
    
    def connectLauch(self):
        self.setVisible(True)
        self.clicked.connect(self.lauch)
    
    def disconnectLauch(self):
        self.setVisible(False)
        self.min = 1601
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

        signe = 0
        for i in self.Const.keys():
            if self.Const[i] !=0:
                if signe == 0 :
                    s = s + self.Const[i]
                    t = t + str(self.Const[i])
                    signe = 1
                else : 
                    s = s- self.Const[i]
                    t = t + " -"+str(self.Const[i])

        t = t + "= "+str(s) + "\nBest Result : "
        if self.pre_res  > s :
            t = t+ str(self.pre_res)
            if self.min > s : 
                self.min = s

        else:
            t = t+ str(s)
            tmp = self.pre_res 
            self.pre_res = s
            if self.min > tmp : 
                self.min = tmp
        if self.min == 1601:
            self.min = self.pre_res
        t = t + "\nMin Result : " + str(self.min)

            
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

class Space_Dice_Constante(QLabel):
    W = 30
    H = 70


    def __init__(self, parent : View_GameMode, scene : QGraphicsScene,Dice_Box:DicesBox):

        super().__init__(parent)
        
        self.setFixedSize(self.W, self.H)
        
        self.scene = scene
        self.diceBox = Dice_Box

        self.setStyleSheet(
            "background-color: transparent;"
            "color: #ffffff;"
            "font-size: 12px;"
            "border-radius: 3px;")
        
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        
        self.raise_()
        self._reposition()

        self.plus = Dice_option_Const(self,"+",parent)
        self.moins = Dice_option_Const(self,"-",parent)
    
    def _reposition(self):
        parent = self.parent()
        if parent is not None:
            self.move((parent.width()-self.W)/2+self.diceBox.width()/2.1,parent.height()-self.H-60)


    def Align(self):
        self._reposition()     


class Dice_option_Const(QLabel):
    W = 15
    H = 15

    _Open = False

    def __init__(self, parent : Space_Dice_Constante, x : str , view : View_GameMode):

        super().__init__(parent)
        
        self.setFixedSize(self.W, self.H)
        
        self.text = x
        self.view = view
        

        self.setStyleSheet(
            "background-color: black;"
            "color: #ffffff;"
            "font-size: 17.5px;"
            "border-radius: 5px;")
        
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents,False)
        
        self.raise_()
        self._reposition()

    
    def _reposition(self):
        parent = self.parent()
        if parent is not None:
            if self.text == "+":
                self.move((parent.width()-self.W)-1,parent.height()-self.H-45)
            elif self.text == "-":
                self.move((parent.width()-self.W)-1,parent.height()-self.H-25)


    def Align(self):
        self._reposition()        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)  
        

        space = self.rect().toRectF()
        r = QRectF(space.left(),space.top(),space.right(),space.bottom()-4)
        font = painter.font()
        font.setBold(True)
        font.setPixelSize(15)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#FFFFFF")))
        if self.text == "+":
            painter.drawText(r,Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop  , str(self.text))
        elif self.text == "-":
            painter.drawText(r,Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop  , str(self.text))

    def mousePressEvent(self, ev):

        

        if self.text == "+":
            if self._Open == True and not self.view.getplusDice().isVisible():
                self._Open = False
            if self._Open == False :
                self.view.getmoinsDice().hide()
                self.view.getplusDice().setVisible(True)
                self._Open = True
            else:
                self.view.getplusDice().hide()
                self._Open = False
        
        elif self.text == "-":
            if self._Open == True and not self.view.getmoinsDice().isVisible():
                self._Open = False
            if self._Open == False :
                self.view.getplusDice().hide()
                self.view.getmoinsDice().setVisible(True)
                self._Open = True
            else:
                self.view.getmoinsDice().hide()
                self._Open = False
        


        return super().mousePressEvent(ev)

class Enter_Dice_Option_Const(QWidget):
    W = 45
    H = 50

    def __init__(self, parent_view : View_GameMode, t : str):
        super().__init__(parent_view)
        self.setFixedSize(self.W, self.H)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        E = QGraphicsOpacityEffect(self)
        E.setOpacity(1)
        self.setGraphicsEffect(E)

        self.text = ""
        self.round = 5
        self.res = 0
        self.t = t
        
        self._reposition()

        space = self.rect().toRectF()
        #r = QRectF(space.left()+2,space.top()+5,space.right()-2,space.bottom()-5)

        self.enter = QLineEdit(self)
        self.enter.setPlaceholderText(" ")
        self.enter.setStyleSheet(
            "background-color: #2b2b2b;"
            "border-radius: 5px;") 
        
        self.enter.setFixedSize(self.W-6, self.H/1.5)
        self.enter.move((self.W-(self.W-6))/2+2.5,space.top()+12)
        self.enter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.enter.setValidator(QIntValidator(1,100,self))
        self.enter.returnPressed.connect(self._send)


        self.hide()


    def _send(self):
        text = self.enter.text().strip()  
        if text == "":
            return
        self.res = int(text)
        self.enter.clear()
        self.hide()
        self.parent().getDicesBox().CheckLaucheable()

    def getRes(self):
        return self.res

    def resetRes(self):
        self.res=0 

    def _reposition(self):
        parent = self.parent()
        self.move(parent.width()/2+500/2-3,parent.height()-self.H-70)


    # Repositionne au resize de la vue (appele depuis View_Grid.resizeEvent,
    # comme pour Interface_MouseCoord)
    def Align(self):
        self._reposition()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)



        painter.setPen(QPen(Qt.black, 1.5))
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawRoundedRect(rect, self.round, self.round)

        header_rect = rect.adjusted(0, -6, 0, 0)
        font = painter.font()
        font.setBold(True)
        font.setPixelSize(15)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#e1dfdf")))
        painter.drawText(header_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self.t)

class DicePollerThread(QThread):
    """Thread qui vérifie les nouveaux dés en boucle sans bloquer l'interface"""
    new_roll = Signal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.last_roll_time = 0
        self.running = True

    def run(self):
        while self.running:
            try:
                response = requests.get(self.url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    roll_time = data.get("timestamp", 0)
                    # Si c'est un nouveau jet
                    if roll_time > self.last_roll_time:
                        self.new_roll.emit(data) # Envoie les données à l'interface
                        self.last_roll_time = roll_time
            except Exception as e:
                # NB: en build "windowed" (PyInstaller --noconsole, etc.) sys.stdout/stderr
                # valent None : un simple print() leverait alors une AttributeError NON
                # rattrapee ici, ce qui tuait silencieusement ce QThread au 1er echec reseau
                # (=> plus aucun jet de de affiche ensuite). On protege donc le print().
                try:
                    print(f"Erreur lors de la récupération des dés : {e}")
                except Exception:
                    pass
            
            time.sleep(1.5) # Attend 1.5s avant la prochaine requête

    def stop(self):
        self.running = False
        self.wait()


class DiceSenderThread(QThread):
    """Thread qui envoie les dés du MJ sans bloquer l'interface"""
    def __init__(self, url, payload):
        super().__init__()
        self.url = url
        self.payload = payload

    def run(self):
        try:
            requests.post(self.url, json=self.payload, timeout=2)
        except Exception:
            pass

class Token(QGraphicsEllipseItem):
    def __init__(self, x, y, size, color_hex=None, parent=None, image_path=None):
        super().__init__(0, 0, size, size, parent)
        self.setPos(x, y)

        # Memorise la couleur / le chemin d'image d'origine : map_sync.py lit
        # ces attributs en lecture seule pour synchroniser le pion vers le site web.
        self.color_hex = color_hex
        self.image_path = image_path

        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Recadre l'image en carré pour qu'elle remplisse joliment le pion circulaire
                scaled = pixmap.scaled(
                    int(size), int(size),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.setBrush(QBrush(scaled))
            else:
                self.setBrush(QBrush(QColor("#888888"))) # Image invalide -> couleur de repli
        else:
            self.setBrush(QBrush(QColor(color_hex)))

        self.setPen(QPen(QColor("#ffffff"), 2)) # Bordure blanche
        
        # Rend le pion déplaçable et sélectionnable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(100) # Assure que le pion est toujours au-dessus de la grille

    def contextMenuEvent(self, event):
        # Un clic droit sur le pion le supprime de la scène
        if self.scene():
            self.scene().removeItem(self)
        event.accept()
        
class DraggableTokenWidget(QLabel):
    """Un widget représentant un pion dans la barre d'outils, prêt à être glissé.
    Soit une couleur fixe (color_hex), soit l'image d'un personnage (image_path)."""
    def __init__(self, color_hex=None, image_path=None):
        super().__init__()
        self.color_hex = color_hex
        self.image_path = image_path
        self._pixmap_src = QPixmap(image_path) if image_path else None

        self.setFixedSize(30, 30)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        if self._pixmap_src is not None and not self._pixmap_src.isNull():
            self.setToolTip(image_path) # Le rendu se fait dans paintEvent (recadrage circulaire)
        else:
            self.setStyleSheet(f"background-color: {color_hex}; border-radius: 15px; border: 2px solid #555;")

    def paintEvent(self, event):
        # Pion "image" : on dessine nous-mêmes pour recadrer l'image en cercle
        if self._pixmap_src is not None and not self._pixmap_src.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
            clip_path = QPainterPath()
            clip_path.addEllipse(rect)
            painter.setClipPath(clip_path)

            scaled = self._pixmap_src.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter.drawPixmap(-x, -y, scaled)

            painter.setClipping(False)
            painter.setPen(QPen(QColor("#555555"), 2))
            painter.drawEllipse(rect)
        else:
            # Pion "couleur" : le rendu vient du QSS (background-color + border-radius)
            super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        # S'assure qu'on a bougé la souris d'une distance minimale avant de déclencher le drag
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # Création de l'événement de Drag & Drop
        drag = QDrag(self)
        mime_data = QMimeData()
        if self.image_path:
            mime_data.setText(f"IMG::{self.image_path}") # Préfixe pour distinguer une image d'une couleur
        else:
            mime_data.setText(self.color_hex) # On transmet la couleur au format texte
        drag.setMimeData(mime_data)
        
        # Capture l'apparence du widget pour qu'elle suive le curseur de la souris
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        drag.exec(Qt.DropAction.CopyAction)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    gamemode = MainWindow()
    gamemode.show()
    sys.exit(app.exec())