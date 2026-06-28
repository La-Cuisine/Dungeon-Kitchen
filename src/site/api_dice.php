<?php
session_start();
header('Content-Type: application/json');

$dice_file = __DIR__ . '/data/latest_roll.json'; // Utilisation du même dossier 'data' que pour la map

// Si on reçoit une requête POST, on enregistre le nouveau jet
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    
    if ($data) {
        $roll_data = [
            'timestamp' => time(),
            'player' => $data['player'] ?? 'MJ',
            'details' => $data['details'], // ex: "3(d6) + 4(d6)"
            'total' => $data['total']
        ];
        file_put_contents($dice_file, json_encode($roll_data));
        echo json_encode(['status' => 'success']);
        exit;
    }
}

// Si on reçoit une requête GET, on renvoie le dernier jet
if (file_exists($dice_file)) {
    echo file_get_contents($dice_file);
} else {
    echo json_encode(['timestamp' => 0]);
}
?>