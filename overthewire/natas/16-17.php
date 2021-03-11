<?php
$key="$(cut -c2 < /etc/natas_webpass/natas17)";
if(preg_match('/[;|&`\'"]/',$key)) {
    print "Input contains an illegal character!";
} else {
    echo("grep -i \"$key\" dictionary.txt");
}
?>
