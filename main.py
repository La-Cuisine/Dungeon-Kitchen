"""
gui.py
------
Interface graphique PySide6 du PHP Server Launcher.
Ce fichier est le point d'entrée de l'application : il crée la fenêtre Qt,
gère les interactions utilisateur et délègue toute la logique serveur
au module `server.py`.

Contenu :
  - LogReaderThread : thread Qt qui lit les logs du processus PHP en temps réel
  - MainWindow      : fenêtre principale avec boutons, zone de logs et barre d'état
  - Point d'entrée  : bloc `if __name__ == "__main__"` qui lance l'application

Dépendances :
  - PySide6 (pip install PySide6)
  - server.py (doit se trouver dans le même dossier)

Lancement :
    python gui.py
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

    Responsabilités :
      - Afficher l'état du serveur (arrêté / en cours)
      - Proposer les boutons Démarrer, Arrêter, Ouvrir le navigateur
      - Afficher les logs PHP en temps réel dans une zone de texte défilante
      - Arrêter proprement le serveur et le thread de logs à la fermeture

    Dépend de :
      - ServerController (server.py) pour la gestion du processus PHP
      - LogReaderThread (ce fichier) pour la lecture non-bloquante des logs
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