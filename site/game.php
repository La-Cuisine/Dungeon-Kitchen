<!-- la page qui charge les jeux  -->
<?php
ini_set('session.gc_maxlifetime', 7200); // 2 heures
ini_set('session.cookie_lifetime', 7200);
session_start();

//supression des cookie qui serve à faire passer le hiscore entre le js et le php 
setcookie("hiscore", "", time() - 3600, "/");

// Connexion initiale
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

//gestion du bouton logout
if (isset($_POST['logout'])) {
    session_unset();
    session_destroy();
    header("Location: index.php");
}

//get la liste des jeux depuis la bdd
$stmt = $pdo->query("SELECT * FROM games");
$games = $stmt->fetchAll(PDO::FETCH_ASSOC);

foreach ($games as &$game) {
    $game['id'] = (int)$game['id'];
}

// IDs des jeux qui utilisent un système de difficulté
$gamesWithDifficulty = [4];

$hiscore  = 0;      // pour les jeux classiques
$hiscores = null;   // pour les jeux avec difficulté

try {
    $game_id  = (int)$_GET['id'];
    $username = $_SESSION['username'] ?? null;

    if ($username) {
        if (in_array($game_id, $gamesWithDifficulty)) {
            // jeu avec difficultés -> charge les 3 meilleurs temps
            $hiscores = ['easy' => 0, 'medium' => 0, 'hard' => 0];
            $stmt = $pdo->prepare("
                SELECT difficulty, score
                FROM highscores
                WHERE game_id = ? AND player_name = ?
            ");
            $stmt->execute([$game_id, $username]);
            foreach ($stmt->fetchAll() as $row) {
                if (isset($hiscores[$row['difficulty']])) {
                    $hiscores[$row['difficulty']] = (int)$row['score'];
                }
            }
        } else {
            // Jeu classique -> meilleur score unique
            $stmt = $pdo->prepare("
                SELECT score
                FROM highscores
                WHERE game_id = ? AND player_name = ?
                ORDER BY score DESC
                LIMIT 1
            ");
            $stmt->execute([$game_id, $username]);
            $result = $stmt->fetch();
            if ($result) {
                $hiscore = (int)$result['score'];
            }
        }
    }
} catch (Exception $e) {
    $hiscore  = 0;
    $hiscores = null;
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $games[$_GET['id'] - 1]['name'] ?></title>
    <link rel="stylesheet" href="./style.css">
    <link rel="stylesheet" href="./<?php echo $_GET['id'] ?>/style.css">
    <script src="./<?php echo $_GET['id'] ?>/script.js" defer></script>
</head>

<body class="game-page">
    <nav>
        <a href="./index.php" class="nav-logo">BIBOU<span>ARCADE</span></a>
        <ul class="nav-links">
            <li><a href="./index.php#jeux">Jeux</a></li>
            <li><a href="./index.php#scores">Scores</a></li>
            <li><a href="./index.php#">Tournois</a></li>
            <li><a href="./index.php#">Communauté</a></li>
        </ul>
        <?php
        if (isset($_SESSION["username"])) {
            echo "<div id='divlogout'>
                    <p> {$_SESSION['username']} </p>
                    <form action='./game.php' method='post' style='display:inline;'>
                        <button type='submit' name='logout' class='deco-btn'>DECONNEXION</button>
                    </form>
                  </div>";
        }
        ?>
    </nav>

    <?php if ($hiscores !== null): ?>
    <script>
        const DB_HISCORES = <?php echo json_encode($hiscores); ?>;
    </script>
    <?php endif; ?>

    <?php include "./{$_GET['id']}/index.php" ?>
</body>

</html>