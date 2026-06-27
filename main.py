########################################################################
## QT GUI BY SPINN TV(YOUTUBE)
########################################################################
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor,QBrush,QPen,QPainter    

from src.MJ_gamemode.MJ_gamemode import MainWindow as GMainWindow
########################################################################
## IMPORTS
########################################################################
import sys
########################################################################
# IMPORT GUI FILE
from src.ui_QCustomQMainWindow import *
########################################################################
# IMPORT FUNCTION
from src.MJ_application.gui_fonctions import GuiFunctions
from src.MJ_application.LogReaderThread import LogReaderThread
########################################################################
# IMPORT Custom widgets
from Custom_Widgets import loadJsonStyle
from Custom_Widgets import QMainWindow as CustomMain
from Custom_Widgets.QAppSettings import QAppSettings
########################################################################

########################################################################
## MAIN WINDOW CLASS
########################################################################
class EditorMainWindow(CustomMain):
    def __init__(self, parent=None):
        CustomMain.__init__(self)

        self.ui = Ui_CustomMainWindow()
        self.ui.setupUi(self)

        # Use this to specify your json file(s) path/name
        loadJsonStyle(self, self.ui, jsonFiles = {
            "json-styles/style.json"
            }) 

        ########################################################################

        #######################################################################
        # SHOW WINDOW
        #######################################################################
        self.show()

        # self = CustomMain class
        QAppSettings.updateAppSettings(self)

        self.app_functions = GuiFunctions(self)


class ModeMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)
        
        self.edit = EditorMainWindow()
        self.game = GMainWindow()
        self.mode_list = []
        self.mode = QStackedWidget()
        self.mode.addWidget(self.edit)
        self.mode_list.append(self.edit)
        self.mode.addWidget(self.game)
        self.mode_list.append(self.game)

        root.addWidget(self.mode)

        self.choose_mode0 = choose_Mode("Editor",central,0,self)
        self.choose_mode1 = choose_Mode("GameMode",central,1,self)
        
        self.showmode(0)
        
    def showmode(self,n : int):
        if n == 0 :
            self.mode.setCurrentIndex(n)
            self.choose_mode0.hide()
            self.choose_mode1.setVisible(True)
        elif n == 1:
            self.mode.setCurrentIndex(n)
            self.choose_mode1.hide()
            self.choose_mode0.setVisible(True)

        
    
    def resizeEvent(self, event):
        self.choose_mode0.Align()
        self.choose_mode1.Align()
        
        

        return super().resizeEvent(event)

class choose_Mode(QWidget):
    W = 60
    H = 20

    def __init__(self, text : str , parent : ModeMainWindow, i : int , coworker : ModeMainWindow):
        super().__init__(parent)
        self.setFixedSize(self.W, self.H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.value = i
        self.text = text
        self.coworker = coworker
        self.hide()

        self.setStyleSheet("""
            QWidget {
                
                border : 2px dashed white; ;
                }
        """)
      
        E = QGraphicsOpacityEffect(self)
        E.setOpacity(0.7)
        self.setGraphicsEffect(E)
        self.round = 2

        self._reposition()
        
    def _reposition(self):
        parent = self.parent()
        self.move((parent.width()-self.W)/2 + (parent.width()-self.W)/2.11,10)

    def Align(self):
        self._reposition()

    def mousePressEvent(self, event):
        self.coworker.showmode(self.value)
        return super().mousePressEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        painter.setPen(QPen(Qt.white, 0.8,Qt.DashLine))
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawRoundedRect(rect, self.round, self.round)

        header_rect = rect.adjusted(0, -2, 0, 0)
        font = painter.font()
        font.setBold(False)
        font.setPixelSize(10)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#e1dfdf")))
        painter.drawText(header_rect, Qt.AlignmentFlag.AlignCenter, self.text)

        return super().paintEvent(event)
    

########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ########################################################################
    ## 
    ########################################################################
    window = ModeMainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END===>
########################################################################  
