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
    
)
from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QRectF, 
    QSize,
    
    
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

#METTRE DES FONCT / VAR EN PRIVE SI NECESSAIRE "__"

class MainWindow(QMainWindow):

    def __init__(self):
        """
        Constructeur : initialise les objets métier, configure la fenêtre
        et crée tous les widgets de l'interface.
        """
        super().__init__()   # Initialise QMainWindow (obligatoire)
        
        self.setMinimumSize(700, 520)
        self.setWindowTitle("GameMode")

        #cree une scene graphique de taille 700x520 
        self.univers = QGraphicsScene()
        self.univers.setSceneRect(0,0,700, 520)
        # cree un espace de "visualisation"/"rendu" de la scene
        self.view = QGraphicsView(self.univers)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform) #ant
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setBackgroundBrush(QBrush(QColor("#e8e8e8ff")))

        contain = QWidget()
        self.root_layout = QVBoxLayout(contain)
        #root_layout.setSpacing(12)
        self.root_layout.setContentsMargins(7, 7, 7, 7)        
        self.root_layout.addWidget(self.view)
        self.setCentralWidget(contain)

        self.profile_rect = layerrect(0,0,60,400,1)    

        layer1 = layerwindow(50,50,200,500,3,"Black")
        layer2 = layerwindow(300,50,200,500,2,"Black")
        layer3 = layerwindow(300,50,200,500,4,"Black")
        z_dic[layer1] = layer1.zValue()
        z_dic[layer2] = layer2.zValue()
        z_dic[layer3] = layer2.zValue()         
        self.univers.addItem(layer1)
        self.univers.addItem(layer2)
        self.univers.addItem(layer3)
        self.univers.addItem(self.profile_rect)
        self.profile_rect.Align(Qt.AlignmentFlag.AlignVCenter)
        
        #self.user_profile_1 = self.addButItem(15,20)
        
        

    def addButItem(self,x,y):
        button = QPushButton("L") # cree la donnée bouton
        button.setFixedSize(26, 26)
        #button.clicked.connect(self.close) # Bouton clické -> lance close()
        # Fait une beauté au bouton
        button.setStyleSheet("""
                QPushButton {
                             background : transparent ;
                             border : none ;
                             font-size : 22px;
                             }
                QPushButton:hover {
                             font-size : 23px;
                             }""")
        
        #conteneur du boutton
        self.root_layout.addWidget(button)
        
        
        #Defini l'espace comme un lieu ne pouvant pas faire bouger layerwindow
        #cont.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,False)
        #return cont

    def resizeEvent(self, event: QResizeEvent):
        
        self.view.fitInView(self.univers.sceneRect(),Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.profile_rect.Align(Qt.AlignmentFlag.AlignVCenter)
        scale = self.view.transform().m11()

        for item in self.univers.items():
            if isinstance(item,layerwindow):
                item.setScale(1.0/scale)


        print("here")
        super().resizeEvent(event)
   


class layerwindow(QGraphicsItem):
    def __init__(self, x, y, w, h,z,color):
        super().__init__()
        self.setPos(x,y)
        self.rect = QRectF(0,0,w,h)
        self.color = QColor(color)
        self.setZValue(z)

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 
        painter.setPen(QPen(Qt.black,3))
        painter.setBrush(QBrush(self.color))
        painter.drawRoundedRect(self.rect,self.round,self.round)

    
    


class childrect(QGraphicsItem):

    def __init__(self, x, y, w, h, parent):
        super().__init__(parent)
        self.setPos(x,y)
        self.rect = QRectF(0,0,w,h)
        self.color = parent.color
        self.setOpacity(1)
        self.parent = parent
        self.round = 10
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)
        self.button = self.addButItem(80/100*w,y-1)
        
        

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 
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
                            font-size : 13;
                             }
                QPushButton:hover {
                             font-size : 14px;
                             }""")
        
        #conteneur du boutton
        cont = QGraphicsProxyWidget(self)
        cont.setWidget(button)
        
        cont.setPos(x,y)
        # Defini l'espace comme un lieu ne pouvant pas faire bouger layerwindow
        cont.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,False)
       
        return cont

    #Ferme et supprime toute le layerwindow (voir s'il faudra le suppr ou le concerver à l'avanir)
    def close(self):
        scene = self.scene()
        if scene is not None :
            scene.removeItem(self.parent)
            del self.parent           
            del self

class layerrect(QGraphicsRectItem):
    def __init__(self, x, y, w, h,z):
        super().__init__(0, 0, w, h)
        self.setPos(x,y)
        self.rect = QRectF(0,0,w,h)
        
        self.color = QColor(255, 0, 0, 255)
        self.setBrush(QBrush(self.color))
        self.setPen(QPen(Qt.black,-1))
        self.setZValue(z)

        self.round = 12

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable,False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemContainsChildrenInShape)
        

        self.setOpacity(0.8)
                    
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def Align(self,align : Qt.AlignmentFlag):
        scene = self.scene().sceneRect()
        if align == Qt.AlignmentFlag.AlignVCenter:
            y = scene.top() + (scene.height()- self.rect.height()) /2 
        
        x = scene.left() -5
        self.setPos(x,y)

        
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    gamemode = MainWindow()
    gamemode.show()
    sys.exit(app.exec())