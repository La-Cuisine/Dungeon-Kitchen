import os
from pathlib import Path
from PySide6.QtCore import QSettings, QTimer, Qt
from PySide6.QtGui import QColor, QPalette, QPainter, QBrush, QPixmap, QIcon
from PySide6.QtWidgets import QGraphicsScene, QFileDialog, QPushButton, QScrollArea, QWidget, QVBoxLayout, QSizePolicy, QListWidgetItem
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTheme import QCustomTheme
import webbrowser
# Import interne
from src.MJ_application.server import SERVER_URL, ServerController
from src.MJ_application.LogReaderThread import LogReaderThread
from src.MJ_application.grid import View_Grid, Grid, InvisibleWallLimit, DraggableImageList
from src.MJ_gamemode.MJ_gamemode import MainWindow as GameModeWindow
from obj.blueprint import *
from obj.game import *
from obj.items import *
from obj.pawns import *
from obj.player import *
from obj.save import *
from obj.skills import *

class GuiFunctions():
    def __init__(self,MainWindow):
        self.main = MainWindow
        self.ui = MainWindow.ui
        self._log_thread = None
        self._game_window = None
        self._inventory_items = []  # Item(s) du personnage en cours d'édition
        self._selected_inventory_row = None  # Ligne actuellement sélectionnée dans la liste
        self._editing_item_index = None  # Index de l'objet en cours d'édition (None = création)
        self._character_skills = []  # Skill(s)/sort(s) du personnage en cours d'édition
        self._selected_skill_row = None  # Ligne actuellement sélectionnée dans la liste de sorts
        self._editing_spell_index = None  # Index du sort en cours d'édition (None = création)
        self._controller = ServerController()
        self.settings =  QSettings("Dungeon Kitchen Company","Dungeon Kitchen")
        self.last_menu = self.settings.value("Menu")


        self.init_app_theme()
        self.init_action_menubar()
        self.init_app_btn_connect()
        self.init_info_menu()
        self.init_grid()
        self._init_inventory_scroll_areas()
        self._init_map_image_list()

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
        self.ui.character_btn.clicked.connect(self.switch_to_character_menu)
        self.ui.map_btn.clicked.connect(self.switch_to_map_menu)
        self.ui.server_btn.clicked.connect(self.switch_to_server_menu)
        self.ui.settings_btn.clicked.connect(self.switch_to_settings_menu)
        self.ui.information_btn.clicked.connect(self.switch_to_information_menu)
        self.ui.help_btn.clicked.connect(self.switch_to_help_menu)
        self.ui.item_btn.clicked.connect(self.switch_to_item_menu)
        self.ui.spell_btn.clicked.connect(self.switch_to_spell_menu)

        # Ouvre ou ferme le menu d'information
        self.ui.open_info_menu_btn.clicked.connect(self.switch_center_menu_display_state)
        self.ui.close_info_menu_btn.clicked.connect(self.switch_center_menu_display_state)

        # Stat/Inv
        self.ui.isNPC.toggled.connect(self.setNPC)
        self.ui.add_item_btn.clicked.connect(self.add_item_to_character)
        self.ui.edit_item_btn.clicked.connect(self.edit_selected_item)
        self.ui.remove_item_btn.clicked.connect(self.remove_selected_item_from_character)
        self.ui.add_spell_btn.clicked.connect(self.add_skill_to_character)
        self.ui.edit_spell_btn.clicked.connect(self.edit_selected_spell)
        self.ui.remove_spell_btn.clicked.connect(self.remove_selected_skill_from_character)

        # Ouvre ou ferme le log/chat
        self.ui.close_log_view_btn.clicked.connect(self.switch_log_display_state)
        
        # Add images
        # Add images
        self.ui.add_cells_image_btn.clicked.connect(
            lambda: self.load_image(self.CELL_DIRECTORIES, self.ui.cells_image_list)
        )

        self.ui.add_props_image_btn.clicked.connect(
            lambda: self.load_image(self.PROP_DIRECTORIES, self.ui.props_image_list)
        ) 

        # Save/Load
        self.ui.create_new_character_btn.clicked.connect(self.create_new_character)
        self.ui.save_character_btn.clicked.connect(self.save_character_stat)
        self.ui.load_character_btn.clicked.connect(self.load_character)
        self.ui.create_new_item_btn.clicked.connect(self.create_new_item)
        self.ui.save_item.clicked.connect(self.save_item)
        self.ui.load_item.clicked.connect(self.load_item)
        self.ui.create_new_spell_btn.clicked.connect(self.create_new_spell)
        self.ui.save_spell.clicked.connect(self.save_spell)
        self.ui.load_spell.clicked.connect(self.load_spell)
        
        # Démarre ou ferme le serveur
        self.ui.open_server_btn.clicked.connect(self._update_server_label_open)
        self.ui.close_server_btn.clicked.connect(self._update_server_label_close)

        self.ui.open_server_btn.clicked.connect(self._start_server)
        self.ui.close_server_btn.clicked.connect(self._stop_server)
        self.ui.open_website_btn.clicked.connect(self._open_browser)
        self.ui.open_game_interface_btn.clicked.connect(self._open_game_interface)

        # Settings
        self.ui.theme_list.currentTextChanged.connect(self.changeAppTheme)
    
    def _init_inventory_scroll_areas(self):
        """
        Remplace les QGridLayout item_grid et spell_grid (définis dans le fichier
        UI auto-généré) par des QScrollArea contenant un QVBoxLayout dédié.
        Cela permet d'afficher un ascenseur vertical dès que la liste dépasse
        la hauteur disponible, sans modifier le fichier UI.
        """
        # --- Inventory (items) ---
        # Retire le QGridLayout nu de son parent et le remplace par un QScrollArea
        inventory_parent_layout = self.ui.verticalLayout_18  # layout du tab "inventory"

        # Supprime l'ancien item_grid du parent layout
        index = inventory_parent_layout.indexOf(self.ui.item_grid)
        inventory_parent_layout.removeItem(self.ui.item_grid)

        # Crée le conteneur interne (QWidget + QVBoxLayout) pour les boutons
        self._item_list_widget = QWidget()
        self._item_list_layout = QVBoxLayout(self._item_list_widget)
        self._item_list_layout.setContentsMargins(0, 0, 0, 0)
        self._item_list_layout.setSpacing(2)
        self._item_list_layout.addStretch()  # pousse les boutons vers le haut

        # Crée le QScrollArea
        self._item_scroll_area = QScrollArea()
        self._item_scroll_area.setWidgetResizable(True)
        self._item_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._item_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._item_scroll_area.setWidget(self._item_list_widget)
        self._item_scroll_area.setFrameShape(self._item_scroll_area.Shape.NoFrame)

        # Insère le QScrollArea exactement là où était item_grid
        inventory_parent_layout.insertWidget(index, self._item_scroll_area, 1)

        # --- Spell list ---
        spell_parent_layout = self.ui.verticalLayout_16  # layout du tab "spell"

        index_spell = spell_parent_layout.indexOf(self.ui.spell_grid)
        spell_parent_layout.removeItem(self.ui.spell_grid)

        self._spell_list_widget = QWidget()
        self._spell_list_layout = QVBoxLayout(self._spell_list_widget)
        self._spell_list_layout.setContentsMargins(0, 0, 0, 0)
        self._spell_list_layout.setSpacing(2)
        self._spell_list_layout.addStretch()

        self._spell_scroll_area = QScrollArea()
        self._spell_scroll_area.setWidgetResizable(True)
        self._spell_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._spell_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._spell_scroll_area.setWidget(self._spell_list_widget)
        self._spell_scroll_area.setFrameShape(self._spell_scroll_area.Shape.NoFrame)

        spell_parent_layout.insertWidget(index_spell, self._spell_scroll_area, 1)

    # Assets image folder (relative to the project root)
    CELL_DIRECTORIES = [
        Path("Assets/Images/Cells"),
        Path("local/Assets/Images/Cells"),
    ]
    PROP_DIRECTORIES = [
        Path("Assets/Images/Props"),
        Path("local/Assets/Images/Props"),
    ]

    # Image extensions to show in the list
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"}

    def _populate_image_list(self, list_widget, directories):
        """
        Populate a QListWidget with images found in several folders.
        """
        list_widget.clear()

        images = {}

        for directory in directories:
            if not directory.is_dir():
                continue

            for file in directory.iterdir():
                if file.suffix.lower() not in self.IMAGE_EXTENSIONS:
                    continue

                # local folder overrides base folder
                images[file.name] = file

        for file in sorted(images.values(), key=lambda p: p.name.lower()):
            item = QListWidgetItem(file.name)

            pixmap = QPixmap(str(file))
            if not pixmap.isNull():
                item.setIcon(
                    QIcon(
                        pixmap.scaled(
                            32,
                            32,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                )

            item.setData(Qt.ItemDataRole.UserRole, str(file))
            list_widget.addItem(item)

    def _init_map_image_list(self):
        """
        Remplace les QListWidget generes par Qt Designer (cells_image_list,
        props_image_list) par des DraggableImageList : meme apparence et
        meme comportement, mais leurs items peuvent desormais etre glisses
        (drag and drop) vers une case de la grille pour y deposer l'image.

        Remplit ensuite les panneaux Cells et Props.
        """

        if hasattr(self.ui, "cells_image_list") and hasattr(self.ui, "verticalLayout_cells"):
            self.ui.cells_image_list = self._make_draggable_image_list(
                self.ui.cells_image_list, self.ui.verticalLayout_cells
            )
            self._populate_image_list(
                self.ui.cells_image_list,
                self.CELL_DIRECTORIES
            )

        if hasattr(self.ui, "props_image_list") and hasattr(self.ui, "verticalLayout_props"):
            self.ui.props_image_list = self._make_draggable_image_list(
                self.ui.props_image_list, self.ui.verticalLayout_props
            )
            self._populate_image_list(
                self.ui.props_image_list,
                self.PROP_DIRECTORIES
            )

    def _make_draggable_image_list(self, old_list, layout):
        """
        Remplace old_list (QListWidget cree par Qt Designer) par un
        DraggableImageList insere au meme endroit dans layout, en
        conservant son nom d'objet et la taille de ses icones.

        Renvoie la nouvelle instance (a reassigner sur self.ui.<nom>).
        """
        index = layout.indexOf(old_list)
        name = old_list.objectName()
        icon_size = old_list.iconSize()
        parent = old_list.parentWidget()

        layout.removeWidget(old_list)
        old_list.deleteLater()

        new_list = DraggableImageList(parent)
        new_list.setObjectName(name)
        new_list.setIconSize(icon_size)
        new_list.setUniformItemSizes(True)

        layout.insertWidget(index, new_list)
        return new_list

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
        # Display menu
        self.ui.actionLog_Chat.toggled.connect(self.switch_log_display_state)
        self.ui.actionInfo_menu.toggled.connect(self.switch_center_menu_display_state)
        
        # Close application
        self.ui.actionClose.triggered.connect(self.closeEvent)

        # New object
        self.ui.actionNew_character.triggered.connect(self.create_new_character)
        self.ui.actionNew_item.triggered.connect(self.create_new_item)
        self.ui.actionNew_spell.triggered.connect(self.create_new_spell)
        #self.ui.actionNew_map.triggered.connect(self.create_new_map)
        
        # Load object
        self.ui.actionOpen_character.triggered.connect(self.load_character)
        self.ui.actionOpen_item.triggered.connect(self.load_item)
        self.ui.actionOpen_spell.triggered.connect(self.load_spell)
        #self.ui.actionOpen_map.triggered.connect(self.load_map)
        
        # Save/Save as
        self.ui.actionSave.triggered.connect(self.save_actionmenu)
        #self.ui.actionSave_as.triggered.connect(self.save_as_actionmenu)

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

    def switch_to_character_menu(self):
        self.ui.stacked_widget.setCurrentIndex(1)
        self.settings.setValue("MENU INFO",1)
        self._open_center_menu()    

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

    def switch_to_item_menu(self):
        self.ui.stacked_widget.setCurrentIndex(6)
        self.settings.setValue("MENU INFO",6)
        self._open_center_menu()

    def switch_to_spell_menu(self):
        self.ui.stacked_widget.setCurrentIndex(7)
        self.settings.setValue("MENU INFO",7)
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
    # Stat/Inv/Spell
    # ----------------------------------------------------------------

    def setNPC(self):
        """
        Affiche ou cache les options liées au NPC
        """
        # Active le choix de l'alignement d'un npc
        if(self.ui.isNPC.isChecked() == True):
            self.ui.alignement_NPC.setVisible(True)

        # Désactive le choix de l'alignement d'un npc
        elif(self.ui.isNPC.isChecked() == False):
            self.ui.alignement_NPC.setVisible(False)

        else:
            print("Erreur setNPC")

    #--------Création d'objet----------#

    def create_new_character(self):
        """
        Slot connecté au signal clicked du bouton "Create new character".
        Vide le panneau de personnage pour permettre la saisie d'une
        nouvelle fiche, et bascule sur le menu Character.
        """
        # Réinitilialise les widgets
        self.ui.character_name.setText(None)
        self.ui.hp_nb.setValue(0)
        self.ui.str_nb.setValue(0)
        self.ui.dex_nb.setValue(0)
        self.ui.con_nb.setValue(0)
        self.ui.int_nb.setValue(0)
        self.ui.wis_nb.setValue(0)
        self.ui.cha_nb.setValue(0)

        # Décoche la case isNPC
        self.ui.isNPC.blockSignals(True)
        self.ui.isNPC.setChecked(False)
        self.ui.isNPC.blockSignals(False)

        # setNPC() n'est pas déclenché automatiquement (signal bloqué
        # ci-dessus), donc on cache/réinitialise l'alignement à la main.
        self.ui.alignement_NPC.setCurrentIndex(0)
        self.setNPC()

        # Réinitilialise l'inventaire
        self._inventory_items = []
        self._selected_inventory_row = None
        self._refresh_inventory_grid()

        # Réinitilialise la liste de sorts
        self._character_skills = []
        self._selected_skill_row = None
        self._refresh_skill_grid()

        # Affiche le panneau Character pour la saisie
        self.switch_to_character_menu()

    def create_new_item(self):
        """
        Slot connecté au signal clicked du bouton \"Create new item\".
        Vide le panneau Item pour permettre la saisie d'un
        nouvel objet, et bascule sur le menu Item.
        """
        # Mode création : aucun objet existant n'est en cours d'édition
        self._editing_item_index = None

        # Réinitialise les champs de l'objet
        self.ui.item_name.setText("")
        self.ui.item_type.setCurrentIndex(0)
        self.ui.item_description.clear()

        # Affiche le panneau Item pour la saisie
        self.switch_to_item_menu()

    def create_new_spell(self):
        """
        Slot connecté au signal clicked du bouton \"Create new spell\".
        Vide le panneau Spell pour permettre la saisie d'un
        nouveau sort, et bascule sur le menu Spell.
        """
        # Mode création : aucun sort existant n'est en cours d'édition
        self._editing_spell_index = None

        # Réinitialise les champs du sort
        self.ui.spell_name.setText("")
        self.ui.spell_description.clear()

        # Affiche le panneau Spell pour la saisie
        self.switch_to_spell_menu()

    #---------Ajout d'objet----------#

    def add_item_to_character(self):
        """
        Slot connecté au signal clicked du bouton "Add item".
        Ouvre un sélecteur de fichier pour choisir un objet (.xml,
        normalement sous ./local/Items/...) et l'ajoute à l'inventaire
        du personnage en cours de création/édition.
        """
        try:
            item = self.load_xml()
        except Exception as exc:
            # L'utilisateur a annulé la sélection, ou le fichier est invalide
            self._append_log(f"[ERREUR] {exc}")
            return

        if not isinstance(item, Item):
            self._append_log("[ERREUR] Le fichier sélectionné n'est pas un objet (Item) valide.")
            return

        # Ajoute l'objet à l'inventaire en mémoire et rafraîchit l'affichage
        self._inventory_items.append(item)
        self._refresh_inventory_grid()

    def add_skill_to_character(self):
        """
        Slot connecté au signal clicked du bouton "Add Spell" (panneau Spell
        de la fiche de personnage). Ouvre un sélecteur de fichier pour
        choisir un sort (.xml, normalement sous ./local/Spells/) et l'ajoute
        à la liste de sorts du personnage en cours de création/édition.
        """
        try:
            skill = self.load_xml()
        except Exception as exc:
            # L'utilisateur a annulé la sélection, ou le fichier est invalide
            self._append_log(f"[ERREUR] {exc}")
            return

        if not isinstance(skill, Skill):
            self._append_log("[ERREUR] Le fichier sélectionné n'est pas un sort (Skill) valide.")
            return

        # Ajoute le sort à la liste en mémoire et rafraîchit l'affichage
        self._character_skills.append(skill)
        self._refresh_skill_grid()

    #---------Retire d'objet----------#

    def remove_selected_item_from_character(self):
        """
        Slot connecté au signal clicked du bouton "Remove item".
        Retire de l'inventaire en cours d'édition l'objet actuellement
        sélectionné dans la liste (aucune action si rien n'est sélectionné).
        """
        if self._selected_inventory_row is None:
            self._append_log("[ERREUR] Aucun objet sélectionné dans l'inventaire.")
            return

        del self._inventory_items[self._selected_inventory_row]
        self._selected_inventory_row = None
        self._refresh_inventory_grid()

    def remove_selected_skill_from_character(self):
        """
        Slot connecté au signal clicked du bouton "Remove spell".
        Retire de la liste de sorts en cours d'édition le sort actuellement
        sélectionné (aucune action si rien n'est sélectionné).
        """
        if self._selected_skill_row is None:
            self._append_log("[ERREUR] Aucun sort sélectionné dans la liste.")
            return

        del self._character_skills[self._selected_skill_row]
        self._selected_skill_row = None
        self._refresh_skill_grid()

    #---------Edition d'objet----------#

    def edit_selected_item(self):
        """
        Slot connecté au signal clicked du bouton "Edit item".
        Pré-remplit le formulaire Item avec les données de l'objet
        sélectionné dans l'inventaire et bascule vers le menu Item.
        L'index de l'objet est mémorisé dans _editing_item_index pour que
        save_item() mette à jour l'entrée existante au lieu d'en créer une.
        """
        if self._selected_inventory_row is None:
            self._append_log("[ERREUR] Aucun objet sélectionné dans l'inventaire.")
            return

        item = self._inventory_items[self._selected_inventory_row]
        self._editing_item_index = self._selected_inventory_row

        # Pré-remplit le formulaire avec les données de l'objet
        self.ui.item_name.setText(item.name())
        self.ui.item_type.setCurrentText(item.type())
        self.ui.item_description.setText(item.description())

        # Bascule vers le menu Item
        self.switch_to_item_menu()

    def edit_selected_spell(self):
        """
        Slot connecté au signal clicked du bouton "Edit spell".
        Pré-remplit le formulaire Spell avec les données du sort sélectionné
        dans la liste et bascule vers le menu Spell.
        L'index du sort est mémorisé dans _editing_spell_index pour que
        save_spell() mette à jour l'entrée existante au lieu d'en créer une.
        """
        if self._selected_skill_row is None:
            self._append_log("[ERREUR] Aucun sort sélectionné dans la liste.")
            return

        skill = self._character_skills[self._selected_skill_row]
        self._editing_spell_index = self._selected_skill_row

        # Pré-remplit le formulaire avec les données du sort
        self.ui.spell_name.setText(skill.name())
        self.ui.spell_description.setText(skill.description())

        # Bascule vers le menu Spell
        self.switch_to_spell_menu()

    #---------Sélection d'objet----------#

    def _select_inventory_row(self, row):
        """
        Mémorise la ligne actuellement sélectionnée dans la liste de
        l'inventaire et affiche sa description (appelé quand l'utilisateur
        clique sur un objet).
        """
        self._selected_inventory_row = row
        self.ui.item_desc_display.setPlainText(self._inventory_items[row].description())

    def _select_skill_row(self, row):
        """
        Mémorise la ligne actuellement sélectionnée dans la liste de
        sorts et affiche sa description (appelé quand l'utilisateur
        clique sur un sort).
        """
        self._selected_skill_row = row
        self.ui.spell_desc_display.setPlainText(self._character_skills[row].description())

    #---------Rafraichisement des objets----------#

    def _refresh_inventory_grid(self):
        """
        Reconstruit entièrement l'affichage de la liste d'objets dans la
        QScrollArea de l'inventaire : une liste verticale (du haut vers le bas,
        une seule colonne) d'objets sélectionnables.
        Le bouton "Remove item" retire l'objet sélectionné.
        """
        layout = self._item_list_layout

        # Vide le layout (en conservant le stretch final)
        while layout.count() > 1:  # garde le stretch en dernière position
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

        # Vide la description tant qu'aucune sélection n'est restaurée
        self.ui.item_desc_display.clear()

        # Reconstruit une ligne par objet, du haut vers le bas
        for row, item in enumerate(self._inventory_items):
            btn = QPushButton(f"{item.name()} ({item.type()})")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)  # Une seule ligne sélectionnable à la fois
            btn.setStyleSheet(
                "QPushButton {"
                "  text-align: left;"
                "  padding: 4px 8px;"
                "  border: none;"
                "  background: transparent;"
                "}"
                "QPushButton:checked {"
                "  background-color: #3498db;"
                "  color: white;"
                "  border-radius: 4px;"
                "}"
            )
            btn.toggled.connect(lambda checked, r=row: self._select_inventory_row(r) if checked else None)
            layout.insertWidget(row, btn)  # insère avant le stretch

            # Restaure la sélection si elle est encore valide après le rafraîchissement
            if row == self._selected_inventory_row:
                btn.setChecked(True)

    def _refresh_skill_grid(self):
        """
        Reconstruit entièrement l'affichage de la liste de sorts dans la
        QScrollArea dédiée : une liste verticale (du haut vers le bas, une
        seule colonne) de sorts sélectionnables.
        Le bouton "Remove spell" retire le sort sélectionné.
        """
        layout = self._spell_list_layout

        # Vide le layout (en conservant le stretch final)
        while layout.count() > 1:
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()

        # Vide la description tant qu'aucune sélection n'est restaurée
        self.ui.spell_desc_display.clear()

        # Reconstruit une ligne par sort, du haut vers le bas
        for row, skill in enumerate(self._character_skills):
            btn = QPushButton(skill.name())
            btn.setCheckable(True)
            btn.setAutoExclusive(True)  # Une seule ligne sélectionnable à la fois
            btn.setStyleSheet(
                "QPushButton {"
                "  text-align: left;"
                "  padding: 4px 8px;"
                "  border: none;"
                "  background: transparent;"
                "}"
                "QPushButton:checked {"
                "  background-color: #3498db;"
                "  color: white;"
                "  border-radius: 4px;"
                "}"
            )
            btn.toggled.connect(lambda checked, r=row: self._select_skill_row(r) if checked else None)
            layout.insertWidget(row, btn)  # insère avant le stretch

            # Restaure la sélection si elle est encore valide après le rafraîchissement
            if row == self._selected_skill_row:
                btn.setChecked(True)

    #---------Réinitialisation d'objet----------#

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

    def _open_game_interface(self):
        """
        Slot connecté au signal clicked du bouton "Open game interface".
        Ouvre la fenêtre du mode MJ (MJ_gamemode.MainWindow) en tant que
        fenêtre indépendante. La référence est conservée sur self._game_window
        pour éviter que Python ne la détruise (garbage collection) juste
        après l'appel à show().
        """
        if self._game_window is None:
            self._game_window = GameModeWindow()

        self._game_window.show()
        self._game_window.raise_()
        self._game_window.activateWindow()

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

    def save_character_stat(self):
        """
        Sauvegarde les informations du personnage 
        dans un fichier XML
        """
        # Récolte du nom du personnage
        name = self.ui.character_name.toPlainText().strip()
        if not name:
            name = "Unnamed"

        # Récolte des attributs
        is_npc = self.ui.isNPC.isChecked()

        hp  = self.ui.hp_nb.value()
        str = self.ui.str_nb.value()
        dex = self.ui.dex_nb.value()
        con = self.ui.con_nb.value()
        int = self.ui.int_nb.value()
        wis = self.ui.wis_nb.value()
        cha = self.ui.cha_nb.value()

        # Vérifie si l'entité est un NPC ou un PC
        if is_npc:
            alignement = self.ui.alignement_NPC.currentIndex()
            sheet = NPC(Name=name, Alignement=alignement)
            save_dir = "./local/Sheets/NPC/"
        else:
            sheet = PC(Name=name)
            save_dir = "./local/Sheets/PC/"

        # Ajoute les attibuts sur la fiche de personnage
        sheet.add_stat("HP",  hp)
        sheet.add_stat("STR", str)
        sheet.add_stat("DEX", dex)
        sheet.add_stat("CON", con)
        sheet.add_stat("INT", int)
        sheet.add_stat("WIS", wis)
        sheet.add_stat("CHA", cha)

        # Ajoute les objets de l'inventaire en cours d'édition sur la fiche
        for item in self._inventory_items:
            sheet.addItem(item)

        # Ajoute les sorts en cours d'édition sur la fiche
        for skill in self._character_skills:
            sheet.addSkill(skill)


        # Création du fichier XML
        os.makedirs(save_dir, exist_ok=True)
        toXML_saveto(sheet, save_dir)

        self.pc_sheet = sheet  # keep reference if needed elsewhere
        self._append_log(f"[INFO] Personnage '{name}' sauvegardé dans {save_dir}")
    
    def save_item(self):
        """
        Sauvegarde les informations de l'objet.
        - Mode édition (depuis l'inventaire du personnage) : met à jour
          uniquement l'entrée en mémoire, sans toucher au fichier XML sur
          le disque, puis revient au menu Character.
        - Mode création : sauvegarde l'objet dans un fichier XML comme
          d'habitude.
        """
        # Récupère les informations de l'objet
        #TODO
        # Récup image et stocke image
        item_name = self.ui.item_name.text().strip()
        item_type = self.ui.item_type.currentText()
        item_description = self.ui.item_description.toPlainText().strip()
        item = Item(Name=item_name, Type=item_type, Description=item_description)

        if self._editing_item_index is not None:
            # Mode édition : mise à jour en mémoire uniquement
            self._inventory_items[self._editing_item_index] = item
            self._selected_inventory_row = self._editing_item_index
            self._editing_item_index = None
            self._refresh_inventory_grid()
            self.switch_to_character_menu()
            self._append_log(f"[INFO] Objet '{item_name}' mis à jour dans l'inventaire du personnage.")
        else:
            # Mode création : sauvegarde dans le fichier XML
            if item_type == "Weapon":
                save_dir = "./local/Items/Weapon/"
            elif item_type == "Armour":
                save_dir = "./local/Items/Armour/"
            elif item_type == "Consumable":
                save_dir = "./local/Items/Consumable/"
            else:
                save_dir = "./local/Items/Miscellaneous/"

            os.makedirs(save_dir, exist_ok=True)
            toXML_saveto(item, save_dir)
            self._append_log(f"[INFO] Objet '{item_name}' sauvegardé dans {save_dir}")

    def save_spell(self):
        """
        Sauvegarde les informations du sort.
        - Mode édition (depuis la liste de sorts du personnage) : met à jour
          uniquement l'entrée en mémoire, sans toucher au fichier XML sur
          le disque, puis revient au menu Character.
        - Mode création : sauvegarde le sort dans un fichier XML comme
          d'habitude.
        """
        # Récupère les informations du sort
        #TODO
        # Récup image et stocke image
        spell_name = self.ui.spell_name.text().strip()
        spell_description = self.ui.spell_description.toPlainText().strip()
        spell = Skill(Name=spell_name, Description=spell_description)

        if self._editing_spell_index is not None:
            # Mode édition : mise à jour en mémoire uniquement
            self._character_skills[self._editing_spell_index] = spell
            self._selected_skill_row = self._editing_spell_index
            self._editing_spell_index = None
            self._refresh_skill_grid()
            self.switch_to_character_menu()
            self._append_log(f"[INFO] Sort '{spell_name}' mis à jour dans la liste de sorts du personnage.")
        else:
            # Mode création : sauvegarde dans le fichier XML
            save_dir = "./local/Spells/"
            os.makedirs(save_dir, exist_ok=True)
            toXML_saveto(spell, save_dir)
            self._append_log(f"[INFO] Sort '{spell_name}' sauvegardé dans {save_dir}")

    def load_xml(self):
        """
        Charge un fichier XML et renvoie le chemin absolue du fichier
        """
        # Ouvre l'explorateur de fichier et 
        # récupère le chemin absolue du fichier
        fileName = QFileDialog.getOpenFileName( None, "Select File", "", "(*.xml)")
        object = fromXML(fileName[0])

        if(object == None):
            raise Exception("Erreur_file_selection")
        else:
            return object
    
    def load_character(self):
        """
        Charge la feuille d'un personnage et associe 
        les attributs, inventaire, sorts
        """
        sheet = self.load_xml()
        if not(isinstance(sheet,PC) or isinstance(sheet,NPC)):
            raise Exception("Invalid_object_type (Expecting character)")
        else:
            # Récupère les attributs
            name = sheet.name()
            hp  = sheet.get_stat("HP")
            str = sheet.get_stat("STR")
            dex = sheet.get_stat("DEX")
            con = sheet.get_stat("CON")
            int = sheet.get_stat("INT")
            wis = sheet.get_stat("WIS")
            cha = sheet.get_stat("CHA")

            # Assigne les attributs aux bons widgets
            self.ui.character_name.setText(name)
            self.ui.hp_nb.setValue(hp)
            self.ui.str_nb.setValue(str)
            self.ui.dex_nb.setValue(dex)
            self.ui.con_nb.setValue(con)
            self.ui.int_nb.setValue(int)
            self.ui.wis_nb.setValue(wis)
            self.ui.cha_nb.setValue(cha)

            # Déconnecte isNPC du signal
            self.ui.isNPC.blockSignals(True)
            
            # Vérifie si le personnage est un NPC ou un PC
            if(isinstance(sheet,NPC)):
                self.ui.isNPC.setChecked(True)
                self.ui.alignement_NPC.setCurrentIndex(sheet.alignement())
            else:
                self.ui.isNPC.setChecked(False)

            # Reconnecte isNPC du signal
            self.ui.isNPC.blockSignals(False)

            self.setNPC()

            # Récupère l'inventaire stocké dans la fiche et l'affiche
            self._inventory_items = list(sheet.inventory())
            self._selected_inventory_row = None
            self._refresh_inventory_grid()

            # Récupère les sorts stockés dans la fiche et les affiche
            self._character_skills = list(sheet.skills())
            self._selected_skill_row = None
            self._refresh_skill_grid()

            self.switch_to_character_menu()

    def load_item(self):
        """
        Charge un objet et affiche le nom,
        le titre et la description de l'objet
        dans le menu Item
        """
        item = self.load_xml()
        if not(isinstance(item,Item)):
            raise Exception("Invalid_object_type (Expecting item)")
        else:
            # Récupère les informations de l'objet
            #TODO
            # Charge image
            item_name = item.name()
            item_type = item.type()
            item_description = item.description()
            
            # Assigne les attributs aux bons widgets
            self.ui.item_name.setText(item_name)
            self.ui.item_type.setCurrentText(item_type)
            self.ui.item_description.setText(item_description)
            self.switch_to_item_menu()

    def load_spell(self):
        """
        Charge un sort et affiche le nom
        et la description du sort
        dans le menu Spell
        """
        spell = self.load_xml()
        if not(isinstance(spell,Skill)):
            raise Exception("Invalid_object_type (Expecting spell)")
        else:
            # Récupère les informations du sort
            #TODO
            # Charge image
            spell_name = spell.name()
            spell_description = spell.description()

            # Assigne les attributs aux bons widgets
            self.ui.spell_name.setText(spell_name)
            self.ui.spell_description.setText(spell_description)

            self.switch_to_spell_menu()

    def save_actionmenu(self):
        """
        Action de sauvegarde pour l'action save dans le menubar
        """
        index = self.ui.stacked_widget.currentIndex()

        match index:
            case 1: # Character
                self.save_character_stat()
            case 6: # Item
                self.save_item()
            case 7: # Spell
                self.save_spell()
            case _: # Default case
                self._append_log("Ne peut pas sauvegarder ces informations")

    # TODO
    def save_as_actionmenu(self):
        """
        Action de sauvegarde pour l'action save_as dans le menubar
        """
        #fileName = QFileDialog.getSaveFileName(None, "Save File", "", "(*.xml)")
        #print(fileName)
    
    def load_image(self, directories, target_list):
        """
        Import an image into the local assets folder and refresh the list.

        directories:
            [Assets/..., local/Assets/...]
        target_list:
            cells_image_list or props_image_list
        """

        filename, _ = QFileDialog.getOpenFileName(
            self.main,
            "Select image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp)"
        )

        if not filename:
            return

        source = Path(filename)

        # Always save in local folder
        local_dir = directories[-1]
        local_dir.mkdir(parents=True, exist_ok=True)

        destination = local_dir / source.name

        try:
            import shutil

            shutil.copy2(source, destination)

            self._append_log(
                f"[INFO] Image '{source.name}' copied to '{local_dir}'."
            )

            # Refresh list
            self._populate_image_list(target_list, directories)

            matches = target_list.findItems(
                source.name,
                Qt.MatchFlag.MatchExactly
            )
            
            if matches:
                target_list.setCurrentItem(matches[0])
            
        except Exception as exc:
            self._append_log(
                f"[ERREUR] Impossible d'ajouter l'image : {exc}"
            )