<?php
ini_set('session.gc_maxlifetime', 7200);
session_start();
header('Content-Type: application/json');
header('Cache-Control: no-store');
echo json_encode(['logged_in' => isset($_SESSION['username'])]);
