<?php

$hash = crypt('heyhey', '$1$🧂llol$');
$output = exec("/usr/bin/python test.py {$_POST['delim']}");
echo $hash;
echo "\n$output";

?>
