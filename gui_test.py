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
# Import du module serveur local (server.py)
# ---------------------------------------------------------------------------
# On importe la classe ServerController et les constantes de configuration
# depuis server.py, qui est le seul endroit où ces valeurs sont définies.
# Grâce à cette séparation, server.py peut être testé ou utilisé sans GUI.
from server import ServerController, SERVER_URL

# ---------------------------------------------------------------------------
# Imports PySide6 – bibliothèque Qt pour Python (interface graphique)
# ---------------------------------------------------------------------------
from PySide6.QtWidgets import (
    QApplication,    # Objet application Qt : obligatoire avant tout widget
    QMainWindow,     # Fenêtre principale avec barre de titre, menus et barre d'état
    QWidget,         # Widget de base utilisé comme conteneur central
    QVBoxLayout,     # Disposition verticale : les enfants s'empilent de haut en bas
    QHBoxLayout,     # Disposition horizontale : les enfants s'alignent de gauche à droite
    QPushButton,     # Bouton interactif avec texte et style personnalisable
    QTextEdit,       # Zone de texte multi-lignes (lecture seule pour les logs)
    QLabel,          # Étiquette de texte statique (titre, URL, libellés)
    QStatusBar,      # Barre d'état native de QMainWindow, affichée en bas de la fenêtre
    QGridLayout,      # Grille pour afficher la carte
    QMenuBar,
)
from PySide6.QtCore import (
    Qt,              # Espace de noms Qt : constantes d'alignement, drapeaux, etc.
    QThread,         # Classe de base pour créer des threads gérés par Qt
    Signal,          # Décorateur permettant à un thread de communiquer avec l'UI thread
)
from PySide6.QtGui import (
    QIcon,           # Icone de l'application
    QFont,           # Représentation d'une police (famille, taille, graisse)
    QColor,          # Représentation d'une couleur (RGB, hex, nommée)
    QPalette,        # Ensemble de couleurs appliqué globalement à la fenêtre
    QAction,         # Définir les actions pour la barre de menu
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

        # ----------------------------------------------------------------
        # Configuration de la fenêtre Qt
        # ----------------------------------------------------------------

        self.setWindowTitle("PHP Server Launcher")
        # Mettre une icone pour plus tard
        #self.setWindowIcon(QIcon("icons/file.png"))
        self.setMinimumSize(1250, 800)
        self._apply_dark_theme()

        # Barre de menu
        self.createActions()
        self.createMenuBar()

        # ----------------------------------------------------------------
        # Construction de l'interface : layout principal vertical
        # ----------------------------------------------------------------

        central = QWidget()
        self.setCentralWidget(central)   # Définit le conteneur central

        root_layout = QVBoxLayout(central)
        root_layout.setSpacing(12)                      # 12 px entre chaque widget
        root_layout.setContentsMargins(16, 16, 16, 16)  # Marges intérieures de 16 px

        # ----------------------------------------------------------------
        # Label affichant l'URL cliquable du serveur
        # ----------------------------------------------------------------
        partie_haut_layout = QHBoxLayout()
        self.server_label = QLabel("Serveur: Closed")
        self.server_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.server_label.setStyleSheet("color: #e74c3c; font-size: 13px;")
        partie_haut_layout.addWidget(self.server_label)


        url_label = QLabel(f"URL : <a href='{SERVER_URL}'>{SERVER_URL}</a>")
        url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        url_label.setOpenExternalLinks(True)
        url_label.setStyleSheet("color: #7ecfff; font-size: 13px;")
        partie_haut_layout.addWidget(url_label)
        root_layout.addLayout(partie_haut_layout)
        # ----------------------------------------------------------------
        # Interface central
        # ----------------------------------------------------------------

        mj_interface = QHBoxLayout()

        self.infoMenu = QTextEdit()
        self.infoMenu.setFixedWidth(200)
        mj_interface.addWidget(self.infoMenu)

        # ----------------------------------------------------------------
        # Zone pour la carte et le chat
        # ----------------------------------------------------------------
        
        partie_droite_layout = QVBoxLayout()
        self.map = QTextEdit()
        self.map.setFixedHeight(500)

        log_label = QLabel("Logs du serveur PHP/Chat :")
        log_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")

        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)   # L'utilisateur ne peut pas modifier les logs
        self._log_view.setFont(QFont("Consolas", 11))   # Police monospace pour les logs
        self._log_view.setStyleSheet(
            "background-color: #0d1117;"       # Fond très sombre (style terminal)
            "color: #c9d1d9;"                  # Texte gris clair
            "border: 1px solid #30363d;"       # Bordure subtile
            "border-radius: 6px;"              # Coins légèrement arrondis
            "padding: 6px;"                    # Espace intérieur
        )
        partie_droite_layout.addWidget(self.map)
        partie_droite_layout.addWidget(log_label)
        partie_droite_layout.addWidget(self._log_view)
        mj_interface.addLayout(partie_droite_layout)
        root_layout.addLayout(mj_interface)

        # ----------------------------------------------------------------
        # Barre d'état en bas de la fenêtre principale
        # ----------------------------------------------------------------
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)   # QMainWindow gère la barre d'état nativement
        self._set_status("Serveur arrêté", "#e74c3c")   # État initial : rouge = arrêté


    # ====================================================================
    # MenuBar – méthodes pour créer la barre de menu
    # ====================================================================

    def createActions(self):
        # Actions server
        self.ouvre_serveur_text = QAction(QIcon("image/start_icon.png"),"Démarrer le serveur", self)
        self.ouvre_serveur_text.setShortcut("Alt+D")
        self.ouvre_serveur_text.triggered.connect(self._start_server)

        self.ferme_serveur_text = QAction(QIcon("image/stop_icon.png"),"Arrêter le serveur", self)
        self.ferme_serveur_text.setShortcut("Alt+F")
        self.ferme_serveur_text.triggered.connect(self._stop_server)

        self.ouvre_site_text = QAction(QIcon("image/web_icon.png"),"Ouvrir dans le navigateur", self)
        self.ouvre_site_text.setShortcut("Alt+O")
        self.ouvre_site_text.triggered.connect(self._open_browser)

        # Actions edit
        self.undo = QAction(QIcon("image/placeholder.png"),"Undo", self)
        self.undo.setShortcut("Ctrl+Z")

        self.redo = QAction(QIcon("image/placeholder.png"),"Redo", self)
        self.redo.setShortcut("Ctrl+Y")

        self.copy = QAction(QIcon("image/placeholder.png"),"Copy", self)
        self.copy.setShortcut("Ctrl+C")

        self.paste = QAction(QIcon("image/placeholder.png"),"Paste", self)
        self.paste.setShortcut("Ctrl+V")

        self.cut = QAction(QIcon("image/placeholder.png"),"Cut", self)
        self.cut.setShortcut("Ctrl+X")


    def createMenuBar(self):
        menuBar = self.menuBar()
        server = menuBar.addMenu("Serveur")
        server.addAction(self.ouvre_serveur_text)
        server.addAction(self.ferme_serveur_text)
        server.addSeparator()
        server.addAction(self.ouvre_site_text)

        edit = menuBar.addMenu("Edit")
        edit.addAction(self.undo)
        edit.addAction(self.redo)
        edit.addSeparator()
        edit.addAction(self.copy)
        edit.addAction(self.paste)
        edit.addAction(self.cut)

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
            self._append_log("[ERREUR] Serveur ne peut pas être arrêté (Serveur n'est pas ouvert).")

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

    def _update_server_label(self,state: str):
        """
        Met à jour l'affichage pour l'état du serveur.

        :param state: Open ou Closed. Décris si le serveur est 
        ouvert ou non.
        """
        if state == "Closed":
            self.server_label.setText("Serveur: Closed")
            self.server_label.setStyleSheet("color: #e74c3c; font-size: 13px;")
        elif state == "Open":
            self.server_label.setText("Serveur: Open")
            self.server_label.setStyleSheet("color: #2ecc71; font-size: 13px;")

    def _append_log(self, text: str):
        """
        Ajoute une ligne au bas de la zone de logs et fait défiler
        automatiquement vers la dernière ligne.

        :param text: Ligne de texte à afficher (déjà décodée en str).
        """
        self._log_view.append(text)   # Insère la ligne à la fin du QTextEdit

        # Fait défiler la barre verticale jusqu'à sa position maximale
        # pour toujours afficher la ligne la plus récente.
        sb = self._log_view.verticalScrollBar()
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

    # ------------------------------------------------------------------
    @staticmethod
    def _btn_style(color_normal: str, color_hover: str) -> str:
        """
        Génère et retourne une feuille de style QSS (Qt Style Sheet) pour un
        bouton, avec trois états visuels : normal, survol (hover) et désactivé.

        :param color_normal: Couleur de fond à l'état normal (hex).
        :param color_hover:  Couleur de fond quand la souris survole le bouton (hex).
        :return: Chaîne QSS prête à passer à setStyleSheet().
        """
        return (
            # État normal : fond coloré, texte blanc, coins arrondis
            f"QPushButton {{"
            f"  background-color: {color_normal};"
            f"  color: white;"
            f"  border: none;"
            f"  border-radius: 6px;"
            f"  font-size: 13px;"
            f"  padding: 0 14px;"
            f"}}"
            # État survol : couleur légèrement plus sombre (color_hover)
            f"QPushButton:hover {{"
            f"  background-color: {color_hover};"
            f"}}"
            # État désactivé : grisé pour indiquer que l'action n'est pas disponible
            f"QPushButton:disabled {{"
            f"  background-color: #444444;"
            f"  color: #888888;"
            f"}}"
        )

    # ------------------------------------------------------------------
    def _apply_dark_theme(self):
        """
        Applique un thème sombre cohérent à l'ensemble de la fenêtre.

        Deux mécanismes complémentaires sont utilisés :
          1. QPalette : définit les couleurs systèmes Qt (fond, texte, liens…)
             appliquées automatiquement à tous les widgets enfants.
          2. setStyleSheet() : feuille de style QSS pour affiner des composants
             spécifiques que la palette ne couvre pas finement.
        """
        palette = QPalette()

        # Fond principal de la fenêtre (espace derrière les widgets)
        palette.setColor(QPalette.ColorRole.Window,        QColor("#161b22"))

        # Texte affiché sur le fond de la fenêtre (labels, titres…)
        palette.setColor(QPalette.ColorRole.WindowText,    QColor("#e6edf3"))

        # Fond des champs de saisie et zones de texte (QTextEdit, QLineEdit…)
        palette.setColor(QPalette.ColorRole.Base,          QColor("#0d1117"))

        # Fond alterné dans les listes et tableaux (lignes paires/impaires)
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1c2128"))

        # Fond et texte des infobulles (tooltips)
        palette.setColor(QPalette.ColorRole.ToolTipBase,   QColor("#1c2128"))
        palette.setColor(QPalette.ColorRole.ToolTipText,   QColor("#e6edf3"))

        # Texte dans les champs de saisie et zones de texte
        palette.setColor(QPalette.ColorRole.Text,          QColor("#e6edf3"))

        # Fond et texte des boutons Qt natifs (non-stylisés par QSS)
        palette.setColor(QPalette.ColorRole.Button,        QColor("#21262d"))
        palette.setColor(QPalette.ColorRole.ButtonText,    QColor("#e6edf3"))

        # Couleur des liens hypertexte (QLabel avec setOpenExternalLinks)
        palette.setColor(QPalette.ColorRole.Link,          QColor("#58a6ff"))

        self.setPalette(palette)   # Applique la palette à la fenêtre et à ses enfants

        # Feuille de style QSS complémentaire pour les composants spécifiques
        self.setStyleSheet(
            "QMainWindow { background-color: #161b22; }"
            "QStatusBar  { background-color: #0d1117; border-top: 1px solid #30363d; }"
            "QLabel      { color: #e6edf3; }"
        )

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


# ---------------------------------------------------------------------------
# Point d'entrée – exécuté uniquement lors d'un lancement direct du script
# ---------------------------------------------------------------------------
if __name__ == "__main__":   
    app = QApplication(sys.argv)
    app.setApplicationName("PHP Server Launcher")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())