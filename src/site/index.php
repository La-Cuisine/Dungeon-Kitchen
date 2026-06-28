<?php
// Démarrage de la session PHP
session_start();

// Chemins relatifs vers les dossiers de sauvegarde (depuis src/site/ vers local/)
$local_dir = __DIR__ . '/../../local/';
$players_dir = $local_dir . 'Players/';
$pc_dir = $local_dir . 'Sheets/PC/';

// Création des dossiers s'ils n'existent pas
if (!is_dir($players_dir)) mkdir($players_dir, 0777, true);
if (!is_dir($pc_dir)) mkdir($pc_dir, 0777, true);

$error = '';

// 1. GESTION DE LA DÉCONNEXION
if (isset($_GET['action']) && $_GET['action'] === 'logout') {
  session_destroy();
  header("Location: index.php");
  exit;
}

// 2. GESTION DE L'INSCRIPTION
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['register'])) {
  $id = preg_replace('/[^a-zA-Z0-9_-]/', '', $_POST['id']); // Sécurisation de l'ID
  $name = htmlspecialchars($_POST['name']); // Pseudo du joueur
  $pc_name = htmlspecialchars($_POST['pc_name']); //  Récupération du nom du PC
  $password = password_hash($_POST['password'], PASSWORD_DEFAULT); // Hash sécurisé du mot de passe

  $player_file = $players_dir .  $id . '.xml';

  $safe_pc_name = preg_replace('/[^a-zA-Z0-9_-]/', '_', $pc_name);
  $pc_file = $pc_dir . $safe_pc_name . '.xml';

  if (file_exists($player_file)) {
    $error = "Cet ID est déjà utilisé.";
  } else {
    // Création du fichier XML du Joueur (Player)
    $player_xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?><Player></Player>');
    $player_xml->addAttribute('ID', $id);
    $player_xml->addAttribute('name', $name);
    $player_xml->addAttribute('password', $password);
    $player_xml->addAttribute('pc_file', basename($pc_file));
    $player_xml->asXML($player_file);

    // Création du fichier XML du Personnage (PC) conforme à save.py
    $pc_xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?><PC></PC>');
    $pc_xml->addAttribute('ID', $id);
    $pc_xml->addAttribute('name', $pc_name); // On utilise $pc_name au lieu de $name
    $pc_xml->addAttribute('description', '');
    $pc_xml->addAttribute('image', '');
    $pc_xml->addChild('inventory');
    $pc_xml->addChild('skills');

    // Création du bloc stats avec ses couples enfants
    $stats = $pc_xml->addChild('stats');
    $stat_list = ['HP', 'STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'];

    foreach ($stat_list as $stat_name) {
      $couple = $stats->addChild('couple');
      $couple->addAttribute('stat', $stat_name);
      $couple->addAttribute('value', '0');
    }

    // Sauvegarde du fichier XML formaté proprement (avec indentation)
    $dom = new DOMDocument('1.0');
    $dom->preserveWhiteSpace = false;
    $dom->formatOutput = true;
    $dom->loadXML($pc_xml->asXML());
    $dom->save($pc_file);

    // Connexion automatique après l'inscription
    $_SESSION['player_id'] = $id;
    $_SESSION['player_name'] = $name;
    $_SESSION['pc_file'] = basename($pc_file);
    header("Location: index.php");
    exit;
  }
}

// 3. GESTION DE LA CONNEXION
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
  $id = preg_replace('/[^a-zA-Z0-9_-]/', '', $_POST['id']);
  $password = $_POST['password'];
  $player_file = $players_dir  . $id . '.xml';

  if (file_exists($player_file)) {
    $player_xml = simplexml_load_file($player_file);
    if (password_verify($password, (string)$player_xml['password'])) {
      $_SESSION['player_id'] = $id;
      $_SESSION['player_name'] = (string)$player_xml['name'];
      $_SESSION['pc_file'] = (string)$player_xml['pc_file'];
      header("Location: index.php");
      exit;
    } else {
      $error = "Mot de passe incorrect.";
    }
  } else {
    $error = "ID introuvable.";
  }
}

// ============================================================================
// AFFICHAGE HTML (Routeur d'interface)
// ============================================================================
$pc_loaded = false;
if (isset($_SESSION['pc_file'])) {
  $pc_xml_path = $pc_dir . $_SESSION['pc_file'];
  if (file_exists($pc_xml_path)) {
    $pc_data = simplexml_load_file($pc_xml_path);
    $pc_loaded = true;
  }
}
?>
<!DOCTYPE html>
<html lang="fr">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <title>Dungeon Kitchen - Campagne</title>
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

    <?php if (isset($_SESSION['player_id'])): ?>
      <div class="status" id="status" aria-live="polite">
        <span style="color: var(--text-bone); margin-right: 15px;">Joueur: <?= htmlspecialchars($_SESSION['player_name']) ?></span>
        <span class="status__dot" id="statusDot"></span>
        <span class="status__label" id="statusLabel">Connexion…</span>

        <?php if ($pc_loaded && isset($pc_data)): ?>
          <button type="button" class="hudbtn hudbtn--wide" id="toggleSheetBtn" style="margin-left: 10px;">Fiche / Cacher</button>
        <?php endif; ?>

        <a href="?action=logout" class="hudbtn hudbtn--wide" style="margin-left: 10px; text-decoration: none;">Quitter</a>
      </div>
    <?php endif; ?>
  </header>

  <?php if (!isset($_SESSION['player_id'])): ?>
    <main class="auth-stage">

      <div class="auth-card">
        <h2>Connexion</h2>
        <?php if ($error) echo "<div class='auth-error'>$error</div>"; ?>
        <form method="POST" action="index.php">
          <div class="auth-form-group">
            <label for="login_id">ID Joueur</label>
            <input type="text" id="login_id" name="id" required>
          </div>
          <div class="auth-form-group">
            <label for="login_pwd">Mot de passe</label>
            <input type="password" id="login_pwd" name="password" required>
          </div>
          <button type="submit" name="login" class="auth-btn">Rejoindre la table</button>
        </form>
      </div>

      <div class="auth-card">
        <h2>Créer un profil</h2>
        <form method="POST" style="display: flex; flex-direction: column; gap: 10px; margin-top: 20px;">
          <h3>Nouvel aventurier</h3>
          <input type="text" name="id" placeholder="Identifiant (sans espaces)" required
            style="background: var(--bg-panel); color: var(--text-bone); border: 1px solid var(--bg-panel-edge); padding: 8px;">
          <input type="text" name="name" placeholder="Votre pseudo de Joueur" required
            style="background: var(--bg-panel); color: var(--text-bone); border: 1px solid var(--bg-panel-edge); padding: 8px;">
          <input type="text" name="pc_name" placeholder="Nom de votre Personnage" required
            style="background: var(--bg-panel); color: var(--text-bone); border: 1px solid var(--bg-panel-edge); padding: 8px;">
          <input type="password" name="password" placeholder="Mot de passe" required
            style="background: var(--bg-panel); color: var(--text-bone); border: 1px solid var(--bg-panel-edge); padding: 8px;">
          <button type="submit" name="register"
            style="background: var(--text-bone); color: var(--bg-base); padding: 8px; border: none; font-weight: bold; cursor: pointer;">
            Créer un compte
          </button>
        </form>
      </div>

    </main>
  <?php else: ?>
    <main class="stage">
      <div class="hud hud--controls" style="bottom: 16px; left: 16px; right: auto; display: flex; gap: 8px; align-items: center;">
        <select id="diceSelect" style="background: var(--bg-panel, #2a2520); color: var(--text-bone, #f5ecd8); border: 1px solid var(--ember); padding: 8px; font-family: 'IBM Plex Mono', monospace; font-weight: bold;">
          <option value="100">1d00</option>
          <option value="20">1d20</option>
          <option value="12">1d12</option>
          <option value="10">1d10</option>
          <option value="8">1d8</option>
          <option value="6">1d6</option>
          <option value="4">1d4</option>
        </select>
        <button type="button" class="hudbtn hudbtn--wide" id="rollDiceBtn" style="border-color: var(--ember); color: var(--ember); margin: 0;">Lancer</button>
      </div>

      <!-- Zone de notification des dés -->
      <div class="hud" id="diceNotification" style="display: none; top: 20px; left: 50%; transform: translateX(-50%); padding: 15px; text-align: center; border-color: var(--ember); box-shadow: 0 0 15px var(--ember-glow);">
        <strong id="dicePlayer" style="color: var(--text-bone); font-family: var(--font-display); font-size: 16px;"></strong><br>
        <span id="diceDetails" style="font-size: 14px; color: var(--text-dim);"></span><br>
        <strong id="diceTotal" style="font-size: 24px; color: var(--ember);"></strong>
      </div>

      <canvas id="mapCanvas"></canvas>

      <div class="hud hud--coords" id="hudCoords">0 × 0</div>

      <div class="hud hud--controls">
        <button type="button" class="hudbtn" id="zoomOutBtn" aria-label="Zoom arrière">&minus;</button>
        <span class="hudbtn__zoom" id="zoomReadout">100%</span>
        <button type="button" class="hudbtn" id="zoomInBtn" aria-label="Zoom avant">+</button>
        <button type="button" class="hudbtn hudbtn--wide" id="recenterBtn">Recentrer</button>
      </div>

      <?php if ($pc_loaded && isset($pc_data)): ?>
        <!-- Fiche de personnage intégrée comme élément de l'interface (HUD) -->
        <div class="hud hud--character" id="characterSheet" style="pointer-events: auto; position: absolute; top: 60px; right: 20px; width: 300px; max-height: 80vh; overflow-y: auto; background: var(--bg-panel, #2a2520); padding: 15px; border: 1px solid var(--bg-panel-edge, #4a4540); color: var(--text-bone, #f5ecd8); z-index: 100; overscroll-behavior: contain;">

          <!-- En-tête : Nom et Image -->
          <div class="char-header" style="text-align: center; margin-bottom: 15px;">
            <?php
            $charName = (string)$pc_data['name'];
            $charImg = (string)$pc_data['image'];
            ?>
            <h2 style="margin: 0 0 10px 0; font-family: 'Oswald', sans-serif;"><?= htmlspecialchars($charName) ?></h2>

            <?php if (!empty($charImg)): ?>
              <img src="<?= htmlspecialchars($charImg) ?>" alt="Avatar" style="max-width: 100px; border-radius: 50%; border: 2px solid #e8954a;">
            <?php endif; ?>
          </div>

          <hr style="border-color: #4a4540; margin: 10px 0;">

          <!-- Statistiques -->
          <div class="char-section">
            <h3 style="color: #e8954a; font-family: 'Oswald', sans-serif; margin-bottom: 5px;">Statistiques</h3>
            <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 10px;">
              <?php foreach ($pc_data->stats->couple as $stat): ?>
                <li style="background: rgba(0,0,0,0.3); padding: 5px 8px; border-radius: 4px; font-family: 'IBM Plex Mono', monospace; font-size: 14px;">
                  <strong style="color: #e8954a;"><?= htmlspecialchars((string)$stat['stat']) ?>:</strong>
                  <?= htmlspecialchars((string)$stat['value']) ?>
                </li>
              <?php endforeach; ?>
            </ul>
          </div>

          <hr style="border-color: #4a4540; margin: 15px 0 10px 0;">

          <!-- Inventaire -->
          <div class="char-section">
            <h3 style="color: #e8954a; font-family: 'Oswald', sans-serif; margin-bottom: 5px;">Inventaire</h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
              <?php if ($pc_data->inventory->count() > 0): ?>
                <?php foreach ($pc_data->inventory->Item as $item): ?>
                  <li style="margin-bottom: 10px; background: rgba(0,0,0,0.2); padding: 8px; border-left: 3px solid #666;">
                    <strong style="display: block; font-size: 16px;"><?= htmlspecialchars((string)$item['name']) ?></strong>
                    <em style="font-size: 12px; color: #aaa;"><?= htmlspecialchars((string)$item['type']) ?></em>
                    <p style="margin: 5px 0 0 0; font-size: 14px; font-family: 'IBM Plex Mono', monospace; line-height: 1.3;">
                      <?= htmlspecialchars((string)$item['description']) ?>
                    </p>
                  </li>
                <?php endforeach; ?>
              <?php else: ?>
                <li style="font-size: 14px; color: #aaa;">Inventaire vide.</li>
              <?php endif; ?>
            </ul>
          </div>

          <hr style="border-color: #4a4540; margin: 15px 0 10px 0;">

          <!-- Compétences (Skills) -->
          <div class="char-section">
            <h3 style="color: #e8954a; font-family: 'Oswald', sans-serif; margin-bottom: 5px;">Compétences</h3>
            <ul style="list-style: none; padding: 0; margin: 0;">
              <?php if ($pc_data->skills->count() > 0): ?>
                <?php foreach ($pc_data->skills->Skill as $skill): ?>
                  <li style="margin-bottom: 10px; background: rgba(0,0,0,0.2); padding: 8px; border-left: 3px solid #4a90e2;">
                    <strong style="display: block; font-size: 16px;"><?= htmlspecialchars((string)$skill['name']) ?></strong>
                    <em style="font-size: 12px; color: #aaa;"><?= htmlspecialchars((string)$skill['type']) ?></em>
                    <p style="margin: 5px 0 0 0; font-size: 14px; font-family: 'IBM Plex Mono', monospace; line-height: 1.3;">
                      <?= htmlspecialchars((string)$skill['description']) ?>
                    </p>
                  </li>
                <?php endforeach; ?>
              <?php else: ?>
                <li style="font-size: 14px; color: #aaa;">Aucune compétence.</li>
              <?php endif; ?>
            </ul>
          </div>

        </div>
      <?php endif; ?>

    </main>

    <script src="assets/js/map.js"></script>
  <?php endif; ?>

</body>

</html>