<?php
// index.php
// ---------
// Page unique qui affiche la carte du MJ et la tient a jour en interrogeant
// data/map_state.json (ecrit par src/MJ_application/map_sync.py a chaque
// deplacement de la carte ou modification d'une case). Aucune logique PHP
// n'est necessaire ici : le fichier JSON est servi tel quel comme un
// fichier statique par le serveur PHP integre (server.py).
?>
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Carte de campagne</title>
<link rel="stylesheet" href="assets/css/style.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Oswald:wght@500;600&display=swap" rel="stylesheet">
</head>
<body>

  <header class="topbar">
    <div class="topbar__title">
      <span class="topbar__mark">&#10209;</span>
      <span class="topbar__text">Carte de campagne</span>
    </div>
    <div class="status" id="status" aria-live="polite">
      <span class="status__dot" id="statusDot"></span>
      <span class="status__label" id="statusLabel">Connexion…</span>
    </div>
  </header>

  <main class="stage">
    <canvas id="mapCanvas"></canvas>

    <div class="hud hud--coords" id="hudCoords">0 × 0</div>

    <div class="hud hud--controls">
      <button type="button" class="hudbtn" id="zoomOutBtn" aria-label="Zoom arrière">&minus;</button>
      <span class="hudbtn__zoom" id="zoomReadout">100%</span>
      <button type="button" class="hudbtn" id="zoomInBtn" aria-label="Zoom avant">+</button>
      <button type="button" class="hudbtn hudbtn--wide" id="recenterBtn">Recentrer</button>
    </div>
  </main>

<script src="assets/js/map.js"></script>
</body>
</html>
