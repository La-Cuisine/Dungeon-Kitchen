from PySide6.QtCore import QSettings, QTimer, Qt
from PySide6.QtGui import QColor, QPalette, QPainter, QBrush
from PySide6.QtWidgets import QGraphicsScene
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTheme import QCustomTheme

import webbrowser
# Import interne
from src.MJ_application.server import SERVER_URL, ServerController
from src.MJ_application.LogReaderThread import LogReaderThread
from src.MJ_application.grid import View_Grid, Grid, InvisibleWallLimit
from obj.blueprint import *
from obj.game import *
from obj.items import *
from obj.pawns import *
from obj.player import *
from obj.save import *

class GuiFunctions():
    def __init__(self,MainWindow):
        self.main = MainWindow
        self.ui = MainWindow.ui
        self._log_thread = None
        self._controller = ServerController()
        self.settings =  QSettings("Dungeon Kitchen Company","Dungeon Kitchen")
        self.last_menu = self.settings.value("Menu")
        self.loaded_character = False


        self.init_app_theme()
        self.init_action_menubar()
        self.init_app_btn_connect()
        self.init_info_menu()
        self.init_grid()

    # ----------------------------------------------------------------
    # Initialisation de l'application 
    # ----------------------------------------------------------------

    def init_app_theme(self):
        """
        Initialise le thème de l'application
        """
        self.themeEngine = QCustomTheme()
        current_theme = self.settings.value("THEME")
        # Ajoute des thèmes à la liste des thèmes
        self.ui.theme_list.addItem("Dark")
        self.ui.theme_list.addItem("Light")
        self.ui.theme_list.setCurrentText(current_theme)

        if current_theme == "Light":
            self._apply_light_theme()
        else:
            self._apply_dark_theme()

        # Couleur du label du menu "server"
        self.ui.server_state_label.setStyleSheet("color: #e74c3c; font-size: 13px;")

        # Cache des éléments à l'initialisation
        self.ui.alignement_NPC.setVisible(False)

        # Couleurs des boutons du menu "server"
        self.ui.open_server_btn.setStyleSheet(
            self._btn_style("#2ecc71", "#27ae60")
        )
        self.ui.close_server_btn.setStyleSheet(
            self._btn_style("#e74c3c", "#c0392b")
        )
        self.ui.open_website_btn.setStyleSheet(
            self._btn_style("#3498db", "#2980b9")
        )
        self.ui.open_game_interface_btn.setStyleSheet(
            self._btn_style("#db8534", "#be732c")
        )

        # Affiche le lien de l'URL correctement
        link = "URL : <a href='",SERVER_URL,"'>",SERVER_URL,"</a>"
        link_string = ''.join(link)
        self.ui.url_link_label.setText(link_string)

    def init_app_btn_connect(self):
        """
        Initialise les signaux pour les boutons de l'application
        """
        # Change le menu d'information
        self.ui.character_btn.clicked.connect(self.switch_to_character_menu_selection)
        self.ui.map_btn.clicked.connect(self.switch_to_map_menu)
        self.ui.server_btn.clicked.connect(self.switch_to_server_menu)
        self.ui.settings_btn.clicked.connect(self.switch_to_settings_menu)
        self.ui.information_btn.clicked.connect(self.switch_to_information_menu)
        self.ui.help_btn.clicked.connect(self.switch_to_help_menu)
        self.ui.create_character_btn.clicked.connect(self.switch_to_character_menu_info)

        # Ouvre ou ferme le menu d'information
        self.ui.open_info_menu_btn.clicked.connect(self.switch_center_menu_display_state)
        self.ui.close_info_menu_btn.clicked.connect(self.switch_center_menu_display_state)

        # Stat/Inv
        self.ui.isNPC.toggled.connect(self.setNPC)

        # Ouvre ou ferme le log/chat
        self.ui.close_log_view_btn.clicked.connect(self.switch_log_display_state)

        # Save/Load
        self.ui.save_character_btn.clicked.connect(self.save_character)

        # Démarre ou ferme le serveur
        self.ui.open_server_btn.clicked.connect(self._update_server_label_open)
        self.ui.close_server_btn.clicked.connect(self._update_server_label_close)

        self.ui.open_server_btn.clicked.connect(self._start_server)
        self.ui.close_server_btn.clicked.connect(self._stop_server)
        self.ui.open_website_btn.clicked.connect(self._open_browser)

        # Settings
        self.ui.theme_list.currentTextChanged.connect(self.changeAppTheme)
    
    def init_grid(self, n: int = 100, s_cell: int = 64):
        """
        Remplace le QGraphicsView généré par Qt Designer par un View_Grid,
        puis y injecte la scène, le mur invisible et la grille.

        :param n:      Nombre de cellules par côté de la grille.
        :param s_cell: Taille en pixels d'une cellule.
        """
        from PySide6.QtWidgets import QGraphicsItem
        import src.MJ_application.grid as _grid_module

        # Recupere le layout parent du graphicsView
        layout = self.ui.verticalLayout_10

        # Cree la scene graphique
        self._scene = QGraphicsScene()
        self._scene.setSceneRect(0, 0, 700, 520)
        # Desactive l'index BSP : inutile pour une grille rigide,
        # evite de recalculer les bounding rects de tous les enfants au drag.
        self._scene.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        # Crée le View_Grid et le branche sur la scène
        self._view_grid = View_Grid(self._scene)
        self._view_grid.setObjectName("graphicsView")
        self._view_grid.setRenderHint(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self._view_grid.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view_grid.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view_grid.setBackgroundBrush(QBrush(QColor("#171717ff")))
        self._view_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._view_grid.setDragMode(View_Grid.DragMode.ScrollHandDrag)
        self._view_grid.setMouseTracking(True)

        # Insere le View_Grid AVANT de creer l'overlay (la vue doit etre
        # dans le layout pour avoir une taille et un parent valides).
        layout.insertWidget(0, self._view_grid)

        # Overlay coordonnees souris : QLabel enfant de la vue (plus un item scene).
        # Taille fixe, toujours en haut a droite, insensible au pan/zoom.
        self.InterMouseCoor = _grid_module.Interface_MouseCoord(self._view_grid)
        self._view_grid.addItemNeeds(self.InterMouseCoor)

        # Mur invisible (doit exister avant la grille)
        self._wall = InvisibleWallLimit(self._scene)
        _grid_module._wall = self._wall          # Met à jour la globale du module
        self._scene.addItem(self._wall)

        # Grille
        self._world = Grid(n, s_cell)
        (self._world.atoms[0]).setName("TL")
        (self._world.atoms[0]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        (self._world.atoms[n - 1]).setName("TR")
        (self._world.atoms[n - 1]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        (self._world.atoms[(n - 1) * n]).setName("BL")
        (self._world.atoms[(n - 1) * n]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        (self._world.atoms[(n - 1) * n + (n - 1)]).setName("BR")
        (self._world.atoms[(n - 1) * n + (n - 1)]).setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self._scene.addItem(self._world)

        # Reference directe sur la grille pour que _cell_at_view_pos()
        # fonctionne meme avant le premier mouseMoveEvent.
        self._view_grid._grid = self._world

        # Met à jour la référence ui.graphicsView pour que le reste du code
        # continue à fonctionner via self.ui.graphicsView si besoin
        self.ui.graphicsView = self._view_grid
    
    def init_action_menubar(self):
        """
        Initialise les signaux pour les actions de la menubar
        """
        self.ui.actionLog_Chat.toggled.connect(self.switch_log_display_state)
        self.ui.actionInfo_menu.toggled.connect(self.switch_center_menu_display_state)
        self.ui.actionClose.triggered.connect(self.closeEvent)

    def init_info_menu(self):
        """
        Ouvre la dernière page consulté de information menu au 
        lancement de l'application. 
        Ouvre la page du serveur si il n'y pas d'information sur
        la dernière page consulté.
        """
        self.last_menu = self.settings.value("MENU INFO")

        if(self.last_menu == None):
            self.switch_to_server_menu()
        else:
            self.ui.stacked_widget.setCurrentIndex(self.last_menu)

    # ----------------------------------------------------------------
    # Slots – méthodes connectées aux signaux des boutons et du thread
    # ----------------------------------------------------------------
    
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
        self._update_server_label_open()

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
            self._update_server_label_close()

    def _open_browser(self):
        """
        Slot connecté au signal clicked du bouton "Ouvrir dans le navigateur".
        Délègue l'ouverture de l'URL au module webbrowser de Python,
        qui utilise le navigateur par défaut du système d'exploitation.
        """
        if self._log_thread is None:
            self._append_log("[ERREUR] Site ne peut pas s'ouvrir (Serveur n'est pas ouvert).")
        else:
            webbrowser.open(SERVER_URL)   # Ouvre http://127.0.0.1:8080 dans le navigateur
            self._append_log(f"[INFO] Navigateur ouvert sur {SERVER_URL}")

    # ----------------------------------------------------------------
    # Menu d'information 
    # ----------------------------------------------------------------

    def switch_to_settings_menu(self):
        self.ui.stacked_widget.setCurrentIndex(0)
        self.settings.setValue("MENU INFO",0)
        self._open_center_menu()

    def switch_to_character_menu_selection(self):
        if(self.loaded_character == False):
            self.ui.stacked_widget.setCurrentIndex(6)
            self.settings.setValue("MENU INFO",6)
        else:
            self.ui.stacked_widget.setCurrentIndex(1)
        self._open_center_menu()

    def switch_to_character_menu_info(self):
        self.loaded_character = True
        self.ui.stacked_widget.setCurrentIndex(1)

    def switch_to_map_menu(self):
        self.ui.stacked_widget.setCurrentIndex(2)
        self.settings.setValue("MENU INFO",2)
        self._open_center_menu()
    
    def switch_to_server_menu(self):
        self.ui.stacked_widget.setCurrentIndex(3)
        self.settings.setValue("MENU INFO",3)
        self._open_center_menu()

    def switch_to_information_menu(self):
        self.ui.stacked_widget.setCurrentIndex(4)
        self.settings.setValue("MENU INFO",4)
        self._open_center_menu()

    def switch_to_help_menu(self):
        self.ui.stacked_widget.setCurrentIndex(5)
        self.settings.setValue("MENU INFO",5)
        self._open_center_menu()

    def _open_center_menu(self):
        """
        Affiche le menu d'information
        """
        # Déconnecte actionInfo_menu du signal
        self.ui.actionInfo_menu.blockSignals(True)
        
        self.ui.center_menu.setVisible(True)
        self.ui.open_info_menu_btn.setIcon(QIcon("ui/image/Undo.png"))
        self.ui.actionInfo_menu.setChecked(True)

        # Reconnecte actionInfo_menu du signal
        self.ui.actionInfo_menu.blockSignals(False)

    def _close_center_menu(self):
        """
        Cache le menu d'information
        """       
        # Déconnecte actionInfo_menu du signal
        self.ui.actionInfo_menu.blockSignals(True)

        self.ui.center_menu.setVisible(False)
        self.ui.open_info_menu_btn.setIcon(QIcon("ui/image/Redo.png"))
        self.ui.actionInfo_menu.setChecked(False)

        # Reconnecte actionInfo_menu du signal
        self.ui.actionInfo_menu.blockSignals(False)

    def switch_center_menu_display_state(self):
        """
        Affiche ou cache le menu d'information selon
        l'état de visibilité du menu
        """
        # Déconnecte actionInfo_menu du signal
        self.ui.actionInfo_menu.blockSignals(True)
        
        # Cacher la fenêtre
        if(self.ui.center_menu.isVisible() == True):
            self._close_center_menu()

        # Afficher la fenêtre
        elif(self.ui.center_menu.isVisible() == False):
            self._open_center_menu()
        
        else:
            print("Erreur switch center menu display")

        # Reconnecte actionInfo_menu du signal
        self.ui.actionInfo_menu.blockSignals(False)
            
    # ----------------------------------------------------------------
    # Stat/Inv
    # ----------------------------------------------------------------

    def setNPC(self):
        # Active le choix de l'alignement d'un npc
        if(self.ui.isNPC.isChecked() == True):
            self.ui.alignement_NPC.setVisible(True)

        # Désactive le choix de l'alignement d'un npc
        elif(self.ui.isNPC.isChecked() == False):
            self.ui.alignement_NPC.setVisible(False)

        else:
            print("Erreur setNPC")

    # ----------------------------------------------------------------
    # Chat/Log
    # ----------------------------------------------------------------

    def _append_log(self, text: str):
        """
        Ajoute une ligne au bas de la zone de logs et fait défiler
        automatiquement vers la dernière ligne.

        :param text: Ligne de texte à afficher (déjà décodée en str).
        """
        self.ui.log_view.append(text)   # Insère la ligne à la fin du QTextEdit

        # Fait défiler la barre verticale jusqu'à sa position maximale
        # pour toujours afficher la ligne la plus récente.
        sb = self.ui.log_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def switch_log_display_state(self):
        # Cache le chat
        self.ui.actionLog_Chat.toggled.disconnect(self.switch_log_display_state)
        if(self.ui.log_view.isVisible() == True):
            self.ui.log_view.setVisible(False)
            self.ui.log_view_top.setVisible(False)
            if(self.ui.actionLog_Chat.isChecked() == True):
                self.ui.actionLog_Chat.setChecked(False)

        # Affiche le chat
        elif(self.ui.log_view.isVisible() == False):
            self.ui.log_view.setVisible(True)
            self.ui.log_view_top.setVisible(True)
            if(self.ui.actionLog_Chat.isChecked() == False):
                self.ui.actionLog_Chat.setChecked(True)

        else:
            print("Erreur switch log_view display")

        self.ui.actionLog_Chat.toggled.connect(self.switch_log_display_state)

    # ----------------------------------------------------------------
    # Fonctions pour manipuler le style de la page et des boutons
    # ----------------------------------------------------------------

    def changeAppTheme(self):
        """
        Change le thème de l'application
        """ 
        current_theme = self.settings.value("THEME")
        selected_theme = self.ui.theme_list.currentText()
        if current_theme != selected_theme:
            self.settings.setValue("THEME", selected_theme)
            QAppSettings.updateAppSettings(self.main, reloadJson=True)
            if selected_theme == "Dark":
                self._apply_dark_theme()
            else:
                self._apply_light_theme()

    def _update_server_label_open(self):
        """
        Met à jour l'affichage pour l'état du serveur.

        """
        self.ui.server_state_label.setText("Server: open")
        self.ui.server_state_label.setStyleSheet("color: #2ecc71; font-size: 13px;")

    def _update_server_label_close(self):
        """
        Met à jour l'affichage pour l'état du serveur.

        """
        self.ui.server_state_label.setText("Server: closed")
        self.ui.server_state_label.setStyleSheet("color: #e74c3c; font-size: 13px;")

    # Inutilisé
    def _set_status(self, message: str, color: str):
        """
        Met à jour le texte et la couleur de la barre d'état en bas de la fenêtre.

        :param message: Texte à afficher dans la barre d'état.
        :param color:   Code couleur hexadécimal CSS (ex. "#2ecc71" pour vert).
        """
        # Applique un style QSS pour colorer et mettre en gras le message
        #self._status_bar.setStyleSheet(f"color: {color}; font-weight: bold;")
        # showMessage() remplace le contenu actuel de la barre d'état
        #self._status_bar.showMessage(message)
        pass

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

        self.main.setPalette(palette)   # Applique la palette à la fenêtre et à ses enfants

        # Feuille de style QSS complémentaire pour les composants spécifiques
        self.main.setStyleSheet(
            "QMainWindow { background-color: #161b22; }"
            "QStatusBar  { background-color: #0d1117; border-top: 1px solid #30363d; }"
            "QLabel      { color: #e6edf3; }"
            "QTextEdit   { background-color: #0d1117; color: #e6edf3; border: 1px solid #30363d; }"
            "QComboBox   { background-color: #21262d; color: #e6edf3; border: 1px solid #30363d; }"
            "QComboBox QAbstractItemView { background-color: #1c2128; color: #e6edf3; selection-background-color: #30363d; }"
        )

        # Force le fond + texte du panneau central et du stacked_widget
        self.ui.center_menu.setAutoFillBackground(True)
        self.ui.center_menu.setStyleSheet(
            "QWidget#center_menu { background-color: #161b22; }"
            "QWidget#center_menu QLabel    { color: #e6edf3; }"
            "QWidget#center_menu QComboBox { background-color: #21262d; color: #e6edf3; border: 1px solid #30363d; }"
            "QComboBox QAbstractItemView   { background-color: #1c2128; color: #e6edf3; selection-background-color: #30363d; }"
        )
        self.ui.stacked_widget.setStyleSheet(
            "QStackedWidget { background-color: #161b22; }"
        )

        # Custom_Widgets réapplique son style APRÈS cette fonction (via la boucle
        # d'événements Qt). On utilise QTimer.singleShot(0) pour s'exécuter après
        # que CW ait terminé — c'est le seul moyen fiable de garder le dernier mot.
        def _force_dark_text():
            for btn in [
                self.ui.character_btn, self.ui.map_btn, self.ui.server_btn,
                self.ui.settings_btn, self.ui.information_btn, self.ui.help_btn,
            ]:
                s = btn.styleSheet()
                # Remplace ou ajoute la couleur de texte directement dans le style inline
                if "color:" in s:
                    import re
                    s = re.sub(r'color\s*:\s*[^;]+;', 'color: #fefefe;', s)
                else:
                    s = s.rstrip() + " color: #fefefe;"
                btn.setStyleSheet(s)

        QTimer.singleShot(0, _force_dark_text)
        
    def _apply_light_theme(self):
        """
        Applique un thème clair cohérent à l'ensemble de la fenêtre.

        Même logique que _apply_dark_theme : QPalette pour les couleurs
        système Qt, puis QSS pour affiner certains composants.
        """
        palette = QPalette()

        # Fond principal de la fenêtre (espace derrière les widgets)
        palette.setColor(QPalette.ColorRole.Window,        QColor("#f5f6f8"))

        # Texte affiché sur le fond de la fenêtre (labels, titres…)
        palette.setColor(QPalette.ColorRole.WindowText,    QColor("#1c1f24"))

        # Fond des champs de saisie et zones de texte (QTextEdit, QLineEdit…)
        palette.setColor(QPalette.ColorRole.Base,          QColor("#ffffff"))

        # Fond alterné dans les listes et tableaux (lignes paires/impaires)
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#eceef1"))

        # Fond et texte des infobulles (tooltips)
        palette.setColor(QPalette.ColorRole.ToolTipBase,   QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ToolTipText,   QColor("#1c1f24"))

        # Texte dans les champs de saisie et zones de texte
        palette.setColor(QPalette.ColorRole.Text,          QColor("#1c1f24"))

        # Fond et texte des boutons Qt natifs (non-stylisés par QSS)
        palette.setColor(QPalette.ColorRole.Button,        QColor("#e6e8eb"))
        palette.setColor(QPalette.ColorRole.ButtonText,    QColor("#1c1f24"))

        # Couleur des liens hypertexte (QLabel avec setOpenExternalLinks)
        palette.setColor(QPalette.ColorRole.Link,          QColor("#2563eb"))

        self.main.setPalette(palette)   # Applique la palette à la fenêtre et à ses enfants

        # Feuille de style QSS complémentaire pour les composants spécifiques
        # NOTE : QPushButton est explicitement stylé ici car Custom_Widgets
        # applique son propre QSS (issu du JSON de thème) qui peut laisser
        # un texte clair sur fond clair après reloadJson=True -> boutons
        # invisibles. On force donc fond + texte + hover + disabled.
        self.main.setStyleSheet(
            "QMainWindow { background-color: #f5f6f8; }"
            "QStatusBar  { background-color: #ffffff; border-top: 1px solid #d0d4d9; }"
            "QLabel      { color: #1c1f24; }"
            "QTextEdit   { background-color: #ffffff; color: #1c1f24; border: 1px solid #d0d4d9; }"
            "QComboBox   { background-color: #e6e8eb; color: #1c1f24; border: 1px solid #d0d4d9; }"
            "QPushButton {"
            "  background-color: #e6e8eb;"
            "  color: #1c1f24;"
            "  border: 1px solid #d0d4d9;"
            "  border-radius: 6px;"
            "  padding: 6px 10px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #d8dbdf;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #c6cad0;"
            "}"
            "QPushButton:disabled {"
            "  background-color: #f0f1f3;"
            "  color: #9aa0a8;"
            "}"
            "QComboBox QAbstractItemView { background-color: #ffffff; color: #1c1f24; selection-background-color: #d8dbdf; }"
        )

        # Force le fond + texte + widgets du panneau central
        self.ui.center_menu.setAutoFillBackground(True)
        self.ui.center_menu.setStyleSheet(
            "QWidget#center_menu { background-color: #f5f6f8; }"
            "QWidget#center_menu QLabel    { color: #1c1f24; }"
            "QWidget#center_menu QFrame    { background-color: #eceef1; }"
            "QWidget#center_menu QComboBox { background-color: #e6e8eb; color: #1c1f24; border: 1px solid #d0d4d9; }"
            "QComboBox QAbstractItemView   { background-color: #ffffff; color: #1c1f24; selection-background-color: #d8dbdf; }"
            "QWidget#center_menu QPushButton { background-color: #e6e8eb; color: #1c1f24; border: 1px solid #d0d4d9; border-radius: 6px; padding: 6px 10px; }"
            "QWidget#center_menu QPushButton:hover    { background-color: #d8dbdf; }"
            "QWidget#center_menu QPushButton:pressed  { background-color: #c6cad0; }"
            "QWidget#center_menu QPushButton:disabled { background-color: #f0f1f3; color: #9aa0a8; }"
        )
        self.ui.stacked_widget.setStyleSheet(
            "QStackedWidget { background-color: #f5f6f8; }"
        )

        # Meme logique que le dark : Custom_Widgets ecrase le QSS global avec un
        # setStyleSheet inline par bouton. QTimer.singleShot s'execute apres CW.
        def _force_light_text():
            for btn in [
                self.ui.character_btn, self.ui.map_btn, self.ui.server_btn,
                self.ui.settings_btn, self.ui.information_btn, self.ui.help_btn,
            ]:
                s = btn.styleSheet()
                if "color:" in s:
                    import re
                    s = re.sub(r'color\s*:\s*[^;]+;', 'color: #1c1f24;', s)
                else:
                    s = s.rstrip() + " color: #1c1f24;"
                btn.setStyleSheet(s)

        QTimer.singleShot(0, _force_light_text)

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

    # ----------------------------------------------------------------
    # Gestion de l'événement de fermeture de la fenêtre
    # ----------------------------------------------------------------

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
        try:
            event.accept()        # Confirme la fermeture → la fenêtre est détruite
        except:
            exit()

    # ----------------------------------------------------------------
    # Gestion de save/load
    # ----------------------------------------------------------------

    def save_character(self):
        name = self.ui.character_name.toMarkdown()
        self.pc_sheet = PC(Name=name)

        # Add stats to the save file
        hp = self.ui.hp_nb.value()
        str = self.ui.str_nb.value()
        dex = self.ui.dex_nb.value()
        con = self.ui.con_nb.value()
        int = self.ui.int_nb.value()
        wis = self.ui.wis_nb.value()
        cha = self.ui.cha_nb.value()
        
        self.pc_sheet.add_stat("HP",hp)
        self.pc_sheet.add_stat("STR",str)
        self.pc_sheet.add_stat("DEX",dex)
        self.pc_sheet.add_stat("CON",con)
        self.pc_sheet.add_stat("INT",int)
        self.pc_sheet.add_stat("WIS",wis)
        self.pc_sheet.add_stat("CHA",cha)


