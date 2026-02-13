<?php
$host = "localhost";
$dbname = "violation";
$user = "root";
$password = ""; // WAMP par défaut

try {
    $conn = new PDO(
        "mysql:host=$host;dbname=$dbname;charset=utf8",
        $user,
        $password
    );
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("❌ Erreur connexion DB : " . $e->getMessage());
}

/*********************************
 * 2️⃣ DOSSIER DES IMAGES
 *********************************/
$folder = "ligne/"; // dossier images
$images = glob($folder . "*.{jpg,jpeg,png}", GLOB_BRACE);

if (!$images) {
    die("❌ Aucun fichier image trouvé.");
}

/*********************************
 * 3️⃣ INSERTION AVEC DATE DE MODIFICATION
 *********************************/
foreach ($images as $image) {
    // Récupérer les informations du fichier
    $file_info = stat($image);
    
    // Le temps de modification est à l'index 9 (mtime)
    $modification_time = $file_info[9];
    
    // Convertir le timestamp en format date/heure
    $date  = date("Y-m-d", $modification_time);
    $temps = date("H:i:s", $modification_time);
    
    // Extraire le nom du fichier sans le chemin
    $photo_name = basename($image);

    $sql = "INSERT INTO voiture (temps, date, lieu, type, photo, prix)
            VALUES (?, ?, ?, ?, ?, ?)";

    $stmt = $conn->prepare($sql);
    $stmt->execute([
        $temps,
        $date,
        "Atlas",
        "Solid Line Line Violation",
        $image,
        700
    ]);
    
    // Optionnel: Afficher les informations pour vérification
    echo "Image: $photo_name<br>";
    echo "Modifié le: $date $temps<br>";
    echo "Timestamp: $modification_time<br>";
    echo "---<br>";
}

echo "✅ Connexion OK — images insérées avec date de modification.";
