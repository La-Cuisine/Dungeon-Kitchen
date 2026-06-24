<?php
ini_set('session.gc_maxlifetime', 7200); // 2 heures
ini_set('session.cookie_lifetime', 7200);
session_start();

//gestion du bouton logout
if (isset($_POST['logout'])) {
    session_unset();
    session_destroy();
    header("Location: index.php");
}

try {
    //les information de la base de donnée sont pour se connecter à une base hoster en ligne avec pour host aivencloud, 
    //port 17718, username website, password AVNS_dpjXuViC-5w0UUQqILl
    $pdo = new PDO(
        "mysql:host=mysql-1a5cae60-bibou-arcade.h.aivencloud.com;port=17718;dbname=bibouarcade;charset=utf8mb4",
        "website",
        "AVNS_dpjXuViC-5w0UUQqILl",
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
} catch (PDOException $e) {
    die("Erreur connexion : " . $e->getMessage());
}

//message d'erreur quand on tente de se connecter
$login_error = '';

//verification que le compte exite et accède au données de la bdd
if (!isset($_SESSION['username']) && isset($_POST['username']) && isset($_POST['password'])) {
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$_POST['username']]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($user && password_verify($_POST['password'], $user['password'])) {
        $_SESSION['username'] = $user['username'];
        $_SESSION['user_id'] = $user['id'];
        header("Location: index.php");
        exit;
    } else {
        $login_error = 'Identifiants incorrects.';
    }
}

//inscription, ajoute les donner dans la bdd
if (isset($_POST['register']) && isset($_POST['username']) && isset($_POST['password'])) {
    $hash = password_hash($_POST['password'], PASSWORD_BCRYPT);
    try {
        $stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
        $stmt->execute([$_POST['username'], $hash]);
        $_SESSION['username'] = $_POST['username'];
        $_SESSION['user_id'] = $pdo->lastInsertId();
        header("Location: index.php");
        exit;
    } catch (PDOException $e) {
        $login_error = 'Ce nom d\'utilisateur est déjà pris.';
    }
}

$stmt = $pdo->query("SELECT * FROM games");
$games = $stmt->fetchAll(PDO::FETCH_ASSOC);

foreach ($games as &$game) {
    $game['id'] = (int)$game['id'];
    $game['rating'] = (float)$game['rating'];
}
unset($game);


$stmt = $pdo->query("SELECT * FROM users");
$users = $stmt->fetchAll(PDO::FETCH_ASSOC);

$total_players = count($users);
$total_games = count($games);

// Hall of Fame : top 3 par jeu
// Pour les jeux avec difficulty (game_id dans $gamesWithDifficulty),
// le score est un temps (plus petit = meilleur), on prend le MIN par joueur.
// Pour les autres, score classique (plus grand = meilleur), on prend le MAX.
$gamesWithDifficulty = [4];

$hallOfFame = []; // [ game_id => [ ['player_name', 'score', 'difficulty', 'rank'], ... ] ]

$difficulties = ['easy' => 'Facile', 'medium' => 'Moyen', 'hard' => 'Difficile'];

foreach ($games as $g) {
    $gid = $g['id'];

    if (in_array($gid, $gamesWithDifficulty)) {
        // Jeu avec difficulté : 1 bloc par difficulté, top 3 chacun
        foreach ($difficulties as $diff => $label) {
            $stmt = $pdo->prepare("
                SELECT player_name, MIN(score) AS score
                FROM highscores
                WHERE game_id = ? AND difficulty = ?
                GROUP BY player_name
                ORDER BY score ASC
                LIMIT 3
            ");
            $stmt->execute([$gid, $diff]);
            $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

            if (!empty($rows)) {
                $hallOfFame[$gid . '_' . $diff] = [
                    'rows'   => $rows,
                    'label'  => $label,
                    'game'   => $g,
                    'isTime' => true,
                ];
            }
        }
    } else {
        // Jeu classique : meilleur score par joueur, top 3
        $stmt = $pdo->prepare("
            SELECT player_name, MAX(score) AS score
            FROM highscores
            WHERE game_id = ?
            GROUP BY player_name
            ORDER BY score DESC
            LIMIT 3
        ");
        $stmt->execute([$gid]);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        if (!empty($rows)) {
            $hallOfFame[$gid] = [
                'rows'   => $rows,
                'label'  => null,
                'game'   => $g,
                'isTime' => false,
            ];
        }
    }
}

$rankClasses = ['gold', 'silver', 'bronze'];
$rankEmojis  = ['🥇', '🥈', '🥉'];
?>
<!DOCTYPE html>
<html lang="fr">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIBOUS-ARCADE — Mini Jeux Arcade</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
</head>

<body>

    <nav>
        <a href="#" class="nav-logo">BIBOU<span>ARCADE</span></a>
        <ul class="nav-links">
            <li><a href="#jeux">Jeux</a></li>
            <li><a href="#scores">Scores</a></li>
            <li><a href="#">Tournois</a></li>
            <li><a href="#">Communauté</a></li>
        </ul>
        <?php
        //les bouton de connexion et d'inscription
        if (!isset($_SESSION["username"])) {
            echo '<div id="err-log">' . $login_error . '</div>' .
                '<form action="#" id="connexion-form" style="display: none" method="post">
                    <input type="text" name="username" id="username" placeholder="username" required>
                    <input type="password" name="password" id="password" placeholder="password" required>
                    <input type="submit" name="login" value="CONNEXION" class="connexion-btn">
                    <input type="submit" name="register" value="INSCRIPTION" class="inscription-btn">
                </form>
                <button type="button" class="nav-btn">CONNEXION</button>';
        } else {
            echo "<div id='divlogout'>
                    <p> {$_SESSION['username']} </p>
                    <form method='post' style='display:inline;'>
                        <button type='submit' name='logout' class='deco-btn'>DECONNEXION</button>
                    </form>
                  </div>";
        }
        ?>
    </nav>

    <div class="GrosAcceuil">
        <div class="GrosAcceuil-glow"></div>
        <div class="GrosAcceuil-glow-2"></div>
        <div class="GrosAcceuil-badge">▶ INSERT COIN TO PLAY ◀</div>
        <h1 class="GrosAcceuil-title">
            <span class="line-cyan">JOUE.</span>
            <span class="line-mag">BATS LE SCORE.</span>
            <span>RECOMMENCE.</span>
        </h1>
        <p class="GrosAcceuil-sub"><?= $total_games ?> mini-jeux · <?= $total_players ?> joueurs · gratuit</p>
        <div class="GrosAcceuil-cta">
            <a href="#jeux" class="btn-primary">▶ JOUER MAINTENANT</a>
            <a href="#scores" class="btn-secondary">VOIR LES SCORES</a>
        </div>
    </div>

    <!-- STATS BAR -->
    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-number"><?= $total_games ?></span>
            <span class="stat-label">Jeux disponibles</span>
        </div>
        <div class="stat-item">
            <span class="stat-number"><?= $total_players ?></span>
            <span class="stat-label">Joueurs actifs</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">200</span>
            <span class="stat-label">Parties aujourd'hui</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">24/7</span>
            <span class="stat-label">Toujours en ligne</span>
        </div>
    </div>

    <!-- MARQUEE -->
    <div class="marquee-wrap">
        <div class="marquee-track">
            <?php for ($i = 0; $i < 6; $i++): ?>
                <span class="marquee-item">🎮 TETRIS</span>
                <span class="marquee-item">★ NOUVEAU RECORD : 89,420 PTS</span>
                <span class="marquee-item">🏆 TOURNOI CE WEEK-END</span>
                <span class="marquee-item">👾 Space Invader 40ÈME ANNIVERSAIRE</span>
                <span class="marquee-item">🔥 2048 — MEILLEUR DU MOIS</span>
                <span class="marquee-item">⚡ SERVEURS 100% OPÉRATIONNELS</span>
            <?php endfor; ?>
        </div>
    </div>

    <!-- FEATURED GAME -->
    <div class="featured-banner">
        <div>
            <div class="featured-label">⭐ JEU DE LA SEMAINE</div>
            <div class="featured-title">TETRIS<br>CLASSIQUE</div>
            <p class="featured-desc">Le puzzle game qui a tout inventé. Fais tomber les tetrominos, complète les lignes et dépasse ton record. Simple à apprendre, impossible à maîtriser.</p>
            <a href="game.php?id=1" class="btn-primary">▶ JOUER </a>
        </div>
        <div class="featured-visual" id="tetrisGrid"></div>
    </div>

    <!-- GAMES SECTION -->
    <section id="jeux">
        <div class="section-header">
            <h2 class="section-title">TOUS LES <span>JEUX</span></h2>
            <div class="section-line"></div>
            <a href="#" class="section-link">VOIR TOUT →</a>
        </div>

        <div class="filter-tabs">
            <button class="filter-tab active" onclick="filterGames('all', this)">TOUS</button>
            <button class="filter-tab" onclick="filterGames('Puzzle', this)">PUZZLE</button>
            <button class="filter-tab" onclick="filterGames('Arcade', this)">ARCADE</button>
            <button class="filter-tab" onclick="filterGames('Action', this)">ACTION</button>
        </div>

        <div class="games-grid" id="gamesGrid">
            <!-- affichage des jeux en case pour chaque jeu -->
            <?php foreach ($games as $game): ?>
                <a href="game.php?id=<?= $game['id'] ?>" class="game-card"
                    data-category="<?= $game['category'] ?>"
                    style="--card-color: <?= $game['color'] ?>">
                    <div class="card-top">
                        <div class="card-icon"><?= $game['icon'] ?></div>
                        <div class="card-tag"><?= $game['tag'] ?></div>
                    </div>
                    <div class="card-body">
                        <div class="card-name"><?= htmlspecialchars($game['name']) ?></div>
                        <p class="card-desc"><?= htmlspecialchars($game['description']) ?></p>
                        <div class="card-meta">
                            <div class="card-players"><span><?= $game['players'] ?></span> joueurs</div>
                            <div class="card-rating">★ <?= $game['rating'] ?></div>
                        </div>
                    </div>
                    <button class="card-play-btn">▶ JOUER</button>
                </a>
            <?php endforeach; ?>
        </div>
    </section>

    <!-- HALL OF FAME -->
    <div class="leaderboard" id="scores">
        <div class="lb-header">
            <h2 class="section-title">HALL OF <span>FAME</span></h2>
            <div class="section-line"></div>
        </div>

        <?php if (empty($hallOfFame)): ?>
            <p style="text-align:center; color:var(--dim); padding: 40px 0;">Aucun score enregistré pour l'instant. Soyez le premier !</p>
        <?php else: ?>
            <div class="hof-grid">
                <?php foreach ($hallOfFame as $key => $entry):
                    // Extraction des données de chaque entrée du hall of fame
                    $g      = $entry['game'];    // Infos du jeu
                    $rows   = $entry['rows'];    // Lignes du classement (joueurs + scores)
                    $isTime = $entry['isTime'];  // true = score en secondes, false = score classique
                    $label  = $entry['label'];   // Label optionnel (ex: difficulté)
                ?>
                    <div class="hof-block">
                        <div class="hof-game-title">
                            <!-- icon et difficulté du jeu -->
                            <span class="hof-icon"><?= $g['icon'] ?></span>
                            <?= htmlspecialchars($g['name']) ?>
                            <?php if ($label): ?>
                                <span class="hof-diff-badge"><?= $label ?></span>
                            <?php endif; ?>
                        </div>
                        <table class="lb-table">
                            <thead>
                                <tr>
                                    <!-- label de la case du leaderboard -->
                                    <th>#</th>
                                    <th>JOUEUR</th>
                                    <th><?= $isTime ? 'TEMPS' : 'SCORE' ?></th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- affiche le top 3 avec le rank de chacun -->
                                <?php foreach ($rows as $i => $row): ?>
                                    <tr>
                                        <td><span class="lb-rank <?= $rankClasses[$i] ?? '' ?>"><?= $rankEmojis[$i] ?? ($i + 1) ?></span></td>
                                        <td><?= htmlspecialchars($row['player_name']) ?></td>
                                        <td>
                                            <span class="lb-score">
                                                <?= $isTime ? $row['score'] . 's' : number_format($row['score']) ?>
                                            </span>
                                        </td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>

    <!-- FOOTER -->
    <footer>
        <div class="footer-logo">BIBOU<span>ARCADE</span></div>
        <p class="footer-copy">© <?= date('Y') ?> Bibou-Arcade — Tous droits réservés</p>
        <div class="footer-links">
            <a href="#">CGU</a>
            <a href="#">Contact</a>
            <a href="#">Discord</a>
        </div>
    </footer>
</body>

</html>