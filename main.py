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
import subprocess    # Utilisé uniquement pour le type hint subprocess.Popen
import webbrowser    # Ouverture de l'URL du serveur dans le navigateur par défaut

# ---------------------------------------------------------------------------
# Import de fichier 
# ---------------------------------------------------------------------------
from server import ServerController, SERVER_URL
from ui import *
from gui_fonction import GuiFunctions

# ---------------------------------------------------------------------------
# Imports PySide6 – bibliothèque Qt pour Python (interface graphique)
# ---------------------------------------------------------------------------
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import (
    QThread,         # Classe de base pour créer des threads gérés par Qt
    Signal,          # Décorateur permettant à un thread de communiquer avec l'UI thread

)
from PySide6.QtGui import (
    QIcon,           # Icone de l'application
    QColor,          # Représentation d'une couleur (RGB, hex, nommée)
    QPalette,        # Ensemble de couleurs appliqué globalement à la fenêtre
    QAction,         # Définir les actions pour la barre de menu
    QPixmap,         # Image de la carte
)


# ---------------------------------------------------------------------------
# LogReaderThread – lit les sorties du processus PHP dans un thread Qt dédié
# ---------------------------------------------------------------------------
class LogReaderThread(QThread):
    """
    Thread secondaire chargé de lire en continu la sortie standard (stdout)
    du processus PHP et d'émettre chaque ligne via un signal Qt.

    Cycle de vie :
        1. Instancié avec le Popen du processus PHP (après start())
        2. Démarré avec .start() → run() s'exécute dans le thread secondaire
        3. Arrêté avec .stop() → le drapeau _running passe à False
        4. Attendu avec .wait() dans MainWindow._stop_server()
    """

    # Signal Qt émis chaque fois qu'une nouvelle ligne de log est disponible.
    # La signature `str` indique que chaque émission transporte une chaîne.
    # Le slot connecté (MainWindow._append_log) reçoit cette chaîne en argument.
    new_line = Signal(str)

    def __init__(self, process: subprocess.Popen):
        """
        Initialise le thread avec le processus PHP à surveiller.

        :param process: Objet Popen retourné par ServerController.start().
                        Son attribut stdout est le flux à lire.
        """
        super().__init__()          # Initialise QThread (obligatoire)
        self._process = process     # Processus PHP dont on lit la sortie
        self._running = True        # Drapeau booléen : True = continuer la lecture

    # ------------------------------------------------------------------
    def run(self):
        """
        Boucle principale du thread secondaire, exécutée après .start().
        
        """
        # readline() est bloquant : le thread attend une nouvelle ligne
        # avant de continuer, ce qui évite de consommer du CPU inutilement.
        for line in iter(self._process.stdout.readline, b""):
            if not self._running:   # Vérifie à chaque itération si on doit s'arrêter
                break
            # Décode les bytes en str UTF-8 ; errors="replace" évite les crashs
            # si le processus PHP émet des caractères non-UTF-8.
            # rstrip() supprime le saut de ligne final (\n ou \r\n).
            decoded = line.decode("utf-8", errors="replace").rstrip()
            if decoded:             # Ignore les lignes vides (lignes blanches du log PHP)
                self.new_line.emit(decoded)   # Émet le signal → MainWindow._append_log()

    # ------------------------------------------------------------------
    def stop(self):
        """
        Demande l'arrêt propre du thread en mettant le drapeau à False.
        Le thread s'arrêtera au prochain passage dans la boucle run(),
        c'est-à-dire après la prochaine ligne lue (ou à l'EOF du processus).
        """
        self._running = False       # La boucle dans run() vérifie ce drapeau


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

        # Contrôleur du serveur PHP (défini dans server.py).
        # La fenêtre le crée et le détruit ; sa durée de vie est liée à la fenêtre.
        self._controller = ServerController()

        # Thread de lecture des logs du processus PHP.
        # Vaut None quand le serveur est arrêté (pas de processus à surveiller).
        self._log_thread: LogReaderThread | None = None

        self.ui = Ui_CustomMainWindow()
        self.ui.setupUi(self)

        self.app_functions = GuiFunctions(self)

    # ====================================================================
    # Slots – méthodes connectées aux signaux des boutons et du thread
    # ====================================================================
    def _start_server(self):
        """
        Slot connecté au signal clicked du bouton "Démarrer le serveur".

        Séquence d'actions :
          1. Appelle ServerController.start() pour lancer le processus PHP.
          2. Instancie LogReaderThread avec le Popen retourné.
          3. Connecte le signal new_line du thread à _append_log (ce slot
             s'exécutera dans l'UI thread grâce au mécanisme Qt).
          4. Démarre le thread de lecture des logs.
          5. Met à jour les boutons et la barre d'état.
        """
        try:
            # Délègue le démarrage du processus PHP à ServerController (server.py)
            process = self._controller.start()
        except (FileNotFoundError, RuntimeError) as exc:
            # En cas d'erreur (PHP absent, serveur déjà lancé…), affiche le message
            # dans la zone de logs sans faire crasher l'application.
            self._append_log(f"[ERREUR] {exc}")
            return

        # Crée le thread qui lira les logs du processus PHP en temps réel
        self._log_thread = LogReaderThread(process)

        # Connecte le signal new_line → slot _append_log.
        # Qt s'assure que _append_log s'exécute dans l'UI thread (thread-safe).
        self._log_thread.new_line.connect(self._append_log)

        # Lance le thread secondaire (appelle run() dans un thread OS séparé)
        self._log_thread.start()

        # Met à jour la barre d'état avec un message vert (serveur actif)
        self._set_status(f"Serveur en cours d'exécution sur {SERVER_URL}", "#2ecc71")
        self._append_log(f"[INFO] Serveur PHP démarré → {SERVER_URL}")
        self._update_server_label("Open")

    # ------------------------------------------------------------------
    def _stop_server(self):
        """
        Slot connecté au signal clicked du bouton "Arrêter le serveur".

        Séquence d'actions :
          1. Arrête le thread de lecture des logs (stop() + wait()).
          2. Appelle ServerController.stop() pour tuer le processus PHP.
          3. Met à jour les boutons et la barre d'état.

        L'ordre est important : on arrête le thread AVANT le processus pour
        éviter que le thread tente de lire un stdout fermé.
        """

        if self._log_thread is None:
            # SAMY j'ai désactiver pour faire marcher le reste
            #self._append_log("[ERREUR] Serveur ne peut pas être arrêté (Serveur n'est pas ouvert).")
            print("TEST")

        else:
            # 1. Signale au thread de ne plus émettre de nouveaux logs
            self._log_thread.stop()   # Positionne le drapeau _running à False
    
            # 2. Arrête le processus PHP → provoque l'EOF sur stdout du thread
            self._controller.stop()
    
            # 3. Attend la fin du thread (désormais débloqué par l'EOF)
            self._log_thread.wait(3000)   # Timeout 3 s en sécurité (ne bloque plus)
            self._log_thread = None       # Libère la référence pour le garbage collector
    
            # Met à jour la barre d'état avec un message rouge (serveur arrêté)
            self._set_status("Serveur arrêté", "#e74c3c")
            self._append_log("[INFO] Serveur PHP arrêté.")
            self._update_server_label("Closed")

    # ------------------------------------------------------------------
    def _open_browser(self):
        """
        Slot connecté au signal clicked du bouton "Ouvrir dans le navigateur".
        Délègue l'ouverture de l'URL au module webbrowser de Python,
        qui utilise le navigateur par défaut du système d'exploitation.
        """
        webbrowser.open(SERVER_URL)   # Ouvre http://127.0.0.1:8080 dans le navigateur
        self._append_log(f"[INFO] Navigateur ouvert sur {SERVER_URL}")

    # ====================================================================
    # Méthodes utilitaires internes (préfixe _ = usage interne à la classe)
    # ====================================================================

    def _append_log(self, text: str):
        """
        Ajoute une ligne au bas de la zone de logs et fait défiler
        automatiquement vers la dernière ligne.

        :param text: Ligne de texte à afficher (déjà décodée en str).
        """
        self.log_view.append(text)   # Insère la ligne à la fin du QTextEdit

        # Fait défiler la barre verticale jusqu'à sa position maximale
        # pour toujours afficher la ligne la plus récente.
        sb = self.log_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ------------------------------------------------------------------
    def _set_status(self, message: str, color: str):
        """
        Met à jour le texte et la couleur de la barre d'état en bas de la fenêtre.

        :param message: Texte à afficher dans la barre d'état.
        :param color:   Code couleur hexadécimal CSS (ex. "#2ecc71" pour vert).
        """
        # Applique un style QSS pour colorer et mettre en gras le message
        self._status_bar.setStyleSheet(f"color: {color}; font-weight: bold;")
        # showMessage() remplace le contenu actuel de la barre d'état
        self._status_bar.showMessage(message)

    # ====================================================================
    # Gestion de l'événement de fermeture de la fenêtre
    # ====================================================================

    def closeEvent(self, event):
        """
        Surcharge de l'événement Qt déclenché quand l'utilisateur ferme la fenêtre
        (clic sur la croix, Alt+F4, Cmd+Q…).

        Sans cette surcharge, fermer la fenêtre laisserait le processus PHP
        tourner en arrière-plan (processus orphelin). On s'assure ici d'arrêter
        proprement le serveur et le thread de logs avant de fermer.

        :param event: QCloseEvent transmis par Qt ; on l'accepte pour confirmer la fermeture.
        """
        self._stop_server()   # Arrête le thread de logs et le processus PHP
        event.accept()        # Confirme la fermeture → la fenêtre est détruite


if __name__ == "__main__":   
    app = QApplication(sys.argv)
    app.setApplicationName("PHP Server Launcher")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())