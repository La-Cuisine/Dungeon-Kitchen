from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QFont, QPalette
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings

class GuiFunctions():
    def __init__(self,MainWindow):
        self.main = MainWindow
        self.ui = MainWindow.ui

        self.initialiseAppTheme()
        self.ui.character_btn.clicked.connect(self.switch_character_menu)
        self.ui.map_btn.clicked.connect(self.switch_map_menu)
        self.ui.server_btn.clicked.connect(self.switch_server_menu)
        self.ui.settings_btn.clicked.connect(self.switch_settings_menu)
        self.ui.information_btn.clicked.connect(self.switch_information_menu)
        self.ui.help_btn.clicked.connect(self.switch_help_menu)

    def initialiseAppTheme(self):
        """
        Initialise le thème de l'application
        """
        settings = QSettings()
        current_theme = settings.value("THEME")
        
        # Ajoute des thèmes à la liste des thèmes
        self.ui.theme_list.addItem("Dark")
        self.ui.theme_list.addItem("Light")

        # Connect le signal pour changer de thème
        self.ui.theme_list.currentTextChanged.connect(self.changeAppTheme)

    def changeAppTheme(self):
        """
        Change le thème de l'application
        """
        settings = QSettings()
        current_theme = settings.value("THEME")
        selected_theme = self.ui.theme_list.currentText()

        if current_theme != selected_theme:
            print("AAAAA")
            # Applique le nouveau thème
            settings.setValue("THEME", selected_theme)
            QAppSettings.updateAppSettings(self.main, reloadJson=True)

    def _update_server_label(self, state: str):
        """
        Met à jour l'affichage pour l'état du serveur.


        """
        if state == "Closed":
            self.server_label.setText("Serveur: Closed")
            self.server_label.setStyleSheet("color: #e74c3c; font-size: 13px;")
        elif state == "Open":
            self.server_label.setText("Serveur: Open")
            self.server_label.setStyleSheet("color: #2ecc71; font-size: 13px;")

    # ----------------------------------------------------------------
    # Fonctions pour changer le menu d'information 
    # ----------------------------------------------------------------

    def switch_settings_menu(self):
        self.ui.stacked_widget.setCurrentIndex(0)

    def switch_character_menu(self):
        self.ui.stacked_widget.setCurrentIndex(1)

    def switch_map_menu(self):
        self.ui.stacked_widget.setCurrentIndex(2)
    
    def switch_server_menu(self):
        self.ui.stacked_widget.setCurrentIndex(3)

    def switch_information_menu(self):
        self.ui.stacked_widget.setCurrentIndex(4)

    def switch_help_menu(self):
        self.ui.stacked_widget.setCurrentIndex(5)

    # ----------------------------------------------------------------
    # Fonctions pour manipuler le style de la page et des boutons
    # ----------------------------------------------------------------

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



