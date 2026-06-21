"""
gui.py
------
Interface graphique PySide6 du PHP Server Launcher.
"""

# ---------------------------------------------------------------------------
# Imports de la bibliothèque standard Python
# ---------------------------------------------------------------------------
import sys           # Transmission du code de retour à sys.exit() et accès aux args

# ---------------------------------------------------------------------------
# Import de fichier interne
# ---------------------------------------------------------------------------
from ui import *
from gui_fonctions import GuiFunctions
from LogReaderThread import LogReaderThread

# ---------------------------------------------------------------------------
# Imports PySide6 – bibliothèque Qt pour Python (interface graphique)
# ---------------------------------------------------------------------------
from PySide6.QtWidgets import QMainWindow

# ---------------------------------------------------------------------------
# MainWindow – fenêtre principale de l'interface graphique
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application PHP Server Launcher.
    """

    def __init__(self):
        """
        Constructeur : initialise les objets métier, configure la fenêtre
        et crée tous les widgets de l'interface.
        """
        super().__init__()

        # ----------------------------------------------------------------
        # Objets métier instanciés par la fenêtre principale
        # ----------------------------------------------------------------

        # Thread de lecture des logs du processus PHP.
        # Vaut None quand le serveur est arrêté (pas de processus à surveiller).
        self._log_thread: LogReaderThread | None = None

        self.ui = Ui_CustomMainWindow()
        self.ui.setupUi(self)

        self.app_functions = GuiFunctions(self)


if __name__ == "__main__":   
    app = QApplication(sys.argv)
    app.setApplicationName("PHP Server Launcher")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())