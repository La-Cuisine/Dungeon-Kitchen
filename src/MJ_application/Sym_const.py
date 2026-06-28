"""
Sym_const.py
---------
Fichier contenant toutes les constantes symboliques.
"""
from PySide6.QtCore import QSize
from pathlib import Path
import sys           
import os            

# ----------------------------------------------------------------
# Racine de l'application
# En mode PyInstaller --onedir : dossier contenant le .exe
# En mode développement        : racine du projet (3 niveaux au-dessus de ce fichier)
# ----------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # Exécutable PyInstaller : sys.executable = .../dist/MJ_Application/MJ_Application.exe
    APP_ROOT = Path(os.path.dirname(sys.executable))
else:
    # Développement : src/MJ_application/Sym_const.py → remonter 3 niveaux
    APP_ROOT = Path(os.path.abspath(__file__)).parent.parent.parent

# ----------------------------------------------------------------
# Chemins relatifs de dossiers pour les éléments du jeu 
# ----------------------------------------------------------------

CHARACTER_ICON_DIRECTORIES = [
    APP_ROOT / "Assets/Images/Characters",
    APP_ROOT / "local/Assets/Images/Characters",
]
CELL_DIRECTORIES = [
    APP_ROOT / "Assets/Images/Cells",
    APP_ROOT / "local/Assets/Images/Cells",
]
PROP_DIRECTORIES = [
    APP_ROOT / "Assets/Images/Props",
    APP_ROOT / "local/Assets/Images/Props",
]
ITEM_DIRECTORIES = [
    APP_ROOT / "Assets/Images/Items",
    APP_ROOT / "local/Assets/Images/Items",
]
SKILL_DIRECTORIES = [
    APP_ROOT / "Assets/Images/Spells",
    APP_ROOT / "local/Assets/Images/Spells",
]
BLUEPRINT_DIRECTORY = APP_ROOT / "local/Blueprint"

SESSION_LOCAL_DIRECTORY    = APP_ROOT / "local"
SESSION_PROJECTS_DIRECTORY = APP_ROOT / "projects"

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
# Chemins serveur PHP
# ----------------------------------------------------------------

# Répertoire de ce fichier → src/MJ_application/
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PHP_DIR        = os.path.join(_BASE_DIR, "php-portable")
PHP_BIN        = "php.exe" if sys.platform == "win32" else "php"
PHP_EXECUTABLE = os.path.join(PHP_DIR, PHP_BIN)
SITE_DIR       = os.path.join(_BASE_DIR, "../site")

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080
SERVER_URL  = f"http://localhost:{SERVER_PORT}"

# ----------------------------------------------------------------
# Raccourcis pour certains éléments 
# ----------------------------------------------------------------

# Chemin absolu vers l'image placeholder (ne dépend plus du CWD)
PLACEHOLDER_IMAGE = str(APP_ROOT / "image" / "placeholder.png")

INVENTORY_ICON_SIZE = QSize(24, 24)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".PNG"}