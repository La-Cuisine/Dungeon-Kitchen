"""
Sym_const.py
---------
Fichier contenant toutes les constantes symboliques.

Contenu :
  - Constantes pour le serveur.
  - Constantes pour les chemins relatifs de dossiers 
    pour les éléments du jeu (map, item, character...) 
  - Raccourcis pour certains éléments (extensions d'images, chemin de placeholder... )
"""
from PySide6.QtCore import QSize
from pathlib import Path
import sys           
import os            

# ----------------------------------------------------------------
# Chemins relatifs de dossiers pour les éléments du jeu 
# ----------------------------------------------------------------

# Assets image folder for character icons
CHARACTER_ICON_DIRECTORIES = [
    Path("Assets/Images/Characters"),
    Path("local/Assets/Images/Characters"),
]
CELL_DIRECTORIES = [
    Path("Assets/Images/Cells"),
    Path("local/Assets/Images/Cells"),
]
PROP_DIRECTORIES = [
    Path("Assets/Images/Props"),
    Path("local/Assets/Images/Props"),
]
ITEM_DIRECTORIES = [
    Path("Assets/Images/Items"),
    Path("local/Assets/Images/Items"),
]
SPELL_DIRECTORIES = [
    Path("Assets/Images/Spells"),
    Path("local/Assets/Images/Spells"),
]
BLUEPRINT_DIRECTORY = Path("local/Blueprint")

# Dossier de travail courant (la "session" active) et dossier
# dans lequel les sessions sont archivées / sauvegardées
SESSION_LOCAL_DIRECTORY = Path("local")
SESSION_PROJECTS_DIRECTORY = Path("projects")

# Arborescence de base recréée dans local/ lors de la création
# d'une nouvelle session vide
SESSION_SUBFOLDERS = [
    "Assets/Images/Cells",
    "Assets/Images/Characters",
    "Assets/Images/Props",
    "Assets/Images/Items",
    "Assets/Images/Spells",
    "Blueprint",
    "Sheets/NPC",
    "Sheets/PC",
    "Items/Weapon",
    "Items/Armour",
    "Items/Consumable",
    "Items/Miscellaneous",
    "Spells",
]

# ----------------------------------------------------------------
# Chemins relatifs de dossiers pour les éléments du jeu 
# ----------------------------------------------------------------

# Répertoire du script courant, utilisé comme base pour construire
# les chemins relatifs vers php-portable/ et site/.
# os.path.abspath garantit un chemin absolu même si le script est lancé
# depuis un répertoire différent.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin vers le dossier contenant le binaire PHP portable.
# Ce dossier doit se trouver au même niveau que server.py.
PHP_DIR = os.path.join(_BASE_DIR, "php-portable")

# Nom de l'exécutable PHP selon la plateforme :
#   - "php.exe" sur Windows (sys.platform == "win32")
#   - "php"     sur Linux / macOS
PHP_BIN = "php.exe" if sys.platform == "win32" else "php"

# Chemin complet vers l'exécutable PHP (utilisé dans la commande subprocess).
PHP_EXECUTABLE = os.path.join(PHP_DIR, PHP_BIN)

# Chemin vers le dossier racine du site PHP à servir.
# PHP utilisera ce dossier comme document root (option -t).
SITE_DIR = os.path.join(_BASE_DIR, "../site")

# Adresse IP sur laquelle le serveur PHP écoute.
# "127.0.0.1" = localhost uniquement (non accessible depuis le réseau local).
# Remplacez par "0.0.0.0" pour exposer le serveur sur le réseau local.
SERVER_HOST = "0.0.0.0"

# Port TCP sur lequel le serveur PHP écoute les requêtes HTTP.
# 8080 est un port non privilégié couramment utilisé pour le développement.
SERVER_PORT = 8080

# URL complète construite à partir de l'hôte et du port.
# Utilisée pour l'affichage dans l'interface et pour ouvrir le navigateur.
SERVER_URL = f"http://localhost:{SERVER_PORT}"

# ----------------------------------------------------------------
# Raccourcis pour certains éléments 
# ----------------------------------------------------------------

# Image utilisee comme aperçu quand aucune image n'a ete choisie
PLACEHOLDER_IMAGE = "image/placeholder.png"

# Taille des icones affichees devant chaque objet/sort dans les listes
# de l'inventaire et des sorts du menu Character
INVENTORY_ICON_SIZE = QSize(24, 24)

# Image extensions to show in the list
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".PNG"}
