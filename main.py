########################################################################
## QT GUI BY SPINN TV(YOUTUBE)
########################################################################

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
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
########################################################################

########################################################################
## MAIN WINDOW CLASS
########################################################################
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        # Thread de lecture des logs du processus PHP.
        # Vaut None quand le serveur est arrêté (pas de processus à surveiller).
        self._log_thread: LogReaderThread | None = None

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

        # self = QMainWindow class
        QAppSettings.updateAppSettings(self)

        self.app_functions = GuiFunctions(self)


########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ########################################################################
    ## 
    ########################################################################
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END===>
########################################################################  
