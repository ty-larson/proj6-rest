<html>
<head>
    <title>CIS 322 Brevet REST API Consumer</title>
</head>
<body>
    <h1>Brevet Control Times (REST API Consumer)</h1>

    <h2>All Control Times (JSON: /listAll/json)</h2>
    <ul>
        <?php
        $json = @file_get_contents('http://laptop-service/listAll/json');
        if ($json !== false) {
            $obj = json_decode($json, true);
            $controls = $obj['controls'] ?? [];
            if (empty($controls)) {
                echo "<li>No control times stored yet.</li>";
            } else {
                foreach ($controls as $c) {
                    $open = htmlspecialchars($c['open'] ?? '');
                    $close = htmlspecialchars($c['close'] ?? '');
                    echo "<li>Open: $open | Close: $close</li>";
                }
            }
        } else {
            echo "<li>Could not reach REST API service.</li>";
        }
        ?>
    </ul>

    <h2>Top 3 Open Times (JSON: /listOpenOnly/json?top=3)</h2>
    <ul>
        <?php
        $open_json = @file_get_contents('http://laptop-service/listOpenOnly/json?top=3');
        if ($open_json !== false) {
            $obj = json_decode($open_json, true);
            $controls = $obj['controls'] ?? [];
            foreach ($controls as $c) {
                $open = htmlspecialchars($c['open'] ?? '');
                echo "<li>Open: $open</li>";
            }
        }
        ?>
    </ul>

    <h2>Close Times (CSV: /listCloseOnly/csv)</h2>
    <pre><?php
        $csv = @file_get_contents('http://laptop-service/listCloseOnly/csv');
        echo $csv !== false ? htmlspecialchars($csv) : "Could not load CSV.";
    ?></pre>
</body>
</html>