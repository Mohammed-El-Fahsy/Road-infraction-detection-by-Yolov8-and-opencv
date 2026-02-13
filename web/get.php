<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");

$conn = new mysqli("localhost", "root", "", "violation");

if ($conn->connect_error) {
    die(json_encode(["error" => "DB connection failed"]));
}

$sql = "SELECT temps, date, lieu, type, prix, photo FROM voiture ORDER BY id DESC";
$result = $conn->query($sql);

$data = [];

while ($row = $result->fetch_assoc()) {
    $data[] = $row;
}

echo json_encode($data);
$conn->close();
