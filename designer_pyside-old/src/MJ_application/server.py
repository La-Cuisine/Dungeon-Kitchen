"""
server.py
---------
Module responsable de toute la logique liée au serveur PHP.

Contenu :
  - Constantes de configuration (chemins, hôte, port)
  - ServerController : démarre et arrête le processus PHP via subprocess


Utilisation autonome (sans GUI) :
    from server import ServerController
    ctrl = ServerController()
    process = ctrl.start()   # démarre php -S 127.0.0.1:8080 -t site/
    ...
    ctrl.stop()              # arrête le processus PHP proprement
"""

# Imports de la bibliothèque standard Python uniquement
import sys           # Détection de la plateforme (Windows vs Linux/macOS)
import os            # Manipulation des chemins de fichiers et dossiers
import subprocess    # Lancement et contrôle de processus externes (PHP)


# Configuration – toutes les constantes modifiables sont regroupées ici

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


# ---------------------------------------------------------------------------
# ServerController – gère le cycle de vie du processus PHP
# ---------------------------------------------------------------------------
class ServerController:
    """
    Encapsule le démarrage et l'arrêt du serveur PHP intégré (`php -S`).

    Ce contrôleur est découplé de l'interface graphique : il ne connaît
    aucun widget Qt. L'interface graphique l'instancie et l'appelle,
    mais le contrôleur fonctionnerait tout aussi bien dans un script CLI.

    Exemple d'usage minimal :
        ctrl = ServerController()
        proc = ctrl.start()     # Lance php -S 127.0.0.1:8080 -t site/
        ctrl.stop()             # Termine le processus proprement
    """

    def __init__(self):
        """
        Initialise le contrôleur sans aucun processus actif.
        L'attribut _process vaut None tant que start() n'a pas été appelé.
        """
        # Référence au processus PHP en cours d'exécution.
        # Vaut None quand le serveur est arrêté.
        self._process: subprocess.Popen | None = None

    # ------------------------------------------------------------------
    def start(self) -> subprocess.Popen:
        """
        Lance le serveur PHP intégré en arrière-plan.

        Commande équivalente dans un terminal :
            php-portable/php.exe -S 127.0.0.1:8080 -t site/

        Les sorties stdout et stderr du processus PHP sont redirigées
        dans un pipe (subprocess.PIPE / subprocess.STDOUT) afin que
        le thread de logs défini dans gui.py puisse les lire ligne par ligne
        et les afficher dans l'interface graphique.

        :return: L'objet subprocess.Popen représentant le processus PHP actif.
        :raises RuntimeError:       Si un serveur est déjà en cours d'exécution.
        :raises FileNotFoundError:  Si le binaire PHP ou le dossier site/ est absent.
        """
        # Empêche de démarrer un second serveur si l'un est déjà actif.
        # poll() retourne None si le processus tourne encore.
        if self._process is not None and self._process.poll() is None:
            raise RuntimeError(
                "Le serveur PHP est déjà en cours d'exécution. "
                "Appelez stop() avant de relancer start()."
            )

        # --- Vérifications préalables ---

        # Contrôle l'existence du binaire PHP avant de tenter de le lancer.
        # Sans cette vérification, subprocess lèverait une FileNotFoundError
        # peu explicite au moment du Popen.
        if not os.path.isfile(PHP_EXECUTABLE):
            raise FileNotFoundError(
                f"Binaire PHP introuvable : {PHP_EXECUTABLE}\n"
                f"Assurez-vous que le dossier 'php-portable/' est présent "
                f"à côté de server.py et qu'il contient '{PHP_BIN}'."
            )

        # Contrôle l'existence du dossier racine du site.
        if not os.path.isdir(SITE_DIR):
            raise FileNotFoundError(
                f"Dossier du site introuvable : {SITE_DIR}\n"
                f"Assurez-vous que le dossier 'site/' est présent "
                f"à côté de server.py."
            )

        # --- Construction de la commande ---

        # Liste des arguments passés à subprocess.Popen :
        #   PHP_EXECUTABLE  → chemin vers php.exe ou php
        #   -S              → active le serveur intégré de PHP
        #   HOST:PORT       → adresse et port d'écoute
        #   -t              → document root (dossier servi)
        #   SITE_DIR        → chemin absolu vers le dossier site/
        cmd = [
            PHP_EXECUTABLE,
            "-S", f"{SERVER_HOST}:{SERVER_PORT}",
            "-t", SITE_DIR,
        ]

        # --- Lancement du processus ---

        # stdout=PIPE  : capture la sortie standard du processus PHP
        #                dans un objet file-like lisible depuis Python.
        # stderr=STDOUT: fusionne la sortie d'erreur dans stdout
        #                pour n'avoir qu'un seul flux à lire.
        # cwd=SITE_DIR : définit le répertoire de travail du processus,
        #                utile si le site PHP utilise des chemins relatifs.
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=SITE_DIR,
        )

        return self._process   # Retourné à l'appelant (gui.py) pour lecture des logs

    # ------------------------------------------------------------------
    def stop(self):
        """
        Arrête proprement le processus PHP s'il est actif.

        Séquence d'arrêt :
          1. terminate() envoie SIGTERM (Unix) ou TerminateProcess (Windows),
             demandant au processus de se terminer gracieusement.
          2. wait() bloque jusqu'à ce que le processus soit réellement terminé,
             évitant ainsi les processus zombies.
          3. La référence _process est remise à None.

        Si le serveur n'est pas en cours d'exécution, la méthode ne fait rien
        (comportement idempotent, sans exception).
        """
        if self._process is not None:
            self._process.terminate()   # Demande l'arrêt au système d'exploitation
            self._process.wait()        # Attend la fin effective du processus
            self._process = None        # Libère la référence pour permettre un redémarrage

    # ------------------------------------------------------------------
    @property
    def is_running(self) -> bool:
        """
        Indique si le serveur PHP est actuellement actif.

        poll() est non-bloquant : il retourne None si le processus tourne
        encore, ou son code de retour (entier) s'il s'est terminé.

        :return: True si le processus existe et est en cours d'exécution.
        """
        # self._process est None → jamais démarré ou déjà arrêté via stop()
        # self._process.poll() non-None → le processus s'est terminé tout seul
        return self._process is not None and self._process.poll() is None
