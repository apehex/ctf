<?php
include 'otphp/lib/otphp.php';

$totp = new \OTPHP\TOTP("orxxi4c7orxwwzlo");
echo $totp->at(time() + 918);
?>
