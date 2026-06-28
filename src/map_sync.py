"""
map_sync.py
-----------
Synchronise la carte du MJ vers le site web (src/site/) SANS modifier le
moindre fichier de src/MJ_application/ (ni grid.py, ni MJ_gamemode.py).

Principe
--------
install() doit etre appele UNE FOIS, apres la creation de la
QApplication et avant la creation de la fenetre du MJ (MainWindow,
dans MJ_gamemode.py)

Cet appel fait deux choses, toutes deux purement en memoire (rien
n'est ecrit sur disque dans src/MJ_application/) :

  1. On enveloppe la methode existante pour, en plus de son comportement d'origine,
     retenir une reference vers la grille (Grid) qui vient d'etre injectee. 
     set_map() est le point d'injection documente par le commentaire en tete 
     de MJ_gamemode.py ("La grille est injectee depuis gui_fonctions via 
     MainWindow.set_map()"), donc ce point d'accroche unique couvre le flux normal de l'application.
  2. Demarrage d'un thread d'arriere-plan qui relit l'etat de cette
     grille (cases occupees, position, zoom) toutes les
     poll_interval secondes et n'ecrit site/data/map_state.json que si
     quelque chose a reellement change (comparaison d'empreinte), pour
     ne jamais spammer le disque.

Comme ce module ne fait que LIRE les objets Qt depuis un thread separe
(jamais les modifier), et que toute erreur d'IO est silencieusement
absorbee, il ne peut pas faire planter la partie en cours meme si la
structure interne de grid.py changeait legerement plus tard - au pire
la synchronisation s'arrete silencieusement.
"""

from __future__ import annotations

import os
import json
import shutil
import hashlib
import tempfile
import threading
import functools

# ---------------------------------------------------------------------------
# Chemins : src/ est le parent direct de ce fichier, site/ est son frere.
# ---------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_BASE_DIR, "site")
DATA_DIR = os.path.join(SITE_DIR, "data")
ASSETS_DIR = os.path.join(SITE_DIR, "assets", "cells")
STATE_FILE = os.path.join(DATA_DIR, "map_state.json")

DEFAULT_POLL_INTERVAL = 0.4  # secondes entre deux lectures de la grille

_installed = False
_grid_ref: dict = {"grid": None}
_stop_event = threading.Event()
_poll_thread: threading.Thread | None = None

_version = 0
_last_fingerprint = None
_image_url_cache: dict[str, str] = {}  # chemin source absolu -> url relative


# ---------------------------------------------------------------------------
# Activation - aucun fichier de MJ_application n'est touche, tout se fait
# en memoire sur les objets deja charges.
# ---------------------------------------------------------------------------
def install(poll_interval: float = DEFAULT_POLL_INTERVAL) -> None:
    global _installed, _poll_thread

    if _installed:
        return
    _installed = True

    import src.MJ_gamemode.MJ_gamemode as MJ_gamemode  # import local : evite tout cycle

    original_set_map = MJ_gamemode.MainWindow.set_map

    @functools.wraps(original_set_map)
    def patched_set_map(self, scene, world, wall):
        result = original_set_map(self, scene, world, wall)
        _grid_ref["grid"] = world
        _export_if_changed(world)  # export immediat, sans attendre le prochain poll
        return result

    MJ_gamemode.MainWindow.set_map = patched_set_map

    _stop_event.clear()
    _poll_thread = threading.Thread(
        target=_poll_loop, args=(poll_interval,), daemon=True
    )
    _poll_thread.start()


def stop() -> None:
    """Arrete le thread de synchronisation (facultatif, surtout utile en test)."""
    _stop_event.set()


def _poll_loop(interval: float) -> None:
    while not _stop_event.wait(interval):
        grid = _grid_ref.get("grid")
        if grid is not None:
            _export_if_changed(grid)


# ---------------------------------------------------------------------------
# Lecture de l'etat de la grille (lecture seule, aucune ecriture sur les
# objets Qt - on ne fait que lire des attributs simples)
# ---------------------------------------------------------------------------
def _read_cells(grid) -> list[tuple[int, int, str | None, str | None]]:
    cells = []
    for cell in getattr(grid, "atoms", []):
        path = getattr(cell, "Path", None)
        prop_path = getattr(cell, "PropPath", None)
        if not path and not prop_path:
            continue
        # grid.py n'est pas modifie au-dela de l'ajout du calque "prop" :
        # pas de getCoord(), on lit directement l'attribut "prive" _coord
        # (col, row) deja pose par Grid.__init__.
        coord = getattr(cell, "_coord", (None, None))
        cells.append((coord[0], coord[1], path, prop_path))
    return cells

def _read_tokens(grid) -> list[dict]:
    tokens = []
    # On parcourt les enfants attachés à la grille
    for item in grid.childItems():
        # Si l'objet est un de nos pions (Token)
        if type(item).__name__ == "Token":
            pos = item.pos()
            color = item.brush().color().name()
            size = item.rect().width()
            tokens.append({
                "x": round(pos.x(), 2),
                "y": round(pos.y(), 2),
                "color": color,
                "size": round(size, 2)
            })
    return tokens


def _fingerprint(grid, cells, tokens) -> tuple:
    pos = grid.pos()
    return (
        grid.n,
        grid.s_cell,
        round(pos.x(), 3),
        round(pos.y(), 3),
        round(grid.scale(), 5),
        tuple(sorted(cells)),
        tuple(sorted((t["x"], t["y"], t["color"]) for t in tokens)) # On surveille les pions
    )


def _export_if_changed(grid) -> None:
    global _last_fingerprint

    if grid is None:
        return

    try:
        cells = _read_cells(grid)
        tokens = _read_tokens(grid) # Lecture
        fingerprint = _fingerprint(grid, cells, tokens) # Hash
    except Exception:
        return

    if fingerprint == _last_fingerprint:
        return
    _last_fingerprint = fingerprint

    _write_export(grid, cells, tokens) # Export


# ---------------------------------------------------------------------------
# Copie des images + ecriture JSON (identique en esprit a la 1re version,
# simplement invoque depuis le poll plutot que depuis grid.py)
# ---------------------------------------------------------------------------
def _ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)


def _register_image(path: str) -> str | None:
    if not path:
        return None

    abs_path = os.path.abspath(path)
    cached = _image_url_cache.get(abs_path)
    if cached is not None:
        return cached

    if not os.path.isfile(abs_path):
        return None

    try:
        _ensure_dirs()
        ext = os.path.splitext(abs_path)[1].lower()
        digest = hashlib.sha1(abs_path.encode("utf-8")).hexdigest()[:16]
        dest_name = f"{digest}{ext}"
        dest_path = os.path.join(ASSETS_DIR, dest_name)
        if not os.path.isfile(dest_path):
            shutil.copyfile(abs_path, dest_path)
    except OSError:
        return None

    url = f"assets/cells/{dest_name}"
    _image_url_cache[abs_path] = url
    return url


def _atomic_write_json(data: dict) -> None:
    try:
        _ensure_dirs()
        fd, tmp_path = tempfile.mkstemp(
            dir=DATA_DIR, prefix=".map_state_", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp_path, STATE_FILE)
        except OSError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    except OSError:
        pass


def _write_export(grid, cells, tokens) -> None:
    global _version

    out_cells = []
    for col, row, path, prop_path in cells:
        entry = {"col": col, "row": row}

        if path:
            url = _register_image(path)
            if url is not None:
                entry["image"] = url

        if prop_path:
            prop_url = _register_image(prop_path)
            if prop_url is not None:
                entry["prop"] = prop_url

        # n'exporte la case que si au moins une des deux images a pu
        # etre resolue (sinon entry ne contient que col/row, inutile)
        if "image" in entry or "prop" in entry:
            out_cells.append(entry)

    pos = grid.pos()
    _version += 1
    data = {
        "version": _version,
        "n": grid.n,
        "s_cell": grid.s_cell,
        "pos": {"x": pos.x(), "y": pos.y()},
        "scale": grid.scale(),
        "cells": out_cells,
        "tokens": tokens,
    }
    _atomic_write_json(data)