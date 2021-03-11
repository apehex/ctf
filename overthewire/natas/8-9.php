<?php
$encoded_secret = "3d3d516343746d4d6d6c315669563362";
function encode_secret($secret) {
    return bin2hex(strrev(base64_encode($secret)));
}
function decode_secret($secret) {
    return base64_decode(strrev(hex2bin($secret)));
}
echo("es:       ".$encoded_secret."\r\n");
echo("D(es):    ".base64_decode(strrev(hex2bin($encoded_secret)))."\r\n");
echo("E(D(es)): ".encode_secret(decode_secret($encoded_secret))."\r\n");
?>
