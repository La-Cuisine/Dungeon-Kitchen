from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QPalette
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
import webbrowser
# Import interne
from designer_pyside.src.MJ_application.server import SERVER_URL, ServerController
from designer_pyside.src.MJ_application.LogReaderThread import LogReaderThread

class GuiFunctions():
    def __init__(self,MainWindow):
        self.main = MainWindow
        self.ui = MainWindow.ui
        self._controller = ServerController()

        self.init_app_theme()
        self.init_app_widget_color()
        self.init_app_btn_connect()
        self._open_center_menu()

    # ----------------------------------------------------------------
    # Initialisation de l'application 
    # ----------------------------------------------------------------

    def init_app_widget_color(self):
        """
        Initialise les couleurs de certains éléments de l'UI
        """
        # Couleur du label du menu "server"
        self.ui.server_state_label.setStyleSheet("color: #e74c3c; font-size: 13px;")

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

    def init_app_theme(self):
        """
        Initialise le thème de l'application
        """
        settings = QSettings()
        settings.setValue("theme",0)
        current_theme = settings.value("theme")
        # Ajoute des thèmes à la liste des thèmes
        self.ui.theme_list.addItem("Dark")
        self.ui.theme_list.addItem("Light")
        if(current_theme == None):
            self._apply_dark_theme()

        # Positionne le combobox sur le thème actuel sans déclencher le signal
        index = self.ui.theme_list.findText(current_theme)
        if index >= 0:
            self.ui.theme_list.setCurrentIndex(index)

        # Connect le signal pour changer de thème
        self.ui.theme_list.currentTextChanged.connect(self.changeAppTheme)
        
        
    def init_app_btn_connect(self):
        """
        Initialise les signaux pour les boutons de l'application
        """
        # Change le menu d'information
        self.ui.character_btn.clicked.connect(self.switch_to_character_menu)
        self.ui.map_btn.clicked.connect(self.switch_to_map_menu)
        self.ui.server_btn.clicked.connect(self.switch_to_server_menu)
        self.ui.settings_btn.clicked.connect(self.switch_to_settings_menu)
        self.ui.information_btn.clicked.connect(self.switch_to_information_menu)
        self.ui.help_btn.clicked.connect(self.switch_to_help_menu)
        
        # Ouvre ou ferme le menu d'information
        self.ui.open_info_menu_btn.clicked.connect(self._open_center_menu)
        self.ui.close_info_menu_btn.clicked.connect(self._close_center_menu)
        
        # Démarre ou ferme le serveur
        self.ui.open_server_btn.clicked.connect(self._update_server_label_open)
        self.ui.close_server_btn.clicked.connect(self._update_server_label_close)

        self.ui.open_server_btn.clicked.connect(self._start_server)
        self.ui.close_server_btn.clicked.connect(self._stop_server)
        self.ui.open_website_btn.clicked.connect(self._open_browser)
    
    # ----------------------------------------------------------------
    # Changement des attributs de widget
    # ----------------------------------------------------------------

    def change_open_menu_btn(self, state):
        if(state == True):
            self.ui.open_info_menu_btn.clicked.connect(self._close_center_menu)
            self.ui.open_info_menu_btn.setIcon(QIcon("image/Undo.png"))
        elif(state == False):
            self.ui.open_info_menu_btn.clicked.connect(self._open_center_menu)
            self.ui.open_info_menu_btn.setIcon(QIcon("image/Redo.png"))

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
        event.accept()        # Confirme la fermeture → la fenêtre est détruite

    # ----------------------------------------------------------------
    # Menu d'information 
    # ----------------------------------------------------------------

    def switch_to_settings_menu(self):
        self.ui.stacked_widget.setCurrentIndex(0)
        if self.ui.center_menu.isVisible() == False:
            self._open_center_menu()

    def switch_to_character_menu(self):
        self.ui.stacked_widget.setCurrentIndex(1)
        if self.ui.center_menu.isVisible() == False:
            self._open_center_menu()

    def switch_to_map_menu(self):
        self.ui.stacked_widget.setCurrentIndex(2)
        if self.ui.center_menu.isVisible() == False:
            self._open_center_menu()
    
    def switch_to_server_menu(self):
        self.ui.stacked_widget.setCurrentIndex(3)
        if self.ui.center_menu.isVisible() == False:
            self._open_center_menu()

    def switch_to_information_menu(self):
        self.ui.stacked_widget.setCurrentIndex(4)
        if self.ui.center_menu.isVisible() == False:
            self._open_center_menu()

    def switch_to_help_menu(self):
        self.ui.stacked_widget.setCurrentIndex(5)
        if self.ui.center_menu.isVisible() == False:
            self._open_center_menu()

    def _open_center_menu(self):
        """Affiche le panneau central."""
        self.ui.center_menu.setVisible(True)
        self.change_open_menu_btn(True)

    def _close_center_menu(self):
        """Cache le panneau central."""
        self.ui.center_menu.setVisible(False)
        self.change_open_menu_btn(False)

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

    # ----------------------------------------------------------------
    # Fonctions pour manipuler le style de la page et des boutons
    # ----------------------------------------------------------------

    def changeAppTheme(self):
        """
        Change le thème de l'application
        """ 
        settings = QSettings()
        current_theme = settings.value("THEME")
        selected_theme = self.ui.theme_list.currentText()

        #deka
        # if current_theme != selected_theme:
        #     print("AAAAA")
        #     # Applique le nouveau thème
        #     settings.setValue("THEME", selected_theme)
        #     QAppSettings.updateAppSettings(self.main, reloadJson=True)
        
        #sam
        if current_theme != selected_theme:
            settings.setValue("THEME", selected_theme)
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
        print("STATUS")

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
        )
        
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
        )

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



