<?php
echo('$time = date("' . addslashes($_GET['format']) . '", strtotime("+10 day +1 hour +53 minute +34 second"));');
?>
