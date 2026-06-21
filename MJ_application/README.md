# Dungeons-Kitchen

<h2>Fichier test:</h2>
-designer pyside: dossier pour utiliser QtDesigner et conceptualiser l'interface <br>
-test zoom: fichier pour zoomer sur une interface pyside avec la molette de la souris <br>
-zoomlinechart: dossier contenant des fichers pour zoomer sur un graphe pyside <br>
-draw_on_image.py: fichier pour dessiner sur une image <br>
-gui.py: première version de l'UI (version obselète mais conservé pour regarder l'implémentation initiale) <br>


<h2>Architecture finale (idée en cours):</h2>
-ui.py: fichier contenant le code de l'UI de QtDesigner <br>
-function.py: fichier rassemblant toutes les fonctions pour manipuler l'interface graphique <br>
-main.py: fichier main du projet <br>
-image: dossier contenant l'ensemble des images utilisées pour l'UI


<h2>Autre</h2>
Dans le cas où quelqu'un veut manipuler le fichier QtDesigner (designer pyside):

<h3>Dépendance:</h3>
-pyside6: pip install PySide6 <br>
-librairie custom de KhamisiKibet: pip install QT-PyQt-PySide-Custom-Widgets <br>

<h3>Dans le fichier designer pyside:</h3>
-ui: contient le fichier .ui pour QtDesigner <br>
-src: une traduction automatique du fichier .ui en .py <br>
-image: dossier contenant l'ensemble des images utilisées pour l'UI <br>
-Ignore tous les autres dossiers <br>

<h3>Instruction</h3>
-Dans un terminal, taper "pyside6-designer" pour ouvrir l'interface QtDesigner puis ouvrir le fichier .ui dans le dossier "ui" <br>
-Dans un autre terminal, taper "Custom_Widgets --monitor-ui ui" pour automatiquement convertir le fichier .ui en .py à chaque sauvegarde du fichier .ui dans QtDesigner <br>
-Lorsque que tu es satisfait du résultat, copie tout le contenue du fichier .py dans le fichier ui.py qui est dans le dossier principal <br>
-Lancé la commande "make run"


Pour Samy (ToDo):<br>
-Pour manipuler un widget: self.ui.widget_name<br>
-Rendre le chat fonctionnelle (il n'est pas relier)<br>
-Gerer les autres fonction ui (pas besoin de faire les fonctions avec le serveur pour l'instant sauf si t'as le temps). Ex: _apply_dark_theme et btn_style<br>
