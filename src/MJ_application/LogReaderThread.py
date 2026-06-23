# ---------------------------------------------------------------------------
# Imports de la bibliothèque standard Python
# ---------------------------------------------------------------------------
import subprocess    # Utilisé uniquement pour le type hint subprocess.Popen

from PySide6.QtCore import (
    QThread,         # Classe de base pour créer des threads gérés par Qt
    Signal,          # Décorateur permettant à un thread de communiquer avec l'UI thread
)

# ---------------------------------------------------------------------------
# LogReaderThread – lit les sorties du processus PHP dans un thread Qt dédié
# ---------------------------------------------------------------------------
class LogReaderThread(QThread):
    """
    Thread secondaire chargé de lire en continu la sortie standard (stdout)
    du processus PHP et d'émettre chaque ligne via un signal Qt.

    Cycle de vie :
        1. Instancié avec le Popen du processus PHP (après start())
        2. Démarré avec .start() → run() s'exécute dans le thread secondaire
        3. Arrêté avec .stop() → le drapeau _running passe à False
        4. Attendu avec .wait() dans MainWindow._stop_server()
    """

    # Signal Qt émis chaque fois qu'une nouvelle ligne de log est disponible.
    # La signature `str` indique que chaque émission transporte une chaîne.
    # Le slot connecté (MainWindow._append_log) reçoit cette chaîne en argument.
    new_line = Signal(str)

    def __init__(self, process: subprocess.Popen):
        """
        Initialise le thread avec le processus PHP à surveiller.

        :param process: Objet Popen retourné par ServerController.start().
                        Son attribut stdout est le flux à lire.
        """
        super().__init__()          # Initialise QThread (obligatoire)
        self._process = process     # Processus PHP dont on lit la sortie
        self._running = True        # Drapeau booléen : True = continuer la lecture

    def run(self):
        """
        Boucle principale du thread secondaire, exécutée après .start().
        
        """
        # readline() est bloquant : le thread attend une nouvelle ligne
        # avant de continuer, ce qui évite de consommer du CPU inutilement.
        for line in iter(self._process.stdout.readline, b""):
            if not self._running:   # Vérifie à chaque itération si on doit s'arrêter
                break
            # Décode les bytes en str UTF-8 ; errors="replace" évite les crashs
            # si le processus PHP émet des caractères non-UTF-8.
            # rstrip() supprime le saut de ligne final (\n ou \r\n).
            decoded = line.decode("utf-8", errors="replace").rstrip()
            if decoded:             # Ignore les lignes vides (lignes blanches du log PHP)
                self.new_line.emit(decoded)   # Émet le signal → MainWindow._append_log()

    def stop(self):
        """
        Demande l'arrêt propre du thread en mettant le drapeau à False.
        Le thread s'arrêtera au prochain passage dans la boucle run(),
        c'est-à-dire après la prochaine ligne lue (ou à l'EOF du processus).
        """
        self._running = False       # La boucle dans run() vérifie ce drapeau
