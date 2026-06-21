# ===========================================================================
# Makefile – MJ Application (designer_pyside)
# Compatible Windows (cmd via GNU Make) et Linux/macOS
# Cibles : run | build-win | build-linux | clean
# Prérequis : python, pyinstaller  →  pip install pyinstaller
# ===========================================================================

# ── Détection de l'OS ───────────────────────────────────────────────────────
ifeq ($(OS), Windows_NT)
    DETECTED_OS := Windows
    SEP         := ;
    PYTHON      := python
    RM_DIR      := rmdir /s /q
    RM_FILE     := del /f /q
    MKDIR       := mkdir
else
    DETECTED_OS := Linux
    SEP         := :
    PYTHON      := python3
    RM_DIR      := rm -rf
    RM_FILE     := rm -f
    MKDIR       := mkdir -p
    CLEAN_PYC   := find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
                   find . -name "*.pyc" -delete 2>/dev/null; true
endif

# ── Répertoires ─────────────────────────────────────────────────────────────
SRC_DIR   := designer_pyside
DIST_DIR  := dist
BUILD_DIR := build
SPEC_DIR  := .

# ── Nom de l'exécutable ─────────────────────────────────────────────────────
APP_NAME  := MJ_Application

# ── Chemins sources des données à embarquer ─────────────────────────────────
D_IMAGE := $(SRC_DIR)/image
D_JSON  := $(SRC_DIR)/json-styles
D_QSS   := $(SRC_DIR)/Qss
D_SITE  := $(SRC_DIR)/src/site
D_PHP   := $(SRC_DIR)/src/MJ_application/php-portable

# ── Options PyInstaller communes ────────────────────────────────────────────
#    --add-data utilise SEP (';' Windows, ':' Linux)
PYINST_OPTS := \
	--noconfirm \
	--clean \
	--name "$(APP_NAME)" \
	--distpath "$(DIST_DIR)" \
	--workpath "$(BUILD_DIR)" \
	--specpath "$(SPEC_DIR)" \
	--add-data "$(D_IMAGE)$(SEP)image" \
	--add-data "$(D_JSON)$(SEP)json-styles" \
	--add-data "$(D_QSS)$(SEP)Qss" \
	--add-data "$(D_SITE)$(SEP)src/site" \
	--add-data "$(D_PHP)$(SEP)src/MJ_application/php-portable" \
	--hidden-import Custom_Widgets \
	--hidden-import PySide6.QtSvg \
	--hidden-import PySide6.QtXml

# ---------------------------------------------------------------------------
.PHONY: help run build-win build-linux clean

help:
	@echo ""
	@echo "  OS detecte : $(DETECTED_OS)"
	@echo ""
	@echo "  Cibles disponibles :"
	@echo "    make run          - Lance l'application avec Python"
	@echo "    make build-win    - Compile un .exe Windows (--onedir)"
	@echo "    make build-linux  - Compile un binaire Linux  (--onedir)"
	@echo "    make clean        - Supprime build/, dist/ et les .spec"
	@echo ""

# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
run:
	cd $(SRC_DIR) && $(PYTHON) main.py

# ---------------------------------------------------------------------------
# build-win  (peut aussi être lancé depuis Linux si cross-toolchain dispo)
# ---------------------------------------------------------------------------
build-win:
	cd $(SRC_DIR) && pyinstaller \
		$(PYINST_OPTS) \
		--windowed \
		--icon "image/placeholder.png" \
		--onedir \
		main.py
	@echo ""
	@echo "  OK  Executable Windows : $(DIST_DIR)/$(APP_NAME).exe"

# ---------------------------------------------------------------------------
# build-linux
# ---------------------------------------------------------------------------
build-linux:
	cd $(SRC_DIR) && pyinstaller \
		$(PYINST_OPTS) \
		--onedir \
		main.py
	@echo ""
	@echo "  OK  Binaire Linux : $(DIST_DIR)/$(APP_NAME)"

# ---------------------------------------------------------------------------
# clean  –  fonctionne sur Windows (cmd) et Linux
# ---------------------------------------------------------------------------
clean:
ifeq ($(DETECTED_OS), Windows)
	-$(RM_DIR) $(BUILD_DIR) 2>nul
	-$(RM_DIR) $(DIST_DIR)  2>nul
	-$(RM_FILE) $(APP_NAME).spec 2>nul
	-for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
	-del /s /q *.pyc 2>nul
else
	$(RM_DIR) $(BUILD_DIR) $(DIST_DIR) $(APP_NAME).spec
	$(CLEAN_PYC)
endif
	@echo "  OK  Nettoyage termine."