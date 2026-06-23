import sys


from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGraphicsItem,
    QVBoxLayout,
    QHBoxLayout,
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
    QMenu,
    
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
    QAction,
    QCursor,
    QMouseEvent,
    QKeySequence,
    
) 

_wall = None

_view_bounds = {"cw": 350.0, "ch": 260.0}

_col_cell = {"TL" : (None,None) , "TR" : (None,None) , "BL" : (None,None) , "BR" : (None,None) }

_cell_cp_data = {"fill" : False ,"img" : None , "text" : None}

# ---------------------------------------------------------------------------
# une seule lecture + redimensionnement par (path, w, h)
# ---------------------------------------------------------------------------
_pixmap_cache: dict[tuple, QPixmap] = {}

def _get_scaled_pixmap(path: str, w: int, h: int) -> QPixmap:
    key = (path, w, h)
    if key not in _pixmap_cache:
        _pixmap_cache[key] = QPixmap(path).scaled(
            w, h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    return _pixmap_cache[key]


class Interface_Proprieties(QGraphicsItem):
    def __init__(self, xy :QPointF,text : str):
        super().__init__()
        self.setPos(xy.x()-25,xy.y()-50)
        self.rect = QRectF(xy.x()-25.,xy.y()-50,200,320)
        
        self.x = xy.x()-25
        self.y = xy.y()-50
        
        self.text = text

        self.setZValue(15)

        self.round = 5

        self.setCursor(Qt.CursorShape.ArrowCursor)
        

    #Espace de rafraichissement un peu plus grand que le rect        
    def boundingRect(self):
        return self.rect.adjusted(-1,-1,1,1)
        
    #Ajuste l'espace invisible autour l'objet (comparable à une hitbox)    
    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect,self.round,self.round)
        
        return path

    #Dessine
    def paint(self, painter = None, option = None, widget = None):
         
        painter.setPen(QPen(Qt.black,1.5))
        painter.setBrush(QBrush( QColor("#212121")))
        painter.drawRoundedRect(self.rect,self.round,self.round)

        
        print(self.text)
        font = painter.font()
        font.setBold(True)
        font.setPixelSize(15)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#e1dfdf")))
        painter.drawText(self.rect,Qt.AlignmentFlag.AlignHCenter| Qt.AlignmentFlag.AlignJustify,"Proprietes")
        
        font.setPixelSize(12)
        
        painter.setFont(font)
        painter.drawText(self.rect,Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignJustify,self.text)
        


class Interface_Cell(QGraphicsRectItem):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)

        self._coord = (None, None)
        self._name = ""

        self._img = Img()
        self.Path = None
        self._text = None
        self.w = w
        self.h = h

    # boundingRect() supprimé : Qt l'appelait des millions de fois via

    def paint(self, painter, option, /, widget = ...):
        # render hints supprimés ici : ils sont déjà activés globalement
        # sur la QGraphicsView (ligne dans Window.__init__), inutile de les
        # répéter sur chaque cellule à chaque frame.
        if isinstance(self._img, Img):
            if self._img.pixmap().isNull():
                self.setPen(QPen(Qt.black, 0.5))
                self.setBrush(QBrush(QColor("#686767ff")))
        elif self._img is None:
            self.setPen(QPen(Qt.black, 0.5))
            self.setBrush(QBrush(QColor("#686767ff")))

        return super().paint(painter, option, widget)

    def setCoord(self, x: int, y: int):
        self._coord = (x, y)

    def setName(self, i: str):
        self._name = i

    def getName(self):
        return self._name

    def setImage(self, Path: str):
        self.Path = Path
        # utilise le cache au lieu de recharger depuis le disque
        scaled = _get_scaled_pixmap(Path, self.w, self.h)
        # Ne retirer de la scène que si l'item y est déjà (pixmap non null = déjà posé)
        if not self._img.pixmap().isNull() and self._img.scene() is not None:
            self._img.scene().removeItem(self._img)
        self._img.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self._img.setPixmap(scaled)
        self._img.setPos(self.w * self._coord[0], self.h * self._coord[1])
        self._img.setParentItem(self)
        self.update()



    # Copy Paste imgae

    def _CPimage(self):
        if not (self._img.pixmap().isNull()):
            self._img.setPos(self.w * self._coord[0], self.h * self._coord[1])
            self._img.setParentItem(self)
        else : 
            self.scene().removeItem(self._img)
            del self._img
            self._img = Img()
        self.update()

    def Copy(self):
        global _cell_cp_data
        _cell_cp_data["fill"] = True
        _cell_cp_data["img"] = self._img

    def Paste(self):
        global _cell_cp_data
        if self._img is not None:
            self.scene().removeItem(self._img)
            tmp = self._img
            del tmp
        self._img = _cell_cp_data["img"].copy_for_cell()
        self._CPimage()

    def Cut(self):
        self.Copy()
        self.scene().removeItem(self._img)
        tmp = self._img
        del tmp
        self._img = None
        self.update()

    def Proprieties(self,xy:QPointF|None):
        if xy is not None : 
            view =self.scene().views()[0]
            text = "\n\n\n    Coord :   " + str(self._coord[0]) + " : " + str(self._coord[0]) + "\n" + "\n    Img :   "
            if self._img is None:
                text = text + "None\n"
            elif self._img.pixmap().isNull():
                text = text + "None\n"
            else:
                text = text + self.Path + "\n"
            prop = Interface_Proprieties(xy,text)
            view.addItemNeeds(prop)
            self.scene().addItem(prop)
        
        


class Interface_MouseCoord(QLabel):
    """Overlay fixe en haut a droite de la QGraphicsView.
    Taille fixe, z-order au-dessus de tout (widget enfant de la vue),
    non affecte par le pan ni le zoom."""

    W = 120
    H = 22

    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.setFixedSize(self.W, self.H)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "background-color: rgba(30,30,30,180);"
            "color: #ffffff;"
            "font-size: 12px;"
            "border-radius: 3px;"
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.raise_()
        self._reposition()

    def _reposition(self):
        parent = self.parent()
        if parent is not None:
            self.move(parent.width() - self.W - 4, 4)

    def setMxy(self, x: float, y: float):
        self.setText(f"{round(x, 1)} : {round(y, 1)}")

    def align(self):
        self._reposition()


class View_Grid(QGraphicsView):

    zoomfac = 1.15
    zoomMax = 2.5
    zoomMin = 0.5

    def __init__(self, scene):
        super().__init__(scene)

        self._grid = None
        self._shift_press = False

        self._cell_select = None
        self._cell_select_use = False

        self.zoom = 1.0
        self._fitted_once = False

        self._Mxy = None

        self._Items_needs = []

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        #  mise à jour viewport limitée à la zone modifiée (pas toute la vue)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate
        )

    def _update_world_bounds(self):
        global _wall, _view_bounds

        if self.scene() is None:
            return

        visible = self.mapToScene(self.viewport().rect()).boundingRect()
        _view_bounds["cw"] = visible.center().x()
        _view_bounds["ch"] = visible.center().y()

        if _wall is not None:
            _wall.sizeUpdate(visible)

    # résolution mathématique de la cellule sous le curseur :
    # au lieu d'appeler itemAt() (qui parcourt les 160 000 enfants un par un),
    # on calcule directement la colonne/ligne à partir de la position.
    def _cell_at_view_pos(self, view_pos) -> "Interface_Cell | None":
        if self._grid is None:
            return None
        scene_pos = self.mapToScene(view_pos)
        grid_pos = self._grid.mapFromScene(scene_pos)
        s = self._grid.s_cell
        n = self._grid.n
        col = int(grid_pos.x() / s)
        row = int(grid_pos.y() / s)
        if 0 <= col < n and 0 <= row < n:
            idx = row * n + col
            return self._grid.atoms[idx]
        return None

    def mouseMoveEvent(self, event):
        # itemAt() complètement supprimé du mouseMoveEvent.
        # C'était la source principale du lag drag : avec NoIndex, Qt parcourt
        # tous les items de premier niveau à chaque micro-mouvement.
        # Le movable est maintenant géré dans mousePressEvent / mouseReleaseEvent
        # (activé une fois au clic, désactivé une fois au relâchement).

        for it in self._Items_needs:
            if hasattr(it, "setMxy"):
                it.setMxy(event.position().x(), event.position().y())
        
        return super().mouseMoveEvent(event)

    def addItemNeeds(self, item : QGraphicsItem):
        self._Items_needs.append(item)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Shift:
            self._shift_press = True

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                if self._cell_select is not None:
                    self._cell_select.Copy()
                    self._cell_select_use = True

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_V:
                if self._cell_select is not None:
                    self._cell_select.Paste()
                    self._cell_select_use = True

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_X:
                if self._cell_select is not None:
                    self._cell_select.Cut()
                    self._cell_select_use = True

        return super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # on utilise la résolution mathématique pour le double-clic
        cell = self._cell_at_view_pos(event.position().toPoint())
        if cell is not None:
            if cell != self._cell_select:
                self._cell_select_use = False
                cell.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                cell.setSelected(True)
                self._cell_select = cell
            elif not cell.isSelected():
                cell.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                cell.setSelected(True)
        return super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        view_pt = event.position().toPoint()

        #PAS PARFAIT
        for it in self._Items_needs:
            if isinstance(it,Interface_Proprieties) :
                if  not ((it.x+7 < view_pt.x()< it.x+164) and (it.y < view_pt.y() < it.y + 275)) : 
                    self.scene().removeItem(it)

        # Désélection cellule précédente si on clique ailleurs
        if self._cell_select is not None:
            cell = self._cell_at_view_pos(view_pt)
            if cell != self._cell_select:
                self._cell_select.setFlag(
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False
                )
                if not self._cell_select_use:
                    self._cell_select = None

        if event.button() == Qt.MouseButton.RightButton:
            self._Mxy = view_pt
            print(self._Mxy)

        # activer le movable ici (une seule fois par clic).
        # On remonte la hiérarchie pour gérer tous les cas :
        #   fond Grid          → item est Grid
        #   cellule sans image → item est Interface_Cell, parent est Grid
        #   cellule avec image → item est Img, parent est Interface_Cell, grand-parent est Grid
        item = self.itemAt(view_pt)
        candidate = item
        while candidate is not None:
            if isinstance(candidate, Grid):
                candidate.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
                self._grid = candidate
                break
            candidate = candidate.parentItem()


        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # désactiver le movable au relâchement
        if self._grid is not None:
            self._grid.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        return super().mouseReleaseEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            self._shift_press = False
        return super().keyReleaseEvent(event)

    # zoom non au point
    def wheelEvent(self, event):

        if self._shift_press:
            angle = event.angleDelta().y()
            if angle == 0:
                event.accept()
                return

            factor = self.zoomfac if angle > 0 else 1 / self.zoomfac
            new_zoom = max(self.zoomMin, min(self.zoomMax, self.zoom * factor))
            applied = new_zoom / self.zoom

            if applied != 1.0:
                self.zoom = new_zoom

                cursor_scene = self.mapToScene(event.position().toPoint())
                self.scale(applied, applied)
                cursor_scene_after = self.mapToScene(event.position().toPoint())
                delta = cursor_scene_after - cursor_scene
                self.translate(delta.x(), delta.y())

                self._update_world_bounds()

            event.accept()
            return

        return super().wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        if not self._fitted_once and self.scene() is not None:
            self.fitInView(
                self.scene().sceneRect(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            )
            self.zoom = self.transform().m11()
            self._fitted_once = True

        self._update_world_bounds()
        # Repositionner l'overlay coordonnees apres chaque resize
        for it in self._Items_needs:
            if hasattr(it, "align"):
                it.align()
        super().resizeEvent(event)

    def contextMenuEvent(self, event):
        # résolution mathématique pour le menu contextuel aussi
        # QContextMenuEvent.pos() retourne déjà un QPoint (pas de .position() ici)
        cell = self._cell_at_view_pos(event.pos())
        global _cell_cp_data
        
        if cell is not None:
            self.menu = QMenu(self)

            if _cell_cp_data["fill"]:
                nameAction = QAction("Paste", self)
                nameAction.triggered.connect(lambda: cell.Paste())
                self.menu.addAction(nameAction)

            nameAction = QAction("Copy", self)
            nameAction.triggered.connect(lambda: cell.Copy())
            self.menu.addAction(nameAction)

            nameAction = QAction("Cut", self)
            nameAction.triggered.connect(lambda: cell.Cut())
            self.menu.addAction(nameAction)

            nameAction = QAction("Proprieties", self)
            nameAction.triggered.connect(lambda: cell.Proprieties(self._Mxy))
            self.menu.addAction(nameAction)

            ## add other required actions
            self.menu.popup(QCursor.pos())
            return  # on court-circuite super() pour éviter le double-menu

        return super().contextMenuEvent(event)


class Window(QMainWindow):

    def __init__(self, n, s_cell):
        super().__init__()

        self.s_cell = s_cell
        self.size = n

        self.setMinimumSize(700, 520)
        #cree une scene graphique de taille 700x520 
        self.TheVoid = QGraphicsScene()
        self.TheVoid.setSceneRect(0, 0, 700, 520)

        # désactivation de l'index BSP : inutile ici (la grille bouge
        # comme un seul bloc rigide), et sa mise à jour forçait Qt à recalculer
        # les bounding rects des 160 000 enfants à chaque déplacement.
        self.TheVoid.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        self.view = View_Grid(self.TheVoid)

        self.view.setRenderHint(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(QBrush(QColor("#171717ff")))
        self.view.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setMouseTracking(True)

        contain = QWidget()
        #root_layout.setSpacing(12)
        self.root_layout = QVBoxLayout(contain)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.addWidget(self.view)
        self.setCentralWidget(contain)

        # Interface_MouseCoord est maintenant un QLabel overlay sur la vue
        # (pas un item de scene) : taille fixe, toujours en haut a droite,
        # au-dessus de tout, insensible au pan/zoom.
        self.InterMouseCoor = Interface_MouseCoord(self.view)
        self.view.addItemNeeds(self.InterMouseCoor)

        global _wall
        _wall = InvisibleWallLimit(self.TheVoid)
        self.TheVoid.addItem(_wall)

        self.world = Grid(n, s_cell)
        (self.world.atoms[0]).setName("TL")
        (self.world.atoms[0]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        (self.world.atoms[n - 1]).setName("TR")
        (self.world.atoms[n - 1]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        (self.world.atoms[(n - 1) * n]).setName("BL")
        (self.world.atoms[(n - 1) * n]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        (self.world.atoms[(n - 1) * n + (n - 1)]).setName("BR")
        (self.world.atoms[(n - 1) * n + (n - 1)]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.TheVoid.addItem(self.world)

        # On donne à la vue une référence directe sur la grille pour que
        # _cell_at_view_pos() fonctionne même avant le premier mouseMoveEvent.
        self.view._grid = self.world


class Grid(QGraphicsRectItem):

    def __init__(self, n, s_cell):
        super().__init__(0, 0, n * s_cell, n * s_cell)
        self.n = n
        self.s_cell = s_cell
        self.setZValue(0)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        for i in range(n):
            for j in range(n):
                cell = Interface_Cell(s_cell * j, s_cell * i, s_cell, s_cell)
                cell.setCoord(j, i)
                cell.setParentItem(self)
                if j <= i:
                    cell.setImage("image/sponge.jpg")
        self.atoms = [item for item in self.childItems() if isinstance(item, Interface_Cell)]

        self._gpos = QPointF(0, 0)

    def itemChange(self, change, value):

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            global _col_cell
            global _wall
            global _view_bounds
            new_pos = value
            old_pos = self.pos()
            l = self.n
            b = []
            b.append(self.atoms[0])
            b.append(self.atoms[l - 1])
            b.append(self.atoms[(l - 1) * l])
            b.append(self.atoms[(l - 1) * l + (l - 1)])

            cw = _view_bounds["cw"]
            ch = _view_bounds["ch"]

            for i in range(len(b)):
                if b[i].getName() != "":
                    # une seule lecture/écriture par coin (était 2 avant)
                    prev = _col_cell[b[i].getName()][1]
                    _col_cell[b[i].getName()] = (prev, b[i].scenePos())

            for i in range(len(b)):
                if i == 0:
                    if not (b[i].scenePos().x() < cw - (self.n * self.s_cell / 2) or b[i].scenePos().y() < ch - (self.n * self.s_cell / 2)):
                        # QRectF + intersects() au lieu de QGraphicsRectItem temporaire
                        j = QRectF(b[i].scenePos().x(), b[i].scenePos().y(), b[i].rect().width(), b[i].rect().height())
                        if _wall.path().intersects(j):
                            return QPointF(min(old_pos.x(), new_pos.x()), min(old_pos.y(), new_pos.y()))

                        inter = self._sweep(b[i], i)
                        if inter is None:
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(min(old_pos.x(), new_pos.x()), min(old_pos.y(), new_pos.y()))
                        if b[i].scenePos().x() >= cw + 8 or b[i].scenePos().y() >= ch + 8:
                            self.ungrabMouse()
                            return QPointF(self._gpos.x() + cw - self.s_cell, self._gpos.y() + ch - self.s_cell)

                elif i == 1:
                    if not (b[i].scenePos().x() + self.n * self.s_cell - self.s_cell > cw + (self.n * self.s_cell / 2) or b[i].scenePos().y() < ch - (self.n * self.s_cell / 2)):
                        j = QRectF(b[i].scenePos().x() + self.n * self.s_cell - self.s_cell, b[i].scenePos().y(), b[i].rect().width(), b[i].rect().height())
                        if _wall.path().intersects(j):
                            return QPointF(max(old_pos.x(), new_pos.x()), min(old_pos.y(), new_pos.y()))

                        inter = self._sweep(b[i], i)
                        if inter is None:
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(max(old_pos.x(), new_pos.x()), min(old_pos.y(), new_pos.y()))
                        if b[i].scenePos().x() + self.n * self.s_cell - self.s_cell <= cw - 8 or b[i].scenePos().y() >= ch + 8:
                            self.ungrabMouse()
                            return QPointF(self._gpos.x() + cw - (self.n * self.s_cell - self.s_cell) + self.s_cell, self._gpos.y() + ch - self.s_cell)

                elif i == 2:
                    if not (b[i].scenePos().y() + self.n * self.s_cell - self.s_cell > ch + (self.n * self.s_cell / 2) or b[i].scenePos().x() < ch - (self.n * self.s_cell / 2)):
                        j = QRectF(b[i].scenePos().x(), b[i].scenePos().y() + self.n * self.s_cell - self.s_cell, b[i].rect().width(), b[i].rect().height())
                        if _wall.path().intersects(j):
                            return QPointF(min(old_pos.x(), new_pos.x()), max(old_pos.y(), new_pos.y()))

                        inter = self._sweep(b[i], i)
                        if inter is None:
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(min(old_pos.x(), new_pos.x()), max(old_pos.y(), new_pos.y()))
                        if b[i].scenePos().x() >= cw + 8 or b[i].scenePos().y() + self.n * self.s_cell - self.s_cell <= ch - 8:
                            self.ungrabMouse()
                            return QPointF(self._gpos.x() + cw - self.s_cell, self._gpos.y() + ch - (self.n * self.s_cell - self.s_cell) + self.s_cell)

                elif i == 3:
                    if not (b[i].scenePos().y() + self.n * self.s_cell - self.s_cell > ch + (self.n * self.s_cell / 2) or b[i].scenePos().x() + self.n * self.s_cell - self.s_cell > cw + (self.n * self.s_cell / 2)):
                        j = QRectF(b[i].scenePos().x() + self.n * self.s_cell - self.s_cell, b[i].scenePos().y() + self.n * self.s_cell - self.s_cell, b[i].rect().width(), b[i].rect().height())
                        if _wall.path().intersects(j):
                            return QPointF(max(old_pos.x(), new_pos.x()), max(old_pos.y(), new_pos.y()))

                        inter = self._sweep(b[i], i)
                        if inter is None:
                            return super().itemChange(change, value)
                        col = _wall.mapFromScene(_wall.shape())
                        if inter.intersects(col):
                            return QPointF(max(old_pos.x(), new_pos.x()), max(old_pos.y(), new_pos.y()))
                        if b[i].scenePos().x() + self.n * self.s_cell - self.s_cell <= cw - 8 or b[i].scenePos().y() + self.n * self.s_cell - self.s_cell <= ch + 8:
                            self.ungrabMouse()
                            return QPointF(self._gpos.x() + cw - (self.n * self.s_cell - self.s_cell) + self.s_cell, self._gpos.y() + ch - (self.n * self.s_cell - self.s_cell) + self.s_cell)

            self.update()

        return super().itemChange(change, value)

    def _sweep(self, b: Interface_Cell, correction: int):
        global _col_cell

        w = b.rect().width() + 4   # rect() au lieu de boundingRect()
        h = b.rect().height() + 4
        if _col_cell.get(b.getName())[0] is None:
            return None
        if correction == 0:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x(), _col_cell.get(b.getName())[0].y())
            new_cell = QPointF(_col_cell.get(b.getName())[1].x(), _col_cell.get(b.getName())[1].y())
        elif correction == 2:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x(), _col_cell.get(b.getName())[0].y() + self.n * self.s_cell - self.s_cell)
            new_cell = QPointF(_col_cell.get(b.getName())[1].x(), _col_cell.get(b.getName())[1].y() + self.n * self.s_cell - self.s_cell)
        elif correction == 1:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x() + self.n * self.s_cell - self.s_cell, _col_cell.get(b.getName())[0].y())
            new_cell = QPointF(_col_cell.get(b.getName())[1].x() + self.n * self.s_cell - self.s_cell, _col_cell.get(b.getName())[1].y())
        elif correction == 3:
            old_cell = QPointF(_col_cell.get(b.getName())[0].x() + self.n * self.s_cell - self.s_cell, _col_cell.get(b.getName())[0].y() + self.n * self.s_cell - self.s_cell)
            new_cell = QPointF(_col_cell.get(b.getName())[1].x() + self.n * self.s_cell - self.s_cell, _col_cell.get(b.getName())[1].y() + self.n * self.s_cell - self.s_cell)

        dx = new_cell.x() - old_cell.x()
        dy = new_cell.y() - old_cell.y()

        # De l'intervalle [old;new] on obitent old et new 
        old = QPainterPath()
        old.addRect(QRectF(old_cell.x() - 4, old_cell.y() - 4, w, h))
        new = QPainterPath()
        new.addRect(QRectF(new_cell.x() - 4, new_cell.y() - 4, w, h))

        # De l'intervalle [old;new] on determine ]old;new[
        intersection = QPainterPath()
        if dx != 0:
            intersection.moveTo(old_cell.x(), old_cell.y())
            intersection.lineTo(old_cell.x() + w, old_cell.y())
            intersection.lineTo(new_cell.x() + w, new_cell.y())
            intersection.lineTo(new_cell.x(), new_cell.y())
            intersection.closeSubpath()

            intersection.moveTo(old_cell.x(), old_cell.y() + h)
            intersection.lineTo(old_cell.x() + w, old_cell.y() + h)
            intersection.lineTo(new_cell.x() + w, new_cell.y() + h)
            intersection.lineTo(new_cell.x(), new_cell.y() + h)
            intersection.closeSubpath()

        if dy != 0:
            intersection.moveTo(old_cell.x(), old_cell.y())
            intersection.lineTo(old_cell.x(), old_cell.y() + h)
            intersection.lineTo(new_cell.x(), new_cell.y() + h)
            intersection.lineTo(new_cell.x(), new_cell.y())
            intersection.closeSubpath()

            intersection.moveTo(old_cell.x() + w, old_cell.y())
            intersection.lineTo(old_cell.x() + w, old_cell.y() + h)
            intersection.lineTo(new_cell.x() + w, new_cell.y() + h)
            intersection.lineTo(new_cell.x() + w, new_cell.y())
            intersection.closeSubpath()

        return old.united(new).united(intersection)


class Img(QGraphicsPixmapItem):

    def paint(self, painter, option, widget):
        # render hints supprimés ici aussi (activés sur la View)
        return super().paint(painter, option, widget)

    def copy_for_cell(self):
        img = Img()
        img.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        img.setPixmap(self.pixmap())
        return img


class InvisibleWallLimit(QGraphicsPathItem):
    """Croix de murs invisibles utilisee par Grid pour limiter le
    deplacement. Sa position/etendue suit desormais la zone REELLEMENT
    VISIBLE dans la vue (passee via sizeUpdate), et non plus le centre
    fixe de la sceneRect d'origine -> elle reste coherente quand on
    zoome ou qu'on redimensionne la fenetre."""

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.setZValue(0)
        self.setPen(QPen(QColor("#8f8f8fff"), 2))
        self.setPos(0, 0)
        self.sizeUpdate(scene.sceneRect())

    def sizeUpdate(self, visible_rect: QRectF):
        cx = visible_rect.center().x()
        cy = visible_rect.center().y()
        span_w = max(visible_rect.width(), 1.0) * 4
        span_h = max(visible_rect.height(), 1.0) * 4

        walls = QPainterPath()
        walls.addRect(cx, cy - span_h / 2, 1, span_h)
        walls.addRect(cx - span_w / 2, cy, span_w, 1)
        self.setPath(walls)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = Window(400, 64)
    window.show()
    sys.exit(app.exec())