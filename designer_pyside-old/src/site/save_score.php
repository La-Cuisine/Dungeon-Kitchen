//fichier pour enregistrer les et récupérer les highscores pour l'upddate en temps réel
//sur la page des jeux
<?php
session_start();

try {

    if (!isset($_POST['score']) || !isset($_POST['game_id'])) {
        exit("Missing data");
    }

    if (!isset($_SESSION['username'])) {
        exit("Not logged in");
    }

    $score      = (int) $_POST['score'];
    $game_id    = (int) $_POST['game_id'];
    $username   = $_SESSION['username'];
    $difficulty = $_POST['difficulty'] ?? null;

    //les information de la base de donnée sont pour se connecter à une base hoster en ligne avec pour host aivencloud, 
    //port 17718, username website, password AVNS_dpjXuViC-5w0UUQqILl
    $pdo = new PDO(
        "mysql:host=mysql-1a5cae60-bibou-arcade.h.aivencloud.com;port=17718;dbname=bibouarcade;charset=utf8mb4",
        "website",
        "AVNS_dpjXuViC-5w0UUQqILl",
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );

    if ($difficulty !== null) {
        // jeux avec difficulté (ex: démineur)
        // 1 ligne par (game_id, player_name, difficulty)
        // le score est un TEMPS -> plus petit = meilleur
        $stmt = $pdo->prepare("
            SELECT id, score
            FROM highscores
            WHERE game_id = ? AND player_name = ? AND difficulty = ?
        ");
        $stmt->execute([$game_id, $username, $difficulty]);
        $existing = $stmt->fetch();

        if ($existing) {
            if ($score < $existing['score']) {
                $update = $pdo->prepare("
                    UPDATE highscores
                    SET score = ?
                    WHERE id = ?
                ");
                $update->execute([$score, $existing['id']]);
            }
        } else {
            $insert = $pdo->prepare("
                INSERT INTO highscores (game_id, player_name, score, difficulty)
                VALUES (?, ?, ?, ?)
            ");
            $insert->execute([$game_id, $username, $score, $difficulty]);
        }

    } else {
        // jeux classiques sans difficulté
        // 1 ligne par (game_id, player_name)
        // le score est un POINTS -> plus grand = meilleur
        $stmt = $pdo->prepare("
            SELECT id, score
            FROM highscores
            WHERE game_id = ? AND player_name = ? AND difficulty IS NULL
        ");
        $stmt->execute([$game_id, $username]);
        $existing = $stmt->fetch();

        if ($existing) {
            if ($score > $existing['score']) {
                $update = $pdo->prepare("
                    UPDATE highscores
                    SET score = ?
                    WHERE id = ?
                ");
                $update->execute([$score, $existing['id']]);
            }
        } else {
            $insert = $pdo->prepare("
                INSERT INTO highscores (game_id, player_name, score, difficulty)
                VALUES (?, ?, ?, NULL)
            ");
            $insert->execute([$game_id, $username, $score]);
        }
    }

    echo "OK";
} catch (Exception $e) {
    echo "ERROR: " . $e->getMessage();
}