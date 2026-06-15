#	 			Makefile – PHP Server Launcher
# Ce Makefile centralise toutes les opérations du projet.
# Le projet est maintenant divisé en deux fichiers Python distincts :
#
#   server.py  → Logique du serveur PHP (subprocess, chemins, config)
#                Aucune dépendance graphique. Peut être importé seul.
#
#   gui.py     → Interface graphique PySide6. Importe server.py.
#                Point d'entrée principal de l'application.
#
# Commandes disponibles :
#   make run          → Lance l'interface graphique (gui.py)
#   make server       → Lance uniquement le serveur PHP (server.py en mode CLI(Command Line Interface))
#   make build        → Compile l'exécutable avec PyInstaller (point d'entrée : gui.py)
#   make clean-build  → Supprime les artefacts de compilation (conserve dist/)
#   make clean        → Supprime TOUT ce qui a été généré
#   make help         → Affiche ce tableau d'aide (défaut)
#
# Prérequis :
#   - Python 3.10+ avec `python3` accessible dans le PATH
#   - PySide6     : pip install PySide6
#   - PyInstaller : pip install pyinstaller



# 				Variables de configuration

# Interpréteur Python utilisé pour toutes les commandes.
PYTHON = python

# Script principal de l'interface graphique.
# C'est le point d'entrée de l'application et la cible de PyInstaller.
GUI_SCRIPT = main.py

# Module serveur autonome (sans GUI).
# Peut être lancé seul pour tester le serveur sans interface graphique.
SERVER_SCRIPT = server.py

# Nom de l'exécutable final produit par PyInstaller.
# Définit aussi le nom du sous-dossier dans dist/.
APP_NAME = PHPServerLauncher

# Dossier de sortie de PyInstaller contenant l'exécutable prêt à distribuer.
# Structure : dist/PHPServerLauncher/PHPServerLauncher[.exe]
DIST_DIR = dist

# Dossier temporaire créé par PyInstaller pendant la compilation.
# Contient bytecode, bibliothèques extraites et fichiers intermédiaires.
# Supprimable sans risque après une compilation réussie.
BUILD_DIR = build

# Fichier .spec généré par PyInstaller décrivant comment assembler l'application.
# Peut être conservé pour personnaliser des compilations futures.
SPEC_FILE = $(APP_NAME).spec



# .PHONY – cibles sans fichier correspondant sur le disque

# Déclarer les cibles comme .PHONY empêche Make de les confondre avec des
# fichiers du même nom qui pourraient exister dans le répertoire du projet.
.PHONY: run server build clean-build clean help



# Cible par défaut : affiche l'aide quand `make` est lancé sans argument

# La première cible du Makefile est exécutée par défaut.
# On la nomme `help` pour éviter d'exécuter accidentellement une opération.
.DEFAULT_GOAL := help



# run – Lance l'interface graphique PySide6 (gui.py)

# gui.py importe automatiquement server.py au démarrage.
# L'interface graphique permet de démarrer/arrêter le serveur PHP
# et d'en suivre les logs en temps réel.
#
# Usage :
#   make run
run:
	@echo "==> Lancement de l'interface graphique ($(GUI_SCRIPT))..."
# Exécute gui.py avec l'interpréteur Python défini dans la variable PYTHON.
# gui.py importe server.py, qui doit donc se trouver dans le même dossier.
	$(PYTHON) $(GUI_SCRIPT)



# server – Lance uniquement le serveur PHP en ligne de commande (sans GUI)

# Utile pour tester rapidement que le serveur PHP fonctionne
# sans avoir besoin de l'interface graphique PySide6.
#
# server.py est exécuté directement ; son bloc `if __name__ == "__main__"`
# démarre le serveur et affiche les logs dans le terminal.
#
# Usage :
#   make server
server:
	@echo "==> Lancement du serveur PHP en mode CLI ($(SERVER_SCRIPT))..."
# Lance server.py seul, sans interface graphique.
# Les logs PHP s'affichent directement dans ce terminal.
# Appuyez sur Ctrl+C pour arrêter le serveur.
	$(PYTHON) $(SERVER_SCRIPT)



# build – Compile gui.py en exécutable autonome avec PyInstaller

# PyInstaller analyse gui.py, résout toutes ses dépendances (PySide6, server.py…)
# et les empaquète dans dist/PHPServerLauncher/.
#
# Options PyInstaller utilisées :
#   --onedir      : Produit un dossier contenant l'exe + ses dépendances.
#                   Plus rapide au démarrage que --onefile sur Windows.
#   --windowed    : Masque la console noire Windows en mode GUI pur.
#                   Supprimez cette option pour garder la console visible.
#   --name        : Nom de l'exécutable et du dossier de sortie dans dist/.
#   --noconfirm   : Écrase dist/ sans demander de confirmation.
#   --add-data    : Inclut server.py dans l'exécutable.
#                   Syntaxe Linux/macOS : src:dest (séparateur :)
#                   Syntaxe Windows     : src;dest (séparateur ;)
#                   server.py est déposé à la racine de l'exécutable (.).
#
# Résultat :
#   dist/PHPServerLauncher/PHPServerLauncher        (Linux/macOS)
#   dist\PHPServerLauncher\PHPServerLauncher.exe    (Windows)
#
# Usage :
#   make build
build:
	@echo "==> Compilation de $(GUI_SCRIPT) avec PyInstaller..."
# Lance PyInstaller avec les options définies ci-dessus.
# server.py est inclus via --add-data car il est importé par gui.py
# et PyInstaller ne le détecterait pas toujours automatiquement.
# Séparateur --add-data : "src;dest" sur Windows (au lieu de "src:dest" sur Linux/macOS)
	python -m PyInstaller --onedir --windowed --name $(APP_NAME) --noconfirm --add-data "$(SERVER_SCRIPT);." $(GUI_SCRIPT)
	@echo ""
	@echo "==> Compilation terminée avec succès !"
	@echo "    Exécutable disponible dans : $(DIST_DIR)/$(APP_NAME)/"
	@echo ""
	@echo "    +-- AVANT DE DISTRIBUER ----------------------------------+"
	@echo "    | Copiez ces dossiers dans dist/$(APP_NAME)/ :            |"
	@echo "    |   php-portable/  -> binaire PHP (php.exe ou php)        |"
	@echo "    |   site/          -> fichiers source du site web         |"
	@echo "    +---------------------------------------------------------+"



# clean-build – Supprime les artefacts de compilation, conserve dist/

# Après une compilation réussie, les fichiers dans build/ et le .spec ne sont
# plus nécessaires pour exécuter ou distribuer l'application.
# Cette cible libère de l'espace disque tout en gardant l'exécutable final.
#
# Supprimé :
#   build/          → Fichiers intermédiaires de PyInstaller
#   *.spec          → Fichier de spécification PyInstaller
#   __pycache__/    → Dossiers de cache bytecode Python (créés par Python)
#   *.pyc           → Fichiers bytecode compilés (.pyc)
#
# Conservé :
#   dist/           → Exécutable final (ne pas supprimer si vous le distribuez)
#   server.py       → Module serveur PHP
#   gui.py          → Interface graphique
#   Makefile        → Ce fichier
#   php-portable/   → Binaire PHP portable
#   site/           → Fichiers du site web
#
# Usage :
#   make clean-build
clean-build:
	@echo "==> Nettoyage des artefacts de compilation (dist/ conservé)..."
# Supprime le dossier build/ (commande Windows)
	if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR)
# Supprime le fichier .spec généré automatiquement par PyInstaller
	if exist $(SPEC_FILE) del /f /q $(SPEC_FILE)
# Supprime tous les dossiers __pycache__ récursivement (Windows)
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
# Supprime tous les fichiers .pyc récursivement (Windows)
	del /s /q *.pyc 2>nul || exit 0
	@echo "==> Nettoyage partiel terminé. L'exécutable dans dist/ est conservé."



# clean – Supprime TOUT ce qui a été généré (nettoyage complet)

# Remet le projet dans l'état d'un dépôt Git fraîchement cloné.
# Utile avant un commit, pour partager le code source sans binaires,
# ou pour repartir d'une compilation complètement propre.
#
# Supprimé (en plus de ce que clean-build supprime) :
#   dist/           → Dossier contenant l'exécutable compilé
#
# ⚠ ATTENTION : l'exécutable dans dist/ sera PERDU définitivement.
#               Utilisez `make clean-build` pour le conserver.
#
# Usage :
#   make clean
clean:
	@echo "==> Nettoyage complet (build/ + dist/ supprimés)..."
# Supprime le dossier build/ (fichiers intermédiaires de PyInstaller)
	if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR)
# Supprime le dossier dist/ et l'exécutable qu'il contient (⚠ irréversible)
	if exist $(DIST_DIR) rmdir /s /q $(DIST_DIR)
# Supprime le fichier .spec de PyInstaller
	if exist $(SPEC_FILE) del /f /q $(SPEC_FILE)
# Supprime tous les dossiers __pycache__ récursivement (Windows)
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
# Supprime tous les fichiers .pyc récursivement (Windows)
	del /s /q *.pyc 2>nul || exit 0
	@echo "==> Nettoyage complet terminé. Le projet est dans son état initial."



# help – Affiche le tableau récapitulatif des commandes disponibles

# Cible par défaut (.DEFAULT_GOAL). Exécutée quand `make` est lancé sans cible.
# Fournit une référence rapide de toutes les opérations possibles.
#
# Usage :
#   make
#   make help
help:
	@echo ""
	@echo "+------------------------------------------------------------------+"
	@echo "|              PHP Server Launcher - Makefile Help                 |"
	@echo "+------------------------------------------------------------------+"
	@echo "|  Fichiers du projet :                                            |"
	@echo "|    server.py -> Logique serveur PHP (sans GUI, importable seul)  |"
	@echo "|    gui.py    -> Interface graphique PySide6 (importe server.py)  |"
	@echo "+------------------------------------------------------------------+"
	@echo "|  Commandes :                                                     |"
	@echo "|    make run          Lance l'interface graphique (gui.py)        |"
	@echo "|    make server       Lance uniquement le serveur PHP (CLI)       |"
	@echo "|    make build        Compile l'exécutable avec PyInstaller       |"
	@echo "|    make clean-build  Supprime build/ et .spec (conserve dist/)   |"
	@echo "|    make clean        Supprime TOUT (build/ + dist/)              |"
	@echo "|    make help         Affiche ce message (défaut)                 |"
	@echo "+------------------------------------------------------------------+"
	@echo ""