#	 			Makefile – PHP Server Launcher
# Ce Makefile centralise toutes les opérations du projet.
# Le projet est maintenant divisé en deux fichiers Python distincts :
#
#   server.py  → Logique du serveur PHP (subprocess, chemins, config)
#                Aucune dépendance graphique. Peut être importé seul.
#
#   main.py    → Interface graphique PySide6. Importe server.py.
#                Point d'entrée principal de l'application.
#
# Commandes disponibles :
#   make run          → Lance l'interface graphique (main.py)
#   make server       → Lance uniquement le serveur PHP (server.py en mode CLI)
#   make build        → Compile l'exécutable avec PyInstaller (point d'entrée : main.py)
#   make clean-build  → Supprime les artefacts de compilation (conserve dist/)
#   make clean        → Supprime TOUT ce qui a été généré
#   make help         → Affiche ce tableau d'aide (défaut)
#
# Prérequis :
#   - Python 3.10+ avec `python` accessible dans le PATH
#   - PySide6     : pip install PySide6
#   - PyInstaller : pip install pyinstaller



# 				Détection de l'OS

# On détecte Windows via la variable d'environnement OS (toujours définie sur Windows).
# Sur Linux/macOS, $(OS) est vide ou différent de "Windows_NT".
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
else
    PLATFORM := linux
endif



# 				Variables de configuration

# Interpréteur Python utilisé pour toutes les commandes.
PYTHON = python

# Script principal de l'interface graphique.
GUI_SCRIPT = main.py

# Module serveur autonome (sans GUI).
SERVER_SCRIPT = server.py

# Nom de l'exécutable final produit par PyInstaller.
APP_NAME = PHPServerLauncher

# Dossier de sortie de PyInstaller.
DIST_DIR = dist

# Dossier temporaire créé par PyInstaller pendant la compilation.
BUILD_DIR = build

# Fichier .spec généré par PyInstaller.
SPEC_FILE = $(APP_NAME).spec

# Séparateur --add-data : ";" sur Windows, ":" sur Linux/macOS
ifeq ($(PLATFORM),windows)
    SEP = ;
else
    SEP = :
endif



# .PHONY – cibles sans fichier correspondant sur le disque
.PHONY: run server build clean-build clean help

# Cible par défaut
.DEFAULT_GOAL := help



# run – Lance l'interface graphique PySide6
run:
	@echo "==> Lancement de l'interface graphique ($(GUI_SCRIPT))..."
	$(PYTHON) $(GUI_SCRIPT)



# server – Lance uniquement le serveur PHP en ligne de commande (sans GUI)
server:
	@echo "==> Lancement du serveur PHP en mode CLI ($(SERVER_SCRIPT))..."
	$(PYTHON) $(SERVER_SCRIPT)



# build – Compile main.py en exécutable autonome avec PyInstaller
#
# Options PyInstaller utilisées :
#   --onedir      : Produit un dossier contenant l'exe + ses dépendances.
#   --windowed    : Masque la console noire Windows en mode GUI pur.
#   --name        : Nom de l'exécutable et du dossier de sortie dans dist/.
#   --noconfirm   : Écrase dist/ sans demander de confirmation.
#   --add-data    : Inclut server.py dans l'exécutable.
#                   Syntaxe Linux/macOS : src:dest  (SEP = :)
#                   Syntaxe Windows     : src;dest  (SEP = ;)
build:
	@echo "==> Compilation de $(GUI_SCRIPT) avec PyInstaller (plateforme : $(PLATFORM))..."
	$(PYTHON) -m PyInstaller --onedir --windowed --name $(APP_NAME) --noconfirm --add-data "$(SERVER_SCRIPT)$(SEP)." $(GUI_SCRIPT)
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
#
# Supprimé :
#   build/          → Fichiers intermédiaires de PyInstaller
#   *.spec          → Fichier de spécification PyInstaller
#   __pycache__/    → Dossiers de cache bytecode Python
#   *.pyc           → Fichiers bytecode compilés
#
# Conservé :
#   dist/           → Exécutable final
clean-build:
	@echo "==> Nettoyage des artefacts de compilation (dist/ conservé)..."
ifeq ($(PLATFORM),windows)
	if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR)
	if exist $(SPEC_FILE) del /f /q $(SPEC_FILE)
	for /d /r . %%d in (__pycache__) do @if /i not "%%~fd"=="%CD%\designer pyside\src\__pycache__" if exist "%%d" rmdir /s /q "%%d"
	for /r %%f in (*.pyc) do @if /i not "%%~dpf"=="%CD%\designer pyside\src\__pycache__\" del /f /q "%%f"
else
	rm -rf $(BUILD_DIR)
	rm -f $(SPEC_FILE)
	find . -type d -name "__pycache__" -not -path "*/designer pyside/src/__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -not -path "*/designer pyside/src/__pycache__/*" -delete 2>/dev/null || true
endif
	@echo "==> Nettoyage partiel terminé. L'exécutable dans dist/ est conservé."
	@echo "    (designer pyside/src/__pycache__ préservé)"



# clean – Supprime TOUT ce qui a été généré (nettoyage complet)
#
# ⚠ ATTENTION : l'exécutable dans dist/ sera PERDU définitivement.
#               Utilisez `make clean-build` pour le conserver.
clean:
	@echo "==> Nettoyage complet (build/ + dist/ supprimés)..."
ifeq ($(PLATFORM),windows)
	if exist $(BUILD_DIR) rmdir /s /q $(BUILD_DIR)
	if exist $(DIST_DIR) rmdir /s /q $(DIST_DIR)
	if exist $(SPEC_FILE) del /f /q $(SPEC_FILE)
	for /d /r . %%d in (__pycache__) do @if /i not "%%~fd"=="%CD%\designer pyside\src\__pycache__" if exist "%%d" rmdir /s /q "%%d"
	for /r %%f in (*.pyc) do @if /i not "%%~dpf"=="%CD%\designer pyside\src\__pycache__\" del /f /q "%%f"
else
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	rm -f $(SPEC_FILE)
	find . -type d -name "__pycache__" -not -path "*/designer pyside/src/__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -not -path "*/designer pyside/src/__pycache__/*" -delete 2>/dev/null || true
endif
	@echo "==> Nettoyage complet terminé. Le projet est dans son état initial."
	@echo "    (designer pyside/src/__pycache__ préservé)"



# help – Affiche le tableau récapitulatif des commandes disponibles
help:
	@echo ""
	@echo "+------------------------------------------------------------------+"
	@echo "|              PHP Server Launcher - Makefile Help                 |"
	@echo "+------------------------------------------------------------------+"
	@echo "|  Plateforme détectée : $(PLATFORM)                                     |"
	@echo "+------------------------------------------------------------------+"
	@echo "|  Fichiers du projet :                                            |"
	@echo "|    server.py -> Logique serveur PHP (sans GUI, importable seul)  |"
	@echo "|    main.py   -> Interface graphique PySide6 (importe server.py)  |"
	@echo "+------------------------------------------------------------------+"
	@echo "|  Commandes :                                                     |"
	@echo "|    make run          Lance l'interface graphique (main.py)       |"
	@echo "|    make server       Lance uniquement le serveur PHP (CLI)       |"
	@echo "|    make build        Compile l'exécutable avec PyInstaller       |"
	@echo "|    make clean-build  Supprime build/ et .spec (conserve dist/)   |"
	@echo "|    make clean        Supprime TOUT (build/ + dist/)              |"
	@echo "|    make help         Affiche ce message (défaut)                 |"
	@echo "+------------------------------------------------------------------+"
	@echo ""